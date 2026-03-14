from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.employees import Employees


class Licenses(SQLModel, table=True):
    __tablename__ = "Licenses"
    __table_args__ = {"schema": "dbo"}

    LicenseId: int | None = Field(default=None, primary_key=True)
    Software: str | None = None
    Version: str | None = None
    CreatedAt: date | None = None
    ExpiryDate: date | None = None
    Key: str | None = None
    Account: str | None = None
    Password: str | None = None
    Notes: str | None = None

    EmployeeId: int | None = Field(foreign_key="dbo.Employees.EmployeeId")

    Employee: Optional["Employees"] = Relationship(back_populates="Licenses")
