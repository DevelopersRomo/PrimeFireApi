from datetime import date

from sqlmodel import SQLModel

from schemas.employees import EmployeeRead


class LicenseCreate(SQLModel):
    software: str
    version: str
    created_at: date | None = None
    expiry_date: date | None = None
    key: str
    account: str
    password: str
    notes: str | None = None
    employee_id: int


class LicenseUpdate(SQLModel):
    software: str | None = None
    version: str | None = None
    created_at: date | None = None
    expiry_date: date | None = None
    key: str | None = None
    account: str | None = None
    password: str | None = None
    notes: str | None = None
    employee_id: int | None = None


class LicenseRead(SQLModel):
    license_id: int
    software: str | None
    version: str | None
    created_at: date | None
    expiry_date: date | None
    key: str | None
    account: str | None
    password: str | None
    notes: str | None
    employee_id: int | None
    employee: EmployeeRead | None


class License(LicenseRead):
    pass
