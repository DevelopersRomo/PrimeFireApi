import enum
from datetime import date, datetime, time
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlmodel import Field, SQLModel


class AbsenceTypeEnum(str, enum.Enum):
    VACATION = "vacation"
    PERSONAL = "personal"
    SICK = "sick"


class RequestStatusEnum(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class TimeUnitEnum(str, enum.Enum):
    FULL_DAY = "full_day"
    HALF_DAY = "half_day"
    HOURS = "hours"


class TimeOffRequest(SQLModel, table=True):
    __tablename__ = "TimeOffRequests"
    __table_args__ = (
        CheckConstraint("AbsenceType IN ('vacation','personal','sick')"),
        CheckConstraint("Status IN ('pending','approved','rejected','cancelled')"),
        CheckConstraint("TimeUnit IN ('full_day','half_day','hours')"),
        {"schema": "dbo"},
    )

    RequestId: Optional[int] = Field(default=None, primary_key=True)
    EmployeeId: int = Field(foreign_key="dbo.Employees.EmployeeId", nullable=False)
    AbsenceType: str = Field(nullable=False, max_length=20)
    Status: str = Field(default="pending", nullable=False, max_length=20)
    TimeUnit: str = Field(nullable=False, max_length=20)
    StartDate: str = Field(nullable=False, max_length=10)
    EndDate: str = Field(nullable=False, max_length=10)
    StartTime: Optional[str] = Field(default=None, max_length=8)
    EndTime: Optional[str] = Field(default=None, max_length=8)
    TotalHours: Optional[str] = Field(default=None, max_length=10)
    TotalDays: str = Field(nullable=False, max_length=10)
    Reason: Optional[str] = Field(default=None, max_length=2000)
    ReviewedBy: Optional[int] = Field(
        default=None, foreign_key="dbo.Employees.EmployeeId"
    )
    ReviewedAt: Optional[str] = Field(default=None, max_length=19)
    ReviewNotes: Optional[str] = Field(default=None, max_length=2000)
    CreatedAt: str = Field(nullable=False, max_length=19)
    UpdatedAt: str = Field(nullable=False, max_length=19)


class TimeOffBalance(SQLModel, table=True):
    __tablename__ = "TimeOffBalances"
    __table_args__ = (
        CheckConstraint("AbsenceType IN ('vacation','personal','sick')"),
        UniqueConstraint("EmployeeId", "AbsenceType", "Year"),
        {"schema": "dbo"},
    )

    BalanceId: Optional[int] = Field(default=None, primary_key=True)
    EmployeeId: int = Field(foreign_key="dbo.Employees.EmployeeId", nullable=False)
    AbsenceType: str = Field(nullable=False, max_length=20)
    Year: int = Field(nullable=False)
    EntitledDays: str = Field(default="0.00", nullable=False, max_length=10)
    UsedDays: str = Field(default="0.00", nullable=False, max_length=10)
    PendingDays: str = Field(default="0.00", nullable=False, max_length=10)
    CarryoverDays: str = Field(default="0.00", nullable=False, max_length=10)


class Holiday(SQLModel, table=True):
    __tablename__ = "Holidays"
    __table_args__ = {"schema": "dbo"}

    HolidayId: Optional[int] = Field(default=None, primary_key=True)
    Name: str = Field(max_length=100, nullable=False)
    Date: str = Field(nullable=False, max_length=10)
    Year: int = Field(nullable=False)


class Department(SQLModel, table=True):
    __tablename__ = "Departments"
    __table_args__ = {"schema": "dbo"}

    DepartmentId: Optional[int] = Field(default=None, primary_key=True)
    Name: str = Field(max_length=100, nullable=False, unique=True)
    Code: Optional[str] = Field(default=None, max_length=20)
