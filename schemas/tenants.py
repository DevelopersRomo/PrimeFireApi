from sqlmodel import SQLModel
from datetime import datetime
from typing import Optional, List

class TenantCreate(SQLModel):
    Name: str
    DbConnectionKey: str
    Description: Optional[str] = None

class TenantRead(SQLModel):
    TenantId: int
    Name: str
    Description: Optional[str]
    IsActive: bool
    CreatedAt: datetime

class TenantEmployeeRegister(SQLModel):
    # Information to complete profile and request access
    FirstName: str
    LastName: str
    Phone: Optional[str] = None
    CompanyName: str # To suggest tenant name or identify organization
    Country: Optional[str] = None

class TenantEmployeeRead(SQLModel):
    Id: int
    TenantId: int
    EmployeeId: int
    Status: str
    IsDefault: bool
    TenantName: str

class ApprovalRequest(SQLModel):
    ExternalUserId: int  # ID del ExternalUser en BD Principal
    TenantId: int  # ID del Tenant a asignar
    Status: str = "Active"  # Active o Rejected

class TenantApprovalRequest(SQLModel):
    TenantId: int
    Status: str = "Active"

class ExternalUserRead(SQLModel):
    ExternalUserId: int
    Email: str
    TenantId: Optional[int] = None
    TenantName: Optional[str] = None
    CreatedAt: datetime

class TenantLogoCreate(SQLModel):
    TenantId: int
    Title: str
    Description: Optional[str] = None
    Path: str
    Url: str
    PathBackground: Optional[str] = None
    PrimaryColor: Optional[str] = None
    SecondaryColor: Optional[str] = None
    TertiaryColor: Optional[str] = None

class TenantLogoUpdate(SQLModel):
    Title: Optional[str] = None
    Description: Optional[str] = None
    Path: Optional[str] = None
    Url: Optional[str] = None
    PathBackground: Optional[str] = None
    PrimaryColor: Optional[str] = None
    SecondaryColor: Optional[str] = None
    TertiaryColor: Optional[str] = None

class TenantLogoRead(SQLModel):
    LogoId: int
    TenantId: int
    Title: str
    Description: Optional[str] = None
    Path: str
    Url: str
    PathBackground: Optional[str] = None
    PrimaryColor: Optional[str] = None
    SecondaryColor: Optional[str] = None
    TertiaryColor: Optional[str] = None
    CreatedAt: datetime
    UpdatedAt: Optional[datetime] = None
