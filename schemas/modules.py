from datetime import datetime

from pydantic import BaseModel, Field


# ----------------------------
# 📌 MODULE SCHEMAS
# ----------------------------
class ModuleBase(BaseModel):
    ModuleName: str = Field(..., max_length=50, description="Name of the module")
    ModuleKey: str = Field(..., max_length=50, description="Unique key identifier for the module")
    Description: str | None = Field(None, max_length=200, description="Module description")
    Icon: str | None = Field(None, max_length=50, description="Material icon name")
    RouteUrl: str | None = Field(None, max_length=100, description="Angular route URL")
    DisplayOrder: int | None = Field(0, description="Display order in menu")
    IsActive: bool = Field(True, description="Whether the module is active")
    ParentModuleId: int | None = Field(None, description="Parent module ID for hierarchical structure")


class ModuleCreate(ModuleBase):
    pass


class ModuleUpdate(BaseModel):
    ModuleName: str | None = Field(None, max_length=50)
    ModuleKey: str | None = Field(None, max_length=50)
    Description: str | None = Field(None, max_length=200)
    Icon: str | None = Field(None, max_length=50)
    RouteUrl: str | None = Field(None, max_length=100)
    DisplayOrder: int | None = None
    IsActive: bool | None = None
    ParentModuleId: int | None = None


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
    CanView: bool | None = None
    CanCreate: bool | None = None
    CanEdit: bool | None = None
    CanDelete: bool | None = None
    CanExport: bool | None = None
    AdminActions: bool | None = None
    OtherActions: bool | None = None


class Permission(PermissionBase):
    AssignedAt: datetime | None = None

    class Config:
        from_attributes = True


# ----------------------------
# 📌 EXTENDED SCHEMAS WITH RELATIONSHIPS
# ----------------------------
class ModuleWithPermissions(Module):
    """Module with its permissions for all roles."""

    permissions: list[Permission] = []


class PermissionWithDetails(Permission):
    """Permission with role and module details."""

    role_name: str | None = None
    module_name: str | None = None
    module_key: str | None = None


class RolePermissionsResponse(BaseModel):
    """Response for getting all permissions of a role."""

    RoleId: int
    RoleName: str
    permissions: list[PermissionWithDetails]


class BulkPermissionUpdate(BaseModel):
    """Bulk update permissions for a role."""

    RoleId: int
    permissions: list[PermissionCreate]
