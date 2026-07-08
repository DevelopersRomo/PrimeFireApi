from datetime import date, time

from pydantic import field_validator
from sqlmodel import SQLModel

from models.time_off import AbsenceTypeEnum, RequestStatusEnum, TimeUnitEnum


class TimeOffRequestCreate(SQLModel):
    employee_id: int | None = None
    absence_type: AbsenceTypeEnum
    time_unit: TimeUnitEnum
    start_date: date
    end_date: date
    start_time: time | None = None
    end_time: time | None = None
    reason: str | None = None


class TimeOffRequestUpdate(SQLModel):
    absence_type: AbsenceTypeEnum | None = None
    time_unit: TimeUnitEnum | None = None
    start_date: date | None = None
    end_date: date | None = None
    start_time: time | None = None
    end_time: time | None = None
    reason: str | None = None


class TimeOffRequestRead(SQLModel):
    request_id: int
    employee_id: int
    absence_type: AbsenceTypeEnum
    status: RequestStatusEnum
    time_unit: TimeUnitEnum
    start_date: str
    end_date: str
    start_time: str | None = None
    end_time: str | None = None
    total_hours: str | None = None
    total_days: str
    reason: str | None = None
    reviewed_by: int | None = None
    reviewed_at: str | None = None
    review_notes: str | None = None
    created_at: str
    updated_at: str

    @classmethod
    @field_validator("start_time", "end_time", mode="before")
    @classmethod
    def append_z_to_time(cls, v: str | None) -> str | None:
        if v and isinstance(v, str) and not v.endswith("Z"):
            return f"{v}Z"
        return v

    @classmethod
    @field_validator("reviewed_at", "created_at", "updated_at", mode="before")
    @classmethod
    def format_datetime_utc(cls, v: str | None) -> str | None:
        if v and isinstance(v, str):
            if len(v) == 19 and v[10] == " ":
                return v.replace(" ", "T") + "Z"
            if not v.endswith("Z"):
                return f"{v}Z"
        return v

    class Config:
        from_attributes = True


class RequestReview(SQLModel):
    review_notes: str | None = None


class TimeOffBalanceRead(SQLModel):
    balance_id: int
    employee_id: int
    absence_type: AbsenceTypeEnum
    year: int
    entitled_days: str
    used_days: str
    pending_days: str
    carryover_days: str

    class Config:
        from_attributes = True


class HolidayRead(SQLModel):
    holiday_id: int
    name: str
    date: str
    year: int

    class Config:
        from_attributes = True


class DepartmentRead(SQLModel):
    department_id: int
    name: str
    code: str | None = None

    class Config:
        from_attributes = True


class CalendarEvent(SQLModel):
    id: str
    type: str
    title: str
    start_date: str
    end_date: str
    status: RequestStatusEnum | None = None
    time_unit: TimeUnitEnum | None = None
    employee_id: int | None = None
    start_time: str | None = None
    end_time: str | None = None

    @classmethod
    @field_validator("start_time", "end_time", mode="before")
    @classmethod
    def append_z_to_time(cls, v: str | None) -> str | None:
        if v and isinstance(v, str) and not v.endswith("Z"):
            return f"{v}Z"
        return v


class StatusSummary(SQLModel):
    pending: int = 0
    approved: int = 0
    rejected: int = 0
    cancelled: int = 0


class AbsenceTotals(SQLModel):
    vacation: float = 0
    personal: float = 0
    sick: float = 0


class BalanceTotals(SQLModel):
    entitled: float = 0
    used: float = 0
    pending: float = 0
    carryover: float = 0


class ReportSummary(SQLModel):
    total_requests: int
    status: StatusSummary
    totals_by_absence: AbsenceTotals
    balances: dict[str, BalanceTotals]
