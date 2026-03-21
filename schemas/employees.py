from datetime import datetime

from sqlmodel import SQLModel


class RoleCreate(SQLModel):
    role_name: str
    description: str | None = None


class Role(SQLModel):
    role_id: int | None = None
    role_name: str
    description: str | None = None


class EmployeeRoleAssignment(SQLModel):
    role_id: int


class EmployeeUpdate(SQLModel):
    first_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None
    title: str | None = None
    department: str | None = None
    office: str | None = None
    email: str | None = None
    phone: str | None = None
    mobile_phone: str | None = None
    office_phone: str | None = None
    anydesk: str | None = None
    manager: str | None = None
    manager_email: str | None = None
    manager_employee_id: int | None = None
    street_address: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country_id: int | None = None


class EmployeeMicrosoftSync(SQLModel):
    sync_to_microsoft: bool = False


class EmployeeRole(SQLModel):
    role_id: int
    role_name: str
    description: str | None = None


class Employee(SQLModel):
    employee_id: int | None = None
    first_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None
    title: str | None = None
    department: str | None = None
    office: str | None = None
    email: str | None = None
    phone: str | None = None
    mobile_phone: str | None = None
    office_phone: str | None = None
    anydesk: str | None = None
    manager: str | None = None
    manager_email: str | None = None
    manager_employee_id: int | None = None
    street_address: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country_id: int | None = None
    azure_oid: str | None = None
    azure_upn: str | None = None
    last_synced_at: datetime | None = None

    country_name: str | None = None
    roles: list[EmployeeRole] = []


class EmployeeRead(SQLModel):
    employee_id: int
    first_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None
    department: str | None = None
    email: str | None = None
