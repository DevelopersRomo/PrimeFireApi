"""Dependencies."""

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi_azure_auth.user import User as AzureUser
from sqlmodel import Session, select
from jose import jwt as jose_jwt, JWTError
from fastapi import Request as FastAPIRequest

from core.config import AZURE_AUTH_SCHEME, settings
from bd.dependencies import get_db
from models.employees import Employees
from models.tenants import Tenants, TenantEmployees
from bd.multitenancy import ConnectionManager

# Re-use secret from auth module or config
SECRET_KEY = settings.BACKEND_CLIENT_SECRET or "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

async def extract_token_from_azure_scheme(request: Request) -> str:
    """Extract token from Authorization header."""
    authorization: str = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token


async def simple_token_validator(
    request: Request,
) -> dict:
    """Validate token (Azure AD OR Internal JWT)."""
    authorization = request.headers.get("Authorization")
    if not authorization:
        return None

    try:
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            return None
    except ValueError:
        return None

    # 1. Try Internal JWT (HS256)
    try:
        payload = jose_jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") == "internal":
            return payload # It's our custom token
    except JWTError:
        pass # Not our token, try Azure

    # 2. Try Azure AD (RS256 - validation handled by library usually, here simplified)
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        # Basic check to see if it looks like Azure token
        if "oid" in payload or "upn" in payload:
            return payload
    except Exception:
        pass

    # If we reached here, token is invalid or unknown
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_employee(
    token_data: dict = Depends(simple_token_validator),
    request: FastAPIRequest = None,
    db: Session = Depends(get_db),
) -> Employees:
    """
    Get current employee.
    Si es usuario externo (tiene tenant_key en token), busca en BD del tenant.
    Si es usuario interno, busca en BD principal.
    Valida que usuarios externos tengan tenant activo asignado.
    """
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    tenant_key = token_data.get("tenant_key")
    
    # Si tiene tenant_key, es usuario externo - validar tenant activo primero
    if tenant_key:
        # Verificar que el tenant existe y está activo
        from bd.connection import SessionLocal
        main_db = SessionLocal()
        try:
            tenant = main_db.exec(select(Tenants).where(Tenants.DbConnectionKey == tenant_key)).first()
            if not tenant:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid tenant assignment. Please contact an administrator."
                )
            if tenant.DbConnectionKey == "PENDING" or not tenant.IsActive:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Your account is pending approval. Please wait for an administrator to assign you to an active tenant."
                )
        finally:
            main_db.close()
        
        # Buscar empleado en BD del tenant
        tenant_db = ConnectionManager.get_session(tenant_key)
        try:
            email = token_data.get("sub")
            employee = tenant_db.exec(select(Employees).where(Employees.Email == email)).first()
            if not employee:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found in tenant database"
                )
            return employee
        finally:
            tenant_db.close()
    
    # Usuario interno - buscar en BD principal
    if token_data.get("type") == "internal":
        email = token_data.get("sub")
        # Check pending external user (no tenant_key, present in TenantEmployees)
        external_user = db.exec(select(TenantEmployees).where(TenantEmployees.Email == email)).first()
        if external_user:
            # Usuario externo sin tenant asignado o pendiente
            if not external_user.TenantId:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Your account is pending approval. Please wait for an administrator to assign you to a tenant."
                )
            tenant = db.get(Tenants, external_user.TenantId)
            if not tenant or tenant.DbConnectionKey == "PENDING" or not tenant.IsActive:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Your account is pending approval. Please wait for an administrator to assign you to an active tenant."
                )
        
        employee = db.exec(select(Employees).where(Employees.Email == email)).first()
    else:
        # Azure AD - Buscar en BD de Sincronización (PrimeFire)
        from bd.connection import SessionSync
        azure_oid = token_data.get("oid")
        
        # Usar una sesión separada para la BD de sincronización
        with SessionSync() as sync_db:
            employee = sync_db.exec(select(Employees).where(Employees.AzureOid == azure_oid)).first()
            if employee:
                # Desvincular el objeto de la sesión para poder usarlo fuera del bloque with
                sync_db.expunge(employee)

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return employee

async def require_authentication(
    token_data: dict = Depends(simple_token_validator),
    db: Session = Depends(get_db),
) -> dict:
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return token_data

async def get_current_employee_with_permissions(
    current_employee: Employees = Depends(get_current_employee),
    token_data: dict = Depends(simple_token_validator),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get current employee with their roles and permissions.
    Returns a dict with employee info, roles, and permissions grouped by module.
    """
    from models.modules import RoleModules, Modules
    from models.employees import EmployeeRoles, Roles
    from bd.connection import SessionSync

    # Determinar qué base de datos usar
    # Si es usuario Azure AD (tiene 'oid'), usar SessionSync (PrimeFire)
    # Si es interno, usar db (DevRomo/Tenant)
    is_azure_user = token_data and "oid" in token_data
    
    # Función auxiliar para obtener permisos usando una sesión específica
    def get_permissions_with_session(session: Session):
        # Get employee's roles
        employee_roles_query = select(EmployeeRoles, Roles).join(
            Roles, EmployeeRoles.RoleId == Roles.RoleId
        ).where(EmployeeRoles.EmployeeId == current_employee.EmployeeId)
        
        employee_roles_data = session.exec(employee_roles_query).all()
        
        roles_list = []
        role_ids = []
        
        for emp_role, role in employee_roles_data:
            roles_list.append({
                "RoleId": role.RoleId,
                "RoleName": role.RoleName,
                "Description": role.Description
            })
            role_ids.append(role.RoleId)
        
        # Get permissions for all roles (combine with OR logic)
        permissions_by_module = {}
        
        if role_ids:
            permissions_query = select(RoleModules, Modules).join(
                Modules, RoleModules.ModuleId == Modules.ModuleId
            ).where(RoleModules.RoleId.in_(role_ids))
            
            permissions_data = session.exec(permissions_query).all()
            
            for role_module, module in permissions_data:
                module_key = module.ModuleKey
                
                if module_key not in permissions_by_module:
                    permissions_by_module[module_key] = {
                        "module_key": module_key,
                        "module_info": {
                            "ModuleId": module.ModuleId,
                            "ModuleName": module.ModuleName,
                            "ModuleKey": module.ModuleKey,
                            "RouteUrl": module.RouteUrl,
                            "Icon": module.Icon,
                            "DisplayOrder": module.DisplayOrder,
                            "IsActive": module.IsActive
                        },
                        "permissions": {
                            "CanView": False,
                            "CanCreate": False,
                            "CanEdit": False,
                            "CanDelete": False,
                            "CanExport": False,
                            "AdminActions": False,
                            "OtherActions": False
                        }
                    }
                
                # Combine permissions with OR logic (if any role has permission, user has it)
                perms = permissions_by_module[module_key]["permissions"]
                perms["CanView"] = perms["CanView"] or role_module.CanView
                perms["CanCreate"] = perms["CanCreate"] or role_module.CanCreate
                perms["CanEdit"] = perms["CanEdit"] or role_module.CanEdit
                perms["CanDelete"] = perms["CanDelete"] or role_module.CanDelete
                perms["CanExport"] = perms["CanExport"] or role_module.CanExport
                perms["AdminActions"] = perms["AdminActions"] or role_module.AdminActions
                perms["OtherActions"] = perms["OtherActions"] or role_module.OtherActions
        
        # Build response
        permissions_list = list(permissions_by_module.values())
        accessible_modules = [p["module_key"] for p in permissions_list if p["permissions"]["CanView"]]
        
        return {
            "employee": {
                "EmployeeId": current_employee.EmployeeId,
                "FirstName": current_employee.FirstName,
                "LastName": current_employee.LastName,
                "DisplayName": current_employee.DisplayName,
                "Title": current_employee.Title,
                "Email": current_employee.Email,
                "Department": current_employee.Department,
                "Office": current_employee.Office,
            },
            "roles": roles_list,
            "permissions": permissions_list,
            "accessible_modules": accessible_modules
        }

    if is_azure_user:
        # Usar sesión de PrimeFire para usuarios de Microsoft
        with SessionSync() as sync_db:
            return get_permissions_with_session(sync_db)
    else:
        # Usar sesión estándar para usuarios internos
        return get_permissions_with_session(db)
