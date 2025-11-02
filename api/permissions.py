from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from api.dependencies import require_authentication, get_current_employee_with_permissions
from bd.dependencies import get_db
from models.modules import RoleModules, Modules
from models.employees import Roles
from schemas.modules import (
    Permission, 
    PermissionCreate, 
    PermissionUpdate, 
    PermissionWithDetails,
    RolePermissionsResponse,
    BulkPermissionUpdate
)

router = APIRouter()

# ----------------------------
# 📌 CREATE PERMISSION
# ----------------------------
@router.post("/", response_model=Permission)
async def create_permission(
    permission: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authentication)
):
    """Create a new permission (assign a module to a role with specific permissions)."""
    # Validate role exists
    role = db.exec(select(Roles).where(Roles.RoleId == permission.RoleId)).first()
    if not role:
        raise HTTPException(status_code=404, detail=f"Role with ID {permission.RoleId} not found")
    
    # Validate module exists
    module = db.exec(select(Modules).where(Modules.ModuleId == permission.ModuleId)).first()
    if not module:
        raise HTTPException(status_code=404, detail=f"Module with ID {permission.ModuleId} not found")
    
    # Check if permission already exists
    existing = db.exec(
        select(RoleModules).where(
            RoleModules.RoleId == permission.RoleId,
            RoleModules.ModuleId == permission.ModuleId
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"Permission already exists for role '{role.RoleName}' and module '{module.ModuleName}'"
        )
    
    db_permission = RoleModules(**permission.model_dump())
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission

# ----------------------------
# 📌 READ ALL PERMISSIONS
# ----------------------------
@router.get("/", response_model=List[PermissionWithDetails])
async def get_all_permissions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authentication)
):
    """Get all permissions with role and module details."""
    query = select(RoleModules, Roles, Modules).join(
        Roles, RoleModules.RoleId == Roles.RoleId
    ).join(
        Modules, RoleModules.ModuleId == Modules.ModuleId
    ).order_by(Roles.RoleName, Modules.DisplayOrder, Modules.ModuleName)
    
    results = db.exec(query).all()
    
    permissions = []
    for role_module, role, module in results:
        permissions.append(
            PermissionWithDetails(
                RoleId=role_module.RoleId,
                ModuleId=role_module.ModuleId,
                CanView=role_module.CanView,
                CanCreate=role_module.CanCreate,
                CanEdit=role_module.CanEdit,
                CanDelete=role_module.CanDelete,
                CanExport=role_module.CanExport,
                AdminActions=role_module.AdminActions,
                OtherActions=role_module.OtherActions,
                AssignedAt=role_module.AssignedAt,
                role_name=role.RoleName,
                module_name=module.ModuleName,
                module_key=module.ModuleKey
            )
        )
    
    return permissions

# ----------------------------
# 📌 GET PERMISSIONS BY ROLE
# ----------------------------
@router.get("/role/{role_id}", response_model=RolePermissionsResponse)
async def get_role_permissions(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authentication)
):
    """Get all permissions for a specific role."""
    # Validate role exists
    role = db.exec(select(Roles).where(Roles.RoleId == role_id)).first()
    if not role:
        raise HTTPException(status_code=404, detail=f"Role with ID {role_id} not found")
    
    query = select(RoleModules, Modules).join(
        Modules, RoleModules.ModuleId == Modules.ModuleId
    ).where(
        RoleModules.RoleId == role_id
    ).order_by(Modules.DisplayOrder, Modules.ModuleName)
    
    results = db.exec(query).all()
    
    permissions = []
    for role_module, module in results:
        permissions.append(
            PermissionWithDetails(
                RoleId=role_module.RoleId,
                ModuleId=role_module.ModuleId,
                CanView=role_module.CanView,
                CanCreate=role_module.CanCreate,
                CanEdit=role_module.CanEdit,
                CanDelete=role_module.CanDelete,
                CanExport=role_module.CanExport,
                AdminActions=role_module.AdminActions,
                OtherActions=role_module.OtherActions,
                AssignedAt=role_module.AssignedAt,
                role_name=role.RoleName,
                module_name=module.ModuleName,
                module_key=module.ModuleKey
            )
        )
    
    return RolePermissionsResponse(
        RoleId=role.RoleId,
        RoleName=role.RoleName,
        permissions=permissions
    )

# ----------------------------
# 📌 GET PERMISSIONS BY MODULE
# ----------------------------
@router.get("/module/{module_id}", response_model=List[PermissionWithDetails])
async def get_module_permissions(
    module_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authentication)
):
    """Get all permissions for a specific module (which roles have access)."""
    # Validate module exists
    module = db.exec(select(Modules).where(Modules.ModuleId == module_id)).first()
    if not module:
        raise HTTPException(status_code=404, detail=f"Module with ID {module_id} not found")
    
    query = select(RoleModules, Roles).join(
        Roles, RoleModules.RoleId == Roles.RoleId
    ).where(
        RoleModules.ModuleId == module_id
    ).order_by(Roles.RoleName)
    
    results = db.exec(query).all()
    
    permissions = []
    for role_module, role in results:
        permissions.append(
            PermissionWithDetails(
                RoleId=role_module.RoleId,
                ModuleId=role_module.ModuleId,
                CanView=role_module.CanView,
                CanCreate=role_module.CanCreate,
                CanEdit=role_module.CanEdit,
                CanDelete=role_module.CanDelete,
                CanExport=role_module.CanExport,
                AdminActions=role_module.AdminActions,
                OtherActions=role_module.OtherActions,
                AssignedAt=role_module.AssignedAt,
                role_name=role.RoleName,
                module_name=module.ModuleName,
                module_key=module.ModuleKey
            )
        )
    
    return permissions

# ----------------------------
# 📌 GET SPECIFIC PERMISSION
# ----------------------------
@router.get("/{role_id}/{module_id}", response_model=Permission)
async def get_permission(
    role_id: int,
    module_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authentication)
):
    """Get a specific permission by role and module."""
    db_permission = db.exec(
        select(RoleModules).where(
            RoleModules.RoleId == role_id,
            RoleModules.ModuleId == module_id
        )
    ).first()
    
    if not db_permission:
        raise HTTPException(
            status_code=404, 
            detail=f"Permission not found for role ID {role_id} and module ID {module_id}"
        )
    
    return db_permission

# ----------------------------
# 📌 UPDATE PERMISSION
# ----------------------------
@router.put("/{role_id}/{module_id}", response_model=Permission)
async def update_permission(
    role_id: int,
    module_id: int,
    permission: PermissionUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authentication)
):
    """Update a permission."""
    db_permission = db.exec(
        select(RoleModules).where(
            RoleModules.RoleId == role_id,
            RoleModules.ModuleId == module_id
        )
    ).first()
    
    if not db_permission:
        raise HTTPException(
            status_code=404, 
            detail=f"Permission not found for role ID {role_id} and module ID {module_id}"
        )
    
    for key, value in permission.model_dump(exclude_unset=True).items():
        setattr(db_permission, key, value)
    
    db.commit()
    db.refresh(db_permission)
    return db_permission

# ----------------------------
# 📌 DELETE PERMISSION
# ----------------------------
@router.delete("/{role_id}/{module_id}")
async def delete_permission(
    role_id: int,
    module_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authentication)
):
    """Delete a permission (revoke module access from a role)."""
    db_permission = db.exec(
        select(RoleModules).where(
            RoleModules.RoleId == role_id,
            RoleModules.ModuleId == module_id
        )
    ).first()
    
    if not db_permission:
        raise HTTPException(
            status_code=404, 
            detail=f"Permission not found for role ID {role_id} and module ID {module_id}"
        )
    
    db.delete(db_permission)
    db.commit()
    return {"detail": "Permission deleted successfully"}

# ----------------------------
# 📌 BULK UPDATE PERMISSIONS FOR A ROLE
# ----------------------------
@router.post("/bulk-update", response_model=RolePermissionsResponse)
async def bulk_update_permissions(
    bulk_update: BulkPermissionUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authentication)
):
    """
    Bulk update permissions for a role.
    This will replace all existing permissions for the role with the new ones.
    """
    # Validate role exists
    role = db.exec(select(Roles).where(Roles.RoleId == bulk_update.RoleId)).first()
    if not role:
        raise HTTPException(status_code=404, detail=f"Role with ID {bulk_update.RoleId} not found")
    
    # Delete existing permissions for this role
    existing_permissions = db.exec(
        select(RoleModules).where(RoleModules.RoleId == bulk_update.RoleId)
    ).all()
    for perm in existing_permissions:
        db.delete(perm)
    
    # Create new permissions
    for permission in bulk_update.permissions:
        # Validate module exists
        module = db.exec(select(Modules).where(Modules.ModuleId == permission.ModuleId)).first()
        if not module:
            db.rollback()
            raise HTTPException(status_code=404, detail=f"Module with ID {permission.ModuleId} not found")
        
        db_permission = RoleModules(**permission.model_dump())
        db.add(db_permission)
    
    db.commit()
    
    # Return updated permissions
    return await get_role_permissions(bulk_update.RoleId, db, current_user)

# ----------------------------
# 📌 CHECK USER PERMISSION
# ----------------------------
@router.get("/check/{module_key}/{action}")
async def check_user_permission(
    module_key: str,
    action: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authentication)
):
    """
    Check if the current user has permission to perform an action on a module.
    Actions: view, create, edit, delete, export, admin_actions, other_actions
    """
    # Get module by key
    module = db.exec(select(Modules).where(Modules.ModuleKey == module_key)).first()
    if not module:
        raise HTTPException(status_code=404, detail=f"Module with key '{module_key}' not found")
    
    # Get user's roles (this would need to be implemented based on your auth system)
    # For now, we'll return a placeholder response
    # In production, you'd get the user's roles from the JWT token or session
    
    return {
        "module_key": module_key,
        "module_name": module.ModuleName,
        "action": action,
        "allowed": True,  # Placeholder - implement actual permission check
        "message": "Permission check endpoint - implement with actual user roles"
    }

# ----------------------------
# 📌 GET CURRENT USER PERMISSIONS
# ----------------------------
@router.get("/me", response_model=dict)
async def get_current_user_permissions(
    user_permissions: dict = Depends(get_current_employee_with_permissions),
) -> dict:
    """
    Get permissions for the currently authenticated user.

    This endpoint:
    1. Identifies the user from the JWT token (Azure OID)
    2. Gets all roles assigned to the user
    3. Combines permissions from all roles (OR logic)
    4. Returns employee info, roles, and permissions

    Returns:
        {
            "employee": {EmployeeId, FirstName, LastName, etc.},
            "roles": [{RoleId, RoleName, Description}],
            "permissions": [
                {
                    "module_key": "dashboard",
                    "module_info": {ModuleId, ModuleName, RouteUrl, etc.},
                    "permissions": {CanView, CanCreate, CanEdit, CanDelete, CanExport, AdminActions, OtherActions}
                }
            ],
            "accessible_modules": [list of modules user can access]
        }
    """
    return user_permissions

