import uuid
from datetime import datetime, timedelta

import bcrypt
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlmodel import Session, select

from bd.dependencies import get_main_db
from core.config import settings
from models.employees import Employees
from models.tenants import TenantEmployees, Tenants

# --- CONFIGURACIÓN ---
# Usar una clave secreta segura en producción
SECRET_KEY = settings.BACKEND_CLIENT_SECRET or "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300
REFRESH_TOKEN_EXPIRE_DAYS = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

router = APIRouter()


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
    expire = datetime.utcnow() + expires_delta if expires_delta else datetime.utcnow() + timedelta(minutes=15)  # noqa: DTZ003
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta  # noqa: DTZ003
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)  # noqa: DTZ003
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
    existing_external = db.exec(select(TenantEmployees).where(TenantEmployees.Email == user_data.email)).first()
    if existing_external:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed_password = get_password_hash(user_data.password)

    # 2. Si tiene tenant_key, verificar que existe y está activo
    if user_data.tenant_key:
        tenant = db.exec(select(Tenants).where(Tenants.DbConnectionKey == user_data.tenant_key)).first()
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Tenant '{user_data.tenant_key}' not found"
            )
        if not tenant.IsActive:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Tenant '{user_data.tenant_key}' is not active"
            )

        # Save external user in main DB
        external_user = TenantEmployees(Email=user_data.email, PasswordHash=hashed_password, TenantId=tenant.TenantId)
        db.add(external_user)
        db.commit()
        db.refresh(external_user)

        # Save full user in main DB as well (ignoring tenant DB separation)
        existing_user = db.exec(select(Employees).where(Employees.Email == user_data.email)).first()

        if not existing_user:
            # Generate unique AzureOid for external users to avoid UNIQUE constraint violation
            external_oid = str(uuid.uuid4())
            new_employee = Employees(
                Email=user_data.email,
                FirstName=user_data.first_name,
                LastName=user_data.last_name,
                DisplayName=f"{user_data.first_name} {user_data.last_name}",
                PasswordHash=hashed_password,
                Title="External User",
                AzureOid=external_oid,  # Unique identifier for external users
            )
            db.add(new_employee)
            db.commit()
            db.refresh(new_employee)
        else:
            # Update password if needed
            existing_user.PasswordHash = hashed_password
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
    external_user = TenantEmployees(Email=user_data.email, PasswordHash=hashed_password, TenantId=None)
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
    external_user = db.exec(select(TenantEmployees).where(TenantEmployees.Email == form_data.username)).first()

    if external_user:
        # Usuario externo - validar password
        if not external_user.PasswordHash or not verify_password(form_data.password, external_user.PasswordHash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verificar que tenga tenant asignado
        if not external_user.TenantId:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is pending approval. Please wait for an administrator to assign you to a tenant.",
            )

        # Obtener tenant info
        tenant = db.get(Tenants, external_user.TenantId)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your tenant assignment is invalid. Please contact an administrator.",
            )

        # Verificar que el tenant no sea PENDING y esté activo
        if tenant.DbConnectionKey == "PENDING" or not tenant.IsActive:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is pending approval. Please wait for an administrator to assign you to an active tenant.",
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token_data = {"sub": external_user.Email, "type": "internal"}
        if tenant.TenantId != 1:
            token_data["tenant_key"] = tenant.DbConnectionKey
        access_token = create_access_token(data=token_data, expires_delta=access_token_expires)
        refresh_token = create_refresh_token(data={"sub": external_user.Email, "tenant_key": tenant.DbConnectionKey})
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "refresh_token": refresh_token,
        }

    # 2. Si no es externo, buscar en Employees de BD Principal (usuarios internos de PrimeFire)
    user = db.exec(select(Employees).where(Employees.Email == form_data.username)).first()

    if not user or not user.PasswordHash or not verify_password(form_data.password, user.PasswordHash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.Email, "type": "internal"}, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(data={"sub": user.Email})
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
    external_user = db.exec(select(TenantEmployees).where(TenantEmployees.Email == email)).first()
    if external_user:
        if not external_user.TenantId:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is pending approval. Please wait for an administrator to assign you to a tenant.",
            )

        tenant = db.get(Tenants, external_user.TenantId)
        if not tenant or tenant.DbConnectionKey == "PENDING" or not tenant.IsActive:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is pending approval. Please wait for an administrator to assign you to an active tenant.",
            )

        token_data = {"sub": external_user.Email, "type": "internal"}
        if tenant.TenantId != 1:
            token_data["tenant_key"] = tenant.DbConnectionKey
        refresh_payload = {"sub": external_user.Email, "tenant_key": tenant.DbConnectionKey}
    else:
        user = db.exec(select(Employees).where(Employees.Email == email)).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        token_data = {"sub": user.Email, "type": "internal"}
        refresh_payload = {"sub": user.Email}

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
