from collections.abc import Generator

from fastapi import HTTPException, Request
from jose import JWTError  # type: ignore[import-untyped]
from jose import jwt as jose_jwt  # type: ignore[import-untyped]
from sqlmodel import Session

from bd.connection import SessionLocal, SessionPrimeFire
from bd.multitenancy import ConnectionManager
from core.azure_token import looks_like_azure_token, validate_azure_token
from core.config import settings

# Internal JWT signing secret (see core/config.py). No hardcoded fallback.
SECRET_KEY = settings.jwt_secret
ALGORITHM = "HS256"
PRIMEFIRE_EMAIL_DOMAINS = ("@primefire.us", "@primefire.do")


def get_claim_email(payload: dict) -> str | None:
    """Return the best email-like claim from an Azure AD token payload."""
    for claim in ("preferred_username", "upn", "email", "unique_name", "sub"):
        value = payload.get(claim)
        if isinstance(value, str) and "@" in value:
            return value.lower()
    return None


def is_primefire_email(email: str | None) -> bool:
    return bool(email and email.lower().endswith(PRIMEFIRE_EMAIL_DOMAINS))


def get_primefire_session() -> Session:
    """Create a PrimeFire DB session without falling back to the main DB."""
    if SessionPrimeFire is None:
        raise HTTPException(
            status_code=500,
            detail="PRIMEFIRE_DB_SERVER is not configured. Azure AD PrimeFire users cannot be routed safely.",
        )
    return SessionPrimeFire()


def _extract_bearer_token(request: Request | None) -> str | None:
    if not request:
        return None

    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None

    try:
        scheme, token = auth_header.split(" ", 1)
    except ValueError:
        return None

    return token if scheme.lower() == "bearer" else None


def _get_token_route(token: str | None) -> tuple[str | None, bool, str | None]:
    if not token:
        return None, False, None

    try:
        payload = jose_jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": True})
        return payload.get("tenant_key"), False, None
    except (ValueError, JWTError):
        pass

    # Azure AD token: full signature/audience/issuer validation via JWKS
    if looks_like_azure_token(token):
        payload = validate_azure_token(token)
        return None, True, get_claim_email(payload)

    return None, False, None


def _validate_tenant_exists(tenant_key: str) -> None:
    from sqlmodel import select

    from models.tenants import Tenants

    main_db = SessionLocal()
    try:
        tenant = main_db.exec(select(Tenants).where(Tenants.db_connection_key == tenant_key)).first()
        if not tenant:
            raise HTTPException(
                status_code=404,
                detail=f"Tenant '{tenant_key}' not found in database. Available tenants can be checked at /tenants/list-all",
            )
        if not tenant.is_active:
            raise HTTPException(status_code=400, detail=f"Tenant '{tenant_key}' is not active")
    finally:
        main_db.close()


# Dependency function to get DB session
def get_db(request: Request = None) -> Generator[Session, None, None]:
    """
    Get DB session. Tenant routing derives ONLY from the verified bearer token:
    1. tenant_key claim from a verified Internal JWT -> tenant DB.
    2. Verified Azure AD token with @primefire.us/@primefire.do -> PrimeFire DB.
    3. Otherwise -> Main DB (DevRomo).

    NOTE: the X-Tenant-ID header is intentionally ignored (it allowed cross-tenant access).
    """
    tenant_key, is_azure_token, azure_email = _get_token_route(_extract_bearer_token(request))

    if tenant_key:
        try:
            _validate_tenant_exists(tenant_key)
            db = ConnectionManager.get_session(tenant_key)
        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid Tenant ID '{tenant_key}': {e!s}. Check that DB_CONNECTION_{tenant_key.upper()} is set in .env",
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error connecting to tenant '{tenant_key}': {e!s}")
    elif is_azure_token:
        if not is_primefire_email(azure_email):
            raise HTTPException(
                status_code=403,
                detail="Azure AD user is not allowed for this database route.",
            )
        db = get_primefire_session()
    else:
        # Internal users without tenant go to Main DB (DevRomo)
        db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def get_tenant_cache_scope(request: Request = None) -> str:
    """Identificador del tenant del request, para FIRMAR claves de cache.

    Evita fugas cross-tenant: un cache global en memoria nunca debe servir
    datos de un tenant a usuarios de otro. Deriva SOLO del token verificado.
    """
    tenant_key, is_azure_token, _ = _get_token_route(_extract_bearer_token(request))
    if tenant_key:
        return f"tenant:{tenant_key}"
    if is_azure_token:
        return "primefire"
    return "main"


# Dependency function to always get MAIN DB session (ignores tenant headers)
def get_main_db() -> Generator[Session, None, None]:
    """
    Get MAIN database session. Always connects to main DB, ignoring X-Tenant-ID header.
    Use this for operations that must always run on the main database (e.g., TenantLogos).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
