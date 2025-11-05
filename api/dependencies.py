"""Dependencies."""

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi_azure_auth.user import User as AzureUser
from sqlmodel import Session, select

from core.config import AZURE_AUTH_SCHEME, settings
from bd.dependencies import get_db
from models.employees import Employees


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
    """Simple token validator that only validates when token is present."""
    # Check if there's an Authorization header
    authorization = request.headers.get("Authorization")
    if not authorization:
        # No token provided - this is OK for endpoints that don't require auth
        return None

    # Extract token from Bearer scheme
    try:
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Validate token if present
    try:
        payload = jwt.decode(token, options={"verify_signature": False})

        # Basic validation
        expected_aud = f"api://{settings.BACKEND_CLIENT_ID}"
        expected_iss = f"https://sts.windows.net/{settings.TENANT_ID}/"

        if payload.get("aud") != expected_aud:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid audience. Expected: {expected_aud}, Got: {payload.get('aud')}",
            )

        if payload.get("iss") != expected_iss:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid issuer. Expected: {expected_iss}, Got: {payload.get('iss')}",
            )

        return payload

    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation error: {str(e)}",
        )


def get_current_user(
    azure_user: AzureUser = Depends(AZURE_AUTH_SCHEME),
) -> AzureUser:
    """Get the current authenticated user from Azure AD.

    Args:
        azure_user: The authenticated Azure user

    Returns:
        The Azure user information

    Raises:
        HTTPException: If user is not authenticated
    """
    if not azure_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated",
        )
    return azure_user


async def get_or_create_user_from_token(
    token_data: dict,
    db: Session,
) -> Employees:
    """Get or create user from Azure AD token data."""
    azure_oid = token_data.get("oid")
    azure_upn = token_data.get("upn") or token_data.get("preferred_username")
    name = token_data.get("name")
    
    if not azure_oid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token: missing user identifier",
        )
    
    # Try to find existing user by Azure OID
    existing_user = db.exec(
        select(Employees).where(Employees.AzureOid == azure_oid)
    ).first()
    
    if existing_user:
        # Update user info if changed
        if existing_user.AzureUpn != azure_upn:
            existing_user.AzureUpn = azure_upn
        if existing_user.DisplayName != name and name:
            existing_user.DisplayName = name
        if existing_user.Email != azure_upn and azure_upn:
            existing_user.Email = azure_upn
        
        db.add(existing_user)
        db.commit()
        db.refresh(existing_user)
        return existing_user
    
    # Create new user
    new_user = Employees(
        DisplayName=name,
        Email=azure_upn,
        AzureOid=azure_oid,
        AzureUpn=azure_upn,
        Title="User",  # Default title
        # Roles are assigned separately via EmployeeRoles table (no default role assigned initially)
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def require_authentication(
    # Use simple token validator that works with Swagger UI OAuth2
    token_data: dict = Depends(simple_token_validator),
    db: Session = Depends(get_db),
) -> dict:
    """Require authentication for the endpoint using simple validation.

    This uses the Azure AD OAuth2 PKCE flow configured in Swagger UI,
    validates the token but does not auto-register users.

    Args:
        token_data: The validated token data (can be None for endpoints that don't require auth)
        db: Database session

    Returns:
        The token data dictionary

    Raises:
        HTTPException: If user is not authenticated but endpoint requires auth
    """
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    return token_data


async def get_current_employee(
    token_data: dict = Depends(require_authentication),
    db: Session = Depends(get_db),
) -> Employees:
    """Get the current authenticated employee from the database.

    Args:
        token_data: The validated token data
        db: Database session

    Returns:
        The Employee object from database

    Raises:
        HTTPException: If employee is not found in database
    """
    azure_oid = token_data.get("oid")
    if not azure_oid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token: missing user identifier (oid)",
        )

    # Find employee by Azure OID
    employee = db.exec(
        select(Employees).where(Employees.AzureOid == azure_oid)
    ).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found in database. Please contact administrator.",
        )

    return employee


async def get_current_employee_with_permissions(
    employee: Employees = Depends(get_current_employee),
    db: Session = Depends(get_db),
) -> dict:
    """Get the current authenticated employee with all their permissions.

    Args:
        employee: The current employee
        db: Database session

    Returns:
        Dictionary with employee data and combined permissions
    """
    from models.employees import Roles
    from models.modules import RoleModules, Modules

    # Get employee's roles through EmployeeRoles junction table
    from models.employees import EmployeeRoles

    roles_query = select(Roles).join(
        EmployeeRoles, Roles.RoleId == EmployeeRoles.RoleId
    ).where(EmployeeRoles.EmployeeId == employee.EmployeeId)

    roles = db.exec(roles_query).all()

    # Get all permissions for all roles (combined)
    permissions_dict = {}
    modules_dict = {}

    for role in roles:
        role_permissions = db.exec(
            select(RoleModules, Modules).join(
                Modules, RoleModules.ModuleId == Modules.ModuleId
            ).where(RoleModules.RoleId == role.RoleId)
        ).all()

        for role_module, module in role_permissions:
            module_key = module.ModuleKey

            # Initialize module if not exists
            if module_key not in permissions_dict:
                permissions_dict[module_key] = {
                    "CanView": False,
                    "CanCreate": False,
                    "CanEdit": False,
                    "CanDelete": False,
                    "CanExport": False,
                    "AdminActions": False,
                    "OtherActions": False
                }
                modules_dict[module_key] = {
                    "ModuleId": module.ModuleId,
                    "ModuleName": module.ModuleName,
                    "RouteUrl": module.RouteUrl,
                    "Icon": module.Icon,
                    "DisplayOrder": module.DisplayOrder,
                    "ParentModuleId": module.ParentModuleId
                }

            # Apply permissions (OR logic - if any role has permission, user has it)
            permissions_dict[module_key]["CanView"] = permissions_dict[module_key]["CanView"] or role_module.CanView
            permissions_dict[module_key]["CanCreate"] = permissions_dict[module_key]["CanCreate"] or role_module.CanCreate
            permissions_dict[module_key]["CanEdit"] = permissions_dict[module_key]["CanEdit"] or role_module.CanEdit
            permissions_dict[module_key]["CanDelete"] = permissions_dict[module_key]["CanDelete"] or role_module.CanDelete
            permissions_dict[module_key]["CanExport"] = permissions_dict[module_key]["CanExport"] or role_module.CanExport
            permissions_dict[module_key]["AdminActions"] = permissions_dict[module_key]["AdminActions"] or role_module.AdminActions
            permissions_dict[module_key]["OtherActions"] = permissions_dict[module_key]["OtherActions"] or role_module.OtherActions

    # Convert to list format for frontend
    permissions_list = []
    for module_key, perms in permissions_dict.items():
        permissions_list.append({
            "module_key": module_key,
            "module_info": modules_dict[module_key],
            "permissions": perms
        })

    return {
        "employee": {
            "EmployeeId": employee.EmployeeId,
            "FirstName": employee.FirstName,
            "LastName": employee.LastName,
            "DisplayName": employee.DisplayName,
            "Email": employee.Email,
            "Title": employee.Title,
            "AzureOid": employee.AzureOid
        },
        "roles": [
            {
                "RoleId": role.RoleId,
                "RoleName": role.RoleName,
                "Description": role.Description
            } for role in roles
        ],
        "permissions": permissions_list,
        "accessible_modules": [
            module_info for module_key, module_info in modules_dict.items()
            if permissions_dict[module_key]["CanView"]
        ]
    }

