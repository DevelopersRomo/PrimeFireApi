from datetime import datetime

from sqlmodel import SQLModel


class TenantCreate(SQLModel):
    Name: str
    DbConnectionKey: str
    Description: str | None = None


class TenantUpdate(SQLModel):
    Name: str | None = None
    DbConnectionKey: str | None = None
    Description: str | None = None
    IsActive: bool | None = None


class TenantRead(SQLModel):
    TenantId: int
    Name: str
    DbConnectionKey: str
    Description: str | None
    IsActive: bool
    CreatedAt: datetime


class TenantEmployeeRegister(SQLModel):
    # Information to complete profile and request access
    FirstName: str
    LastName: str
    Phone: str | None = None
    CompanyName: str  # To suggest tenant name or identify organization
    Country: str | None = None


class TenantEmployeeRead(SQLModel):
    Id: int
    Email: str
    TenantId: int | None = None
    TenantName: str | None = None
    CreatedAt: datetime


class ApprovalRequest(SQLModel):
    TenantEmployeeId: int  # ID del TenantEmployee en BD Principal
    TenantId: int  # ID del Tenant a asignar


class TenantApprovalRequest(SQLModel):
    TenantId: int
    Status: str = "Active"


class TenantEmployeePendingRead(SQLModel):
    Id: int
    Email: str
    TenantId: int | None = None
    TenantName: str | None = None
    CreatedAt: datetime


class TenantLogoCreate(SQLModel):
    TenantId: int
    Title: str
    Description: str | None = None
    Path: str
    Url: str
    Email: str | None = None
    PathBackground: str | None = None
    PrimaryColor: str | None = None
    SecondaryColor: str | None = None
    TertiaryColor: str | None = None
    FavIcon: str | None = None


class TenantLogoUpdate(SQLModel):
    Title: str | None = None
    Description: str | None = None
    Path: str | None = None
    Url: str | None = None
    Email: str | None = None
    PathBackground: str | None = None
    PrimaryColor: str | None = None
    SecondaryColor: str | None = None
    TertiaryColor: str | None = None
    FavIcon: str | None = None


class TenantLogoRead(SQLModel):
    LogoId: int
    TenantId: int
    Title: str
    Description: str | None = None
    Path: str
    Url: str
    Email: str | None = None
    PathBackground: str | None = None
    PrimaryColor: str | None = None
    SecondaryColor: str | None = None
    TertiaryColor: str | None = None
    FavIcon: str | None = None
    CreatedAt: datetime
    UpdatedAt: datetime | None = None
