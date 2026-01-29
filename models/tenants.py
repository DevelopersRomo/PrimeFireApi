from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

# Forward reference

class Tenants(SQLModel, table=True):
    __tablename__ = "Tenants"
    __table_args__ = {'schema': 'dbo'}

    TenantId: Optional[int] = Field(default=None, primary_key=True, index=True)
    Name: str = Field(max_length=100)
    DbConnectionKey: str = Field(max_length=50) # Key to find connection string in env
    Description: Optional[str] = Field(default=None, max_length=255)
    IsActive: bool = Field(default=True)
    CreatedAt: datetime = Field(default_factory=datetime.now)

    # Relationships
    tenant_employees: List["TenantEmployees"] = Relationship(back_populates="tenant")
    logos: List["TenantLogos"] = Relationship(back_populates="tenant")


class TenantEmployees(SQLModel, table=True):
    __tablename__ = "TenantEmployees"
    __table_args__ = {'schema': 'dbo'}

    Id: Optional[int] = Field(default=None, primary_key=True)
    Email: Optional[str] = Field(default=None, max_length=100, unique=True)
    PasswordHash: Optional[str] = Field(default=None, max_length=255)
    TenantId: Optional[int] = Field(default=None, foreign_key="dbo.Tenants.TenantId")
    CreatedAt: datetime = Field(default_factory=datetime.now)

    tenant: Tenants = Relationship(back_populates="tenant_employees")


class TenantLogos(SQLModel, table=True):
    __tablename__ = "TenantLogos"
    __table_args__ = {'schema': 'dbo'}

    LogoId: Optional[int] = Field(default=None, primary_key=True, index=True)
    TenantId: int = Field(foreign_key="dbo.Tenants.TenantId")
    Title: str = Field(max_length=100)
    Description: Optional[str] = Field(default=None, max_length=500)
    Path: str = Field(max_length=500)  # Path used by frontend to identify logo
    Url: str = Field(max_length=500, unique=True, index=True)  # URL identifier for frontend to fetch logo config
    PathBackground: Optional[str] = Field(default=None, max_length=500)
    PrimaryColor: Optional[str] = Field(default=None, max_length=50)
    SecondaryColor: Optional[str] = Field(default=None, max_length=50)
    TertiaryColor: Optional[str] = Field(default=None, max_length=50)
    FavIcon: Optional[str] = Field(default=None, max_length=500)
    CreatedAt: datetime = Field(default_factory=datetime.now)
    UpdatedAt: Optional[datetime] = Field(default=None)

    tenant: Tenants = Relationship(back_populates="logos")

