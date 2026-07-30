import asyncio
import json
import logging
from datetime import UTC, date, datetime, time, timedelta, timezone
from decimal import Decimal
from io import BytesIO
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from openpyxl import Workbook
from sqlalchemy import func
from sqlmodel import Session, and_, select

from api.dependencies import (
    get_current_employee,
    get_current_employee_with_permissions,
)
from bd.dependencies import get_db
from core.config import settings
from helpers.date_helpers import calculate_regular_overtime, format_hours_minutes
from models.customers import Customers
from models.employees import Employees
from models.time_off import Holiday, RequestStatusEnum, TimeOffRequest, TimeUnitEnum
from models.timesheet import (
    TimeSheetLocationSnapshot,
    TimeSheetPunch,
    TimeSheetPunchStatusEnum,
    TimeSheetSettings,
)
from schemas.pagination import PaginatedResponse
from schemas.timesheet import (
    TimeSheetClockInCreate,
    TimeSheetClockOutCreate,
    TimeSheetCustomerRead,
    TimeSheetLocationRead,
    TimeSheetNotificationCheckResponse,
    TimeSheetOpenRead,
    TimeSheetPunchRead,
    TimeSheetPunchUpdate,
    TimeSheetSummaryItem,
    TimeSheetSummaryResponse,
    TimeSheetSummaryTotals,
)
from services.notifications.notifications import notify_timesheet_hours

router = APIRouter(prefix="/api/v1", tags=["timesheet"])
logger = logging.getLogger(__name__)

DEFAULT_DAILY_OVERTIME = Decimal("8.00")
DEFAULT_WEEKLY_OVERTIME = Decimal("40.00")
DEFAULT_WORKDAY_HOURS = Decimal("8.00")


def _now_str() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")  # noqa: DTZ003


def _parse_dt(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")  # noqa: DTZ007


def _calculate_minutes(start_str: str, end_str: str, daily_limit: int | None = None) -> int:
    """Return total worked minutes between start and end (integer).

    daily_limit is minutes; if provided the function still returns total minutes.
    """
    if daily_limit is None:
        # Fallback to default overtime limit if none provided
        daily_limit = int(DEFAULT_DAILY_OVERTIME * 60)
    start_dt = _parse_dt(start_str)
    end_dt = _parse_dt(end_str)
    return int((end_dt - start_dt).total_seconds() / 60)


def _get_client_ip(request: Request) -> str | None:
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
        return UTC, "UTC"


def _get_utc_range(start_date: date, end_date: date, tzinfo: timezone | ZoneInfo) -> tuple[str, str]:
    local_start = datetime.combine(start_date, time.min).replace(tzinfo=tzinfo)
    local_end = datetime.combine(end_date, time.max).replace(tzinfo=tzinfo)
    utc_start = local_start.astimezone(UTC)
    utc_end = local_end.astimezone(UTC)
    return (
        utc_start.strftime("%Y-%m-%d %H:%M:%S"),
        utc_end.strftime("%Y-%m-%d %H:%M:%S"),
    )


def _to_local_date(clock_in_at: str, tzinfo: timezone | ZoneInfo) -> date:
    utc_dt = _parse_dt(clock_in_at).replace(tzinfo=UTC)
    return utc_dt.astimezone(tzinfo).date()


def _to_utc_string(dt: datetime, tzinfo: timezone | ZoneInfo) -> str:
    """Convert an aware or naive datetime to a UTC string for storage."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tzinfo)
    return dt.astimezone(UTC).strftime("%Y-%m-%d %H:%M:%S")


def _fetch_ip_geolocation(ip_address: str | None) -> dict | None:
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


def _extract_location(data: dict) -> dict[str, str | None]:
    if not data:
        return {}
    timezone_name = None
    if isinstance(data.get("time_zone"), dict):
        timezone_name = data["time_zone"].get("name")
    return {
        "ip_address": data.get("ip"),
        "latitude": data.get("latitude"),
        "longitude": data.get("longitude"),
        "city": data.get("city"),
        "region": data.get("state_prov") or data.get("region"),
        "country": data.get("country_name") or data.get("country"),
        "timezone": timezone_name,
        "location_raw": json.dumps(data),
    }


def _apply_location_to_punch(punch: TimeSheetPunch, location: dict[str, str | None]) -> None:
    if not location:
        return
    punch.ip_address = location.get("ip_address")
    punch.latitude = location.get("latitude")
    punch.longitude = location.get("longitude")
    punch.gps_accuracy = location.get("gps_accuracy")
    punch.city = location.get("city")
    punch.region = location.get("region")
    punch.country = location.get("country")
    if not punch.timezone:
        punch.timezone = location.get("timezone")
    if location.get("location_raw") is not None:
        punch.location_raw = location.get("location_raw")


def _create_location_snapshot(
    db: Session,
    employee_id: int,
    customer_id: int | None,
    location: dict[str, str | None],
) -> TimeSheetLocationSnapshot | None:
    if not location:
        return None
    snapshot = TimeSheetLocationSnapshot(
        employee_id=employee_id,
        customer_id=customer_id,
        ip_address=location.get("ip_address"),
        latitude=location.get("latitude"),
        longitude=location.get("longitude"),
        gps_accuracy=location.get("gps_accuracy"),
        city=location.get("city"),
        region=location.get("region"),
        country=location.get("country"),
        timezone=location.get("timezone"),
        location_raw=location.get("location_raw") or None,
        captured_at=_now_str(),
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return snapshot


def _get_open_punch(db: Session, employee_id: int) -> TimeSheetPunch | None:
    return db.exec(
        select(TimeSheetPunch).where(
            TimeSheetPunch.employee_id == employee_id,
            TimeSheetPunch.status == TimeSheetPunchStatusEnum.OPEN.value,
            TimeSheetPunch.clock_out_at.is_(None),
        )
    ).first()


def _get_settings(db: Session) -> TimeSheetSettings:
    settings_row = db.exec(
        select(TimeSheetSettings)
        .where(TimeSheetSettings.is_active == True)  # noqa: E712
        .order_by(TimeSheetSettings.setting_id.desc())
    ).first()
    if not settings_row:
        now_str = _now_str()
        settings_row = TimeSheetSettings(
            overtime_daily_hours="8.00",
            overtime_weekly_hours="40.00",
            max_overtime_daily_hours="8.00",
            round_to_minutes=None,
            is_active=True,
            created_at=now_str,
            updated_at=now_str,
        )
        db.add(settings_row)
        db.commit()
        db.refresh(settings_row)
    return settings_row


def _get_time_off_maps(
    db: Session, employee_id: int, start_date: date, end_date: date
) -> tuple[dict[date, dict[str, Decimal]], dict[date, list[TimeOffRequest]]]:
    totals: dict[date, dict[str, Decimal]] = {}
    daily_requests: dict[date, list[TimeOffRequest]] = {}

    requests = db.exec(
        select(TimeOffRequest).where(
            TimeOffRequest.employee_id == employee_id,
            TimeOffRequest.status.in_([RequestStatusEnum.APPROVED.value, RequestStatusEnum.PENDING.value]),
            TimeOffRequest.start_date <= end_date.strftime("%Y-%m-%d"),
            TimeOffRequest.end_date >= start_date.strftime("%Y-%m-%d"),
        )
    ).all()

    for request in requests:
        request_start = datetime.strptime(request.start_date, "%Y-%m-%d").date()  # noqa: DTZ007
        request_end = datetime.strptime(request.end_date, "%Y-%m-%d").date()  # noqa: DTZ007
        current = max(request_start, start_date)
        last = min(request_end, end_date)
        while current <= last:
            if current not in totals:
                totals[current] = {
                    "vacation": Decimal(0),
                    "sick": Decimal(0),
                    "holiday": Decimal(0),
                }
            if current not in daily_requests:
                daily_requests[current] = []
            if request not in daily_requests[current]:
                daily_requests[current].append(request)

            if request.status == RequestStatusEnum.APPROVED.value:
                bucket = "sick" if request.absence_type == "sick" else "vacation"
                if request.time_unit == TimeUnitEnum.HOURS.value and request.total_hours:
                    if request_start == request_end:
                        hours = Decimal(request.total_hours)
                    else:
                        span_days = (request_end - request_start).days + 1
                        hours = Decimal(request.total_hours) / Decimal(span_days)
                elif request.time_unit == TimeUnitEnum.HALF_DAY.value:
                    hours = DEFAULT_WORKDAY_HOURS / Decimal(2)
                else:
                    hours = DEFAULT_WORKDAY_HOURS
                totals[current][bucket] += hours
            current += timedelta(days=1)

    holidays = db.exec(
        select(Holiday).where(
            Holiday.date >= start_date.strftime("%Y-%m-%d"),
            Holiday.date <= end_date.strftime("%Y-%m-%d"),
        )
    ).all()
    for holiday in holidays:
        holiday_date = datetime.strptime(holiday.date, "%Y-%m-%d").date()  # noqa: DTZ007
        if holiday_date not in totals:
            totals[holiday_date] = {
                "vacation": Decimal(0),
                "sick": Decimal(0),
                "holiday": Decimal(0),
            }
        totals[holiday_date]["holiday"] += DEFAULT_WORKDAY_HOURS

    return totals, daily_requests


def _has_admin_actions(user_permissions: dict) -> bool:
    for perm in user_permissions.get("permissions", []):
        if perm.get("module_key") == "timesheet":
            return perm.get("permissions", {}).get("admin_actions", False)
    return False


def _resolve_range(view: str, start_date: date | None, end_date: date | None) -> tuple[date | None, date | None]:
    today = date.today()  # noqa: DTZ011
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


def _format_period_start_end(view: str, current_date: date) -> tuple[str, str]:
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
    punches: list[TimeSheetPunch],
    time_off_map: dict[date, dict[str, Decimal]],
    time_off_requests_map: dict[date, list[TimeOffRequest]],
    overtime_daily: Decimal,
    tzinfo: ZoneInfo,
) -> list[TimeSheetSummaryItem]:
    daily_minutes: dict[date, int] = {}
    daily_punches: dict[date, list[TimeSheetPunch]] = {}
    for punch in punches:
        if not punch.clock_out_at:
            continue
        punch_date = _to_local_date(punch.clock_in_at, tzinfo)
        if punch_date < start_date or punch_date > end_date:
            continue
        daily_minutes[punch_date] = daily_minutes.get(punch_date, 0) + punch.worked_minutes
        daily_punches.setdefault(punch_date, []).append(punch)

    items_map: dict[date, TimeSheetSummaryItem] = {}
    current = start_date
    while current <= end_date:
        group_key = _group_key(view, current)
        if group_key not in items_map:
            period_start, period_end = _format_period_start_end(view, current)
            items_map[group_key] = TimeSheetSummaryItem(
                period_start=period_start,
                period_end=period_end,
            )
        minutes = daily_minutes.get(current, 0)
        hours = Decimal(minutes) / Decimal(60) if minutes else Decimal(0)
        overtime_hours = max(hours - overtime_daily, Decimal(0))
        regular_hours = max(hours - overtime_hours, Decimal(0))

        time_off = time_off_map.get(
            current,
            {"vacation": Decimal(0), "holiday": Decimal(0), "sick": Decimal(0)},
        )

        item = items_map[group_key]
        item.regular_hours += float(regular_hours)
        item.overtime_hours += float(overtime_hours)
        item.vacation_hours += float(time_off["vacation"])
        item.holiday_hours += float(time_off["holiday"])
        item.sick_hours += float(time_off["sick"])
        item.total_hours += float(hours + time_off["vacation"] + time_off["holiday"] + time_off["sick"])
        if item.punches is None:
            item.punches = []
        item.punches.extend(daily_punches.get(current, []))

        if item.time_off_requests is None:
            item.time_off_requests = []
        item.time_off_requests.extend(time_off_requests_map.get(current, []))

        current += timedelta(days=1)

    return [items_map[key] for key in sorted(items_map.keys())]


def _build_totals(items: list[TimeSheetSummaryItem]) -> TimeSheetSummaryTotals:
    totals = TimeSheetSummaryTotals()
    for item in items:
        totals.regular_hours += item.regular_hours
        totals.overtime_hours += item.overtime_hours
        totals.vacation_hours += item.vacation_hours
        totals.holiday_hours += item.holiday_hours
        totals.sick_hours += item.sick_hours
        totals.total_hours += item.total_hours
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
    customer = db.exec(select(Customers).where(Customers.customer_id == payload.customer_id)).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    open_punch = _get_open_punch(db, current_employee.employee_id)
    if open_punch:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="There is already an open punch",
        )

    # Check weekly hours before allowing clock in
    tzinfo, tz_name = _get_request_timezone(request)

    # Get current week start and end
    today = date.today()  # noqa: DTZ011
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    utc_start, utc_end = _get_utc_range(week_start, week_end, tzinfo)

    # Get punches for this week (excluding current open punch which doesn't exist yet)
    weekly_punches = db.exec(
        select(TimeSheetPunch).where(
            TimeSheetPunch.employee_id == current_employee.employee_id,
            TimeSheetPunch.clock_in_at >= utc_start,
            TimeSheetPunch.clock_in_at <= utc_end,
            TimeSheetPunch.status == TimeSheetPunchStatusEnum.CLOSED.value,
        )
    ).all()

    # Calculate weekly hours
    weekly_minutes = sum(p.worked_minutes or 0 for p in weekly_punches)
    weekly_hours = float(Decimal(weekly_minutes) / Decimal(60)) if weekly_minutes else 0

    # Get settings
    settings_row = _get_settings(db)
    weekly_hours_limit = float(settings_row.overtime_weekly_hours) if settings_row.overtime_weekly_hours else 40.0
    float(settings_row.overtime_daily_hours) if settings_row.overtime_daily_hours else 8.0

    # Check if user is already in overtime (weekly)
    is_already_in_overtime = weekly_hours >= weekly_hours_limit

    now_str = _now_str()
    punch = TimeSheetPunch(
        employee_id=current_employee.employee_id,
        customer_id=payload.customer_id,
        clock_in_at=now_str,
        status=TimeSheetPunchStatusEnum.OPEN.value,
        note=payload.note,
        timezone=tz_name,
        created_at=now_str,
        updated_at=now_str,
    )

    if payload.use_location:
        ip_address = _get_client_ip(request)
        location_data = _fetch_ip_geolocation(ip_address)
        location = _extract_location(location_data) if location_data else {}
        if payload.latitude or payload.longitude:
            location["Latitude"] = payload.latitude
            location["Longitude"] = payload.longitude
            location["GpsAccuracy"] = payload.gps_accuracy
        _apply_location_to_punch(punch, location)
    elif payload.latitude or payload.longitude:
        punch.latitude = payload.latitude
        punch.longitude = payload.longitude
        punch.gps_accuracy = payload.gps_accuracy

    db.add(punch)
    db.commit()
    db.refresh(punch)

    # If user is already in overtime, send notification after clock in
    if is_already_in_overtime:
        employee = db.exec(select(Employees).where(Employees.employee_id == current_employee.employee_id)).first()
        employee_email = employee.email if employee else None
        employee_name = f"{employee.first_name or ''} {employee.last_name or ''}".strip() if employee else "Employee"

        customer_name = customer.company_name or (f"{customer.first_name or ''} {customer.last_name or ''}".strip())

        app_url = getattr(settings, "APP_URL", None)
        if employee_email:
            try:
                asyncio.run(
                    notify_timesheet_hours(
                        employee_id=current_employee.employee_id,
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
                    extra={"employee_id": current_employee.employee_id},
                )

    return punch


@router.post("/timesheet/clock-out", response_model=TimeSheetPunchRead)
def clock_out(
    payload: TimeSheetClockOutCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
):
    open_punch = _get_open_punch(db, current_employee.employee_id)
    if not open_punch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Open punch not found")

    now_str = _now_str()
    _, tz_name = _get_request_timezone(request)
    open_punch.clock_out_at = now_str
    open_punch.worked_minutes = _calculate_minutes(open_punch.clock_in_at, now_str)
    open_punch.status = TimeSheetPunchStatusEnum.CLOSED.value
    if payload.note:
        open_punch.note = payload.note
    open_punch.timezone = tz_name

    if payload.use_location:
        ip_address = _get_client_ip(request)
        location_data = _fetch_ip_geolocation(ip_address)
        location = _extract_location(location_data) if location_data else {}
        if payload.latitude or payload.longitude:
            location["latitude"] = payload.latitude
            location["longitude"] = payload.longitude
            location["gps_accuracy"] = payload.gps_accuracy
        _apply_location_to_punch(open_punch, location)
    elif payload.latitude or payload.longitude:
        open_punch.latitude = payload.latitude
        open_punch.longitude = payload.longitude
        open_punch.gps_accuracy = payload.gps_accuracy

    open_punch.updated_at = now_str
    db.add(open_punch)
    db.commit()
    db.refresh(open_punch)
    return open_punch


@router.get("/timesheet", response_model=TimeSheetSummaryResponse)
def list_timesheet(
    request: Request,
    view: str = Query("day", pattern="^(day|week|month)$"),
    start_date: date | None = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: date | None = Query(None, description="End date (YYYY-MM-DD)"),
    customer_id: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
):
    tzinfo, _ = _get_request_timezone(request)
    start_date, end_date = _resolve_range(view, start_date, end_date)
    utc_start, utc_end = _get_utc_range(start_date, end_date, tzinfo)

    filters = [
        TimeSheetPunch.employee_id == current_employee.employee_id,
        TimeSheetPunch.clock_in_at >= utc_start,
        TimeSheetPunch.clock_in_at <= utc_end,
    ]
    if customer_id:
        filters.append(TimeSheetPunch.customer_id == customer_id)

    punches = db.exec(select(TimeSheetPunch).where(and_(*filters))).all()

    settings_row = _get_settings(db)
    overtime_daily = (
        Decimal(settings_row.overtime_daily_hours) if settings_row.overtime_daily_hours else DEFAULT_DAILY_OVERTIME
    )

    time_off_map, time_off_requests_map = _get_time_off_maps(db, current_employee.employee_id, start_date, end_date)
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
        items=items,
        totals=totals,
        skip=skip,
        limit=limit,
        total=total_count,
    )


@router.get("/timesheet/open", response_model=TimeSheetOpenRead)
def get_open_punch(
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
):
    punch = _get_open_punch(db, current_employee.employee_id)
    if not punch:
        return TimeSheetOpenRead(punch=None, elapsed_minutes=0, elapsed_hours=0)
    now_str = _now_str()
    elapsed_minutes = _calculate_minutes(punch.clock_in_at, now_str)
    elapsed_hours = float(Decimal(elapsed_minutes) / Decimal(60)) if elapsed_minutes else 0
    return TimeSheetOpenRead(
        punch=punch,
        elapsed_minutes=elapsed_minutes,
        elapsed_hours=elapsed_hours,
    )


@router.get("/timesheet/export")
def export_timesheet(
    request: Request,
    view: str = Query("day", pattern="^(day|week|month)$"),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    customer_id: int | None = Query(None),
    employee_id: int | None = Query(None),
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
    user_permissions: dict = Depends(get_current_employee_with_permissions),
):
    is_admin = _has_admin_actions(user_permissions)
    target_employee_id = employee_id if (employee_id and is_admin) else current_employee.employee_id

    tzinfo, _ = _get_request_timezone(request)
    start_date, end_date = _resolve_range(view, start_date, end_date)
    utc_start, utc_end = _get_utc_range(start_date, end_date, tzinfo)
    filters = [
        TimeSheetPunch.employee_id == target_employee_id,
        TimeSheetPunch.clock_in_at >= utc_start,
        TimeSheetPunch.clock_in_at <= utc_end,
    ]
    if customer_id:
        filters.append(TimeSheetPunch.customer_id == customer_id)
    punches = db.exec(select(TimeSheetPunch).where(and_(*filters))).all()
    customer_ids = {punch.customer_id for punch in punches}
    customer_map = {}
    if customer_ids:
        customers = db.exec(select(Customers).where(Customers.customer_id.in_(list(customer_ids)))).all()
        customer_map = {customer.customer_id: customer for customer in customers}

    # Get settings for overtime calculation
    settings = db.exec(select(TimeSheetSettings).where(TimeSheetSettings.is_active)).first()
    overtime_daily_minutes = 480  # default 8 hours
    if settings and settings.overtime_daily_hours:
        overtime_daily_minutes = int(float(settings.overtime_daily_hours) * 60)

    # Get holidays for the date range
    holidays = db.exec(
        select(Holiday).where(
            Holiday.date >= start_date.strftime("%Y-%m-%d"), Holiday.date <= end_date.strftime("%Y-%m-%d")
        )
    ).all()
    holiday_dates = {h.date for h in holidays}

    # Get time off requests for the employee in date range
    time_off_requests = db.exec(
        select(TimeOffRequest).where(
            TimeOffRequest.employee_id == target_employee_id,
            TimeOffRequest.status == "approved",
            TimeOffRequest.start_date >= start_date.strftime("%Y-%m-%d"),
            TimeOffRequest.end_date <= end_date.strftime("%Y-%m-%d"),
        )
    ).all()

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
        local_day = _to_local_date(punch.clock_in_at, tzinfo).strftime("%Y-%m-%d")

        # Calculate regular and overtime
        regular_minutes, overtime_minutes = calculate_regular_overtime(
            punch.worked_minutes or 0, overtime_daily_minutes
        )

        # Check if it's a holiday
        is_holiday = local_day in holiday_dates

        # Check if there's a time off request for this day
        is_vacation = False
        is_sick = False
        for req in time_off_requests:
            if req.start_date <= local_day <= req.end_date:
                if req.absence_type == "vacation":
                    is_vacation = True
                elif req.absence_type == "sick":
                    is_sick = True

        customer = customer_map.get(punch.customer_id)
        customer_name = (
            customer.company_name or " ".join(filter(None, [customer.first_name, customer.last_name]))
            if customer
            else None
        )
        sheet.append(
            [
                local_day,
                punch.clock_in_at,
                punch.clock_out_at,
                format_hours_minutes(punch.worked_minutes or 0),
                format_hours_minutes(regular_minutes),
                format_hours_minutes(overtime_minutes),
                "true" if is_vacation else "false",
                "true" if is_holiday else "false",
                "true" if is_sick else "false",
                customer_name,
                punch.note,
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
    customer_id: int | None = Query(None),
    latitude: str | None = Query(None),
    longitude: str | None = Query(None),
    gps_accuracy: str | None = Query(None),
    timezone_header: str | None = Query(None, alias="timezone"),
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
):
    if customer_id:
        customer = db.exec(select(Customers).where(Customers.customer_id == customer_id)).first()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    location: dict[str, str | None] = {}
    ip_address = _get_client_ip(request)
    if latitude or longitude:
        location = {
            "ip_address": ip_address,
            "latitude": latitude,
            "longitude": longitude,
            "gps_accuracy": gps_accuracy,
            "timezone": timezone_header,
        }
    else:
        location_data = _fetch_ip_geolocation(ip_address)
        location = _extract_location(location_data) if location_data else {}

    snapshot = _create_location_snapshot(
        db=db,
        employee_id=current_employee.employee_id,
        customer_id=customer_id,
        location=location,
    )

    captured_at = snapshot.captured_at if snapshot else _now_str()
    return TimeSheetLocationRead(
        ip_address=location.get("ip_address"),
        latitude=location.get("latitude"),
        longitude=location.get("longitude"),
        gps_accuracy=location.get("gps_accuracy"),
        city=location.get("city"),
        region=location.get("region"),
        country=location.get("country"),
        timezone=location.get("timezone"),
        captured_at=captured_at,
    )


@router.get("/timesheet/admin", response_model=list[TimeSheetPunchRead] | PaginatedResponse[TimeSheetPunchRead])
def list_punches_admin(
    employee_id: list[int] | None = Query(None),
    customer_id: list[int] | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    with_meta: bool = Query(False),
    user_permissions: dict = Depends(get_current_employee_with_permissions),
    db: Session = Depends(get_db),
):
    if not _has_admin_actions(user_permissions):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    filters = []
    if employee_id:
        filters.append(TimeSheetPunch.employee_id.in_(employee_id))
    if customer_id:
        filters.append(TimeSheetPunch.customer_id.in_(customer_id))
    if status_filter:
        filters.append(TimeSheetPunch.status == status_filter)
    if start_date:
        filters.append(TimeSheetPunch.clock_in_at >= f"{start_date.strftime('%Y-%m-%d')} 00:00:00")
    if end_date:
        filters.append(TimeSheetPunch.clock_in_at <= f"{end_date.strftime('%Y-%m-%d')} 23:59:59")

    query = select(TimeSheetPunch)
    if filters:
        query = query.where(and_(*filters))
    query = query.order_by(TimeSheetPunch.clock_in_at.desc(), TimeSheetPunch.punch_id.desc()).offset(skip).limit(limit)
    punches = db.exec(query).all()

    # Fetch employee and customer names
    employee_ids = {p.employee_id for p in punches}
    customer_ids = {p.customer_id for p in punches if p.customer_id}

    employee_map = {}
    if employee_ids:
        employees = db.exec(select(Employees).where(Employees.employee_id.in_(list(employee_ids)))).all()
        employee_map = {emp.employee_id: emp for emp in employees}

    customer_map = {}
    if customer_ids:
        customers = db.exec(select(Customers).where(Customers.customer_id.in_(list(customer_ids)))).all()
        customer_map = {cust.customer_id: cust for cust in customers}

    # Build response with names
    result: list[TimeSheetPunchRead] = []
    for punch in punches:
        emp = employee_map.get(punch.employee_id)
        employee_name = " ".join(filter(None, [emp.first_name, emp.last_name])) if emp else None

        cust = customer_map.get(punch.customer_id) if punch.customer_id else None
        customer_data = None
        if cust:
            customer_data = TimeSheetCustomerRead(
                customer_id=cust.customer_id,
                customer_type=cust.customer_type,
                company_name=cust.company_name,
                first_name=cust.first_name,
                last_name=cust.last_name,
            )

        result.append(
            TimeSheetPunchRead(
                punch_id=punch.punch_id,
                employee_id=punch.employee_id,
                employee_name=employee_name,
                customer_id=punch.customer_id,
                customer=customer_data,
                clock_in_at=punch.clock_in_at,
                clock_out_at=punch.clock_out_at,
                worked_minutes=punch.worked_minutes,
                status=punch.status,
                note=punch.note,
                timezone=punch.timezone,
                ip_address=punch.ip_address,
                latitude=punch.latitude,
                longitude=punch.longitude,
                gps_accuracy=punch.gps_accuracy,
                city=punch.city,
                region=punch.region,
                country=punch.country,
                approved_by=punch.approved_by,
                approved_at=punch.approved_at,
                created_at=punch.created_at,
                updated_at=punch.updated_at,
            )
        )

    if not with_meta:
        return result

    count_query = select(func.count()).select_from(TimeSheetPunch)
    if filters:
        count_query = count_query.where(and_(*filters))
    total = db.exec(count_query).one()

    return PaginatedResponse[TimeSheetPunchRead](
        items=result,
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + len(result) < total,
    )


@router.get("/timesheet/admin/export")
def export_punches_admin(
    request: Request,
    employee_id: list[int] | None = Query(None),
    customer_id: list[int] | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    user_permissions: dict = Depends(get_current_employee_with_permissions),
    db: Session = Depends(get_db),
):
    if not _has_admin_actions(user_permissions):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    tzinfo, _ = _get_request_timezone(request)
    filters = []
    if employee_id:
        filters.append(TimeSheetPunch.employee_id.in_(employee_id))
    if customer_id:
        filters.append(TimeSheetPunch.customer_id.in_(customer_id))
    if status_filter:
        filters.append(TimeSheetPunch.status == status_filter)
    if start_date:
        filters.append(TimeSheetPunch.clock_in_at >= f"{start_date.strftime('%Y-%m-%d')} 00:00:00")
    if end_date:
        filters.append(TimeSheetPunch.clock_in_at <= f"{end_date.strftime('%Y-%m-%d')} 23:59:59")

    query = select(TimeSheetPunch)
    if filters:
        query = query.where(and_(*filters))
    query = query.order_by(TimeSheetPunch.clock_in_at.desc())
    punches = db.exec(query).all()

    customer_ids = {punch.customer_id for punch in punches}
    employee_ids = {punch.employee_id for punch in punches}
    customer_map = {}
    employee_map = {}
    if customer_ids:
        customers = db.exec(select(Customers).where(Customers.customer_id.in_(list(customer_ids)))).all()
        customer_map = {customer.customer_id: customer for customer in customers}
    if employee_ids:
        employees = db.exec(select(Employees).where(Employees.employee_id.in_(list(employee_ids)))).all()
        employee_map = {employee.employee_id: employee for employee in employees}

    # Get settings for overtime calculation
    settings = db.exec(select(TimeSheetSettings).where(TimeSheetSettings.is_active)).first()
    overtime_daily_minutes = 480  # default 8 hours
    if settings and settings.overtime_daily_hours:
        overtime_daily_minutes = int(float(settings.overtime_daily_hours) * 60)

    # Get date range for holidays and time off
    query_start = start_date.strftime("%Y-%m-%d") if start_date else "1900-01-01"
    query_end = end_date.strftime("%Y-%m-%d") if end_date else "2100-12-31"

    # Get holidays for the date range
    holidays = db.exec(select(Holiday).where(Holiday.date >= query_start, Holiday.date <= query_end)).all()
    holiday_dates = {h.date for h in holidays}

    # Get time off requests for all employees in date range
    time_off_filter = [TimeOffRequest.status == "approved"]
    if employee_ids:
        time_off_filter.append(TimeOffRequest.employee_id.in_(list(employee_ids)))
    time_off_requests = db.exec(select(TimeOffRequest).where(*time_off_filter)).all()

    # Group time off requests by employee and date
    time_off_by_employee = {}
    for req in time_off_requests:
        if req.employee_id not in time_off_by_employee:
            time_off_by_employee[req.employee_id] = {}
        for d in range(
            (datetime.strptime(req.end_date, "%Y-%m-%d") - datetime.strptime(req.start_date, "%Y-%m-%d")).days + 1  # noqa: DTZ007
        ):
            current_date = (datetime.strptime(req.start_date, "%Y-%m-%d") + timedelta(days=d)).strftime("%Y-%m-%d")  # noqa: DTZ007
            time_off_by_employee[req.employee_id][current_date] = req.absence_type

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
        local_day = _to_local_date(punch.clock_in_at, tzinfo).strftime("%Y-%m-%d")

        # Calculate regular and overtime
        regular_minutes, overtime_minutes = calculate_regular_overtime(
            punch.worked_minutes or 0, overtime_daily_minutes
        )

        # Check if it's a holiday
        is_holiday = local_day in holiday_dates

        # Check if there's a time off request for this employee and day
        employee_time_offs = time_off_by_employee.get(punch.employee_id, {})
        day_off_type = employee_time_offs.get(local_day)
        is_vacation = day_off_type == "vacation"
        is_sick = day_off_type == "sick"

        customer = customer_map.get(punch.customer_id)
        employee = employee_map.get(punch.employee_id)
        customer_name = (
            customer.company_name or " ".join(filter(None, [customer.first_name, customer.last_name]))
            if customer
            else None
        )
        employee_name = " ".join(filter(None, [employee.first_name, employee.last_name])) if employee else None
        sheet.append(
            [
                employee_name,
                local_day,
                punch.clock_in_at,
                punch.clock_out_at,
                format_hours_minutes(punch.worked_minutes or 0),
                format_hours_minutes(regular_minutes),
                format_hours_minutes(overtime_minutes),
                "true" if is_vacation else "false",
                "true" if is_holiday else "false",
                "true" if is_sick else "false",
                customer_name,
                punch.note,
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
    request: Request,
    user_permissions: dict = Depends(get_current_employee_with_permissions),
    db: Session = Depends(get_db),
):
    if not _has_admin_actions(user_permissions):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    punch = db.exec(select(TimeSheetPunch).where(TimeSheetPunch.punch_id == punch_id)).first()
    if not punch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Punch not found")

    tzinfo, _ = _get_request_timezone(request)

    if payload.customer_id is not None:
        customer = db.exec(select(Customers).where(Customers.customer_id == payload.customer_id)).first()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        punch.customer_id = payload.customer_id

    if payload.clock_in_at is not None:
        punch.clock_in_at = _to_utc_string(payload.clock_in_at, tzinfo)
    if payload.clock_out_at is not None:
        punch.clock_out_at = _to_utc_string(payload.clock_out_at, tzinfo)
    if payload.note is not None:
        punch.note = payload.note
    if payload.status is not None:
        punch.status = payload.status.value

    if punch.clock_out_at:
        ts_settings = _get_settings(db)
        daily_limit = (
            int(float(ts_settings.overtime_daily_hours) * 60)
            if ts_settings and ts_settings.overtime_daily_hours
            else 480
        )
        punch.worked_minutes = _calculate_minutes(punch.clock_in_at, punch.clock_out_at, daily_limit)

    punch.updated_at = _now_str()
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
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    punch = db.exec(select(TimeSheetPunch).where(TimeSheetPunch.punch_id == punch_id)).first()
    if not punch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Punch not found")

    punch.status = TimeSheetPunchStatusEnum.APPROVED.value
    punch.approved_by = user_permissions["employee"]["employee_id"]
    punch.approved_at = _now_str()
    punch.updated_at = punch.approved_at
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
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    punch = db.exec(select(TimeSheetPunch).where(TimeSheetPunch.punch_id == punch_id)).first()
    if not punch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Punch not found")

    punch.status = TimeSheetPunchStatusEnum.REJECTED.value
    punch.approved_by = user_permissions["employee"]["employee_id"]
    punch.approved_at = _now_str()
    punch.updated_at = punch.approved_at
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
    open_punch = _get_open_punch(db, current_employee.employee_id)

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
    regular_hours = float(settings_row.overtime_daily_hours) if settings_row.overtime_daily_hours else 8.0
    max_overtime_hours = float(settings_row.max_overtime_daily_hours) if settings_row.max_overtime_daily_hours else 8.0
    total_hours_limit = regular_hours + max_overtime_hours  # Hours at which auto clock out occurs
    weekly_hours_limit = float(settings_row.overtime_weekly_hours) if settings_row.overtime_weekly_hours else 40.0

    # Calculate elapsed time for current punch
    now_str = _now_str()
    elapsed_minutes = _calculate_minutes(open_punch.clock_in_at, now_str)
    elapsed_hours = float(Decimal(elapsed_minutes) / Decimal(60)) if elapsed_minutes else 0

    # Calculate weekly hours (including current punch)
    tzinfo, _ = _get_request_timezone(request)
    today = date.today()  # noqa: DTZ011
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    utc_start, utc_end = _get_utc_range(week_start, week_end, tzinfo)

    # Get punches for this week (including current open punch)
    weekly_punches = db.exec(
        select(TimeSheetPunch).where(
            TimeSheetPunch.employee_id == current_employee.employee_id,
            TimeSheetPunch.clock_in_at >= utc_start,
            TimeSheetPunch.clock_in_at <= utc_end,
        )
    ).all()

    weekly_minutes = sum(p.worked_minutes or 0 for p in weekly_punches if p.worked_minutes)
    # Add current punch elapsed minutes
    weekly_minutes += elapsed_minutes
    weekly_hours = float(Decimal(weekly_minutes) / Decimal(60))

    # Get customer name
    customer_name = None
    if open_punch.customer_id:
        customer = db.exec(select(Customers).where(Customers.customer_id == open_punch.customer_id)).first()
        if customer:
            customer_name = customer.company_name or (f"{customer.first_name or ''} {customer.last_name or ''}".strip())

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
        clock_in_time=open_punch.clock_in_at,
    )


@router.post("/timesheet/clock-out-auto", response_model=TimeSheetPunchRead)
def clock_out_auto(
    request: Request,
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
):
    """Automatic clock out when overtime limit is reached."""
    open_punch = _get_open_punch(db, current_employee.employee_id)
    if not open_punch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Open punch not found")

    now_str = _now_str()
    _, tz_name = _get_request_timezone(request)
    open_punch.clock_out_at = now_str
    open_punch.worked_minutes = _calculate_minutes(open_punch.clock_in_at, now_str)
    open_punch.status = TimeSheetPunchStatusEnum.CLOSED.value
    open_punch.timezone = tz_name
    open_punch.updated_at = now_str

    # Get customer name
    customer_name = None
    if open_punch.customer_id:
        customer = db.exec(select(Customers).where(Customers.customer_id == open_punch.customer_id)).first()
        if customer:
            customer_name = customer.company_name or (f"{customer.first_name or ''} {customer.last_name or ''}".strip())

    # Get employee's email
    employee = db.exec(select(Employees).where(Employees.employee_id == current_employee.employee_id)).first()
    employee_email = employee.email if employee else None
    employee_name = f"{employee.first_name or ''} {employee.last_name or ''}".strip() if employee else "Employee"

    elapsed_hours = float(Decimal(open_punch.worked_minutes) / Decimal(60)) if open_punch.worked_minutes else 0

    # Send notification email
    app_url = getattr(settings, "APP_URL", None)
    if employee_email:
        try:
            asyncio.run(
                notify_timesheet_hours(
                    employee_id=current_employee.employee_id,
                    employee_name=employee_name,
                    employee_email=employee_email,
                    notification_type="overtime",
                    hours_worked=elapsed_hours,
                    customer_name=customer_name,
                    clock_in_time=open_punch.clock_in_at,
                    action_url=app_url,
                )
            )
        except Exception:
            # Don't fail the request if email fails, but keep traceability.
            logger.exception(
                "Failed to send overtime notification after auto clock-out",
                extra={"employee_id": current_employee.employee_id},
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
    open_punch = _get_open_punch(db, current_employee.employee_id)

    if not open_punch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Open punch not found")

    # Calculate elapsed time
    now_str = _now_str()
    elapsed_minutes = _calculate_minutes(open_punch.clock_in_at, now_str)
    elapsed_hours = float(Decimal(elapsed_minutes) / Decimal(60)) if elapsed_minutes else 0

    # Get customer name
    customer_name = None
    if open_punch.customer_id:
        customer = db.exec(select(Customers).where(Customers.customer_id == open_punch.customer_id)).first()
        if customer:
            customer_name = customer.company_name or (f"{customer.first_name or ''} {customer.last_name or ''}".strip())

    # Get employee's email
    employee = db.exec(select(Employees).where(Employees.employee_id == current_employee.employee_id)).first()
    employee_email = employee.email if employee else None
    employee_name = f"{employee.first_name or ''} {employee.last_name or ''}".strip() if employee else "Employee"

    # Send notification email
    app_url = getattr(settings, "APP_URL", None)
    success = False
    if employee_email:
        try:
            result = asyncio.run(
                notify_timesheet_hours(
                    employee_id=current_employee.employee_id,
                    employee_name=employee_name,
                    employee_email=employee_email,
                    notification_type=notification_type,
                    hours_worked=elapsed_hours,
                    customer_name=customer_name,
                    clock_in_time=open_punch.clock_in_at,
                    action_url=app_url,
                )
            )
            success = result.success if result else False
        except Exception:
            logger.exception(
                "Failed to send timesheet hours notification",
                extra={"employee_id": current_employee.employee_id},
            )

    return {"success": success}
