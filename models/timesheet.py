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
    __tablename__ = "TimeSheetPunches"
    __table_args__ = (
        CheckConstraint("Status IN ('open','closed','approved','rejected')"),
        {"schema": "dbo"},
    )

    PunchId: int | None = Field(default=None, primary_key=True)
    EmployeeId: int = Field(foreign_key="dbo.Employees.EmployeeId", nullable=False)
    CustomerId: int = Field(foreign_key="dbo.Customers.CustomerId", nullable=False)
    ClockInAt: str = Field(nullable=False, max_length=19)
    ClockOutAt: str | None = Field(default=None, max_length=19)
    Timezone: str | None = Field(default=None, max_length=80)
    IpAddress: str | None = Field(default=None, max_length=45)
    Latitude: str | None = Field(default=None, max_length=20)
    Longitude: str | None = Field(default=None, max_length=20)
    GpsAccuracy: str | None = Field(default=None, max_length=20)
    City: str | None = Field(default=None, max_length=100)
    Region: str | None = Field(default=None, max_length=100)
    Country: str | None = Field(default=None, max_length=100)
    LocationRaw: str | None = Field(default=None)
    WorkedMinutes: int = Field(default=0, nullable=False)
    Status: str = Field(default=TimeSheetPunchStatusEnum.OPEN.value, max_length=20)
    Note: str | None = Field(default=None, max_length=2000)
    ApprovedBy: int | None = Field(default=None, foreign_key="dbo.Employees.EmployeeId")
    ApprovedAt: str | None = Field(default=None, max_length=19)
    CreatedAt: str = Field(nullable=False, max_length=19)
    UpdatedAt: str = Field(nullable=False, max_length=19)

    Customer: Optional["Customers"] = Relationship(sa_relationship_kwargs={"lazy": "joined"})


class TimeSheetLocationSnapshot(SQLModel, table=True):
    __tablename__ = "TimeSheetLocationSnapshots"
    __table_args__ = {"schema": "dbo"}

    SnapshotId: int | None = Field(default=None, primary_key=True)
    EmployeeId: int = Field(foreign_key="dbo.Employees.EmployeeId", nullable=False)
    CustomerId: int | None = Field(default=None, foreign_key="dbo.Customers.CustomerId")
    IpAddress: str | None = Field(default=None, max_length=45)
    Latitude: str | None = Field(default=None, max_length=20)
    Longitude: str | None = Field(default=None, max_length=20)
    GpsAccuracy: str | None = Field(default=None, max_length=20)
    City: str | None = Field(default=None, max_length=100)
    Region: str | None = Field(default=None, max_length=100)
    Country: str | None = Field(default=None, max_length=100)
    Timezone: str | None = Field(default=None, max_length=80)
    LocationRaw: str | None = Field(default=None)
    CapturedAt: str = Field(nullable=False, max_length=19)


class TimeSheetSettings(SQLModel, table=True):
    __tablename__ = "TimeSheetSettings"
    __table_args__ = {"schema": "dbo"}

    SettingId: int | None = Field(default=None, primary_key=True)
    OvertimeDailyHours: str = Field(default="8.00", max_length=10)
    OvertimeWeeklyHours: str | None = Field(default="40.00", max_length=10)
    MaxOvertimeDailyHours: str | None = Field(default="8.00", max_length=10)  # Max overtime hours before auto clock out
    RoundToMinutes: int | None = Field(default=None)
    IsActive: bool = Field(default=True)
    CreatedAt: str = Field(nullable=False, max_length=19)
    UpdatedAt: str = Field(nullable=False, max_length=19)
