from datetime import datetime

from sqlmodel import SQLModel


# Schema for creating roles
class RoleCreate(SQLModel):
    RoleName: str
    Description: str | None = None


# Schema for role response
class Role(SQLModel):
    RoleId: int | None = None
    RoleName: str
    Description: str | None = None


# Schema for assigning roles to employees
class EmployeeRoleAssignment(SQLModel):
    RoleId: int


# Schema for updating employees (allows partial updates)
class EmployeeUpdate(SQLModel):
    FirstName: str | None = None
    LastName: str | None = None
    DisplayName: str | None = None
    Title: str | None = None
    Department: str | None = None
    Office: str | None = None
    Email: str | None = None
    Phone: str | None = None
    MobilePhone: str | None = None
    OfficePhone: str | None = None
    Anydesk: str | None = None
    Manager: str | None = None
    ManagerEmail: str | None = None
    ManagerEmployeeId: int | None = None
    StreetAddress: str | None = None
    City: str | None = None
    State: str | None = None
    PostalCode: str | None = None
    CountryId: int | None = None


# Schema for Microsoft sync
class EmployeeMicrosoftSync(SQLModel):
    sync_to_microsoft: bool = False


# Schema for role information in employee responses
class EmployeeRole(SQLModel):
    RoleId: int
    RoleName: str
    Description: str | None = None


# Schema for response (all fields) with computed country_name and roles
class Employee(SQLModel):
    # Employee fields
    EmployeeId: int | None = None
    FirstName: str | None = None
    LastName: str | None = None
    DisplayName: str | None = None
    Title: str | None = None
    Department: str | None = None
    Office: str | None = None
    Email: str | None = None
    Phone: str | None = None
    MobilePhone: str | None = None
    OfficePhone: str | None = None
    Anydesk: str | None = None
    Manager: str | None = None
    ManagerEmail: str | None = None
    ManagerEmployeeId: int | None = None
    StreetAddress: str | None = None
    City: str | None = None
    State: str | None = None
    PostalCode: str | None = None
    CountryId: int | None = None
    AzureOid: str | None = None
    AzureUpn: str | None = None
    LastSyncedAt: datetime | None = None

    # Computed fields
    country_name: str | None = None
    roles: list[EmployeeRole] = []


# EmployeeRead
class EmployeeRead(SQLModel):
    EmployeeId: int
    FirstName: str | None
    LastName: str | None
    DisplayName: str | None
    Department: str | None
    Email: str | None
