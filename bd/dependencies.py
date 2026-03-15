from collections.abc import Generator

import jwt  # type: ignore[import-untyped]
from fastapi import HTTPException, Request
from jose import JWTError  # type: ignore[import-untyped]
from jose import jwt as jose_jwt  # type: ignore[import-untyped]
from sqlmodel import Session

from bd.connection import SessionLocal, SessionSync
from bd.multitenancy import ConnectionManager
from core.config import settings

# Reuse secret from auth module
SECRET_KEY = settings.BACKEND_CLIENT_SECRET or "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"


# Dependency function to get DB session
def get_db(request: Request = None) -> Generator[Session, None, None]:
    """
    Get DB session.
    1. Checks X-Tenant-ID header.
    2. Checks tenant_key from Internal JWT token.
    3. Checks if it's an Azure AD token (oid claim) -> Connects to PrimeFire DB (SessionSync).
    4. Otherwise connects to Main DB (DevRomo).
    """
    tenant_key = None
    is_azure_token = False

    # 1. Check header first
    if request:
        tenant_key = request.headers.get("X-Tenant-ID")

        # 2. If no header, try to extract from JWT token
        if not tenant_key:
            auth_header = request.headers.get("Authorization")
            if auth_header:
                try:
                    scheme, token = auth_header.split(" ", 1)
                    if scheme.lower() == "bearer":
                        # Try Internal JWT first
                        try:
                            payload = jose_jwt.decode(
                                token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": True}
                            )
                            tenant_key = payload.get("tenant_key")
                        except (ValueError, JWTError):
                            # Not internal, check if Azure AD
                            try:
                                # Decode without verification just to check claims
                                # Verification happens in require_authentication dependency
                                payload = jwt.decode(token, options={"verify_signature": False})
                                if "oid" in payload:
                                    is_azure_token = True
                            except Exception:
                                pass
                except Exception:
                    pass  # Invalid header format

    if tenant_key:
        try:
            # First verify tenant exists in DB
            from sqlmodel import select

            from models.tenants import Tenants

            main_db = SessionLocal()
            try:
                tenant = main_db.exec(select(Tenants).where(Tenants.DbConnectionKey == tenant_key)).first()
                if not tenant:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Tenant '{tenant_key}' not found in database. Available tenants can be checked at /tenants/list-all",
                    )
                if not tenant.IsActive:
                    raise HTTPException(status_code=400, detail=f"Tenant '{tenant_key}' is not active")
            finally:
                main_db.close()

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
        # Azure AD users go to PrimeFire DB
        db = SessionSync()
    else:
        # Internal users without tenant go to Main DB (DevRomo)
        db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


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
