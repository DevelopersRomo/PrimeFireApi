from datetime import datetime

from sqlmodel import SQLModel

from models.timesheet import TimeSheetPunchStatusEnum
from schemas.time_off import TimeOffRequestRead


class TimeSheetClockInCreate(SQLModel):
    customer_id: int
    note: str | None = None
    use_location: bool = True
    latitude: str | None = None
    longitude: str | None = None
    gps_accuracy: str | None = None


class TimeSheetClockOutCreate(SQLModel):
    note: str | None = None
    use_location: bool = True
    latitude: str | None = None
    longitude: str | None = None
    gps_accuracy: str | None = None


class TimeSheetCustomerRead(SQLModel):
    customer_id: int
    customer_type: str
    company_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None

    class Config:
        from_attributes = True


class TimeSheetPunchRead(SQLModel):
    punch_id: int
    employee_id: int
    employee_name: str | None = None
    customer_id: int | None = None
    customer: TimeSheetCustomerRead | None = None
    clock_in_at: str
    clock_out_at: str | None = None
    worked_minutes: int
    status: TimeSheetPunchStatusEnum
    note: str | None = None
    timezone: str | None = None
    ip_address: str | None = None
    latitude: str | None = None
    longitude: str | None = None
    gps_accuracy: str | None = None
    city: str | None = None
    region: str | None = None
    country: str | None = None
    approved_by: int | None = None
    approved_at: str | None = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class TimeSheetPunchUpdate(SQLModel):
    customer_id: int | None = None
    clock_in_at: datetime | None = None
    clock_out_at: datetime | None = None
    note: str | None = None
    status: TimeSheetPunchStatusEnum | None = None


class TimeSheetSummaryItem(SQLModel):
    period_start: str
    period_end: str
    regular_hours: float = 0
    overtime_hours: float = 0
    vacation_hours: float = 0
    holiday_hours: float = 0
    sick_hours: float = 0
    total_hours: float = 0
    punches: list["TimeSheetPunchRead"] | None = None
    time_off_requests: list[TimeOffRequestRead] | None = None


class TimeSheetSummaryTotals(SQLModel):
    regular_hours: float = 0
    overtime_hours: float = 0
    vacation_hours: float = 0
    holiday_hours: float = 0
    sick_hours: float = 0
    total_hours: float = 0


class TimeSheetSummaryResponse(SQLModel):
    items: list[TimeSheetSummaryItem]
    totals: TimeSheetSummaryTotals
    skip: int
    limit: int
    total: int


class TimeSheetLocationRead(SQLModel):
    ip_address: str | None = None
    latitude: str | None = None
    longitude: str | None = None
    gps_accuracy: str | None = None
    city: str | None = None
    region: str | None = None
    country: str | None = None
    timezone: str | None = None
    captured_at: str


class TimeSheetOpenRead(SQLModel):
    punch: TimeSheetPunchRead | None = None
    elapsed_minutes: int = 0
    elapsed_hours: float = 0


class TimeSheetSettingsRead(SQLModel):
    setting_id: int
    overtime_daily_hours: str
    overtime_weekly_hours: str | None = None
    max_overtime_daily_hours: str | None = None
    round_to_minutes: int | None = None
    is_active: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class TimeSheetSettingsUpdate(SQLModel):
    overtime_daily_hours: float | None = None
    overtime_weekly_hours: float | None = None
    max_overtime_daily_hours: float | None = None
    round_to_minutes: int | None = None
    is_active: bool | None = None


class TimeSheetNotificationCheckResponse(SQLModel):
    has_open_punch: bool = False
    elapsed_minutes: int = 0
    elapsed_hours: float = 0
    regular_hours_limit: float = 8.0
    overtime_hours_limit: float = 8.0
    max_overtime_hours_limit: float = 8.0
    total_hours_limit: float = 16.0
    weekly_hours_limit: float = 40.0
    should_notify_regular: bool = False
    should_notify_overtime: bool = False
    should_auto_clock_out: bool = False
    customer_name: str | None = None
    clock_in_time: str | None = None
