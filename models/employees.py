from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from models.countries import Countries
    from models.modules import Modules

class EmployeeRoles(SQLModel, table=True):
    __tablename__ = "EmployeeRoles"

    EmployeeId: int = Field(foreign_key="Employees.EmployeeId", primary_key=True)
    RoleId: int = Field(foreign_key="Roles.RoleId", primary_key=True)

class Roles(SQLModel, table=True):
    __tablename__ = "Roles"

    RoleId: Optional[int] = Field(default=None, primary_key=True, index=True)
    RoleName: str = Field(max_length=50)
    Description: Optional[str] = Field(default=None, max_length=200)

    # Many-to-many relationship with Employees through EmployeeRoles
    employees: List["Employees"] = Relationship(
        back_populates="roles",
        link_model=EmployeeRoles
    )

class Employees(SQLModel, table=True):
    __tablename__ = "Employees"

    EmployeeId: Optional[int] = Field(default=None, primary_key=True, index=True)

    # Microsoft Graph fields
    FirstName: Optional[str] = Field(default=None, max_length=50)
    LastName: Optional[str] = Field(default=None, max_length=50)
    DisplayName: Optional[str] = Field(default=None, max_length=100)
    Title: Optional[str] = Field(default=None, max_length=50)
    Department: Optional[str] = Field(default=None, max_length=50)
    Office: Optional[str] = Field(default=None, max_length=50)
    Email: Optional[str] = Field(default=None, max_length=50)
    Phone: Optional[str] = Field(default=None, max_length=20)
    MobilePhone: Optional[str] = Field(default=None, max_length=20)
    OfficePhone: Optional[str] = Field(default=None, max_length=20)
    
    # Address fields
    StreetAddress: Optional[str] = Field(default=None, max_length=100)
    City: Optional[str] = Field(default=None, max_length=50)
    State: Optional[str] = Field(default=None, max_length=50)
    PostalCode: Optional[str] = Field(default=None, max_length=20)
    
    # Internal fields
    CountryId: Optional[int] = Field(default=None, foreign_key="Countries.CountryId")

    # Relationship to Countries
    country: Optional["Countries"] = Relationship()

    # Many-to-many relationship with Roles through EmployeeRoles
    roles: List["Roles"] = Relationship(
        back_populates="employees",
        link_model=EmployeeRoles
    )

    # Azure AD fields for auto-registration
    AzureOid: Optional[str] = Field(default=None, max_length=100, unique=True)
    AzureUpn: Optional[str] = Field(default=None, max_length=100)
    
    # Sync tracking
    LastSyncedAt: Optional[datetime] = Field(default=None)

    # Relationships with Tickets
    created_tickets: List["Tickets"] = Relationship(
        back_populates="creator",
        sa_relationship_kwargs={"foreign_keys": "Tickets.CreatedBy"}
    )
    assigned_tickets: List["Tickets"] = Relationship(
        back_populates="assignee",
        sa_relationship_kwargs={"foreign_keys": "Tickets.AssignedTo"}
    )