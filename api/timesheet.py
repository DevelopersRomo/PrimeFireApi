import asyncio
import logging
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from io import BytesIO, StringIO
import csv
import json
from typing import Dict, List, Optional, Tuple

import httpx
from openpyxl import Workbook
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlmodel import Session, and_, select
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from api.dependencies import (
    get_current_employee,
    get_current_employee_with_permissions,
    require_authentication,
)
from bd.dependencies import get_db
from core.config import settings
from core.date_helpers import format_hours_minutes, calculate_regular_overtime
from models.customers import Customers
from models.employees import Employees
from models.timesheet import (
    TimeSheetLocationSnapshot,
    TimeSheetPunch,
    TimeSheetPunchStatusEnum,
    TimeSheetSettings,
)
from models.time_off import Holiday, RequestStatusEnum, TimeOffRequest, TimeUnitEnum
from services.notifications.notifications import notify_timesheet_hours
from schemas.timesheet import (
    TimeSheetClockInCreate,
    TimeSheetClockOutCreate,
    TimeSheetLocationRead,
    TimeSheetPunchRead,
    TimeSheetPunchUpdate,
    TimeSheetOpenRead,
    TimeSheetSummaryItem,
    TimeSheetSummaryResponse,
    TimeSheetSummaryTotals,
    TimeSheetNotificationCheckResponse,
)


router = APIRouter(prefix="/api/v1", tags=["timesheet"])
logger = logging.getLogger(__name__)

DEFAULT_DAILY_OVERTIME = Decimal("8.00")
DEFAULT_WEEKLY_OVERTIME = Decimal("40.00")
DEFAULT_WORKDAY_HOURS = Decimal("8.00")


def _now_str() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def _parse_dt(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")


def _calculate_minutes(start_str: str, end_str: str, daily_limit: int | None = None) -> int:
    """Return total worked minutes between start and end (integer).

    daily_limit is minutes; if provided the function still returns total minutes.
    """
    if daily_limit is None:
        # Fallback to default overtime limit if none provided
        daily_limit = int(DEFAULT_DAILY_OVERTIME * 60)
    start_dt = _parse_dt(start_str)
    end_dt = _parse_dt(end_str)
    minutes = int((end_dt - start_dt).total_seconds() / 60)
    return minutes


def _get_client_ip(request: Request) -> Optional[str]:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None


def _get_request_timezone(
    request: Request,
) -> tuple[timezone, str] | tuple[ZoneInfo, str]:
    tz_name = request.headers.get("x-timezone") or "UTC"
    try:
        return ZoneInfo(tz_name), tz_name
    except ZoneInfoNotFoundError:
        return timezone.utc, "UTC"


def _get_utc_range(
    start_date: date, end_date: date, tzinfo: timezone | ZoneInfo
) -> tuple[str, str]:
    local_start = datetime.combine(start_date, time.min).replace(tzinfo=tzinfo)
    local_end = datetime.combine(end_date, time.max).replace(tzinfo=tzinfo)
    utc_start = local_start.astimezone(timezone.utc)
    utc_end = local_end.astimezone(timezone.utc)
    return (
        utc_start.strftime("%Y-%m-%d %H:%M:%S"),
        utc_end.strftime("%Y-%m-%d %H:%M:%S"),
    )


def _to_local_date(clock_in_at: str, tzinfo: timezone | ZoneInfo) -> date:
    utc_dt = _parse_dt(clock_in_at).replace(tzinfo=timezone.utc)
    return utc_dt.astimezone(tzinfo).date()


def _fetch_ip_geolocation(ip_address: Optional[str]) -> Optional[dict]:
    api_key = settings.IPGEOLOCATION_API_KEY
    if not api_key:
        return None
    params = {"apiKey": api_key}
    if ip_address:
        params["ip"] = ip_address
    try:
        response = httpx.get(
            "https://api.ipgeolocation.io/ipgeo",
            params=params,
            timeout=10.0,
        )
        if response.status_code != 200:
            return None
        return response.json()
    except httpx.HTTPError:
        return None


def _extract_location(data: dict) -> Dict[str, Optional[str]]:
    if not data:
        return {}
    timezone_name = None
    if isinstance(data.get("time_zone"), dict):
        timezone_name = data["time_zone"].get("name")
    return {
        "IpAddress": data.get("ip"),
        "Latitude": data.get("latitude"),
        "Longitude": data.get("longitude"),
        "City": data.get("city"),
        "Region": data.get("state_prov") or data.get("region"),
        "Country": data.get("country_name") or data.get("country"),
        "Timezone": timezone_name,
        "LocationRaw": json.dumps(data),
    }


def _apply_location_to_punch(punch: TimeSheetPunch, location: Dict[str, Optional[str]]):
    if not location:
        return
    punch.IpAddress = location.get("IpAddress")
    punch.Latitude = location.get("Latitude")
    punch.Longitude = location.get("Longitude")
    punch.GpsAccuracy = location.get("GpsAccuracy")
    punch.City = location.get("City")
    punch.Region = location.get("Region")
    punch.Country = location.get("Country")
    if not punch.Timezone:
        punch.Timezone = location.get("Timezone")
    if location.get("LocationRaw") is not None:
        punch.LocationRaw = location.get("LocationRaw")


def _create_location_snapshot(
    db: Session,
    employee_id: int,
    customer_id: Optional[int],
    location: Dict[str, Optional[str]],
) -> Optional[TimeSheetLocationSnapshot]:
    if not location:
        return None
    snapshot = TimeSheetLocationSnapshot(
        EmployeeId=employee_id,
        CustomerId=customer_id,
        IpAddress=location.get("IpAddress"),
        Latitude=location.get("Latitude"),
        Longitude=location.get("Longitude"),
        GpsAccuracy=location.get("GpsAccuracy"),
        City=location.get("City"),
        Region=location.get("Region"),
        Country=location.get("Country"),
        Timezone=location.get("Timezone"),
        LocationRaw=location.get("LocationRaw")
        if location.get("LocationRaw")
        else None,
        CapturedAt=_now_str(),
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return snapshot


def _get_open_punch(db: Session, employee_id: int) -> Optional[TimeSheetPunch]:
    return db.exec(
        select(TimeSheetPunch).where(
            TimeSheetPunch.EmployeeId == employee_id,
            TimeSheetPunch.Status == TimeSheetPunchStatusEnum.OPEN.value,
            TimeSheetPunch.ClockOutAt.is_(None),
        )
    ).first()


def _get_settings(db: Session) -> TimeSheetSettings:
    settings_row = db.exec(
        select(TimeSheetSettings)
        .where(TimeSheetSettings.IsActive == True)  # noqa: E712
        .order_by(TimeSheetSettings.SettingId.desc())
    ).first()
    if not settings_row:
        now_str = _now_str()
        settings_row = TimeSheetSettings(
            OvertimeDailyHours="8.00",
            OvertimeWeeklyHours="40.00",
            MaxOvertimeDailyHours="8.00",
            RoundToMinutes=None,
            IsActive=True,
            CreatedAt=now_str,
            UpdatedAt=now_str,
        )
        db.add(settings_row)
        db.commit()
        db.refresh(settings_row)
    return settings_row


def _get_time_off_maps(
    db: Session, employee_id: int, start_date: date, end_date: date
) -> Tuple[Dict[date, Dict[str, Decimal]], Dict[date, List[TimeOffRequest]]]:
    totals: Dict[date, Dict[str, Decimal]] = {}
    daily_requests: Dict[date, List[TimeOffRequest]] = {}

    requests = db.exec(
        select(TimeOffRequest).where(
            TimeOffRequest.EmployeeId == employee_id,
            TimeOffRequest.Status.in_(
                [RequestStatusEnum.APPROVED.value, RequestStatusEnum.PENDING.value]
            ),
            TimeOffRequest.StartDate <= end_date.strftime("%Y-%m-%d"),
            TimeOffRequest.EndDate >= start_date.strftime("%Y-%m-%d"),
        )
    ).all()

    for request in requests:
        request_start = datetime.strptime(request.StartDate, "%Y-%m-%d").date()
        request_end = datetime.strptime(request.EndDate, "%Y-%m-%d").date()
        current = max(request_start, start_date)
        last = min(request_end, end_date)
        while current <= last:
            if current not in totals:
                totals[current] = {
                    "vacation": Decimal("0"),
                    "sick": Decimal("0"),
                    "holiday": Decimal("0"),
                }
            if current not in daily_requests:
                daily_requests[current] = []
            if request not in daily_requests[current]:
                daily_requests[current].append(request)

            if request.Status == RequestStatusEnum.APPROVED.value:
                bucket = "sick" if request.AbsenceType == "sick" else "vacation"
                if request.TimeUnit == TimeUnitEnum.HOURS.value and request.TotalHours:
                    if request_start == request_end:
                        hours = Decimal(request.TotalHours)
                    else:
                        span_days = (request_end - request_start).days + 1
                        hours = Decimal(request.TotalHours) / Decimal(span_days)
                elif request.TimeUnit == TimeUnitEnum.HALF_DAY.value:
                    hours = DEFAULT_WORKDAY_HOURS / Decimal("2")
                else:
                    hours = DEFAULT_WORKDAY_HOURS
                totals[current][bucket] += hours
            current += timedelta(days=1)

    holidays = db.exec(
        select(Holiday).where(
            Holiday.Date >= start_date.strftime("%Y-%m-%d"),
            Holiday.Date <= end_date.strftime("%Y-%m-%d"),
        )
    ).all()
    for holiday in holidays:
        holiday_date = datetime.strptime(holiday.Date, "%Y-%m-%d").date()
        if holiday_date not in totals:
            totals[holiday_date] = {
                "vacation": Decimal("0"),
                "sick": Decimal("0"),
                "holiday": Decimal("0"),
            }
        totals[holiday_date]["holiday"] += DEFAULT_WORKDAY_HOURS

    return totals, daily_requests


def _has_admin_actions(user_permissions: dict) -> bool:
    for perm in user_permissions.get("permissions", []):
        if perm.get("module_key") == "timesheet":
            return perm.get("permissions", {}).get("AdminActions", False)
    return False


def _resolve_range(
    view: str, start_date: Optional[date], end_date: Optional[date]
) -> Tuple[date, date]:
    today = date.today()
    if not start_date and not end_date:
        if view == "day":
            return today, today
        if view == "week":
            start = today - timedelta(days=today.weekday())
            return start, start + timedelta(days=6)
        start = today.replace(day=1)
        next_month = (start.replace(day=28) + timedelta(days=4)).replace(day=1)
        return start, next_month - timedelta(days=1)
    if start_date and not end_date:
        return start_date, start_date
    if end_date and not start_date:
        return end_date, end_date
    if end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="EndDate must be greater than or equal to StartDate",
        )
    return start_date, end_date


def _format_period_start_end(view: str, current_date: date) -> Tuple[str, str]:
    if view == "day":
        return current_date.strftime("%Y-%m-%d"), current_date.strftime("%Y-%m-%d")
    if view == "week":
        start = current_date - timedelta(days=current_date.weekday())
        end = start + timedelta(days=6)
        return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")
    start = current_date.replace(day=1)
    next_month = (start.replace(day=28) + timedelta(days=4)).replace(day=1)
    end = next_month - timedelta(days=1)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def _group_key(view: str, current_date: date) -> date:
    if view == "day":
        return current_date
    if view == "week":
        return current_date - timedelta(days=current_date.weekday())
    return current_date.replace(day=1)


def _build_summary_items(
    view: str,
    start_date: date,
    end_date: date,
    punches: List[TimeSheetPunch],
    time_off_map: Dict[date, Dict[str, Decimal]],
    time_off_requests_map: Dict[date, List[TimeOffRequest]],
    overtime_daily: Decimal,
    tzinfo: ZoneInfo,
) -> List[TimeSheetSummaryItem]:
    daily_minutes: Dict[date, int] = {}
    daily_punches: Dict[date, List[TimeSheetPunch]] = {}
    for punch in punches:
        if not punch.ClockOutAt:
            continue
        punch_date = _to_local_date(punch.ClockInAt, tzinfo)
        if punch_date < start_date or punch_date > end_date:
            continue
        daily_minutes[punch_date] = (
            daily_minutes.get(punch_date, 0) + punch.WorkedMinutes
        )
        daily_punches.setdefault(punch_date, []).append(punch)

    items_map: Dict[date, TimeSheetSummaryItem] = {}
    current = start_date
    while current <= end_date:
        group_key = _group_key(view, current)
        if group_key not in items_map:
            period_start, period_end = _format_period_start_end(view, current)
            items_map[group_key] = TimeSheetSummaryItem(
                PeriodStart=period_start,
                PeriodEnd=period_end,
            )
        minutes = daily_minutes.get(current, 0)
        hours = Decimal(minutes) / Decimal(60) if minutes else Decimal("0")
        overtime_hours = max(hours - overtime_daily, Decimal("0"))
        regular_hours = max(hours - overtime_hours, Decimal("0"))

        time_off = time_off_map.get(
            current,
            {"vacation": Decimal("0"), "holiday": Decimal("0"), "sick": Decimal("0")},
        )

        item = items_map[group_key]
        item.RegularHours += float(regular_hours)
        item.OvertimeHours += float(overtime_hours)
        item.VacationHours += float(time_off["vacation"])
        item.HolidayHours += float(time_off["holiday"])
        item.SickHours += float(time_off["sick"])
        item.TotalHours += float(
            hours + time_off["vacation"] + time_off["holiday"] + time_off["sick"]
        )
        if item.Punches is None:
            item.Punches = []
        item.Punches.extend(daily_punches.get(current, []))

        if item.TimeOffRequests is None:
            item.TimeOffRequests = []
        item.TimeOffRequests.extend(time_off_requests_map.get(current, []))

        current += timedelta(days=1)

    return [items_map[key] for key in sorted(items_map.keys())]


def _build_totals(items: List[TimeSheetSummaryItem]) -> TimeSheetSummaryTotals:
    totals = TimeSheetSummaryTotals()
    for item in items:
        totals.RegularHours += item.RegularHours
        totals.OvertimeHours += item.OvertimeHours
        totals.VacationHours += item.VacationHours
        totals.HolidayHours += item.HolidayHours
        totals.SickHours += item.SickHours
        totals.TotalHours += item.TotalHours
    return totals


@router.post(
    "/timesheet/clock-in",
    response_model=TimeSheetPunchRead,
    status_code=status.HTTP_201_CREATED,
)
def clock_in(
    payload: TimeSheetClockInCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
):
    customer = db.exec(
        select(Customers).where(Customers.CustomerId == payload.CustomerId)
    ).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
        )

    open_punch = _get_open_punch(db, current_employee.EmployeeId)
    if open_punch:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="There is already an open punch",
        )

    # Check weekly hours before allowing clock in
    tzinfo, tz_name = _get_request_timezone(request)

    # Get current week start and end
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    utc_start, utc_end = _get_utc_range(week_start, week_end, tzinfo)

    # Get punches for this week (excluding current open punch which doesn't exist yet)
    weekly_punches = db.exec(
        select(TimeSheetPunch).where(
            TimeSheetPunch.EmployeeId == current_employee.EmployeeId,
            TimeSheetPunch.ClockInAt >= utc_start,
            TimeSheetPunch.ClockInAt <= utc_end,
            TimeSheetPunch.Status == TimeSheetPunchStatusEnum.CLOSED.value,
        )
    ).all()

    # Calculate weekly hours
    weekly_minutes = sum(p.WorkedMinutes or 0 for p in weekly_punches)
    weekly_hours = float(Decimal(weekly_minutes) / Decimal(60)) if weekly_minutes else 0

    # Get settings
    settings_row = _get_settings(db)
    weekly_hours_limit = float(settings_row.OvertimeWeeklyHours) if settings_row.OvertimeWeeklyHours else 40.0
    daily_hours_limit = float(settings_row.OvertimeDailyHours) if settings_row.OvertimeDailyHours else 8.0

    # Check if user is already in overtime (weekly)
    is_already_in_overtime = weekly_hours >= weekly_hours_limit

    now_str = _now_str()
    punch = TimeSheetPunch(
        EmployeeId=current_employee.EmployeeId,
        CustomerId=payload.CustomerId,
        ClockInAt=now_str,
        Status=TimeSheetPunchStatusEnum.OPEN.value,
        Note=payload.Note,
        Timezone=tz_name,
        CreatedAt=now_str,
        UpdatedAt=now_str,
    )

    if payload.UseLocation:
        ip_address = _get_client_ip(request)
        location_data = _fetch_ip_geolocation(ip_address)
        location = _extract_location(location_data) if location_data else {}
        if payload.Latitude or payload.Longitude:
            location["Latitude"] = payload.Latitude
            location["Longitude"] = payload.Longitude
            location["GpsAccuracy"] = payload.GpsAccuracy
        _apply_location_to_punch(punch, location)
    elif payload.Latitude or payload.Longitude:
        punch.Latitude = payload.Latitude
        punch.Longitude = payload.Longitude
        punch.GpsAccuracy = payload.GpsAccuracy

    db.add(punch)
    db.commit()
    db.refresh(punch)

    # If user is already in overtime, send notification after clock in
    if is_already_in_overtime:
        employee = db.exec(
            select(Employees).where(Employees.EmployeeId == current_employee.EmployeeId)
        ).first()
        employee_email = employee.Email if employee else None
        employee_name = (
            f"{employee.FirstName or ''} {employee.LastName or ''}".strip()
            if employee
            else "Employee"
        )

        customer_name = customer.CompanyName or (
            f"{customer.FirstName or ''} {customer.LastName or ''}".strip()
        )

        app_url = getattr(settings, "APP_URL", None)
        if employee_email:
            try:
                asyncio.run(
                    notify_timesheet_hours(
                        employee_id=current_employee.EmployeeId,
                        employee_name=employee_name,
                        employee_email=employee_email,
                        notification_type="overtime",
                        hours_worked=weekly_hours,
                        customer_name=customer_name,
                        clock_in_time=now_str,
                        action_url=app_url,
                    )
                )
            except Exception:
                # Don't fail the request if email fails, but keep traceability.
                logger.exception(
                    "Failed to send overtime notification after clock-in",
                    extra={"employee_id": current_employee.EmployeeId},
                )

    return punch


@router.post("/timesheet/clock-out", response_model=TimeSheetPunchRead)
def clock_out(
    payload: TimeSheetClockOutCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
):
    open_punch = _get_open_punch(db, current_employee.EmployeeId)
    if not open_punch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Open punch not found"
        )

    now_str = _now_str()
    _, tz_name = _get_request_timezone(request)
    open_punch.ClockOutAt = now_str
    open_punch.WorkedMinutes = _calculate_minutes(open_punch.ClockInAt, now_str)
    open_punch.Status = TimeSheetPunchStatusEnum.CLOSED.value
    if payload.Note:
        open_punch.Note = payload.Note
    open_punch.Timezone = tz_name

    if payload.UseLocation:
        ip_address = _get_client_ip(request)
        location_data = _fetch_ip_geolocation(ip_address)
        location = _extract_location(location_data) if location_data else {}
        if payload.Latitude or payload.Longitude:
            location["Latitude"] = payload.Latitude
            location["Longitude"] = payload.Longitude
            location["GpsAccuracy"] = payload.GpsAccuracy
        _apply_location_to_punch(open_punch, location)
    elif payload.Latitude or payload.Longitude:
        open_punch.Latitude = payload.Latitude
        open_punch.Longitude = payload.Longitude
        open_punch.GpsAccuracy = payload.GpsAccuracy

    open_punch.UpdatedAt = now_str
    db.add(open_punch)
    db.commit()
    db.refresh(open_punch)
    return open_punch


@router.get("/timesheet", response_model=TimeSheetSummaryResponse)
def list_timesheet(
    request: Request,
    view: str = Query("day", pattern="^(day|week|month)$"),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    customer_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
):
    tzinfo, _ = _get_request_timezone(request)
    start_date, end_date = _resolve_range(view, start_date, end_date)
    utc_start, utc_end = _get_utc_range(start_date, end_date, tzinfo)

    filters = [
        TimeSheetPunch.EmployeeId == current_employee.EmployeeId,
        TimeSheetPunch.ClockInAt >= utc_start,
        TimeSheetPunch.ClockInAt <= utc_end,
    ]
    if customer_id:
        filters.append(TimeSheetPunch.CustomerId == customer_id)

    punches = db.exec(select(TimeSheetPunch).where(and_(*filters))).all()

    settings_row = _get_settings(db)
    overtime_daily = (
        Decimal(settings_row.OvertimeDailyHours)
        if settings_row.OvertimeDailyHours
        else DEFAULT_DAILY_OVERTIME
    )

    time_off_map, time_off_requests_map = _get_time_off_maps(
        db, current_employee.EmployeeId, start_date, end_date
    )
    items = _build_summary_items(
        view=view,
        start_date=start_date,
        end_date=end_date,
        punches=punches,
        time_off_map=time_off_map,
        time_off_requests_map=time_off_requests_map,
        overtime_daily=overtime_daily,
        tzinfo=tzinfo,
    )
    totals = _build_totals(items)

    total_count = len(items)
    items = items[skip : skip + limit]
    return TimeSheetSummaryResponse(
        Items=items,
        Totals=totals,
        Skip=skip,
        Limit=limit,
        Total=total_count,
    )


@router.get("/timesheet/open", response_model=TimeSheetOpenRead)
def get_open_punch(
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
):
    punch = _get_open_punch(db, current_employee.EmployeeId)
    if not punch:
        return TimeSheetOpenRead(Punch=None, ElapsedMinutes=0, ElapsedHours=0)
    now_str = _now_str()
    elapsed_minutes = _calculate_minutes(punch.ClockInAt, now_str)
    elapsed_hours = (
        float(Decimal(elapsed_minutes) / Decimal(60)) if elapsed_minutes else 0
    )
    return TimeSheetOpenRead(
        Punch=punch,
        ElapsedMinutes=elapsed_minutes,
        ElapsedHours=elapsed_hours,
    )


@router.get("/timesheet/export")
def export_timesheet(
    request: Request,
    view: str = Query("day", pattern="^(day|week|month)$"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    customer_id: Optional[int] = Query(None),
    employee_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
    user_permissions: dict = Depends(get_current_employee_with_permissions),
):
    is_admin = _has_admin_actions(user_permissions)
    target_employee_id = (
        employee_id if (employee_id and is_admin) else current_employee.EmployeeId
    )

    tzinfo, _ = _get_request_timezone(request)
    start_date, end_date = _resolve_range(view, start_date, end_date)
    utc_start, utc_end = _get_utc_range(start_date, end_date, tzinfo)
    filters = [
        TimeSheetPunch.EmployeeId == target_employee_id,
        TimeSheetPunch.ClockInAt >= utc_start,
        TimeSheetPunch.ClockInAt <= utc_end,
    ]
    if customer_id:
        filters.append(TimeSheetPunch.CustomerId == customer_id)
    punches = db.exec(select(TimeSheetPunch).where(and_(*filters))).all()
    customer_ids = {punch.CustomerId for punch in punches}
    customer_map = {}
    if customer_ids:
        customers = db.exec(
            select(Customers).where(Customers.CustomerId.in_(list(customer_ids)))
        ).all()
        customer_map = {customer.CustomerId: customer for customer in customers}

    # Get settings for overtime calculation
    settings = db.exec(select(TimeSheetSettings).where(TimeSheetSettings.IsActive == True)).first()
    overtime_daily_minutes = 480  # default 8 hours
    if settings and settings.OvertimeDailyHours:
        overtime_daily_minutes = int(float(settings.OvertimeDailyHours) * 60)

    # Get holidays for the date range
    holidays = db.exec(select(Holiday).where(
        Holiday.Date >= start_date.strftime("%Y-%m-%d"),
        Holiday.Date <= end_date.strftime("%Y-%m-%d")
    )).all()
    holiday_dates = {h.Date for h in holidays}

    # Get time off requests for the employee in date range
    time_off_requests = db.exec(select(TimeOffRequest).where(
        TimeOffRequest.EmployeeId == target_employee_id,
        TimeOffRequest.Status == "approved",
        TimeOffRequest.StartDate >= start_date.strftime("%Y-%m-%d"),
        TimeOffRequest.EndDate <= end_date.strftime("%Y-%m-%d")
    )).all()

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "timesheet"
    sheet.append(
        [
            "day",
            "clocking",
            "clokout",
            "worked_hours_total",
            "regular",
            "overtime",
            "vacation",
            "holiday",
            "sick",
            "customer_name",
            "note",
        ]
    )
    for punch in punches:
        local_day = _to_local_date(punch.ClockInAt, tzinfo).strftime("%Y-%m-%d")

        # Calculate regular and overtime
        regular_minutes, overtime_minutes = calculate_regular_overtime(
            punch.WorkedMinutes or 0, overtime_daily_minutes
        )

        # Check if it's a holiday
        is_holiday = local_day in holiday_dates

        # Check if there's a time off request for this day
        is_vacation = False
        is_sick = False
        for req in time_off_requests:
            if req.StartDate <= local_day <= req.EndDate:
                if req.AbsenceType == "vacation":
                    is_vacation = True
                elif req.AbsenceType == "sick":
                    is_sick = True

        customer = customer_map.get(punch.CustomerId)
        customer_name = (
            customer.CompanyName
            or " ".join(filter(None, [customer.FirstName, customer.LastName]))
            if customer
            else None
        )
        sheet.append(
            [
                local_day,
                punch.ClockInAt,
                punch.ClockOutAt,
                format_hours_minutes(punch.WorkedMinutes or 0),
                format_hours_minutes(regular_minutes),
                format_hours_minutes(overtime_minutes),
                "true" if is_vacation else "false",
                "true" if is_holiday else "false",
                "true" if is_sick else "false",
                customer_name,
                punch.Note,
            ]
        )
    output = BytesIO()
    workbook.save(output)
    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=timesheet.xlsx"},
    )


@router.get("/timesheet/location", response_model=TimeSheetLocationRead)
def get_current_location(
    request: Request,
    customer_id: Optional[int] = Query(None),
    latitude: Optional[str] = Query(None),
    longitude: Optional[str] = Query(None),
    gps_accuracy: Optional[str] = Query(None),
    timezone_header: Optional[str] = Query(None, alias="timezone"),
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
):
    if customer_id:
        customer = db.exec(
            select(Customers).where(Customers.CustomerId == customer_id)
        ).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
            )

    location: Dict[str, Optional[str]] = {}
    ip_address = _get_client_ip(request)
    if latitude or longitude:
        location = {
            "IpAddress": ip_address,
            "Latitude": latitude,
            "Longitude": longitude,
            "GpsAccuracy": gps_accuracy,
            "Timezone": timezone_header,
        }
    else:
        location_data = _fetch_ip_geolocation(ip_address)
        location = _extract_location(location_data) if location_data else {}

    snapshot = _create_location_snapshot(
        db=db,
        employee_id=current_employee.EmployeeId,
        customer_id=customer_id,
        location=location,
    )

    captured_at = snapshot.CapturedAt if snapshot else _now_str()
    return TimeSheetLocationRead(
        IpAddress=location.get("IpAddress"),
        Latitude=location.get("Latitude"),
        Longitude=location.get("Longitude"),
        GpsAccuracy=location.get("GpsAccuracy"),
        City=location.get("City"),
        Region=location.get("Region"),
        Country=location.get("Country"),
        Timezone=location.get("Timezone"),
        CapturedAt=captured_at,
    )


@router.get("/timesheet/admin", response_model=List[TimeSheetPunchRead])
def list_punches_admin(
    employee_id: Optional[List[int]] = Query(None),
    customer_id: Optional[List[int]] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user_permissions: dict = Depends(get_current_employee_with_permissions),
    db: Session = Depends(get_db),
):
    if not _has_admin_actions(user_permissions):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied"
        )

    filters = []
    if employee_id:
        filters.append(TimeSheetPunch.EmployeeId.in_(employee_id))
    if customer_id:
        filters.append(TimeSheetPunch.CustomerId.in_(customer_id))
    if status_filter:
        filters.append(TimeSheetPunch.Status == status_filter)
    if start_date:
        filters.append(
            TimeSheetPunch.ClockInAt >= f"{start_date.strftime('%Y-%m-%d')} 00:00:00"
        )
    if end_date:
        filters.append(
            TimeSheetPunch.ClockInAt <= f"{end_date.strftime('%Y-%m-%d')} 23:59:59"
        )

    query = select(TimeSheetPunch)
    if filters:
        query = query.where(and_(*filters))
    query = query.order_by(TimeSheetPunch.ClockInAt.desc()).offset(skip).limit(limit)
    return db.exec(query).all()


@router.get("/timesheet/admin/export")
def export_punches_admin(
    request: Request,
    employee_id: Optional[List[int]] = Query(None),
    customer_id: Optional[List[int]] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    user_permissions: dict = Depends(get_current_employee_with_permissions),
    db: Session = Depends(get_db),
):
    if not _has_admin_actions(user_permissions):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied"
        )

    tzinfo, _ = _get_request_timezone(request)
    filters = []
    if employee_id:
        filters.append(TimeSheetPunch.EmployeeId.in_(employee_id))
    if customer_id:
        filters.append(TimeSheetPunch.CustomerId.in_(customer_id))
    if status_filter:
        filters.append(TimeSheetPunch.Status == status_filter)
    if start_date:
        filters.append(
            TimeSheetPunch.ClockInAt >= f"{start_date.strftime('%Y-%m-%d')} 00:00:00"
        )
    if end_date:
        filters.append(
            TimeSheetPunch.ClockInAt <= f"{end_date.strftime('%Y-%m-%d')} 23:59:59"
        )

    query = select(TimeSheetPunch)
    if filters:
        query = query.where(and_(*filters))
    query = query.order_by(TimeSheetPunch.ClockInAt.desc())
    punches = db.exec(query).all()

    customer_ids = {punch.CustomerId for punch in punches}
    employee_ids = {punch.EmployeeId for punch in punches}
    customer_map = {}
    employee_map = {}
    if customer_ids:
        customers = db.exec(
            select(Customers).where(Customers.CustomerId.in_(list(customer_ids)))
        ).all()
        customer_map = {customer.CustomerId: customer for customer in customers}
    if employee_ids:
        employees = db.exec(
            select(Employees).where(Employees.EmployeeId.in_(list(employee_ids)))
        ).all()
        employee_map = {employee.EmployeeId: employee for employee in employees}

    # Get settings for overtime calculation
    settings = db.exec(select(TimeSheetSettings).where(TimeSheetSettings.IsActive == True)).first()
    overtime_daily_minutes = 480  # default 8 hours
    if settings and settings.OvertimeDailyHours:
        overtime_daily_minutes = int(float(settings.OvertimeDailyHours) * 60)

    # Get date range for holidays and time off
    query_start = start_date.strftime("%Y-%m-%d") if start_date else "1900-01-01"
    query_end = end_date.strftime("%Y-%m-%d") if end_date else "2100-12-31"

    # Get holidays for the date range
    holidays = db.exec(select(Holiday).where(
        Holiday.Date >= query_start,
        Holiday.Date <= query_end
    )).all()
    holiday_dates = {h.Date for h in holidays}

    # Get time off requests for all employees in date range
    time_off_filter = [TimeOffRequest.Status == "approved"]
    if employee_ids:
        time_off_filter.append(TimeOffRequest.EmployeeId.in_(list(employee_ids)))
    time_off_requests = db.exec(select(TimeOffRequest).where(*time_off_filter)).all()

    # Group time off requests by employee and date
    time_off_by_employee = {}
    for req in time_off_requests:
        if req.EmployeeId not in time_off_by_employee:
            time_off_by_employee[req.EmployeeId] = {}
        for d in range((datetime.strptime(req.EndDate, "%Y-%m-%d") - datetime.strptime(req.StartDate, "%Y-%m-%d")).days + 1):
            current_date = (datetime.strptime(req.StartDate, "%Y-%m-%d") + timedelta(days=d)).strftime("%Y-%m-%d")
            time_off_by_employee[req.EmployeeId][current_date] = req.AbsenceType

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "timesheet_admin"
    sheet.append(
        [
            "employee_name",
            "day",
            "clocking",
            "clokout",
            "worked_hours_total",
            "regular",
            "overtime",
            "vacation",
            "holiday",
            "sick",
            "customer_name",
            "note",
        ]
    )
    for punch in punches:
        local_day = _to_local_date(punch.ClockInAt, tzinfo).strftime("%Y-%m-%d")

        # Calculate regular and overtime
        regular_minutes, overtime_minutes = calculate_regular_overtime(
            punch.WorkedMinutes or 0, overtime_daily_minutes
        )

        # Check if it's a holiday
        is_holiday = local_day in holiday_dates

        # Check if there's a time off request for this employee and day
        employee_time_offs = time_off_by_employee.get(punch.EmployeeId, {})
        day_off_type = employee_time_offs.get(local_day)
        is_vacation = day_off_type == "vacation"
        is_sick = day_off_type == "sick"

        customer = customer_map.get(punch.CustomerId)
        employee = employee_map.get(punch.EmployeeId)
        customer_name = (
            customer.CompanyName
            or " ".join(filter(None, [customer.FirstName, customer.LastName]))
            if customer
            else None
        )
        employee_name = (
            " ".join(filter(None, [employee.FirstName, employee.LastName]))
            if employee
            else None
        )
        sheet.append(
            [
                employee_name,
                local_day,
                punch.ClockInAt,
                punch.ClockOutAt,
                format_hours_minutes(punch.WorkedMinutes or 0),
                format_hours_minutes(regular_minutes),
                format_hours_minutes(overtime_minutes),
                "true" if is_vacation else "false",
                "true" if is_holiday else "false",
                "true" if is_sick else "false",
                customer_name,
                punch.Note,
            ]
        )
    output = BytesIO()
    workbook.save(output)
    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=timesheet_admin.xlsx"},
    )


@router.patch("/timesheet/{punch_id}", response_model=TimeSheetPunchRead)
def update_punch(
    punch_id: int,
    payload: TimeSheetPunchUpdate,
    user_permissions: dict = Depends(get_current_employee_with_permissions),
    db: Session = Depends(get_db),
):
    if not _has_admin_actions(user_permissions):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied"
        )

    punch = db.exec(
        select(TimeSheetPunch).where(TimeSheetPunch.PunchId == punch_id)
    ).first()
    if not punch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Punch not found"
        )

    if payload.CustomerId is not None:
        customer = db.exec(
            select(Customers).where(Customers.CustomerId == payload.CustomerId)
        ).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
            )
        punch.CustomerId = payload.CustomerId

    if payload.ClockInAt is not None:
        punch.ClockInAt = payload.ClockInAt.strftime("%Y-%m-%d %H:%M:%S")
    if payload.ClockOutAt is not None:
        punch.ClockOutAt = payload.ClockOutAt.strftime("%Y-%m-%d %H:%M:%S")
    if payload.Note is not None:
        punch.Note = payload.Note
    if payload.Status is not None:
        punch.Status = payload.Status.value

    if punch.ClockOutAt:
        ts_settings = _get_settings(db)
        daily_limit = (
            int(float(ts_settings.OvertimeDailyHours) * 60)
            if ts_settings and ts_settings.OvertimeDailyHours
            else 480
        )
        punch.WorkedMinutes = _calculate_minutes(
            punch.ClockInAt, punch.ClockOutAt, daily_limit
        )

    punch.UpdatedAt = _now_str()
    db.add(punch)
    db.commit()
    db.refresh(punch)
    return punch


@router.post("/timesheet/{punch_id}/approve", response_model=TimeSheetPunchRead)
def approve_punch(
    punch_id: int,
    user_permissions: dict = Depends(get_current_employee_with_permissions),
    db: Session = Depends(get_db),
):
    if not _has_admin_actions(user_permissions):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied"
        )

    punch = db.exec(
        select(TimeSheetPunch).where(TimeSheetPunch.PunchId == punch_id)
    ).first()
    if not punch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Punch not found"
        )

    punch.Status = TimeSheetPunchStatusEnum.APPROVED.value
    punch.ApprovedBy = user_permissions["employee"]["EmployeeId"]
    punch.ApprovedAt = _now_str()
    punch.UpdatedAt = punch.ApprovedAt
    db.add(punch)
    db.commit()
    db.refresh(punch)
    return punch


@router.post("/timesheet/{punch_id}/reject", response_model=TimeSheetPunchRead)
def reject_punch(
    punch_id: int,
    user_permissions: dict = Depends(get_current_employee_with_permissions),
    db: Session = Depends(get_db),
):
    if not _has_admin_actions(user_permissions):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied"
        )

    punch = db.exec(
        select(TimeSheetPunch).where(TimeSheetPunch.PunchId == punch_id)
    ).first()
    if not punch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Punch not found"
        )

    punch.Status = TimeSheetPunchStatusEnum.REJECTED.value
    punch.ApprovedBy = user_permissions["employee"]["EmployeeId"]
    punch.ApprovedAt = _now_str()
    punch.UpdatedAt = punch.ApprovedAt
    db.add(punch)
    db.commit()
    db.refresh(punch)
    return punch


@router.get("/timesheet/notifications/check", response_model=TimeSheetNotificationCheckResponse)
def check_notifications(
    request: Request,
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
):
    """Check if user should receive notification for hours worked."""
    # Get open punch
    open_punch = _get_open_punch(db, current_employee.EmployeeId)

    if not open_punch:
        return TimeSheetNotificationCheckResponse(
            has_open_punch=False,
            elapsed_minutes=0,
            elapsed_hours=0,
            regular_hours_limit=8.0,
            overtime_hours_limit=8.0,
            max_overtime_hours_limit=8.0,
            total_hours_limit=16.0,
            weekly_hours_limit=40.0,
            should_notify_regular=False,
            should_notify_overtime=False,
            should_auto_clock_out=False,
        )

    # Get settings
    settings_row = _get_settings(db)
    regular_hours = float(settings_row.OvertimeDailyHours) if settings_row.OvertimeDailyHours else 8.0
    max_overtime_hours = float(settings_row.MaxOvertimeDailyHours) if settings_row.MaxOvertimeDailyHours else 8.0
    total_hours_limit = regular_hours + max_overtime_hours  # Hours at which auto clock out occurs
    weekly_hours_limit = float(settings_row.OvertimeWeeklyHours) if settings_row.OvertimeWeeklyHours else 40.0

    # Calculate elapsed time for current punch
    now_str = _now_str()
    elapsed_minutes = _calculate_minutes(open_punch.ClockInAt, now_str)
    elapsed_hours = float(Decimal(elapsed_minutes) / Decimal(60)) if elapsed_minutes else 0

    # Calculate weekly hours (including current punch)
    tzinfo, _ = _get_request_timezone(request)
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    utc_start, utc_end = _get_utc_range(week_start, week_end, tzinfo)

    # Get punches for this week (including current open punch)
    weekly_punches = db.exec(
        select(TimeSheetPunch).where(
            TimeSheetPunch.EmployeeId == current_employee.EmployeeId,
            TimeSheetPunch.ClockInAt >= utc_start,
            TimeSheetPunch.ClockInAt <= utc_end,
        )
    ).all()

    weekly_minutes = sum(p.WorkedMinutes or 0 for p in weekly_punches if p.WorkedMinutes)
    # Add current punch elapsed minutes
    weekly_minutes += elapsed_minutes
    weekly_hours = float(Decimal(weekly_minutes) / Decimal(60))

    # Get customer name
    customer_name = None
    if open_punch.CustomerId:
        customer = db.exec(
            select(Customers).where(Customers.CustomerId == open_punch.CustomerId)
        ).first()
        if customer:
            customer_name = customer.CompanyName or (
                f"{customer.FirstName or ''} {customer.LastName or ''}".strip()
            )

    # Determine if should notify
    # Notify regular when elapsed >= regular_hours
    # Determine if should notify - check both daily and weekly limits
    # Notify regular when elapsed hours >= daily regular hours
    # Notify regular when elapsed >= regular_hours (e.g., 8 hours)
    should_notify_regular = elapsed_hours >= regular_hours

    # Notify overtime when elapsed >= regular_hours but < total_hours_limit
    # (user is in overtime zone but not at auto clock out limit yet)
    should_notify_overtime = elapsed_hours >= regular_hours and elapsed_hours < total_hours_limit

    # Auto clock out when:
    # 1. Daily total exceeded (elapsed >= total_hours_limit) OR
    # 2. Weekly hours exceeded (weekly_hours >= weekly_hours_limit)
    should_auto_clock_out = elapsed_hours >= total_hours_limit or weekly_hours >= weekly_hours_limit

    return TimeSheetNotificationCheckResponse(
        has_open_punch=True,
        elapsed_minutes=elapsed_minutes,
        elapsed_hours=elapsed_hours,
        regular_hours_limit=regular_hours,
        overtime_hours_limit=regular_hours,
        max_overtime_hours_limit=max_overtime_hours,
        total_hours_limit=total_hours_limit,
        weekly_hours_limit=weekly_hours_limit,
        should_notify_regular=should_notify_regular,
        should_notify_overtime=should_notify_overtime,
        should_auto_clock_out=should_auto_clock_out,
        customer_name=customer_name,
        clock_in_time=open_punch.ClockInAt,
    )


@router.post("/timesheet/clock-out-auto", response_model=TimeSheetPunchRead)
def clock_out_auto(
    request: Request,
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
):
    """Automatic clock out when overtime limit is reached."""
    open_punch = _get_open_punch(db, current_employee.EmployeeId)
    if not open_punch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Open punch not found"
        )

    now_str = _now_str()
    _, tz_name = _get_request_timezone(request)
    open_punch.ClockOutAt = now_str
    open_punch.WorkedMinutes = _calculate_minutes(open_punch.ClockInAt, now_str)
    open_punch.Status = TimeSheetPunchStatusEnum.CLOSED.value
    open_punch.Timezone = tz_name
    open_punch.UpdatedAt = now_str

    # Get customer name
    customer_name = None
    if open_punch.CustomerId:
        customer = db.exec(
            select(Customers).where(Customers.CustomerId == open_punch.CustomerId)
        ).first()
        if customer:
            customer_name = customer.CompanyName or (
                f"{customer.FirstName or ''} {customer.LastName or ''}".strip()
            )

    # Get employee's email
    employee = db.exec(
        select(Employees).where(Employees.EmployeeId == current_employee.EmployeeId)
    ).first()
    employee_email = employee.Email if employee else None
    employee_name = (
        f"{employee.FirstName or ''} {employee.LastName or ''}".strip()
        if employee
        else "Employee"
    )

    elapsed_hours = (
        float(Decimal(open_punch.WorkedMinutes) / Decimal(60))
        if open_punch.WorkedMinutes
        else 0
    )

    # Send notification email
    app_url = getattr(settings, "APP_URL", None)
    if employee_email:
        try:
            asyncio.run(
                notify_timesheet_hours(
                    employee_id=current_employee.EmployeeId,
                    employee_name=employee_name,
                    employee_email=employee_email,
                    notification_type="overtime",
                    hours_worked=elapsed_hours,
                    customer_name=customer_name,
                    clock_in_time=open_punch.ClockInAt,
                    action_url=app_url,
                )
            )
        except Exception:
            # Don't fail the request if email fails, but keep traceability.
            logger.exception(
                "Failed to send overtime notification after auto clock-out",
                extra={"employee_id": current_employee.EmployeeId},
            )

    db.add(open_punch)
    db.commit()
    db.refresh(open_punch)
    return open_punch


@router.post("/timesheet/notify-hours")
def notify_hours(
    notification_type: str = "regular_hours",
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
):
    """Send notification email for hours worked."""
    # Get open punch
    open_punch = _get_open_punch(db, current_employee.EmployeeId)

    if not open_punch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Open punch not found"
        )

    # Calculate elapsed time
    now_str = _now_str()
    elapsed_minutes = _calculate_minutes(open_punch.ClockInAt, now_str)
    elapsed_hours = float(Decimal(elapsed_minutes) / Decimal(60)) if elapsed_minutes else 0

    # Get customer name
    customer_name = None
    if open_punch.CustomerId:
        customer = db.exec(
            select(Customers).where(Customers.CustomerId == open_punch.CustomerId)
        ).first()
        if customer:
            customer_name = customer.CompanyName or (
                f"{customer.FirstName or ''} {customer.LastName or ''}".strip()
            )

    # Get employee's email
    employee = db.exec(
        select(Employees).where(Employees.EmployeeId == current_employee.EmployeeId)
    ).first()
    employee_email = employee.Email if employee else None
    employee_name = (
        f"{employee.FirstName or ''} {employee.LastName or ''}".strip()
        if employee
        else "Employee"
    )

    # Send notification email
    app_url = getattr(settings, "APP_URL", None)
    success = False
    if employee_email:
        try:
            result = asyncio.run(
                notify_timesheet_hours(
                    employee_id=current_employee.EmployeeId,
                    employee_name=employee_name,
                    employee_email=employee_email,
                    notification_type=notification_type,
                    hours_worked=elapsed_hours,
                    customer_name=customer_name,
                    clock_in_time=open_punch.ClockInAt,
                    action_url=app_url,
                )
            )
            success = result.success if result else False
        except Exception:
            logger.exception(
                "Failed to send timesheet hours notification",
                extra={"employee_id": current_employee.EmployeeId},
            )

    return {"success": success}
