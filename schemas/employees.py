from typing import List, Optional
from sqlmodel import SQLModel
from datetime import datetime

# Schema for creating roles
class RoleCreate(SQLModel):
    RoleName: str
    Description: Optional[str] = None

# Schema for role response
class Role(SQLModel):
    RoleId: Optional[int] = None
    RoleName: str
    Description: Optional[str] = None

# Schema for assigning roles to employees
class EmployeeRoleAssignment(SQLModel):
    RoleId: int

# Schema for updating employees (allows partial updates)
class EmployeeUpdate(SQLModel):

    FirstName: Optional[str] = None
    LastName: Optional[str] = None
    DisplayName: Optional[str] = None
    Title: Optional[str] = None
    Department: Optional[str] = None
    Office: Optional[str] = None
    Email: Optional[str] = None
    Phone: Optional[str] = None
    MobilePhone: Optional[str] = None
    OfficePhone: Optional[str] = None
    StreetAddress: Optional[str] = None
    City: Optional[str] = None
    State: Optional[str] = None
    PostalCode: Optional[str] = None
    CountryId: Optional[int] = None

# Schema for Microsoft sync
class EmployeeMicrosoftSync(SQLModel):
    sync_to_microsoft: bool = False

# Schema for role information in employee responses
class EmployeeRole(SQLModel):
    RoleId: int
    RoleName: str
    Description: Optional[str] = None

# Schema for response (all fields) with computed country_name and roles
class Employee(SQLModel):
    # Employee fields
    EmployeeId: Optional[int] = None
    FirstName: Optional[str] = None
    LastName: Optional[str] = None
    DisplayName: Optional[str] = None
    Title: Optional[str] = None
    Department: Optional[str] = None
    Office: Optional[str] = None
    Email: Optional[str] = None
    Phone: Optional[str] = None
    MobilePhone: Optional[str] = None
    OfficePhone: Optional[str] = None
    StreetAddress: Optional[str] = None
    City: Optional[str] = None
    State: Optional[str] = None
    PostalCode: Optional[str] = None
    CountryId: Optional[int] = None
    AzureOid: Optional[str] = None
    AzureUpn: Optional[str] = None
    LastSyncedAt: Optional[datetime] = None

    # Computed fields
    country_name: Optional[str] = None
    roles: List[EmployeeRole] = []
