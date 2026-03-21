from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class Modules(SQLModel, table=True):
    __tablename__ = "modules"
    __table_args__ = {"schema": "dbo"}

    module_id: int | None = Field(default=None, primary_key=True, index=True)
    module_name: str = Field(max_length=50)
    module_key: str = Field(max_length=50, unique=True, index=True)
    description: str | None = Field(default=None, max_length=200)
    icon: str | None = Field(default=None, max_length=50)
    route_url: str | None = Field(default=None, max_length=100)
    display_order: int | None = Field(default=0)
    is_active: bool = Field(default=True)
    parent_module_id: int | None = Field(default=None, foreign_key="dbo.modules.module_id")
    created_at: str | None = Field(default=None, max_length=19)

    # Self-referential relationship for parent-child modules
    parent_module: Optional["Modules"] = Relationship(
        sa_relationship_kwargs={"remote_side": "Modules.module_id", "foreign_keys": "Modules.parent_module_id"}
    )


class RoleModules(SQLModel, table=True):
    __tablename__ = "role_modules"
    __table_args__ = {"schema": "dbo"}

    role_id: int = Field(foreign_key="dbo.roles.role_id", primary_key=True)
    module_id: int = Field(foreign_key="dbo.modules.module_id", primary_key=True)
    can_view: bool = Field(default=True)
    can_create: bool = Field(default=False)
    can_edit: bool = Field(default=False)
    can_delete: bool = Field(default=False)
    can_export: bool = Field(default=False)
    admin_actions: bool = Field(default=False)
    other_actions: bool = Field(default=False)
    assigned_at: datetime | None = Field(default_factory=datetime.utcnow)
