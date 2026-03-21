import enum
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from models.customers import Customers

from sqlalchemy import CheckConstraint
from sqlmodel import Field, Relationship, SQLModel


class TimeSheetPunchStatusEnum(enum.StrEnum):
    OPEN = "open"
    CLOSED = "closed"
    APPROVED = "approved"
    REJECTED = "rejected"


class TimeSheetPunch(SQLModel, table=True):
    __tablename__ = "time_sheet_punches"
    __table_args__ = (
        CheckConstraint("status IN ('open','closed','approved','rejected')"),
        {"schema": "dbo"},
    )

    punch_id: int | None = Field(default=None, primary_key=True)
    employee_id: int = Field(foreign_key="dbo.employees.employee_id", nullable=False)
    customer_id: int = Field(foreign_key="dbo.customers.customer_id", nullable=False)
    clock_in_at: str = Field(nullable=False, max_length=19)
    clock_out_at: str | None = Field(default=None, max_length=19)
    timezone: str | None = Field(default=None, max_length=80)
    ip_address: str | None = Field(default=None, max_length=45)
    latitude: str | None = Field(default=None, max_length=20)
    longitude: str | None = Field(default=None, max_length=20)
    gps_accuracy: str | None = Field(default=None, max_length=20)
    city: str | None = Field(default=None, max_length=100)
    region: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    location_raw: str | None = Field(default=None)
    worked_minutes: int = Field(default=0, nullable=False)
    status: str = Field(default=TimeSheetPunchStatusEnum.OPEN.value, max_length=20)
    note: str | None = Field(default=None, max_length=2000)
    approved_by: int | None = Field(default=None, foreign_key="dbo.employees.employee_id")
    approved_at: str | None = Field(default=None, max_length=19)
    created_at: str = Field(nullable=False, max_length=19)
    updated_at: str = Field(nullable=False, max_length=19)

    customer: Optional["Customers"] = Relationship(sa_relationship_kwargs={"lazy": "joined"})


class TimeSheetLocationSnapshot(SQLModel, table=True):
    __tablename__ = "time_sheet_location_snapshots"
    __table_args__ = {"schema": "dbo"}

    snapshot_id: int | None = Field(default=None, primary_key=True)
    employee_id: int = Field(foreign_key="dbo.employees.employee_id", nullable=False)
    customer_id: int | None = Field(default=None, foreign_key="dbo.customers.customer_id")
    ip_address: str | None = Field(default=None, max_length=45)
    latitude: str | None = Field(default=None, max_length=20)
    longitude: str | None = Field(default=None, max_length=20)
    gps_accuracy: str | None = Field(default=None, max_length=20)
    city: str | None = Field(default=None, max_length=100)
    region: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    timezone: str | None = Field(default=None, max_length=80)
    location_raw: str | None = Field(default=None)
    captured_at: str = Field(nullable=False, max_length=19)


class TimeSheetSettings(SQLModel, table=True):
    __tablename__ = "time_sheet_settings"
    __table_args__ = {"schema": "dbo"}

    setting_id: int | None = Field(default=None, primary_key=True)
    overtime_daily_hours: str = Field(default="8.00", max_length=10)
    overtime_weekly_hours: str | None = Field(default="40.00", max_length=10)
    max_overtime_daily_hours: str | None = Field(default="8.00", max_length=10)
    round_to_minutes: int | None = Field(default=None)
    is_active: bool = Field(default=True)
    created_at: str = Field(nullable=False, max_length=19)
    updated_at: str = Field(nullable=False, max_length=19)
