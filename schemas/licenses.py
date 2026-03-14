from datetime import date

from sqlmodel import SQLModel

from schemas.employees import EmployeeRead


# Schema for creating licenses (without auto-generated fields)
class LicenseCreate(SQLModel):
    Software: str
    Version: str
    CreatedAt: date | None = None
    ExpiryDate: date | None = None
    Key: str
    Account: str
    Password: str
    Notes: str | None = None
    EmployeeId: int


class LicenseUpdate(SQLModel):
    Software: str | None = None
    Version: str | None = None
    CreatedAt: date | None = None
    ExpiryDate: date | None = None
    Key: str | None = None
    Account: str | None = None
    Password: str | None = None
    Notes: str | None = None
    EmployeeId: int | None = None


class LicenseRead(SQLModel):
    LicenseId: int
    Software: str | None
    Version: str | None
    CreatedAt: date | None
    ExpiryDate: date | None
    Key: str | None
    Account: str | None
    Password: str | None
    Notes: str | None
    EmployeeId: int | None
    Employee: EmployeeRead | None


class License(LicenseRead):
    pass
