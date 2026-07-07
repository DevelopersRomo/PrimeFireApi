"""Dependencies."""

from typing import Any

from fastapi import Depends, HTTPException, Request, status
from fastapi import Request as FastAPIRequest
from jose import JWTError  # type: ignore[import-untyped]
from jose import jwt as jose_jwt  # type: ignore[import-untyped]
from sqlmodel import Session, select

from bd.dependencies import get_db, get_primefire_session, is_primefire_email
from bd.multitenancy import ConnectionManager
from core.azure_token import looks_like_azure_token, validate_azure_token
from core.config import settings
from models.employees import Employees
from models.tenants import TenantEmployees, Tenants

# Internal JWT signing secret (see core/config.py)
SECRET_KEY = settings.jwt_secret
ALGORITHM = "HS256"


async def extract_token_from_azure_scheme(request: Request) -> str:
    """Extract token from Authorization header."""
    authorization: str | None = request.headers.get("Authorization")
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
) -> dict[str, Any] | None:
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
            return payload  # It's our custom token
    except JWTError:
        pass  # Not our token, try Azure

    # 2. Try Azure AD (RS256): full signature/audience/issuer validation via JWKS
    if looks_like_azure_token(token):
        return validate_azure_token(token)

    # If we reached here, token is invalid or unknown
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_employee(
    token_data: dict[str, Any] | None = Depends(simple_token_validator),
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
            tenant = main_db.exec(select(Tenants).where(Tenants.db_connection_key == tenant_key)).first()
            if not tenant:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid tenant assignment. Please contact an administrator.",
                )
            if tenant.db_connection_key == "PENDING" or not tenant.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Your account is pending approval. Please wait for an administrator to assign you to an active tenant.",
                )
        finally:
            main_db.close()

        # Buscar empleado en BD del tenant
        tenant_db = ConnectionManager.get_session(tenant_key)
        try:
            email = token_data.get("sub")
            employee = tenant_db.exec(select(Employees).where(Employees.email == email)).first()
            if not employee:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found in tenant database")
            return employee
        finally:
            tenant_db.close()

    # Usuario interno - buscar en BD principal
    if token_data.get("type") == "internal":
        email = token_data.get("sub")
        # Check pending external user (no tenant_key, present in TenantEmployees)
        external_user = db.exec(select(TenantEmployees).where(TenantEmployees.email == email)).first()
        if external_user:
            # Usuario externo sin tenant asignado o pendiente
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

        employee = db.exec(select(Employees).where(Employees.email == email)).first()
    else:
        azure_email = (
            token_data.get("preferred_username")
            or token_data.get("upn")
            or token_data.get("email")
            or token_data.get("unique_name")
            or token_data.get("sub")
        )
        if not is_primefire_email(azure_email):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Azure AD user is not allowed for PrimeFire.",
            )
        azure_oid = token_data.get("oid")

        with get_primefire_session() as primefire_db:
            employee = primefire_db.exec(select(Employees).where(Employees.azure_oid == azure_oid)).first()
            if employee:
                primefire_db.expunge(employee)

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
    from models.employees import EmployeeRoles, Roles
    from models.modules import Modules, RoleModules

    is_azure_user = token_data and "oid" in token_data

    # Función auxiliary para obtener permisos usando una sesión específica
    def get_permissions_with_session(session: Session):
        from models.countries import Countries

        country_name: str | None = None
        if current_employee.country_id is not None:
            country_row = session.exec(
                select(Countries).where(Countries.country_id == current_employee.country_id)
            ).first()
            country_name = country_row.name if country_row else None

        # Get employee's roles
        employee_roles_query = (
            select(EmployeeRoles, Roles)
            .join(Roles, EmployeeRoles.role_id == Roles.role_id)  # type: ignore[arg-type]
            .where(EmployeeRoles.employee_id == current_employee.employee_id)
        )

        employee_roles_data = session.exec(employee_roles_query).all()

        roles_list = []
        role_ids = []

        for _emp_role, role in employee_roles_data:
            roles_list.append({"role_id": role.role_id, "role_name": role.role_name, "description": role.description})
            role_ids.append(role.role_id)

        # Get permissions for all roles (combine with OR logic)
        permissions_by_module: dict[str, dict[str, Any]] = {}

        if role_ids:
            permissions_query = (
                select(RoleModules, Modules)
                .join(Modules, RoleModules.module_id == Modules.module_id)  # type: ignore[arg-type]
                .where(RoleModules.role_id.in_(role_ids))  # type: ignore[attr-defined]
            )

            permissions_data = session.exec(permissions_query).all()

            for role_module, module in permissions_data:
                module_key = module.module_key

                if module_key not in permissions_by_module:
                    permissions_by_module[module_key] = {
                        "module_key": module_key,
                        "module_info": {
                            "module_id": module.module_id,
                            "module_name": module.module_name,
                            "module_key": module.module_key,
                            "route_url": module.route_url,
                            "icon": module.icon,
                            "display_order": module.display_order,
                            "is_active": module.is_active,
                        },
                        "permissions": {
                            "can_view": False,
                            "can_create": False,
                            "can_edit": False,
                            "can_delete": False,
                            "can_export": False,
                            "admin_actions": False,
                            "other_actions": False,
                        },
                    }

                # Combine permissions with OR logic (if any role has permission, user has it)
                perms = permissions_by_module[module_key]["permissions"]
                perms["can_view"] = perms["can_view"] or role_module.can_view
                perms["can_create"] = perms["can_create"] or role_module.can_create
                perms["can_edit"] = perms["can_edit"] or role_module.can_edit
                perms["can_delete"] = perms["can_delete"] or role_module.can_delete
                perms["can_export"] = perms["can_export"] or role_module.can_export
                perms["admin_actions"] = perms["admin_actions"] or role_module.admin_actions
                perms["other_actions"] = perms["other_actions"] or role_module.other_actions

        # Build response
        permissions_list = list(permissions_by_module.values())
        accessible_modules = [p["module_key"] for p in permissions_list if p["permissions"]["can_view"]]

        return {
            "employee": {
                "employee_id": current_employee.employee_id,
                "first_name": current_employee.first_name,
                "last_name": current_employee.last_name,
                "display_name": current_employee.display_name,
                "title": current_employee.title,
                "email": current_employee.email,
                "department": current_employee.department,
                "office": current_employee.office,
                "city": current_employee.city,
                "country": country_name,
            },
            "roles": roles_list,
            "permissions": permissions_list,
            "accessible_modules": accessible_modules,
        }

    if is_azure_user:
        azure_email = (
            token_data.get("preferred_username")
            or token_data.get("upn")
            or token_data.get("email")
            or token_data.get("unique_name")
            or token_data.get("sub")
        )
        if not is_primefire_email(azure_email):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Azure AD user is not allowed for PrimeFire.",
            )
        with get_primefire_session() as primefire_db:
            return get_permissions_with_session(primefire_db)
    else:
        return get_permissions_with_session(db)
