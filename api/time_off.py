import csv
from datetime import UTC, date, datetime, time
from decimal import Decimal
from io import StringIO

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request, Response, status
from sqlmodel import Session, select

from api.dependencies import (
    get_current_employee,
    get_current_employee_with_permissions,
    require_authentication,
)
from bd.dependencies import get_db
from core.config import settings
from models.employees import Employees
from models.time_off import (
    AbsenceTypeEnum,
    Department,
    Holiday,
    RequestStatusEnum,
    TimeOffBalance,
    TimeOffRequest,
    TimeUnitEnum,
)
from schemas.time_off import (
    AbsenceTotals,
    BalanceTotals,
    CalendarEvent,
    DepartmentRead,
    HolidayRead,
    ReportSummary,
    RequestReview,
    StatusSummary,
    TimeOffBalanceRead,
    TimeOffRequestCreate,
    TimeOffRequestRead,
    TimeOffRequestUpdate,
)
from services.notifications.notifications import (
    notify_time_off_approved,
    notify_time_off_rejected,
    notify_time_off_submitted,
)

router = APIRouter(prefix="/api/v1", tags=["time_off"])

DECIMAL_PLACES = Decimal("0.01")


def _quantize(value: Decimal | float | None) -> str:
    """Normalize numeric values to two decimal places and return as string."""
    if value is None:
        value = Decimal(0)
    if not isinstance(value, Decimal):
        value = Decimal(value)
    return str(value.quantize(DECIMAL_PLACES))


def _time_to_utc_str(t: time | str) -> str:
    """Convert a time object or string to a UTC string HH:MM:SS."""
    if isinstance(t, str):
        # If it's already a string, try to parse it to handle Z or offsets
        try:
            # Handle ISO format like "14:30:00Z" or "14:30:00-05:00"
            t_obj = time.fromisoformat(t.replace("Z", "+00:00"))
            t = t_obj
        except ValueError:
            # If it fails, just return the first 8 chars (HH:MM:SS)
            return t[:8]

    if t.tzinfo is not None:
        dt = datetime.combine(date.today(), t)  # noqa: DTZ011
        dt_utc = dt.astimezone(UTC)
        return dt_utc.strftime("%H:%M:%S")
    return t.strftime("%H:%M:%S")


def _calculate_totals(payload: TimeOffRequestCreate) -> tuple[Decimal, Decimal | None]:
    """Calculate total days and hours based on payload."""
    if payload.end_date < payload.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end_date must be greater than or equal to start_date",
        )

    if payload.time_unit == TimeUnitEnum.HALF_DAY and payload.start_date != payload.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="half_day requests must use the same start_date and end_date",
        )

    days_span = (payload.end_date - payload.start_date).days + 1

    if payload.time_unit == TimeUnitEnum.FULL_DAY:
        return Decimal(days_span), None

    if payload.time_unit == TimeUnitEnum.HALF_DAY:
        return Decimal(days_span) * Decimal("0.5"), None

    if payload.start_time is None or payload.end_time is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_time and end_time are required when time_unit is 'hours'",
        )

    start_time_str = _time_to_utc_str(payload.start_time)
    end_time_str = _time_to_utc_str(payload.end_time)

    start_time_clean = datetime.strptime(start_time_str, "%H:%M:%S").time()  # noqa: DTZ007
    end_time_clean = datetime.strptime(end_time_str, "%H:%M:%S").time()  # noqa: DTZ007

    combined_start = datetime.combine(date.today(), start_time_clean)  # noqa: DTZ011
    combined_end = datetime.combine(date.today(), end_time_clean)  # noqa: DTZ011
    total_seconds = (combined_end - combined_start).total_seconds()
    if total_seconds <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end_time must be after start_time",
        )

    hours = Decimal(total_seconds / 3600).quantize(DECIMAL_PLACES)
    days = (hours / Decimal(8)).quantize(DECIMAL_PLACES)
    return days, hours


def _parse_time_value(value: str | None) -> time | None:
    if not value:
        return None
    cleaned = value.replace("Z", "")
    try:
        return datetime.strptime(cleaned[:8], "%H:%M:%S").time()  # noqa: DTZ007
    except ValueError:
        return None


def _time_ranges_overlap(start_a: time, end_a: time, start_b: time, end_b: time) -> bool:
    return start_a < end_b and end_a > start_b


def _assert_no_active_overlap(
    db: Session,
    employee_id: int,
    payload: TimeOffRequestCreate,
    exclude_request_id: int | None = None,
) -> None:
    query = select(TimeOffRequest).where(
        TimeOffRequest.employee_id == employee_id,
        TimeOffRequest.status.in_([RequestStatusEnum.PENDING.value, RequestStatusEnum.APPROVED.value]),
        TimeOffRequest.start_date <= payload.end_date.strftime("%Y-%m-%d"),
        TimeOffRequest.end_date >= payload.start_date.strftime("%Y-%m-%d"),
    )
    if exclude_request_id is not None:
        query = query.where(TimeOffRequest.request_id != exclude_request_id)

    overlapping = db.exec(query).all()

    for existing in overlapping:
        existing_start = datetime.strptime(existing.start_date, "%Y-%m-%d").date()  # noqa: DTZ007
        existing_end = datetime.strptime(existing.end_date, "%Y-%m-%d").date()  # noqa: DTZ007

        # Hourly requests can coexist on the same day only when their time ranges do not overlap.
        if (
            payload.time_unit == TimeUnitEnum.HOURS
            and existing.time_unit == TimeUnitEnum.HOURS.value
            and payload.start_date == payload.end_date
            and existing_start == existing_end
            and payload.start_date == existing_start
        ):
            payload_start_time = _parse_time_value(_time_to_utc_str(payload.start_time) if payload.start_time else None)
            payload_end_time = _parse_time_value(_time_to_utc_str(payload.end_time) if payload.end_time else None)
            existing_start_time = _parse_time_value(existing.start_time)
            existing_end_time = _parse_time_value(existing.end_time)

            if (
                payload_start_time
                and payload_end_time
                and existing_start_time
                and existing_end_time
                and not _time_ranges_overlap(
                    payload_start_time,
                    payload_end_time,
                    existing_start_time,
                    existing_end_time,
                )
            ):
                continue

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The request overlaps with an existing pending or approved time off request",
        )


def _get_or_create_balance(db: Session, employee_id: int, absence_type: AbsenceTypeEnum, year: int) -> TimeOffBalance:
    balance = db.exec(
        select(TimeOffBalance).where(
            TimeOffBalance.employee_id == employee_id,
            TimeOffBalance.absence_type == absence_type,
            TimeOffBalance.year == year,
        )
    ).first()
    if balance is None:
        balance = TimeOffBalance(
            employee_id=employee_id,
            absence_type=absence_type,
            year=year,
            entitled_days=Decimal(0),
            used_days=Decimal(0),
            pending_days=Decimal(0),
            carryover_days=Decimal(0),
        )
        db.add(balance)
        db.commit()
        db.refresh(balance)
    return balance


def _get_request_or_404(db: Session, request_id: int) -> TimeOffRequest:
    request = db.exec(select(TimeOffRequest).where(TimeOffRequest.request_id == request_id)).first()
    if not request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    return request


def _has_timeoff_admin_actions(user_permissions: dict) -> bool:
    for perm in user_permissions.get("permissions", []):
        if perm.get("module_key") == "timeoff":
            return perm.get("permissions", {}).get("admin_actions", False)
    return False


def _get_direct_report_ids(db: Session, manager_employee_id: int) -> set[int]:
    rows = db.exec(select(Employees.employee_id).where(Employees.manager_employee_id == manager_employee_id)).all()
    return {employee_id for employee_id in rows if employee_id is not None}


def _build_visible_employee_ids(
    db: Session,
    current_employee: Employees,
    is_admin: bool,
) -> set[int] | None:
    if is_admin:
        return None

    visible_ids = _get_direct_report_ids(db, current_employee.employee_id)
    visible_ids.add(current_employee.employee_id)
    return visible_ids


def _assert_request_visibility(request: TimeOffRequest, visible_employee_ids: set[int] | None) -> None:
    if visible_employee_ids is not None and request.employee_id not in visible_employee_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to access this request",
        )


def _assert_can_review_request(
    db: Session,
    request: TimeOffRequest,
    current_employee: Employees,
    is_admin: bool,
) -> None:
    if request.employee_id == current_employee.employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot approve or reject your own request",
        )

    if is_admin:
        return

    requester = db.exec(select(Employees).where(Employees.employee_id == request.employee_id)).first()
    if not requester:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requester employee not found",
        )

    if requester.manager_employee_id != current_employee.employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the direct manager or an admin can review this request",
        )


@router.get("/requests", response_model=list[TimeOffRequestRead])
def list_requests(
    request_status: str | None = Query(default=None, alias="status"),
    employee_id: int | None = None,
    team_only: bool = False,
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
    user_permissions: dict = Depends(get_current_employee_with_permissions),
):
    is_admin = _has_timeoff_admin_actions(user_permissions)
    visible_employee_ids = _build_visible_employee_ids(db, current_employee, is_admin)

    if visible_employee_ids is not None:
        scoped_ids = set(visible_employee_ids)
        if team_only:
            scoped_ids.discard(current_employee.employee_id)
        if not scoped_ids:
            return []
    else:
        scoped_ids = None

    if employee_id is not None and scoped_ids is not None and employee_id not in scoped_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to query this employee",
        )

    query = select(TimeOffRequest)

    if scoped_ids is not None:
        query = query.where(TimeOffRequest.employee_id.in_(scoped_ids))

    if employee_id is not None:
        query = query.where(TimeOffRequest.employee_id == employee_id)

    if request_status is not None:
        query = query.where(TimeOffRequest.status == request_status)

    return db.exec(query.order_by(TimeOffRequest.created_at.desc())).all()


@router.get("/requests/{request_id}", response_model=TimeOffRequestRead)
def get_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
    user_permissions: dict = Depends(get_current_employee_with_permissions),
):
    request = _get_request_or_404(db, request_id)
    is_admin = _has_timeoff_admin_actions(user_permissions)
    visible_employee_ids = _build_visible_employee_ids(db, current_employee, is_admin)
    _assert_request_visibility(request, visible_employee_ids)
    return request


@router.post("/requests", response_model=TimeOffRequestRead, status_code=status.HTTP_201_CREATED)
def create_request(
    payload: TimeOffRequestCreate,
    http_request: Request,
    background_tasks: BackgroundTasks,
    tenant_key: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
):
    employee_id = payload.employee_id or current_employee.employee_id
    employee_exists = db.exec(select(Employees).where(Employees.employee_id == employee_id)).first()
    if not employee_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    total_days, total_hours = _calculate_totals(payload)
    _assert_no_active_overlap(db, employee_id, payload)

    start_time_str = None
    end_time_str = None
    if payload.time_unit == TimeUnitEnum.HOURS and payload.start_time and payload.end_time:
        start_time_str = _time_to_utc_str(payload.start_time)
        end_time_str = _time_to_utc_str(payload.end_time)

    now_str = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")

    time_off_request = TimeOffRequest(
        employee_id=employee_id,
        absence_type=payload.absence_type.value,
        time_unit=payload.time_unit.value,
        start_date=payload.start_date.strftime("%Y-%m-%d"),
        end_date=payload.end_date.strftime("%Y-%m-%d"),
        start_time=start_time_str,
        end_time=end_time_str,
        total_days=_quantize(total_days),
        total_hours=_quantize(total_hours) if total_hours is not None else None,
        reason=payload.reason,
        status=RequestStatusEnum.PENDING.value,
        created_at=now_str,
        updated_at=now_str,
    )

    year = payload.start_date.year
    balance = _get_or_create_balance(db, employee_id, payload.absence_type.value, year)
    balance.pending_days = _quantize(Decimal(balance.pending_days) + total_days)
    db.add(balance)
    db.add(time_off_request)
    db.commit()
    db.refresh(time_off_request)

    # Determine recipient email (Manager or default)
    manager_email = employee_exists.manager_email
    recipient_email = manager_email or "info@primefire.us"
    support_cc_email = getattr(settings, "SUPPORT_EMAIL", "info@primefire.us")

    background_tasks.add_task(
        notify_time_off_submitted,
        request_id=time_off_request.request_id,
        employee_id=employee_exists.employee_id,
        employee_name=employee_exists.display_name,
        employee_email=employee_exists.email,
        absence_type=payload.absence_type.value,
        start_date=payload.start_date.strftime("%Y-%m-%d"),
        end_date=payload.end_date.strftime("%Y-%m-%d"),
        total_days=_quantize(total_days),
        to_email=recipient_email,
        cc_email=support_cc_email,
        reason=payload.reason,
        tenant_key=tenant_key,
        # action_url=f"https://primefireapp.azurewebsites.net/time-off/requests/{time_off_request.request_id}"
    )

    return time_off_request


@router.patch("/requests/{request_id}", response_model=TimeOffRequestRead)
def update_request(
    request_id: int,
    payload: TimeOffRequestUpdate,
    http_request: Request,
    background_tasks: BackgroundTasks,
    tenant_key: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
    user_permissions: dict = Depends(get_current_employee_with_permissions),
):
    request = _get_request_or_404(db, request_id)
    is_admin = _has_timeoff_admin_actions(user_permissions)

    # Visibility check
    visible_employee_ids = _build_visible_employee_ids(db, current_employee, is_admin)
    _assert_request_visibility(request, visible_employee_ids)

    # Permission: only owner, manager, or admin can edit
    is_owner = request.employee_id == current_employee.employee_id
    is_manager = False
    if not is_owner:
        requester_emp = db.exec(
            select(Employees).where(Employees.employee_id == request.employee_id)
        ).first()
        if requester_emp and requester_emp.manager_employee_id == current_employee.employee_id:
            is_manager = True

    if not is_admin and not is_owner and not is_manager:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to edit this request",
        )

    # Status constraint: non-admins can only edit pending
    if not is_admin and request.status != RequestStatusEnum.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending requests can be edited",
        )

    # Build effective values by merging payload with existing request
    effective_absence_type = payload.absence_type.value if payload.absence_type else request.absence_type
    effective_time_unit = payload.time_unit if payload.time_unit else TimeUnitEnum(request.time_unit)
    effective_start_date = payload.start_date or datetime.strptime(request.start_date, "%Y-%m-%d").date()  # noqa: DTZ007
    effective_end_date = payload.end_date or datetime.strptime(request.end_date, "%Y-%m-%d").date()  # noqa: DTZ007

    # For time fields, use payload if provided, else parse from existing
    if payload.start_time is not None:
        effective_start_time = payload.start_time
    else:
        effective_start_time = _parse_time_value(request.start_time)

    if payload.end_time is not None:
        effective_end_time = payload.end_time
    else:
        effective_end_time = _parse_time_value(request.end_time)

    effective_reason = payload.reason if payload.reason is not None else request.reason

    # Construct a TimeOffRequestCreate for validation via existing helpers
    validation_payload = TimeOffRequestCreate(
        employee_id=request.employee_id,
        absence_type=AbsenceTypeEnum(effective_absence_type),
        time_unit=effective_time_unit,
        start_date=effective_start_date,
        end_date=effective_end_date,
        start_time=effective_start_time,
        end_time=effective_end_time,
        reason=effective_reason,
    )

    # Validate and calculate totals
    new_total_days, new_total_hours = _calculate_totals(validation_payload)

    # Overlap check (exclude current request)
    _assert_no_active_overlap(db, request.employee_id, validation_payload, exclude_request_id=request_id)

    # Determine time string values for storage
    new_start_time_str = None
    new_end_time_str = None
    if effective_time_unit == TimeUnitEnum.HOURS and effective_start_time and effective_end_time:
        new_start_time_str = _time_to_utc_str(effective_start_time)
        new_end_time_str = _time_to_utc_str(effective_end_time)

    # Capture old values for balance recalculation
    old_total_days = Decimal(request.total_days)
    old_absence_type = request.absence_type
    old_year = int(request.start_date[:4])
    new_year = effective_start_date.year

    # Apply field updates to the request
    request.absence_type = effective_absence_type
    request.time_unit = effective_time_unit.value
    request.start_date = effective_start_date.strftime("%Y-%m-%d")
    request.end_date = effective_end_date.strftime("%Y-%m-%d")
    request.start_time = new_start_time_str
    request.end_time = new_end_time_str
    request.total_days = _quantize(new_total_days)
    request.total_hours = _quantize(new_total_hours) if new_total_hours is not None else None
    request.reason = effective_reason
    request.updated_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")

    # Balance recalculation if totals, absence_type, or year changed
    needs_balance_update = (
        old_total_days != new_total_days
        or old_absence_type != effective_absence_type
        or old_year != new_year
    )

    if needs_balance_update and request.status in (
        RequestStatusEnum.PENDING.value,
        RequestStatusEnum.APPROVED.value,
    ):
        # Reverse old balance
        old_balance = _get_or_create_balance(db, request.employee_id, old_absence_type, old_year)
        if request.status == RequestStatusEnum.PENDING.value:
            old_balance.pending_days = _quantize(
                max(Decimal(0), Decimal(old_balance.pending_days) - old_total_days)
            )
        else:
            old_balance.used_days = _quantize(
                max(Decimal(0), Decimal(old_balance.used_days) - old_total_days)
            )
        db.add(old_balance)

        # Apply new balance
        if old_absence_type != effective_absence_type or old_year != new_year:
            new_balance = _get_or_create_balance(db, request.employee_id, effective_absence_type, new_year)
        else:
            new_balance = old_balance

        if request.status == RequestStatusEnum.PENDING.value:
            new_balance.pending_days = _quantize(Decimal(new_balance.pending_days) + new_total_days)
        else:
            new_balance.used_days = _quantize(Decimal(new_balance.used_days) + new_total_days)
        db.add(new_balance)

    db.add(request)
    db.commit()
    db.refresh(request)

    # Send notification to manager with updated data
    employee_record = db.exec(
        select(Employees).where(Employees.employee_id == request.employee_id)
    ).first()
    if employee_record:
        manager_email = employee_record.manager_email
        recipient_email = manager_email or "info@primefire.us"
        support_cc_email = getattr(settings, "SUPPORT_EMAIL", "info@primefire.us")

        background_tasks.add_task(
            notify_time_off_submitted,
            request_id=request.request_id,
            employee_id=employee_record.employee_id,
            employee_name=employee_record.display_name,
            employee_email=employee_record.email,
            absence_type=request.absence_type,
            start_date=request.start_date,
            end_date=request.end_date,
            total_days=request.total_days,
            to_email=recipient_email,
            cc_email=support_cc_email,
            reason=request.reason,
            tenant_key=tenant_key,
        )

    return request


@router.patch("/requests/{request_id}/approve", response_model=TimeOffRequestRead)
def approve_request(
    request_id: int,
    review: RequestReview,
    http_request: Request,
    background_tasks: BackgroundTasks,
    tenant_key: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
    user_permissions: dict = Depends(get_current_employee_with_permissions),
):
    request = _get_request_or_404(db, request_id)
    is_admin = _has_timeoff_admin_actions(user_permissions)
    _assert_can_review_request(db, request, current_employee, is_admin)

    if request.status != RequestStatusEnum.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending requests can be approved",
        )

    year = int(request.start_date[:4])
    balance = _get_or_create_balance(db, request.employee_id, request.absence_type, year)
    pending = Decimal(balance.pending_days) - Decimal(request.total_days)
    balance.pending_days = _quantize(pending if pending > 0 else Decimal(0))
    balance.used_days = _quantize(Decimal(balance.used_days) + Decimal(request.total_days))

    now_str = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")

    request.status = RequestStatusEnum.APPROVED.value
    request.reviewed_by = current_employee.employee_id
    request.reviewed_at = now_str
    request.review_notes = review.review_notes
    request.updated_at = now_str

    db.add(balance)
    db.add(request)
    db.commit()
    db.refresh(request)

    # Notify requester
    requester = db.exec(select(Employees).where(Employees.employee_id == request.employee_id)).first()
    if requester and requester.email:
        background_tasks.add_task(
            notify_time_off_approved,
            request_id=request.request_id,
            employee_id=requester.employee_id,
            employee_name=requester.display_name,
            employee_email=requester.email,
            absence_type=request.absence_type,
            start_date=request.start_date,
            end_date=request.end_date,
            total_days=request.total_days,
            reason=request.reason,
            reviewed_by_name=current_employee.display_name,
            reviewed_by_email=current_employee.email,
            review_notes=review.review_notes,
            tenant_key=tenant_key,
        )

    return request


@router.patch("/requests/{request_id}/reject", response_model=TimeOffRequestRead)
def reject_request(
    request_id: int,
    review: RequestReview,
    http_request: Request,
    background_tasks: BackgroundTasks,
    tenant_key: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
    user_permissions: dict = Depends(get_current_employee_with_permissions),
):
    request = _get_request_or_404(db, request_id)
    is_admin = _has_timeoff_admin_actions(user_permissions)
    _assert_can_review_request(db, request, current_employee, is_admin)

    if request.status != RequestStatusEnum.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending requests can be rejected",
        )

    year = int(request.start_date[:4])
    balance = _get_or_create_balance(db, request.employee_id, request.absence_type, year)
    pending = Decimal(balance.pending_days) - Decimal(request.total_days)
    balance.pending_days = _quantize(pending if pending > 0 else Decimal(0))

    now_str = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")

    request.status = RequestStatusEnum.REJECTED.value
    request.reviewed_by = current_employee.employee_id
    request.reviewed_at = now_str
    request.review_notes = review.review_notes
    request.updated_at = now_str

    db.add(balance)
    db.add(request)
    db.commit()
    db.refresh(request)

    # Notify requester
    requester = db.exec(select(Employees).where(Employees.employee_id == request.employee_id)).first()
    if requester and requester.email:
        background_tasks.add_task(
            notify_time_off_rejected,
            request_id=request.request_id,
            employee_id=requester.employee_id,
            employee_name=requester.display_name,
            employee_email=requester.email,
            absence_type=request.absence_type,
            start_date=request.start_date,
            end_date=request.end_date,
            total_days=request.total_days,
            reason=request.reason,
            reviewed_by_name=current_employee.display_name,
            reviewed_by_email=current_employee.email,
            review_notes=review.review_notes,
            tenant_key=tenant_key,
        )

    return request


@router.delete("/requests/{request_id}", response_model=TimeOffRequestRead)
def cancel_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
    user_permissions: dict = Depends(get_current_employee_with_permissions),
):
    request = _get_request_or_404(db, request_id)
    is_admin = _has_timeoff_admin_actions(user_permissions)

    # Visibility check
    visible_employee_ids = _build_visible_employee_ids(db, current_employee, is_admin)
    _assert_request_visibility(request, visible_employee_ids)

    # Permission: only owner or admin can cancel
    is_owner = request.employee_id == current_employee.employee_id
    if not is_admin and not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the request owner or an admin can cancel this request",
        )

    # Status constraint: only pending requests can be cancelled
    if request.status != RequestStatusEnum.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending requests can be cancelled",
        )

    # Reverse pending balance
    year = int(request.start_date[:4])
    balance = _get_or_create_balance(db, request.employee_id, request.absence_type, year)
    pending = Decimal(balance.pending_days) - Decimal(request.total_days)
    balance.pending_days = _quantize(pending if pending > 0 else Decimal(0))

    now_str = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")

    request.status = RequestStatusEnum.CANCELLED.value
    request.updated_at = now_str

    db.add(balance)
    db.add(request)
    db.commit()
    db.refresh(request)

    return request


@router.get("/calendar", response_model=list[CalendarEvent])
def get_calendar(
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
    user_permissions: dict = Depends(get_current_employee_with_permissions),
):
    is_admin = _has_timeoff_admin_actions(user_permissions)
    visible_employee_ids = _build_visible_employee_ids(db, current_employee, is_admin)

    holidays = db.exec(select(Holiday)).all()
    request_query = select(TimeOffRequest)
    if visible_employee_ids is not None:
        request_query = request_query.where(TimeOffRequest.employee_id.in_(visible_employee_ids))
    requests = db.exec(request_query).all()

    events: list[CalendarEvent] = [
        CalendarEvent(
            id=str(holiday.holiday_id),
            type="holiday",
            title=holiday.name,
            start_date=holiday.date,
            end_date=holiday.date,
        )
        for holiday in holidays
    ]

    events.extend(
        CalendarEvent(
            id=str(request.request_id),
            type="time_off_request",
            title=f"{request.absence_type} - {request.status}",
            start_date=request.start_date,
            end_date=request.end_date,
            status=request.status,
            time_unit=request.time_unit,
            employee_id=request.employee_id,
            start_time=request.start_time,
            end_time=request.end_time,
        )
        for request in requests
    )

    return events


@router.get("/reports/summary", response_model=ReportSummary)
def get_report_summary(
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
    user_permissions: dict = Depends(get_current_employee_with_permissions),
):
    is_admin = _has_timeoff_admin_actions(user_permissions)
    visible_employee_ids = _build_visible_employee_ids(db, current_employee, is_admin)

    request_query = select(TimeOffRequest)
    balance_query = select(TimeOffBalance)
    if visible_employee_ids is not None:
        request_query = request_query.where(TimeOffRequest.employee_id.in_(visible_employee_ids))
        balance_query = balance_query.where(TimeOffBalance.employee_id.in_(visible_employee_ids))

    requests = db.exec(request_query).all()
    balances = db.exec(balance_query).all()

    status_counts = {
        "pending": 0,
        "approved": 0,
        "rejected": 0,
        "cancelled": 0,
    }
    absence_totals = {"vacation": 0.0, "personal": 0.0, "sick": 0.0}

    for request in requests:
        status_counts[request.status] += 1
        absence_totals[request.absence_type] += float(request.total_days)

    balance_map: dict[str, BalanceTotals] = {}
    for balance in balances:
        key = balance.absence_type
        if key not in balance_map:
            balance_map[key] = BalanceTotals()
        current = balance_map[key]
        current.entitled += float(balance.entitled_days)
        current.used += float(balance.used_days)
        current.pending += float(balance.pending_days)
        current.carryover += float(balance.carryover_days)

    return ReportSummary(
        total_requests=len(requests),
        status=StatusSummary(**status_counts),
        totals_by_absence=AbsenceTotals(**absence_totals),
        balances=balance_map,
    )


@router.get("/reports/export")
def export_requests_report(
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
    user_permissions: dict = Depends(get_current_employee_with_permissions),
):
    is_admin = _has_timeoff_admin_actions(user_permissions)
    visible_employee_ids = _build_visible_employee_ids(db, current_employee, is_admin)

    query = select(TimeOffRequest)
    if visible_employee_ids is not None:
        query = query.where(TimeOffRequest.employee_id.in_(visible_employee_ids))

    rows = db.exec(query).all()
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "request_id",
            "employee_id",
            "absence_type",
            "status",
            "time_unit",
            "start_date",
            "end_date",
            "start_time",
            "end_time",
            "total_hours",
            "total_days",
            "reason",
            "reviewed_by",
            "reviewed_at",
            "review_notes",
            "created_at",
            "updated_at",
        ]
    )
    for item in rows:
        writer.writerow(
            [
                item.request_id,
                item.employee_id,
                item.absence_type,
                item.status,
                item.time_unit,
                item.start_date,
                item.end_date,
                item.start_time,
                item.end_time,
                item.total_hours,
                item.total_days,
                item.reason,
                item.reviewed_by,
                item.reviewed_at,
                item.review_notes,
                item.created_at,
                item.updated_at,
            ]
        )

    csv_content = buffer.getvalue()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=time_off_requests.csv"},
    )


@router.get("/balances/{employee_id}", response_model=list[TimeOffBalanceRead])
def get_balances(
    employee_id: int,
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
    user_permissions: dict = Depends(get_current_employee_with_permissions),
):
    is_admin = _has_timeoff_admin_actions(user_permissions)
    visible_employee_ids = _build_visible_employee_ids(db, current_employee, is_admin)
    if visible_employee_ids is not None and employee_id not in visible_employee_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to view this employee balances",
        )

    return db.exec(select(TimeOffBalance).where(TimeOffBalance.employee_id == employee_id)).all()


@router.get("/holidays", response_model=list[HolidayRead])
def list_holidays(db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    return db.exec(select(Holiday)).all()


@router.get("/departments", response_model=list[DepartmentRead])
def list_departments(db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    return db.exec(select(Department)).all()
