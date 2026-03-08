from datetime import date, datetime, timezone, time
from decimal import Decimal
from io import StringIO
import csv
from typing import List, Optional, Set

from fastapi import APIRouter, Depends, HTTPException, Response, status, BackgroundTasks, Query, Request
from sqlmodel import Session, select

from api.dependencies import (
    get_current_employee,
    get_current_employee_with_permissions,
    require_authentication,
)
from core.config import settings
from bd.dependencies import get_db
from models.employees import Employees
from services.notifications.notifications import (
    notify_time_off_submitted,
    notify_time_off_approved,
    notify_time_off_rejected,
)
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
)

router = APIRouter(prefix="/api/v1", tags=["time_off"])

DECIMAL_PLACES = Decimal("0.01")


def _quantize(value: Decimal | float | int | None) -> str:
    """Normalize numeric values to two decimal places and return as string."""
    if value is None:
        value = Decimal("0")
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
        dt = datetime.combine(date.today(), t)
        dt_utc = dt.astimezone(timezone.utc)
        return dt_utc.strftime("%H:%M:%S")
    return t.strftime("%H:%M:%S")


def _calculate_totals(payload: TimeOffRequestCreate) -> tuple[Decimal, Decimal | None]:
    """Calculate total days and hours based on payload."""
    if payload.EndDate < payload.StartDate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="EndDate must be greater than or equal to StartDate",
        )

    days_span = (payload.EndDate - payload.StartDate).days + 1

    if payload.TimeUnit == TimeUnitEnum.FULL_DAY:
        return Decimal(days_span), None

    if payload.TimeUnit == TimeUnitEnum.HALF_DAY:
        return Decimal(days_span) * Decimal("0.5"), None

    if payload.StartTime is None or payload.EndTime is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="StartTime and EndTime are required when TimeUnit is 'hours'",
        )

    start_time_str = _time_to_utc_str(payload.StartTime)
    end_time_str = _time_to_utc_str(payload.EndTime)

    start_time_clean = datetime.strptime(start_time_str, "%H:%M:%S").time()
    end_time_clean = datetime.strptime(end_time_str, "%H:%M:%S").time()

    combined_start = datetime.combine(date.today(), start_time_clean)
    combined_end = datetime.combine(date.today(), end_time_clean)
    total_seconds = (combined_end - combined_start).total_seconds()
    if total_seconds <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="EndTime must be after StartTime",
        )

    hours = Decimal(total_seconds / 3600).quantize(DECIMAL_PLACES)
    days = (hours / Decimal("8")).quantize(DECIMAL_PLACES)
    return days, hours


def _get_or_create_balance(
    db: Session, employee_id: int, absence_type: AbsenceTypeEnum, year: int
) -> TimeOffBalance:
    balance = db.exec(
        select(TimeOffBalance).where(
            TimeOffBalance.EmployeeId == employee_id,
            TimeOffBalance.AbsenceType == absence_type,
            TimeOffBalance.Year == year,
        )
    ).first()
    if balance is None:
        balance = TimeOffBalance(
            EmployeeId=employee_id,
            AbsenceType=absence_type,
            Year=year,
            EntitledDays=Decimal("0"),
            UsedDays=Decimal("0"),
            PendingDays=Decimal("0"),
            CarryoverDays=Decimal("0"),
        )
        db.add(balance)
        db.commit()
        db.refresh(balance)
    return balance


def _get_request_or_404(db: Session, request_id: int) -> TimeOffRequest:
    request = db.exec(
        select(TimeOffRequest).where(TimeOffRequest.RequestId == request_id)
    ).first()
    if not request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    return request


def _has_timeoff_admin_actions(user_permissions: dict) -> bool:
    for perm in user_permissions.get("permissions", []):
        if perm.get("module_key") == "timeoff":
            return perm.get("permissions", {}).get("AdminActions", False)
    return False


def _get_direct_report_ids(db: Session, manager_employee_id: int) -> Set[int]:
    rows = db.exec(
        select(Employees.EmployeeId).where(
            Employees.ManagerEmployeeId == manager_employee_id
        )
    ).all()
    return {employee_id for employee_id in rows if employee_id is not None}


def _build_visible_employee_ids(
    db: Session,
    current_employee: Employees,
    is_admin: bool,
) -> Optional[Set[int]]:
    if is_admin:
        return None

    visible_ids = _get_direct_report_ids(db, current_employee.EmployeeId)
    visible_ids.add(current_employee.EmployeeId)
    return visible_ids


def _assert_request_visibility(request: TimeOffRequest, visible_employee_ids: Optional[Set[int]]):
    if visible_employee_ids is not None and request.EmployeeId not in visible_employee_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to access this request",
        )


def _assert_can_review_request(
    db: Session,
    request: TimeOffRequest,
    current_employee: Employees,
    is_admin: bool,
):
    if request.EmployeeId == current_employee.EmployeeId:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot approve or reject your own request",
        )

    if is_admin:
        return

    requester = db.exec(
        select(Employees).where(Employees.EmployeeId == request.EmployeeId)
    ).first()
    if not requester:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requester employee not found",
        )

    if requester.ManagerEmployeeId != current_employee.EmployeeId:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the direct manager or an admin can review this request",
        )


@router.get("/requests", response_model=List[TimeOffRequestRead])
def list_requests(
    request_status: Optional[str] = Query(default=None, alias="status"),
    employee_id: Optional[int] = None,
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
            scoped_ids.discard(current_employee.EmployeeId)
        if not scoped_ids:
            return []
    else:
        scoped_ids = None

    if employee_id is not None:
        if scoped_ids is not None and employee_id not in scoped_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to query this employee",
            )

    query = select(TimeOffRequest)

    if scoped_ids is not None:
        query = query.where(TimeOffRequest.EmployeeId.in_(scoped_ids))

    if employee_id is not None:
        query = query.where(TimeOffRequest.EmployeeId == employee_id)

    if request_status is not None:
        query = query.where(TimeOffRequest.Status == request_status)

    requests = db.exec(query.order_by(TimeOffRequest.CreatedAt.desc())).all()
    return requests


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
    tenant_key: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
):
    employee_id = payload.EmployeeId or current_employee.EmployeeId
    employee_exists = db.exec(
        select(Employees).where(Employees.EmployeeId == employee_id)
    ).first()
    if not employee_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    total_days, total_hours = _calculate_totals(payload)

    start_time_str = None
    end_time_str = None
    if payload.TimeUnit == TimeUnitEnum.HOURS and payload.StartTime and payload.EndTime:
        start_time_str = _time_to_utc_str(payload.StartTime)
        end_time_str = _time_to_utc_str(payload.EndTime)

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    
    time_off_request = TimeOffRequest(
        EmployeeId=employee_id,
        AbsenceType=payload.AbsenceType.value,
        TimeUnit=payload.TimeUnit.value,
        StartDate=payload.StartDate.strftime("%Y-%m-%d"),
        EndDate=payload.EndDate.strftime("%Y-%m-%d"),
        StartTime=start_time_str,
        EndTime=end_time_str,
        TotalDays=_quantize(total_days),
        TotalHours=_quantize(total_hours) if total_hours is not None else None,
        Reason=payload.Reason,
        Status=RequestStatusEnum.PENDING.value,
        CreatedAt=now_str,
        UpdatedAt=now_str,
    )

    year = payload.StartDate.year
    balance = _get_or_create_balance(
        db, employee_id, payload.AbsenceType.value, year
    )
    balance.PendingDays = _quantize(Decimal(balance.PendingDays) + total_days)
    db.add(balance)
    db.add(time_off_request)
    db.commit()
    db.refresh(time_off_request)

    # Determine recipient email (Manager or default)
    manager_email = employee_exists.ManagerEmail
    recipient_email = manager_email if manager_email else "info@primefire.us"
    support_cc_email = getattr(settings, "SUPPORT_EMAIL", "info@primefire.us")
    tenant_key = tenant_key or http_request.headers.get("X-Tenant-ID")

    background_tasks.add_task(
        notify_time_off_submitted,
        request_id=time_off_request.RequestId,
        employee_id=employee_exists.EmployeeId,
        employee_name=employee_exists.DisplayName,
        employee_email=employee_exists.Email,
        absence_type=payload.AbsenceType.value,
        start_date=payload.StartDate.strftime('%Y-%m-%d'),
        end_date=payload.EndDate.strftime('%Y-%m-%d'),
        total_days=_quantize(total_days),
        to_email=recipient_email,
        cc_email=support_cc_email,
        reason=payload.Reason,
        tenant_key=tenant_key,
        # action_url=f"https://primefireapp.azurewebsites.net/time-off/requests/{time_off_request.RequestId}"
    )

    return time_off_request


@router.patch("/requests/{request_id}/approve", response_model=TimeOffRequestRead)
def approve_request(
    request_id: int,
    review: RequestReview,
    http_request: Request,
    background_tasks: BackgroundTasks,
    tenant_key: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
    user_permissions: dict = Depends(get_current_employee_with_permissions),
):
    request = _get_request_or_404(db, request_id)
    is_admin = _has_timeoff_admin_actions(user_permissions)
    _assert_can_review_request(db, request, current_employee, is_admin)

    if request.Status != RequestStatusEnum.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending requests can be approved",
        )

    year = int(request.StartDate[:4])
    balance = _get_or_create_balance(
        db, request.EmployeeId, request.AbsenceType, year
    )
    pending = Decimal(balance.PendingDays) - Decimal(request.TotalDays)
    balance.PendingDays = _quantize(pending if pending > 0 else Decimal("0"))
    balance.UsedDays = _quantize(Decimal(balance.UsedDays) + Decimal(request.TotalDays))

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    
    request.Status = RequestStatusEnum.APPROVED.value
    request.ReviewedBy = current_employee.EmployeeId
    request.ReviewedAt = now_str
    request.ReviewNotes = review.ReviewNotes
    request.UpdatedAt = now_str

    db.add(balance)
    db.add(request)
    db.commit()
    db.refresh(request)

    # Notify requester
    requester = db.exec(select(Employees).where(Employees.EmployeeId == request.EmployeeId)).first()
    if requester and requester.Email:
        tenant_key = tenant_key or http_request.headers.get("X-Tenant-ID")
        background_tasks.add_task(
            notify_time_off_approved,
            request_id=request.RequestId,
            employee_id=requester.EmployeeId,
            employee_name=requester.DisplayName,
            employee_email=requester.Email,
            absence_type=request.AbsenceType,
            start_date=request.StartDate,
            end_date=request.EndDate,
            total_days=request.TotalDays,
            reason=request.Reason,
            reviewed_by_name=current_employee.DisplayName,
            reviewed_by_email=current_employee.Email,
            review_notes=review.ReviewNotes,
            tenant_key=tenant_key,
        )

    return request


@router.patch("/requests/{request_id}/reject", response_model=TimeOffRequestRead)
def reject_request(
    request_id: int,
    review: RequestReview,
    http_request: Request,
    background_tasks: BackgroundTasks,
    tenant_key: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
    user_permissions: dict = Depends(get_current_employee_with_permissions),
):
    request = _get_request_or_404(db, request_id)
    is_admin = _has_timeoff_admin_actions(user_permissions)
    _assert_can_review_request(db, request, current_employee, is_admin)

    if request.Status != RequestStatusEnum.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending requests can be rejected",
        )

    year = int(request.StartDate[:4])
    balance = _get_or_create_balance(
        db, request.EmployeeId, request.AbsenceType, year
    )
    pending = Decimal(balance.PendingDays) - Decimal(request.TotalDays)
    balance.PendingDays = _quantize(pending if pending > 0 else Decimal("0"))

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    
    request.Status = RequestStatusEnum.REJECTED.value
    request.ReviewedBy = current_employee.EmployeeId
    request.ReviewedAt = now_str
    request.ReviewNotes = review.ReviewNotes
    request.UpdatedAt = now_str

    db.add(balance)
    db.add(request)
    db.commit()
    db.refresh(request)

    # Notify requester
    requester = db.exec(select(Employees).where(Employees.EmployeeId == request.EmployeeId)).first()
    if requester and requester.Email:
        tenant_key = tenant_key or http_request.headers.get("X-Tenant-ID")
        background_tasks.add_task(
            notify_time_off_rejected,
            request_id=request.RequestId,
            employee_id=requester.EmployeeId,
            employee_name=requester.DisplayName,
            employee_email=requester.Email,
            absence_type=request.AbsenceType,
            start_date=request.StartDate,
            end_date=request.EndDate,
            total_days=request.TotalDays,
            reason=request.Reason,
            reviewed_by_name=current_employee.DisplayName,
            reviewed_by_email=current_employee.Email,
            review_notes=review.ReviewNotes,
            tenant_key=tenant_key,
        )

    return request


@router.get("/calendar", response_model=List[CalendarEvent])
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
        request_query = request_query.where(
            TimeOffRequest.EmployeeId.in_(visible_employee_ids)
        )
    requests = db.exec(request_query).all()

    events: List[CalendarEvent] = []
    for holiday in holidays:
        events.append(
            CalendarEvent(
                Id=str(holiday.HolidayId),
                Type="holiday",
                Title=holiday.Name,
                StartDate=holiday.Date,
                EndDate=holiday.Date,
            )
        )

    for request in requests:
        events.append(
            CalendarEvent(
                Id=str(request.RequestId),
                Type="time_off_request",
                Title=f"{request.AbsenceType} - {request.Status}",
                StartDate=request.StartDate,
                EndDate=request.EndDate,
                Status=request.Status,
                TimeUnit=request.TimeUnit,
                EmployeeId=request.EmployeeId,
                StartTime=request.StartTime,
                EndTime=request.EndTime,
            )
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
        request_query = request_query.where(
            TimeOffRequest.EmployeeId.in_(visible_employee_ids)
        )
        balance_query = balance_query.where(
            TimeOffBalance.EmployeeId.in_(visible_employee_ids)
        )

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
        status_counts[request.Status] += 1
        absence_totals[request.AbsenceType] += float(request.TotalDays)

    balance_map: dict[str, BalanceTotals] = {}
    for balance in balances:
        key = balance.AbsenceType
        if key not in balance_map:
            balance_map[key] = BalanceTotals()
        current = balance_map[key]
        current.entitled += float(balance.EntitledDays)
        current.used += float(balance.UsedDays)
        current.pending += float(balance.PendingDays)
        current.carryover += float(balance.CarryoverDays)

    summary = ReportSummary(
        total_requests=len(requests),
        status=StatusSummary(**status_counts),
        totals_by_absence=AbsenceTotals(**absence_totals),
        balances=balance_map,
    )
    return summary


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
        query = query.where(TimeOffRequest.EmployeeId.in_(visible_employee_ids))

    rows = db.exec(query).all()
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "RequestId",
            "EmployeeId",
            "AbsenceType",
            "Status",
            "TimeUnit",
            "StartDate",
            "EndDate",
            "StartTime",
            "EndTime",
            "TotalHours",
            "TotalDays",
            "Reason",
            "ReviewedBy",
            "ReviewedAt",
            "ReviewNotes",
            "CreatedAt",
            "UpdatedAt",
        ]
    )
    for item in rows:
        writer.writerow(
            [
                item.RequestId,
                item.EmployeeId,
                item.AbsenceType,
                item.Status,
                item.TimeUnit,
                item.StartDate,
                item.EndDate,
                item.StartTime,
                item.EndTime,
                item.TotalHours,
                item.TotalDays,
                item.Reason,
                item.ReviewedBy,
                item.ReviewedAt,
                item.ReviewNotes,
                item.CreatedAt,
                item.UpdatedAt,
            ]
        )

    csv_content = buffer.getvalue()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=time_off_requests.csv"},
    )


@router.get("/balances/{employee_id}", response_model=List[TimeOffBalanceRead])
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

    balances = db.exec(
        select(TimeOffBalance).where(TimeOffBalance.EmployeeId == employee_id)
    ).all()
    return balances


@router.get("/holidays", response_model=List[HolidayRead])
def list_holidays(db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    return db.exec(select(Holiday)).all()


@router.get("/departments", response_model=List[DepartmentRead])
def list_departments(
    db: Session = Depends(get_db), _auth=Depends(require_authentication)
):
    return db.exec(select(Department)).all()
