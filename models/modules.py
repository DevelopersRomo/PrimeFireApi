from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class RoleModules(SQLModel, table=True):
    __tablename__ = "RoleModules"

    RoleId: int = Field(foreign_key="Roles.RoleId", primary_key=True)
    ModuleId: int = Field(foreign_key="Modules.ModuleId", primary_key=True)
    CanView: bool = Field(default=True)
    CanCreate: bool = Field(default=False)
    CanEdit: bool = Field(default=False)
    CanDelete: bool = Field(default=False)
    CanExport: bool = Field(default=False)
    AdminActions: bool = Field(default=False)
    OtherActions: bool = Field(default=False)
    AssignedAt: Optional[datetime] = Field(default_factory=datetime.utcnow)

class Modules(SQLModel, table=True):
    __tablename__ = "Modules"

    ModuleId: Optional[int] = Field(default=None, primary_key=True, index=True)
    ModuleName: str = Field(max_length=50)
    ModuleKey: str = Field(max_length=50, unique=True, index=True)
    Description: Optional[str] = Field(default=None, max_length=200)
    Icon: Optional[str] = Field(default=None, max_length=50)
    RouteUrl: Optional[str] = Field(default=None, max_length=100)
    DisplayOrder: Optional[int] = Field(default=0)
    IsActive: bool = Field(default=True)
    ParentModuleId: Optional[int] = Field(default=None, foreign_key="Modules.ModuleId")
    CreatedAt: Optional[datetime] = Field(default_factory=datetime.utcnow)

    # Self-referential relationship for parent-child modules
    parent_module: Optional["Modules"] = Relationship(
        sa_relationship_kwargs={
            "remote_side": "Modules.ModuleId",
            "foreign_keys": "Modules.ParentModuleId"
        }
    )

