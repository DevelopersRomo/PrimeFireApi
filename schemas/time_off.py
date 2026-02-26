from datetime import date, datetime, time
from decimal import Decimal
from typing import Dict, Optional

from pydantic import field_validator
from sqlmodel import SQLModel

from models.time_off import AbsenceTypeEnum, RequestStatusEnum, TimeUnitEnum


class TimeOffRequestCreate(SQLModel):
    EmployeeId: Optional[int] = None
    AbsenceType: AbsenceTypeEnum
    TimeUnit: TimeUnitEnum
    StartDate: date
    EndDate: date
    StartTime: Optional[time] = None
    EndTime: Optional[time] = None
    Reason: Optional[str] = None


class TimeOffRequestRead(SQLModel):
    RequestId: int
    EmployeeId: int
    AbsenceType: AbsenceTypeEnum
    Status: RequestStatusEnum
    TimeUnit: TimeUnitEnum
    StartDate: str
    EndDate: str
    StartTime: Optional[str] = None
    EndTime: Optional[str] = None
    TotalHours: Optional[str] = None
    TotalDays: str
    Reason: Optional[str] = None
    ReviewedBy: Optional[int] = None
    ReviewedAt: Optional[str] = None
    ReviewNotes: Optional[str] = None
    CreatedAt: str
    UpdatedAt: str

    @field_validator("StartTime", "EndTime", mode="before")
    @classmethod
    def append_z_to_time(cls, v: Optional[str]) -> Optional[str]:
        if v and isinstance(v, str) and not v.endswith("Z"):
            return f"{v}Z"
        return v

    @field_validator("ReviewedAt", "CreatedAt", "UpdatedAt", mode="before")
    @classmethod
    def format_datetime_utc(cls, v: Optional[str]) -> Optional[str]:
        if v and isinstance(v, str):
            if len(v) == 19 and v[10] == " ":
                return v.replace(" ", "T") + "Z"
            if not v.endswith("Z"):
                return f"{v}Z"
        return v

    class Config:
        from_attributes = True


class RequestReview(SQLModel):
    ReviewNotes: Optional[str] = None


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
    Code: Optional[str] = None

    class Config:
        from_attributes = True


class CalendarEvent(SQLModel):
    Id: str
    Type: str
    Title: str
    StartDate: str
    EndDate: str
    Status: Optional[RequestStatusEnum] = None
    TimeUnit: Optional[TimeUnitEnum] = None
    EmployeeId: Optional[int] = None
    StartTime: Optional[str] = None
    EndTime: Optional[str] = None

    @field_validator("StartTime", "EndTime", mode="before")
    @classmethod
    def append_z_to_time(cls, v: Optional[str]) -> Optional[str]:
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
    balances: Dict[str, BalanceTotals]
