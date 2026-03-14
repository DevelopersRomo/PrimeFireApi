from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.countries import Countries
    from models.hardware_inventory import HardwareInventory
    from models.licenses import Licenses
    from models.tickets import Tickets


class EmployeeRoles(SQLModel, table=True):
    __tablename__ = "EmployeeRoles"
    __table_args__ = {"schema": "dbo"}

    EmployeeId: int = Field(foreign_key="dbo.Employees.EmployeeId", primary_key=True)
    RoleId: int = Field(foreign_key="dbo.Roles.RoleId", primary_key=True)


class Roles(SQLModel, table=True):
    __tablename__ = "Roles"
    __table_args__ = {"schema": "dbo"}

    RoleId: int | None = Field(default=None, primary_key=True, index=True)
    RoleName: str = Field(max_length=50)
    Description: str | None = Field(default=None, max_length=200)

    # Many-to-many relationship with Employees through EmployeeRoles
    employees: list["Employees"] = Relationship(back_populates="roles", link_model=EmployeeRoles)


class Employees(SQLModel, table=True):
    __tablename__ = "Employees"
    __table_args__ = {"schema": "dbo"}

    EmployeeId: int | None = Field(default=None, primary_key=True, index=True)

    # Microsoft Graph fields
    FirstName: str | None = Field(default=None, max_length=50)
    LastName: str | None = Field(default=None, max_length=50)
    DisplayName: str | None = Field(default=None, max_length=100)
    Title: str | None = Field(default=None, max_length=50)
    Department: str | None = Field(default=None, max_length=50)
    Office: str | None = Field(default=None, max_length=50)
    Email: str | None = Field(default=None, max_length=50)
    Phone: str | None = Field(default=None, max_length=20)
    MobilePhone: str | None = Field(default=None, max_length=20)
    OfficePhone: str | None = Field(default=None, max_length=20)
    Anydesk: str | None = Field(default=None, max_length=50)
    Manager: str | None = Field(default=None, max_length=100)
    ManagerEmail: str | None = Field(default=None, max_length=100)
    ManagerEmployeeId: int | None = Field(default=None, foreign_key="dbo.Employees.EmployeeId")

    # Address fields
    StreetAddress: str | None = Field(default=None, max_length=100)
    City: str | None = Field(default=None, max_length=50)
    State: str | None = Field(default=None, max_length=50)
    PostalCode: str | None = Field(default=None, max_length=20)

    # Internal fields
    CountryId: int | None = Field(default=None, foreign_key="dbo.Countries.CountryId")

    # Relationship to Countries
    country: Optional["Countries"] = Relationship()

    # Many-to-many relationship with Roles through EmployeeRoles
    roles: list["Roles"] = Relationship(back_populates="employees", link_model=EmployeeRoles)

    # Azure AD fields for auto-registration
    AzureOid: str | None = Field(default=None, max_length=100, unique=True)
    AzureUpn: str | None = Field(default=None, max_length=100)

    # Auth Fields
    PasswordHash: str | None = Field(default=None, max_length=255)

    # Sync tracking
    LastSyncedAt: datetime | None = Field(default=None)

    # Relationships with Tickets
    created_tickets: list["Tickets"] = Relationship(
        back_populates="creator", sa_relationship_kwargs={"foreign_keys": "[Tickets.CreatedBy]"}
    )
    assigned_tickets: list["Tickets"] = Relationship(
        back_populates="assignee", sa_relationship_kwargs={"foreign_keys": "[Tickets.AssignedTo]"}
    )

    # Relationships with Licenses
    Licenses: list["Licenses"] = Relationship(back_populates="Employee")

    # Relationships with Hardware Inventory
    hardware_inventories: list["HardwareInventory"] = Relationship(back_populates="Employee")
