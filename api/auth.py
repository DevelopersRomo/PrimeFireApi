from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
import bcrypt
import uuid
from sqlmodel import Session, select
from pydantic import BaseModel

from bd.dependencies import get_db, get_main_db
from bd.connection import SessionLocal
from bd.multitenancy import ConnectionManager
from models.employees import Employees
from models.tenants import Tenants, TenantEmployees
from sqlmodel import select
from core.config import settings

# --- CONFIGURACIÓN ---
# Usar una clave secreta segura en producción
SECRET_KEY = settings.BACKEND_CLIENT_SECRET or "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

router = APIRouter()

# --- MODELOS ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserRegister(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    tenant_key: Optional[str] = None  # Opcional - admin lo asignará después

# --- UTILS ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a bcrypt hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    # Bcrypt has a 72 byte limit
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(user_data.password)
    
    # 2. Si tiene tenant_key, verificar que existe y está activo
    if user_data.tenant_key:
        tenant = db.exec(select(Tenants).where(Tenants.DbConnectionKey == user_data.tenant_key)).first()
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tenant '{user_data.tenant_key}' not found"
            )
        if not tenant.IsActive:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tenant '{user_data.tenant_key}' is not active"
            )
        
        # Save external user in main DB
        external_user = TenantEmployees(
            Email=user_data.email,
            PasswordHash=hashed_password,
            TenantId=tenant.TenantId
        )
        db.add(external_user)
        db.commit()
        db.refresh(external_user)
        
        # Save full user in main DB as well (ignoring tenant DB separation)
        existing_user = db.exec(
            select(Employees).where(Employees.Email == user_data.email)
        ).first()
        
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
                AzureOid=external_oid  # Unique identifier for external users
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
             
        access_token = create_access_token(
            data=token_data,
            expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    
    else:
        # No tenant_key: keep TenantId as NULL (pending approval)
        external_user = TenantEmployees(
            Email=user_data.email,
            PasswordHash=hashed_password,
            TenantId=None
        )
        db.add(external_user)
        db.commit()
        db.refresh(external_user)
        
        # Usuario pendiente - NO dar token de acceso (debe esperar aprobación)
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="Registration successful. Your account is pending approval. An administrator will assign you to a tenant shortly."
        )

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_main_db)
):
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
                detail="Your account is pending approval. Please wait for an administrator to assign you to a tenant."
            )
        
        # Obtener tenant info
        tenant = db.get(Tenants, external_user.TenantId)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your tenant assignment is invalid. Please contact an administrator."
            )
        
        # Verificar que el tenant no sea PENDING y esté activo
        if tenant.DbConnectionKey == "PENDING" or not tenant.IsActive:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is pending approval. Please wait for an administrator to assign you to an active tenant."
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token_data = {"sub": external_user.Email, "type": "internal"}
        if tenant.TenantId != 1:
            token_data["tenant_key"] = tenant.DbConnectionKey
        access_token = create_access_token(
            data=token_data,
            expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    
    # 2. Si no es externo, buscar en Employees de BD Principal (usuarios internos de PrimeFire)
    user = db.exec(select(Employees).where(Employees.Email == form_data.username)).first()
    
    if not user or not user.PasswordHash or not verify_password(form_data.password, user.PasswordHash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.Email, "type": "internal"},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

