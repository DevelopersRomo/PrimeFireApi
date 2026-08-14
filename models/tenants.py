from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel


class Tenants(SQLModel, table=True):
    __tablename__ = "tenants"
    __table_args__ = {"schema": "dbo"}

    tenant_id: int | None = Field(default=None, primary_key=True, index=True)
    name: str = Field(max_length=100)
    db_connection_key: str = Field(max_length=50)
    description: str | None = Field(default=None, max_length=255)
    is_active: bool = Field(default=True)
    mail_profile: str = Field(default="default", max_length=50)
    created_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    tenant_employees: list["TenantEmployees"] = Relationship(back_populates="tenant")
    logos: list["TenantLogos"] = Relationship(back_populates="tenant")


class TenantEmployees(SQLModel, table=True):
    __tablename__ = "tenant_employees"
    __table_args__ = {"schema": "dbo"}

    id: int | None = Field(default=None, primary_key=True)
    email: str | None = Field(default=None, max_length=100, unique=True)
    password_hash: str | None = Field(default=None, max_length=255)
    tenant_id: int | None = Field(default=None, foreign_key="dbo.tenants.tenant_id")
    created_at: datetime = Field(default_factory=datetime.now)

    tenant: Tenants = Relationship(back_populates="tenant_employees")


class TenantLogos(SQLModel, table=True):
    __tablename__ = "tenant_logos"
    __table_args__ = {"schema": "dbo"}

    logo_id: int | None = Field(default=None, primary_key=True, index=True)
    tenant_id: int = Field(foreign_key="dbo.tenants.tenant_id")
    title: str = Field(max_length=100)
    description: str | None = Field(default=None, max_length=500)
    logo_dark: str = Field(max_length=500)
    logo_light: str = Field(max_length=500)
    url: str = Field(max_length=500, unique=True, index=True)
    path_background: str | None = Field(default=None, max_length=500)
    primary_color: str | None = Field(default=None, max_length=50)
    secondary_color: str | None = Field(default=None, max_length=50)
    tertiary_color: str | None = Field(default=None, max_length=50)
    fav_icon: str | None = Field(default=None, max_length=500)
    auth_provider: str = Field(default="password", max_length=20)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime | None = Field(default=None)

    tenant: Tenants = Relationship(back_populates="logos")
