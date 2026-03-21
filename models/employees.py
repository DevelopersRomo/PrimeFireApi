from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.countries import Countries
    from models.hardware_inventory import HardwareInventory
    from models.licenses import Licenses
    from models.tickets import Tickets


class EmployeeRoles(SQLModel, table=True):
    __tablename__ = "employee_roles"
    __table_args__ = {"schema": "dbo"}

    employee_id: int = Field(foreign_key="dbo.employees.employee_id", primary_key=True)
    role_id: int = Field(foreign_key="dbo.roles.role_id", primary_key=True)


class Roles(SQLModel, table=True):
    __tablename__ = "roles"
    __table_args__ = {"schema": "dbo"}

    role_id: int | None = Field(default=None, primary_key=True, index=True)
    role_name: str = Field(max_length=50)
    description: str | None = Field(default=None, max_length=200)

    # Many-to-many relationship with Employees through EmployeeRoles
    employees: list["Employees"] = Relationship(back_populates="roles", link_model=EmployeeRoles)


class Employees(SQLModel, table=True):
    __tablename__ = "employees"
    __table_args__ = {"schema": "dbo"}

    employee_id: int | None = Field(default=None, primary_key=True, index=True)

    # Microsoft Graph fields
    first_name: str | None = Field(default=None, max_length=50)
    last_name: str | None = Field(default=None, max_length=50)
    display_name: str | None = Field(default=None, max_length=100)
    title: str | None = Field(default=None, max_length=50)
    department: str | None = Field(default=None, max_length=50)
    office: str | None = Field(default=None, max_length=50)
    email: str | None = Field(default=None, max_length=50)
    phone: str | None = Field(default=None, max_length=20)
    mobile_phone: str | None = Field(default=None, max_length=20)
    office_phone: str | None = Field(default=None, max_length=20)
    anydesk: str | None = Field(default=None, max_length=50)
    manager: str | None = Field(default=None, max_length=100)
    manager_email: str | None = Field(default=None, max_length=100)
    manager_employee_id: int | None = Field(default=None, foreign_key="dbo.employees.employee_id")

    # Address fields
    street_address: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=50)
    state: str | None = Field(default=None, max_length=50)
    postal_code: str | None = Field(default=None, max_length=20)

    # Internal fields
    country_id: int | None = Field(default=None, foreign_key="dbo.countries.country_id")

    # Relationship to Countries
    country: Optional["Countries"] = Relationship()

    # Many-to-many relationship with Roles through EmployeeRoles
    roles: list["Roles"] = Relationship(back_populates="employees", link_model=EmployeeRoles)

    # Azure AD fields for auto-registration
    azure_oid: str | None = Field(default=None, max_length=100, unique=True)
    azure_upn: str | None = Field(default=None, max_length=100)

    # Auth Fields
    password_hash: str | None = Field(default=None, max_length=255)

    # Sync tracking
    last_synced_at: datetime | None = Field(default=None)

    # Relationships with Tickets
    created_tickets: list["Tickets"] = Relationship(
        back_populates="creator", sa_relationship_kwargs={"foreign_keys": "[Tickets.created_by]"}
    )
    assigned_tickets: list["Tickets"] = Relationship(
        back_populates="assignee", sa_relationship_kwargs={"foreign_keys": "[Tickets.assigned_to]"}
    )

    # Relationships with Licenses
    licenses: list["Licenses"] = Relationship(back_populates="employee")

    # Relationships with Hardware Inventory
    hardware_inventories: list["HardwareInventory"] = Relationship(back_populates="employee")
