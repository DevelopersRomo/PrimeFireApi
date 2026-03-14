from datetime import date, time

from pydantic import field_validator
from sqlmodel import SQLModel

from models.time_off import AbsenceTypeEnum, RequestStatusEnum, TimeUnitEnum


class TimeOffRequestCreate(SQLModel):
    EmployeeId: int | None = None
    AbsenceType: AbsenceTypeEnum
    TimeUnit: TimeUnitEnum
    StartDate: date
    EndDate: date
    StartTime: time | None = None
    EndTime: time | None = None
    Reason: str | None = None


class TimeOffRequestRead(SQLModel):
    RequestId: int
    EmployeeId: int
    AbsenceType: AbsenceTypeEnum
    Status: RequestStatusEnum
    TimeUnit: TimeUnitEnum
    StartDate: str
    EndDate: str
    StartTime: str | None = None
    EndTime: str | None = None
    TotalHours: str | None = None
    TotalDays: str
    Reason: str | None = None
    ReviewedBy: int | None = None
    ReviewedAt: str | None = None
    ReviewNotes: str | None = None
    CreatedAt: str
    UpdatedAt: str

    @classmethod
    @field_validator("StartTime", "EndTime", mode="before")
    @classmethod
    def append_z_to_time(cls, v: str | None) -> str | None:
        if v and isinstance(v, str) and not v.endswith("Z"):
            return f"{v}Z"
        return v

    @classmethod
    @field_validator("ReviewedAt", "CreatedAt", "UpdatedAt", mode="before")
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
    ReviewNotes: str | None = None


class TimeOffBalanceRead(SQLModel):
    BalanceId: int
    EmployeeId: int
    AbsenceType: AbsenceTypeEnum
    Year: int
    EntitledDays: str
    UsedDays: str
    PendingDays: str
    CarryoverDays: str

    class Config:
        from_attributes = True


class HolidayRead(SQLModel):
    HolidayId: int
    Name: str
    Date: str
    Year: int

    class Config:
        from_attributes = True


class DepartmentRead(SQLModel):
    DepartmentId: int
    Name: str
    Code: str | None = None

    class Config:
        from_attributes = True


class CalendarEvent(SQLModel):
    Id: str
    Type: str
    Title: str
    StartDate: str
    EndDate: str
    Status: RequestStatusEnum | None = None
    TimeUnit: TimeUnitEnum | None = None
    EmployeeId: int | None = None
    StartTime: str | None = None
    EndTime: str | None = None

    @classmethod
    @field_validator("StartTime", "EndTime", mode="before")
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
