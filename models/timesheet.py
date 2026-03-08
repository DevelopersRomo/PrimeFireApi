import enum
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from models.customers import Customers

from sqlalchemy import CheckConstraint
from sqlmodel import Field, SQLModel, Relationship


class TimeSheetPunchStatusEnum(str, enum.Enum):
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

    PunchId: Optional[int] = Field(default=None, primary_key=True)
    EmployeeId: int = Field(foreign_key="dbo.Employees.EmployeeId", nullable=False)
    CustomerId: int = Field(foreign_key="dbo.Customers.CustomerId", nullable=False)
    ClockInAt: str = Field(nullable=False, max_length=19)
    ClockOutAt: Optional[str] = Field(default=None, max_length=19)
    Timezone: Optional[str] = Field(default=None, max_length=80)
    IpAddress: Optional[str] = Field(default=None, max_length=45)
    Latitude: Optional[str] = Field(default=None, max_length=20)
    Longitude: Optional[str] = Field(default=None, max_length=20)
    GpsAccuracy: Optional[str] = Field(default=None, max_length=20)
    City: Optional[str] = Field(default=None, max_length=100)
    Region: Optional[str] = Field(default=None, max_length=100)
    Country: Optional[str] = Field(default=None, max_length=100)
    LocationRaw: Optional[str] = Field(default=None)
    WorkedMinutes: int = Field(default=0, nullable=False)
    Status: str = Field(default=TimeSheetPunchStatusEnum.OPEN.value, max_length=20)
    Note: Optional[str] = Field(default=None, max_length=2000)
    ApprovedBy: Optional[int] = Field(
        default=None, foreign_key="dbo.Employees.EmployeeId"
    )
    ApprovedAt: Optional[str] = Field(default=None, max_length=19)
    CreatedAt: str = Field(nullable=False, max_length=19)
    UpdatedAt: str = Field(nullable=False, max_length=19)

    Customer: Optional["Customers"] = Relationship(
        sa_relationship_kwargs={"lazy": "joined"}
    )


class TimeSheetLocationSnapshot(SQLModel, table=True):
    __tablename__ = "TimeSheetLocationSnapshots"
    __table_args__ = {"schema": "dbo"}

    SnapshotId: Optional[int] = Field(default=None, primary_key=True)
    EmployeeId: int = Field(foreign_key="dbo.Employees.EmployeeId", nullable=False)
    CustomerId: Optional[int] = Field(
        default=None, foreign_key="dbo.Customers.CustomerId"
    )
    IpAddress: Optional[str] = Field(default=None, max_length=45)
    Latitude: Optional[str] = Field(default=None, max_length=20)
    Longitude: Optional[str] = Field(default=None, max_length=20)
    GpsAccuracy: Optional[str] = Field(default=None, max_length=20)
    City: Optional[str] = Field(default=None, max_length=100)
    Region: Optional[str] = Field(default=None, max_length=100)
    Country: Optional[str] = Field(default=None, max_length=100)
    Timezone: Optional[str] = Field(default=None, max_length=80)
    LocationRaw: Optional[str] = Field(default=None)
    CapturedAt: str = Field(nullable=False, max_length=19)


class TimeSheetSettings(SQLModel, table=True):
    __tablename__ = "TimeSheetSettings"
    __table_args__ = {"schema": "dbo"}

    SettingId: Optional[int] = Field(default=None, primary_key=True)
    OvertimeDailyHours: str = Field(default="8.00", max_length=10)
    OvertimeWeeklyHours: Optional[str] = Field(default="40.00", max_length=10)
    MaxOvertimeDailyHours: Optional[str] = Field(default="8.00", max_length=10)  # Max overtime hours before auto clock out
    RoundToMinutes: Optional[int] = Field(default=None)
    IsActive: bool = Field(default=True)
    CreatedAt: str = Field(nullable=False, max_length=19)
    UpdatedAt: str = Field(nullable=False, max_length=19)
