from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class RoleModules(SQLModel, table=True):
    __tablename__ = "RoleModules"
    __table_args__ = {"schema": "dbo"}

    RoleId: int = Field(foreign_key="dbo.Roles.RoleId", primary_key=True)
    ModuleId: int = Field(foreign_key="dbo.Modules.ModuleId", primary_key=True)
    CanView: bool = Field(default=True)
    CanCreate: bool = Field(default=False)
    CanEdit: bool = Field(default=False)
    CanDelete: bool = Field(default=False)
    CanExport: bool = Field(default=False)
    AdminActions: bool = Field(default=False)
    OtherActions: bool = Field(default=False)
    AssignedAt: datetime | None = Field(default_factory=datetime.utcnow)


class Modules(SQLModel, table=True):
    __tablename__ = "Modules"
    __table_args__ = {"schema": "dbo"}

    ModuleId: int | None = Field(default=None, primary_key=True, index=True)
    ModuleName: str = Field(max_length=50)
    ModuleKey: str = Field(max_length=50, unique=True, index=True)
    Description: str | None = Field(default=None, max_length=200)
    Icon: str | None = Field(default=None, max_length=50)
    RouteUrl: str | None = Field(default=None, max_length=100)
    DisplayOrder: int | None = Field(default=0)
    IsActive: bool = Field(default=True)
    ParentModuleId: int | None = Field(default=None, foreign_key="dbo.Modules.ModuleId")
    CreatedAt: datetime | None = Field(default_factory=datetime.utcnow)

    # Self-referential relationship for parent-child modules
    parent_module: Optional["Modules"] = Relationship(
        sa_relationship_kwargs={"remote_side": "Modules.ModuleId", "foreign_keys": "Modules.ParentModuleId"}
    )
