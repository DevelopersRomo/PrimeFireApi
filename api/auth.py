import logging
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from urllib.parse import parse_qs, unquote, urlsplit

import bcrypt
import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlmodel import Session, select

from bd.dependencies import get_main_db
from core.config import settings
from models.auth_tokens import AuthToken
from models.employees import Employees
from models.tenants import TenantEmployees, TenantLogos, Tenants
from services.notifications.email_functions import send_magic_link_email, send_password_recovery_email

# --- CONFIGURACIÓN ---
# Usar una clave secreta segura en producción
SECRET_KEY = settings.jwt_secret
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300
REFRESH_TOKEN_EXPIRE_DAYS = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

router = APIRouter()
logger = logging.getLogger(__name__)


# --- MODELOS ---
class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str | None = None


class TokenData(BaseModel):
    username: str | None = None


class UserRegister(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    tenant_key: str | None = None  # Opcional - admin lo asignará después


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class AzureRefreshTokenRequest(BaseModel):
    refresh_token: str
    scope: str | None = None


# --- UTILS ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a bcrypt hash."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    # Bcrypt has a 72 byte limit
    password_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(UTC) + expires_delta if expires_delta else datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# --- ENDPOINTS ---


@router.post("/register", response_model=Token)
async def register_user(user_data: UserRegister, db: Session = Depends(get_main_db)):
    """
    Registrar un nuevo usuario externo.
    Si tenant_key está presente, guarda en esa BD. Si no, solo guarda referencia en BD Principal (pendiente de aprobación).
    """
    # Check existing external user in TenantEmployees (main DB)
    existing_external = db.exec(select(TenantEmployees).where(TenantEmployees.email == user_data.email)).first()
    if existing_external:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed_password = get_password_hash(user_data.password)

    # 2. Si tiene tenant_key, verificar que existe y está activo
    if user_data.tenant_key:
        tenant = db.exec(select(Tenants).where(Tenants.db_connection_key == user_data.tenant_key)).first()
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Tenant '{user_data.tenant_key}' not found"
            )
        if not tenant.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Tenant '{user_data.tenant_key}' is not active"
            )

        # Save external user in main DB
        external_user = TenantEmployees(
            email=user_data.email, password_hash=hashed_password, tenant_id=tenant.tenant_id
        )
        db.add(external_user)
        db.commit()
        db.refresh(external_user)

        # Save full user in main DB as well (ignoring tenant DB separation)
        existing_user = db.exec(select(Employees).where(Employees.email == user_data.email)).first()

        if not existing_user:
            # Generate unique AzureOid for external users to avoid UNIQUE constraint violation
            external_oid = str(uuid.uuid4())
            new_employee = Employees(
                email=user_data.email,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                display_name=f"{user_data.first_name} {user_data.last_name}",
                password_hash=hashed_password,
                title="External User",
                azure_oid=external_oid,  # Unique identifier for external users
            )
            db.add(new_employee)
            db.commit()
            db.refresh(new_employee)
        else:
            # Update password if needed
            existing_user.password_hash = hashed_password
            db.add(existing_user)
            db.commit()

        # Automatic login
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token_data = {"sub": user_data.email, "type": "internal"}
        # We don't need tenant_key in token anymore since everything is on main DB
        # But we keep it if needed for other logic, though user said EVERYTHING on main DB
        if user_data.tenant_key:
            token_data["tenant_key"] = user_data.tenant_key

        access_token = create_access_token(data=token_data, expires_delta=access_token_expires)
        refresh_token = create_refresh_token(data={"sub": user_data.email, "tenant_key": user_data.tenant_key})
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "refresh_token": refresh_token,
        }

    # No tenant_key: keep TenantId as NULL (pending approval)
    external_user = TenantEmployees(email=user_data.email, password_hash=hashed_password, tenant_id=None)
    db.add(external_user)
    db.commit()
    db.refresh(external_user)

    # Usuario pendiente - NO dar token de acceso (debe esperar aprobación)
    raise HTTPException(
        status_code=status.HTTP_202_ACCEPTED,
        detail="Registration successful. Your account is pending approval. An administrator will assign you to a tenant shortly.",
    )


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_main_db)):
    """
    Login: Checks TenantEmployees first (main DB).
    If external, determine tenant and validate in that DB.
    """
    # Check TenantEmployees first (main DB)
    external_user = db.exec(select(TenantEmployees).where(TenantEmployees.email == form_data.username)).first()

    if external_user:
        # Usuario externo - validar password
        if not external_user.password_hash or not verify_password(form_data.password, external_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verificar que tenga tenant asignado
        if not external_user.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is pending approval. Please wait for an administrator to assign you to a tenant.",
            )

        # Obtener tenant info
        tenant = db.get(Tenants, external_user.tenant_id)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your tenant assignment is invalid. Please contact an administrator.",
            )

        # Verificar que el tenant no sea PENDING y esté activo
        if tenant.db_connection_key == "PENDING" or not tenant.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is pending approval. Please wait for an administrator to assign you to an active tenant.",
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token_data = {"sub": external_user.email, "type": "internal"}
        if tenant.tenant_id != 1:
            token_data["tenant_key"] = tenant.db_connection_key
        access_token = create_access_token(data=token_data, expires_delta=access_token_expires)
        refresh_token = create_refresh_token(data={"sub": external_user.email, "tenant_key": tenant.db_connection_key})
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "refresh_token": refresh_token,
        }

    # 2. Si no es externo, buscar en Employees de BD Principal (usuarios internos de PrimeFire)
    user = db.exec(select(Employees).where(Employees.email == form_data.username)).first()

    if not user or not user.password_hash or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email, "type": "internal"}, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(data={"sub": user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }


@router.post("/refresh", response_model=Token)
async def refresh_access_token(refresh_data: RefreshTokenRequest, db: Session = Depends(get_main_db)):
    """Refresh internal access token using a refresh token."""
    try:
        payload = jwt.decode(refresh_data.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Validate user status (internal or external)
    external_user = db.exec(select(TenantEmployees).where(TenantEmployees.email == email)).first()
    if external_user:
        if not external_user.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is pending approval. Please wait for an administrator to assign you to a tenant.",
            )

        tenant = db.get(Tenants, external_user.tenant_id)
        if not tenant or tenant.db_connection_key == "PENDING" or not tenant.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is pending approval. Please wait for an administrator to assign you to an active tenant.",
            )

        token_data = {"sub": external_user.email, "type": "internal"}
        if tenant.tenant_id != 1:
            token_data["tenant_key"] = tenant.db_connection_key
        refresh_payload = {"sub": external_user.email, "tenant_key": tenant.db_connection_key}
    else:
        user = db.exec(select(Employees).where(Employees.email == email)).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        token_data = {"sub": user.email, "type": "internal"}
        refresh_payload = {"sub": user.email}

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data=token_data, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(data=refresh_payload)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }


@router.post("/azure/refresh")
async def refresh_azure_token(refresh_data: AzureRefreshTokenRequest):
    """Refresh Azure AD token using refresh token (PKCE authorization code flow)."""
    client_id = settings.FRONTEND_CLIENT_ID or settings.BACKEND_CLIENT_ID
    if not client_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Azure client ID is not configured",
        )

    token_url = f"https://login.microsoftonline.com/{settings.TENANT_ID}/oauth2/v2.0/token"
    scope = refresh_data.scope or " ".join(settings.scopes.keys())

    data = {
        "client_id": client_id,
        "grant_type": "refresh_token",
        "refresh_token": refresh_data.refresh_token,
        "scope": scope,
    }

    if settings.BACKEND_CLIENT_SECRET and client_id == settings.BACKEND_CLIENT_ID:
        data["client_secret"] = settings.BACKEND_CLIENT_SECRET

    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data)

    if response.status_code >= 400:
        detail = (
            response.json()
            if response.headers.get("content-type", "").startswith("application/json")
            else response.text
        )
        raise HTTPException(
            status_code=response.status_code,
            detail=detail,
        )

    return response.json()


# --- PASSWORD RECOVERY & MAGIC LINK ENDPOINTS ---


class PasswordRecoveryRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class MagicLinkRequest(BaseModel):
    email: str


TOKEN_EXPIRE_MINUTES = 15


def _generate_secure_token() -> str:
    """Generate a secure random token."""
    return secrets.token_urlsafe(32)


def _normalize_token_for_lookup(raw_token: str | None) -> str:
    """Normalize token values coming from query/body before DB lookup."""
    candidate = (raw_token or "").strip().strip("\"'<>")
    if not candidate:
        return ""

    decoded = unquote(candidate)

    # Defensive path: some clients may pass full URL or raw query string instead of token value.
    if "token=" in decoded:
        query = urlsplit(decoded).query if "://" in decoded else decoded.lstrip("?")
        extracted_values = parse_qs(query).get("token")
        if extracted_values and extracted_values[0]:
            decoded = unquote(extracted_values[0])

    return decoded.strip().strip("\"'<>")


def _find_user_by_email(db: Session, email: str) -> tuple[Employees | None, TenantEmployees | None]:
    """Find user by email in Employees or TenantEmployees tables."""
    tenant_user = db.exec(select(TenantEmployees).where(TenantEmployees.email == email)).first()
    if tenant_user:
        return None, tenant_user
    internal_user = db.exec(select(Employees).where(Employees.email == email)).first()
    return internal_user, None


def _get_tenant_info(
    db: Session, internal_user: Employees | None, tenant_user: TenantEmployees | None
) -> tuple[str, str]:
    """Resolve the correct frontend app URL and title for a user.

    Returns (app_url, tenant_title):
    - TenantEmployees → use the tenant's URL and title from TenantLogos.
    - Internal Employees → fall back to global APP_URL and "PrimeFire".
    """

    def _force_https(raw_url: str | None) -> str:
        cleaned = (raw_url or "").strip().rstrip("/")
        if not cleaned:
            return ""
        if cleaned.startswith("https://"):
            return cleaned
        if cleaned.startswith("http://"):
            return f"https://{cleaned[len('http://') :]}"
        return f"https://{cleaned}"

    if tenant_user and tenant_user.tenant_id:
        logo = db.exec(
            select(TenantLogos).where(TenantLogos.tenant_id == tenant_user.tenant_id).order_by(TenantLogos.logo_id)
        ).first()
        if logo and logo.url:
            return _force_https(logo.url), logo.title
    return _force_https(getattr(settings, "APP_URL", "")), "PrimeFire"


@router.post("/password-recovery")
async def password_recovery(request: PasswordRecoveryRequest, db: Session = Depends(get_main_db)):
    """
    Request a password recovery email.
    Always returns 200 to prevent email enumeration attacks.
    """
    internal_user, tenant_user = _find_user_by_email(db, request.email)

    if not internal_user and not tenant_user:
        # User not found — still return 200 to prevent enumeration
        return {"message": "If the email exists in our system, you will receive a recovery link."}

    # Determine target user (prefer TenantEmployees for local auth users)
    target_email = tenant_user.email if tenant_user else internal_user.email

    # Invalidate any existing unused recovery tokens for this email
    existing = db.exec(
        select(AuthToken).where(
            AuthToken.email == target_email,
            AuthToken.token_type == "password_recovery",
            AuthToken.used_at.is_(None),
        )
    ).all()
    for tok in existing:
        tok.used_at = datetime.now(UTC)
    db.add_all(existing)
    db.commit()

    # Create new token
    token = _generate_secure_token()
    expires_at = datetime.now(UTC) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    auth_token = AuthToken(
        email=target_email,
        token=token,
        token_type="password_recovery",
        expires_at=expires_at,
    )
    db.add(auth_token)
    db.commit()

    # Send email with tenant-aware URL and title
    app_url, tenant_title = _get_tenant_info(db, internal_user, tenant_user)
    await send_password_recovery_email(to_email=target_email, token=token, app_url=app_url, tenant_title=tenant_title)

    return {"message": "If the email exists in our system, you will receive a recovery link."}


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_main_db)):
    """Reset password using a valid token."""
    token_value = _normalize_token_for_lookup(request.token)

    # Find token
    auth_token = db.exec(
        select(AuthToken).where(
            AuthToken.token == token_value,
            AuthToken.token_type == "password_recovery",
        )
    ).first()

    if not auth_token:
        logger.warning("Password recovery token not found. prefix=%s len=%s", token_value[:8], len(token_value))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or already used token.")

    if auth_token.used_at is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This token has already been used.")

    if auth_token.expires_at < datetime.now(UTC):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="This token has expired. Please request a new one."
        )

    # Find user
    internal_user, tenant_user = _find_user_by_email(db, auth_token.email)
    user = tenant_user or internal_user

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    if not hasattr(user, "password_hash") or user.password_hash is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This user does not use local password authentication. Please sign in with Azure AD.",
        )

    # Update password
    user.password_hash = get_password_hash(request.new_password)
    db.add(user)

    # Mark token as used
    auth_token.used_at = datetime.now(UTC)
    db.add(auth_token)
    db.commit()

    return {"message": "Password updated successfully. You can now sign in."}


@router.post("/magic-link")
async def request_magic_link(request: MagicLinkRequest, db: Session = Depends(get_main_db)):
    """
    Request a magic link email.
    Always returns 200 to prevent email enumeration attacks.
    """
    internal_user, tenant_user = _find_user_by_email(db, request.email)

    if not internal_user and not tenant_user:
        return {"message": "If the email exists in our system, you will receive a login link."}

    target_email = tenant_user.email if tenant_user else internal_user.email

    # Only allow magic link for users with password_hash (local auth users)
    has_local_auth = (tenant_user and tenant_user.password_hash) or (internal_user and internal_user.password_hash)
    if not has_local_auth:
        return {"message": "Si el email existe, recibirás un enlace de acceso."}

    # Invalidate existing unused magic link tokens
    existing = db.exec(
        select(AuthToken).where(
            AuthToken.email == target_email,
            AuthToken.token_type == "magic_link",
            AuthToken.used_at.is_(None),
        )
    ).all()
    for tok in existing:
        tok.used_at = datetime.now(UTC)
    db.add_all(existing)
    db.commit()

    # Create new token
    token = _generate_secure_token()
    expires_at = datetime.now(UTC) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    auth_token = AuthToken(
        email=target_email,
        token=token,
        token_type="magic_link",
        expires_at=expires_at,
    )
    db.add(auth_token)
    db.commit()

    # Send email with tenant-aware URL and title
    app_url, tenant_title = _get_tenant_info(db, internal_user, tenant_user)
    await send_magic_link_email(to_email=target_email, token=token, app_url=app_url, tenant_title=tenant_title)

    return {"message": "If the email exists in our system, you will receive a login link."}


@router.get("/magic-link/verify", response_model=Token)
async def verify_magic_link(token: str = Query(...), db: Session = Depends(get_main_db)):
    """Verify a magic link token and return JWT tokens (auto-login)."""
    token_value = _normalize_token_for_lookup(token)

    auth_token = db.exec(
        select(AuthToken).where(
            AuthToken.token == token_value,
            AuthToken.token_type == "magic_link",
        )
    ).first()

    if not auth_token:
        logger.warning("Magic link token not found. prefix=%s len=%s", token_value[:8], len(token_value))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or already used token.")

    if auth_token.used_at is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This link has already been used.")

    if auth_token.expires_at < datetime.now(UTC):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="This link has expired. Please request a new one."
        )

    # Find user
    internal_user, tenant_user = _find_user_by_email(db, auth_token.email)
    user = tenant_user or internal_user

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")

    # Mark token as used
    auth_token.used_at = datetime.now(UTC)
    db.add(auth_token)
    db.commit()

    # Generate tokens (same as normal login)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    if tenant_user:
        # External user
        tenant = db.get(Tenants, tenant_user.tenant_id)
        token_data = {"sub": tenant_user.email, "type": "internal"}
        if tenant and tenant.tenant_id != 1:
            token_data["tenant_key"] = tenant.db_connection_key
        refresh_payload = {"sub": tenant_user.email, "tenant_key": tenant.db_connection_key if tenant else None}
        access_token = create_access_token(data=token_data, expires_delta=access_token_expires)
        refresh_token = create_refresh_token(data=refresh_payload)
    else:
        # Internal user
        token_data = {"sub": internal_user.email, "type": "internal"}
        access_token = create_access_token(data=token_data, expires_delta=access_token_expires)
        refresh_token = create_refresh_token(data={"sub": internal_user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }
