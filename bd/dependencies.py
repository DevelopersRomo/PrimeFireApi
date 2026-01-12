from fastapi import Request, Header, HTTPException
from sqlmodel import Session
from bd.connection import SessionLocal
from bd.multitenancy import ConnectionManager
from jose import jwt as jose_jwt, JWTError
from core.config import settings

# Re-use secret from auth module
SECRET_KEY = settings.BACKEND_CLIENT_SECRET or "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

# Dependency function to get DB session
def get_db(request: Request = None) -> Session:
    """
    Get DB session. Checks X-Tenant-ID header OR tenant_key from JWT token.
    If tenant_key exists, connects to that tenant's DB.
    Otherwise connects to Main DB.
    """
    tenant_key = None
    
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
                        payload = jose_jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": True})
                        tenant_key = payload.get("tenant_key")
                except (ValueError, JWTError, Exception):
                    pass  # Not a valid JWT or not our token, ignore
    
    if tenant_key:
        try:
            # First verify tenant exists in DB
            from models.tenants import Tenants
            from sqlmodel import select
            main_db = SessionLocal()
            try:
                tenant = main_db.exec(select(Tenants).where(Tenants.DbConnectionKey == tenant_key)).first()
                if not tenant:
                    raise HTTPException(
                        status_code=404, 
                        detail=f"Tenant '{tenant_key}' not found in database. Available tenants can be checked at /tenants/list-all"
                    )
                if not tenant.IsActive:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Tenant '{tenant_key}' is not active"
                    )
            finally:
                main_db.close()
            
            db = ConnectionManager.get_session(tenant_key)
        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid Tenant ID '{tenant_key}': {str(e)}. Check that DB_CONNECTION_{tenant_key.upper()} is set in .env"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error connecting to tenant '{tenant_key}': {str(e)}"
            )
    else:
        db = SessionLocal()
        
    try:
        yield db
    finally:
        db.close()

# Dependency function to always get MAIN DB session (ignores tenant headers)
def get_main_db() -> Session:
    """
    Get MAIN database session. Always connects to main DB, ignoring X-Tenant-ID header.
    Use this for operations that must always run on the main database (e.g., TenantLogos).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()