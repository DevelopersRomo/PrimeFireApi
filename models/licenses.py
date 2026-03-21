from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.employees import Employees


class Licenses(SQLModel, table=True):
    __tablename__ = "licenses"
    __table_args__ = {"schema": "dbo"}

    license_id: int | None = Field(default=None, primary_key=True)
    software: str | None = None
    version: str | None = None
    created_at: date | None = None
    expiry_date: date | None = None
    key: str | None = None
    account: str | None = None
    password: str | None = None
    notes: str | None = None

    employee_id: int | None = Field(foreign_key="dbo.employees.employee_id")

    employee: Optional["Employees"] = Relationship(back_populates="licenses")
