import enum

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlmodel import Field, SQLModel


class AbsenceTypeEnum(enum.StrEnum):
    VACATION = "vacation"
    PERSONAL = "personal"
    SICK = "sick"


class RequestStatusEnum(enum.StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class TimeUnitEnum(enum.StrEnum):
    FULL_DAY = "full_day"
    HALF_DAY = "half_day"
    HOURS = "hours"


class TimeOffRequest(SQLModel, table=True):
    __tablename__ = "time_off_requests"
    __table_args__ = (
        CheckConstraint("absence_type IN ('vacation','personal','sick')"),
        CheckConstraint("status IN ('pending','approved','rejected','cancelled')"),
        CheckConstraint("time_unit IN ('full_day','half_day','hours')"),
        {"schema": "dbo"},
    )

    request_id: int | None = Field(default=None, primary_key=True)
    employee_id: int = Field(foreign_key="dbo.employees.employee_id", nullable=False)
    absence_type: str = Field(nullable=False, max_length=20)
    status: str = Field(default="pending", nullable=False, max_length=20)
    time_unit: str = Field(nullable=False, max_length=20)
    start_date: str = Field(nullable=False, max_length=10)
    end_date: str = Field(nullable=False, max_length=10)
    start_time: str | None = Field(default=None, max_length=8)
    end_time: str | None = Field(default=None, max_length=8)
    total_hours: str | None = Field(default=None, max_length=10)
    total_days: str = Field(nullable=False, max_length=10)
    reason: str | None = Field(default=None, max_length=2000)
    reviewed_by: int | None = Field(default=None, foreign_key="dbo.employees.employee_id")
    reviewed_at: str | None = Field(default=None, max_length=19)
    review_notes: str | None = Field(default=None, max_length=2000)
    created_at: str = Field(nullable=False, max_length=19)
    updated_at: str = Field(nullable=False, max_length=19)


class TimeOffBalance(SQLModel, table=True):
    __tablename__ = "time_off_balances"
    __table_args__ = (
        CheckConstraint("absence_type IN ('vacation','personal','sick')"),
        UniqueConstraint("employee_id", "absence_type", "year"),
        {"schema": "dbo"},
    )

    balance_id: int | None = Field(default=None, primary_key=True)
    employee_id: int = Field(foreign_key="dbo.employees.employee_id", nullable=False)
    absence_type: str = Field(nullable=False, max_length=20)
    year: int = Field(nullable=False)
    entitled_days: str = Field(default="0.00", nullable=False, max_length=10)
    used_days: str = Field(default="0.00", nullable=False, max_length=10)
    pending_days: str = Field(default="0.00", nullable=False, max_length=10)
    carryover_days: str = Field(default="0.00", nullable=False, max_length=10)


class Holiday(SQLModel, table=True):
    __tablename__ = "holidays"
    __table_args__ = {"schema": "dbo"}

    holiday_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, nullable=False)
    date: str = Field(nullable=False, max_length=10)
    year: int = Field(nullable=False)


class Department(SQLModel, table=True):
    __tablename__ = "departments"
    __table_args__ = {"schema": "dbo"}

    department_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, nullable=False, unique=True)
    code: str | None = Field(default=None, max_length=20)
