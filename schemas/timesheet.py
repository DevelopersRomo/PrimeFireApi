from datetime import datetime

from sqlmodel import SQLModel

from models.timesheet import TimeSheetPunchStatusEnum
from schemas.time_off import TimeOffRequestRead


class TimeSheetClockInCreate(SQLModel):
    CustomerId: int
    Note: str | None = None
    UseLocation: bool = True
    Latitude: str | None = None
    Longitude: str | None = None
    GpsAccuracy: str | None = None


class TimeSheetClockOutCreate(SQLModel):
    Note: str | None = None
    UseLocation: bool = True
    Latitude: str | None = None
    Longitude: str | None = None
    GpsAccuracy: str | None = None


class TimeSheetCustomerRead(SQLModel):
    CustomerId: int
    CustomerType: str
    CompanyName: str | None = None
    FirstName: str | None = None
    LastName: str | None = None

    class Config:
        from_attributes = True


class TimeSheetPunchRead(SQLModel):
    PunchId: int
    EmployeeId: int
    CustomerId: int
    Customer: TimeSheetCustomerRead | None = None
    ClockInAt: str
    ClockOutAt: str | None = None
    WorkedMinutes: int
    Status: TimeSheetPunchStatusEnum
    Note: str | None = None
    Timezone: str | None = None
    IpAddress: str | None = None
    Latitude: str | None = None
    Longitude: str | None = None
    GpsAccuracy: str | None = None
    City: str | None = None
    Region: str | None = None
    Country: str | None = None
    ApprovedBy: int | None = None
    ApprovedAt: str | None = None
    CreatedAt: str
    UpdatedAt: str

    class Config:
        from_attributes = True


class TimeSheetPunchUpdate(SQLModel):
    CustomerId: int | None = None
    ClockInAt: datetime | None = None
    ClockOutAt: datetime | None = None
    Note: str | None = None
    Status: TimeSheetPunchStatusEnum | None = None


class TimeSheetSummaryItem(SQLModel):
    PeriodStart: str
    PeriodEnd: str
    RegularHours: float = 0
    OvertimeHours: float = 0
    VacationHours: float = 0
    HolidayHours: float = 0
    SickHours: float = 0
    TotalHours: float = 0
    Punches: list["TimeSheetPunchRead"] | None = None
    TimeOffRequests: list[TimeOffRequestRead] | None = None


class TimeSheetSummaryTotals(SQLModel):
    RegularHours: float = 0
    OvertimeHours: float = 0
    VacationHours: float = 0
    HolidayHours: float = 0
    SickHours: float = 0
    TotalHours: float = 0


class TimeSheetSummaryResponse(SQLModel):
    Items: list[TimeSheetSummaryItem]
    Totals: TimeSheetSummaryTotals
    Skip: int
    Limit: int
    Total: int


class TimeSheetLocationRead(SQLModel):
    IpAddress: str | None = None
    Latitude: str | None = None
    Longitude: str | None = None
    GpsAccuracy: str | None = None
    City: str | None = None
    Region: str | None = None
    Country: str | None = None
    Timezone: str | None = None
    CapturedAt: str


class TimeSheetOpenRead(SQLModel):
    Punch: TimeSheetPunchRead | None = None
    ElapsedMinutes: int = 0
    ElapsedHours: float = 0


class TimeSheetSettingsRead(SQLModel):
    SettingId: int
    OvertimeDailyHours: str
    OvertimeWeeklyHours: str | None = None
    MaxOvertimeDailyHours: str | None = None
    RoundToMinutes: int | None = None
    IsActive: bool
    CreatedAt: str
    UpdatedAt: str

    class Config:
        from_attributes = True


class TimeSheetSettingsUpdate(SQLModel):
    OvertimeDailyHours: float | None = None
    OvertimeWeeklyHours: float | None = None
    MaxOvertimeDailyHours: float | None = None
    RoundToMinutes: int | None = None
    IsActive: bool | None = None


class TimeSheetNotificationCheckResponse(SQLModel):
    """Response for timesheet notification check."""

    has_open_punch: bool = False
    elapsed_minutes: int = 0
    elapsed_hours: float = 0
    regular_hours_limit: float = 8.0
    overtime_hours_limit: float = 8.0
    max_overtime_hours_limit: float = 8.0  # Max overtime before auto clock out
    total_hours_limit: float = 16.0  # regular + max overtime
    weekly_hours_limit: float = 40.0
    should_notify_regular: bool = False
    should_notify_overtime: bool = False
    should_auto_clock_out: bool = False
    customer_name: str | None = None
    clock_in_time: str | None = None
