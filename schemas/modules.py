from datetime import datetime

from pydantic import BaseModel, Field


# ----------------------------
# 📌 MODULE SCHEMAS
# ----------------------------
class ModuleBase(BaseModel):
    module_name: str = Field(..., max_length=50, description="Name of the module")
    module_key: str = Field(..., max_length=50, description="Unique key identifier for the module")
    description: str | None = Field(None, max_length=200, description="Module description")
    icon: str | None = Field(None, max_length=50, description="Material icon name")
    route_url: str | None = Field(None, max_length=100, description="Angular route URL")
    display_order: int | None = Field(0, description="Display order in menu")
    is_active: bool = Field(True, description="Whether the module is active")
    parent_module_id: int | None = Field(None, description="Parent module ID for hierarchical structure")


class ModuleCreate(ModuleBase):
    pass


class ModuleUpdate(BaseModel):
    module_name: str | None = Field(None, max_length=50)
    module_key: str | None = Field(None, max_length=50)
    description: str | None = Field(None, max_length=200)
    icon: str | None = Field(None, max_length=50)
    route_url: str | None = Field(None, max_length=100)
    display_order: int | None = None
    is_active: bool | None = None
    parent_module_id: int | None = None


class Module(ModuleBase):
    module_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ----------------------------
# 📌 PERMISSION SCHEMAS (RoleModules)
# ----------------------------
class PermissionBase(BaseModel):
    role_id: int = Field(..., description="Role ID")
    module_id: int = Field(..., description="Module ID")
    can_view: bool = Field(True, description="Can view the module")
    can_create: bool = Field(False, description="Can create records")
    can_edit: bool = Field(False, description="Can edit records")
    can_delete: bool = Field(False, description="Can delete records")
    can_export: bool = Field(False, description="Can export data")
    admin_actions: bool = Field(False, description="Can perform administrative actions")
    other_actions: bool = Field(False, description="Can perform other actions")


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    can_view: bool | None = None
    can_create: bool | None = None
    can_edit: bool | None = None
    can_delete: bool | None = None
    can_export: bool | None = None
    admin_actions: bool | None = None
    other_actions: bool | None = None


class Permission(PermissionBase):
    assigned_at: datetime | None = None

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

    role_id: int
    role_name: str
    permissions: list[PermissionWithDetails]


class BulkPermissionUpdate(BaseModel):
    """Bulk update permissions for a role."""

    role_id: int
    permissions: list[PermissionCreate]