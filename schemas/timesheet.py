from datetime import datetime
from typing import List, Optional

from sqlmodel import SQLModel

from models.timesheet import TimeSheetPunchStatusEnum
from schemas.time_off import TimeOffRequestRead


class TimeSheetClockInCreate(SQLModel):
    CustomerId: int
    Note: Optional[str] = None
    UseLocation: bool = True
    Latitude: Optional[str] = None
    Longitude: Optional[str] = None
    GpsAccuracy: Optional[str] = None


class TimeSheetClockOutCreate(SQLModel):
    Note: Optional[str] = None
    UseLocation: bool = True
    Latitude: Optional[str] = None
    Longitude: Optional[str] = None
    GpsAccuracy: Optional[str] = None


class TimeSheetCustomerRead(SQLModel):
    CustomerId: int
    CustomerType: str
    CompanyName: Optional[str] = None
    FirstName: Optional[str] = None
    LastName: Optional[str] = None

    class Config:
        from_attributes = True


class TimeSheetPunchRead(SQLModel):
    PunchId: int
    EmployeeId: int
    CustomerId: int
    Customer: Optional[TimeSheetCustomerRead] = None
    ClockInAt: str
    ClockOutAt: Optional[str] = None
    WorkedMinutes: int
    Status: TimeSheetPunchStatusEnum
    Note: Optional[str] = None
    Timezone: Optional[str] = None
    IpAddress: Optional[str] = None
    Latitude: Optional[str] = None
    Longitude: Optional[str] = None
    GpsAccuracy: Optional[str] = None
    City: Optional[str] = None
    Region: Optional[str] = None
    Country: Optional[str] = None
    ApprovedBy: Optional[int] = None
    ApprovedAt: Optional[str] = None
    CreatedAt: str
    UpdatedAt: str

    class Config:
        from_attributes = True


class TimeSheetPunchUpdate(SQLModel):
    CustomerId: Optional[int] = None
    ClockInAt: Optional[datetime] = None
    ClockOutAt: Optional[datetime] = None
    Note: Optional[str] = None
    Status: Optional[TimeSheetPunchStatusEnum] = None


class TimeSheetSummaryItem(SQLModel):
    PeriodStart: str
    PeriodEnd: str
    RegularHours: float = 0
    OvertimeHours: float = 0
    VacationHours: float = 0
    HolidayHours: float = 0
    SickHours: float = 0
    TotalHours: float = 0
    Punches: Optional[List["TimeSheetPunchRead"]] = None
    TimeOffRequests: Optional[List[TimeOffRequestRead]] = None


class TimeSheetSummaryTotals(SQLModel):
    RegularHours: float = 0
    OvertimeHours: float = 0
    VacationHours: float = 0
    HolidayHours: float = 0
    SickHours: float = 0
    TotalHours: float = 0


class TimeSheetSummaryResponse(SQLModel):
    Items: List[TimeSheetSummaryItem]
    Totals: TimeSheetSummaryTotals
    Skip: int
    Limit: int
    Total: int


class TimeSheetLocationRead(SQLModel):
    IpAddress: Optional[str] = None
    Latitude: Optional[str] = None
    Longitude: Optional[str] = None
    GpsAccuracy: Optional[str] = None
    City: Optional[str] = None
    Region: Optional[str] = None
    Country: Optional[str] = None
    Timezone: Optional[str] = None
    CapturedAt: str


class TimeSheetOpenRead(SQLModel):
    Punch: Optional[TimeSheetPunchRead] = None
    ElapsedMinutes: int = 0
    ElapsedHours: float = 0


class TimeSheetSettingsRead(SQLModel):
    SettingId: int
    OvertimeDailyHours: str
    OvertimeWeeklyHours: Optional[str] = None
    RoundToMinutes: Optional[int] = None
    IsActive: bool
    CreatedAt: str
    UpdatedAt: str

    class Config:
        from_attributes = True


class TimeSheetSettingsUpdate(SQLModel):
    OvertimeDailyHours: Optional[float] = None
    OvertimeWeeklyHours: Optional[float] = None
    RoundToMinutes: Optional[int] = None
    IsActive: Optional[bool] = None
