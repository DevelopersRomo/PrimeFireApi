from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# ----------------------------
# 📌 MODULE SCHEMAS
# ----------------------------
class ModuleBase(BaseModel):
    ModuleName: str = Field(..., max_length=50, description="Name of the module")
    ModuleKey: str = Field(..., max_length=50, description="Unique key identifier for the module")
    Description: Optional[str] = Field(None, max_length=200, description="Module description")
    Icon: Optional[str] = Field(None, max_length=50, description="Material icon name")
    RouteUrl: Optional[str] = Field(None, max_length=100, description="Angular route URL")
    DisplayOrder: Optional[int] = Field(0, description="Display order in menu")
    IsActive: bool = Field(True, description="Whether the module is active")
    ParentModuleId: Optional[int] = Field(None, description="Parent module ID for hierarchical structure")

class ModuleCreate(ModuleBase):
    pass

class ModuleUpdate(BaseModel):
    ModuleName: Optional[str] = Field(None, max_length=50)
    ModuleKey: Optional[str] = Field(None, max_length=50)
    Description: Optional[str] = Field(None, max_length=200)
    Icon: Optional[str] = Field(None, max_length=50)
    RouteUrl: Optional[str] = Field(None, max_length=100)
    DisplayOrder: Optional[int] = None
    IsActive: Optional[bool] = None
    ParentModuleId: Optional[int] = None

class Module(ModuleBase):
    ModuleId: int
    CreatedAt: datetime

    class Config:
        from_attributes = True

# ----------------------------
# 📌 PERMISSION SCHEMAS (RoleModules)
# ----------------------------
class PermissionBase(BaseModel):
    RoleId: int = Field(..., description="Role ID")
    ModuleId: int = Field(..., description="Module ID")
    CanView: bool = Field(True, description="Can view the module")
    CanCreate: bool = Field(False, description="Can create records")
    CanEdit: bool = Field(False, description="Can edit records")
    CanDelete: bool = Field(False, description="Can delete records")
    CanExport: bool = Field(False, description="Can export data")
    AdminActions: bool = Field(False, description="Can perform administrative actions")
    OtherActions: bool = Field(False, description="Can perform other actions")

class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(BaseModel):
    CanView: Optional[bool] = None
    CanCreate: Optional[bool] = None
    CanEdit: Optional[bool] = None
    CanDelete: Optional[bool] = None
    CanExport: Optional[bool] = None
    AdminActions: Optional[bool] = None
    OtherActions: Optional[bool] = None

class Permission(PermissionBase):
    AssignedAt: datetime

    class Config:
        from_attributes = True

# ----------------------------
# 📌 EXTENDED SCHEMAS WITH RELATIONSHIPS
# ----------------------------
class ModuleWithPermissions(Module):
    """Module with its permissions for all roles"""
    permissions: List[Permission] = []

class PermissionWithDetails(Permission):
    """Permission with role and module details"""
    role_name: Optional[str] = None
    module_name: Optional[str] = None
    module_key: Optional[str] = None

class RolePermissionsResponse(BaseModel):
    """Response for getting all permissions of a role"""
    RoleId: int
    RoleName: str
    permissions: List[PermissionWithDetails]

class BulkPermissionUpdate(BaseModel):
    """Bulk update permissions for a role"""
    RoleId: int
    permissions: List[PermissionCreate]

