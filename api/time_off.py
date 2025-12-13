from datetime import date, datetime
from decimal import Decimal
from io import StringIO
import csv
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session, select

from api.dependencies import get_current_employee, require_authentication
from bd.dependencies import get_db
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

    start_time_clean = payload.StartTime.replace(tzinfo=None, microsecond=0)
    end_time_clean = payload.EndTime.replace(tzinfo=None, microsecond=0)

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


@router.get("/requests", response_model=List[TimeOffRequestRead])
def list_requests(
    db: Session = Depends(get_db), _auth=Depends(require_authentication)
):
    requests = db.exec(
        select(TimeOffRequest).order_by(TimeOffRequest.CreatedAt.desc())
    ).all()
    return requests


@router.get("/requests/{request_id}", response_model=TimeOffRequestRead)
def get_request(
    request_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    return _get_request_or_404(db, request_id)


@router.post("/requests", response_model=TimeOffRequestRead, status_code=status.HTTP_201_CREATED)
def create_request(
    payload: TimeOffRequestCreate,
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
        start_time_str = payload.StartTime.replace(tzinfo=None, microsecond=0).strftime("%H:%M:%S")
        end_time_str = payload.EndTime.replace(tzinfo=None, microsecond=0).strftime("%H:%M:%S")

    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    
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
    return time_off_request


@router.patch("/requests/{request_id}/approve", response_model=TimeOffRequestRead)
def approve_request(
    request_id: int,
    review: RequestReview,
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
):
    request = _get_request_or_404(db, request_id)
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

    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    
    request.Status = RequestStatusEnum.APPROVED.value
    request.ReviewedBy = current_employee.EmployeeId
    request.ReviewedAt = now_str
    request.ReviewNotes = review.ReviewNotes
    request.UpdatedAt = now_str

    db.add(balance)
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


@router.patch("/requests/{request_id}/reject", response_model=TimeOffRequestRead)
def reject_request(
    request_id: int,
    review: RequestReview,
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
):
    request = _get_request_or_404(db, request_id)
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

    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    
    request.Status = RequestStatusEnum.REJECTED.value
    request.ReviewedBy = current_employee.EmployeeId
    request.ReviewedAt = now_str
    request.ReviewNotes = review.ReviewNotes
    request.UpdatedAt = now_str

    db.add(balance)
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


@router.get("/calendar", response_model=List[CalendarEvent])
def get_calendar(
    db: Session = Depends(get_db), _auth=Depends(require_authentication)
):
    holidays = db.exec(select(Holiday)).all()
    requests = db.exec(select(TimeOffRequest)).all()

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
                Title=f"{request.AbsenceType.value} - {request.Status.value}",
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
    db: Session = Depends(get_db), _auth=Depends(require_authentication)
):
    requests = db.exec(select(TimeOffRequest)).all()
    balances = db.exec(select(TimeOffBalance)).all()

    status_counts = {
        "pending": 0,
        "approved": 0,
        "rejected": 0,
        "cancelled": 0,
    }
    absence_totals = {"vacation": 0.0, "personal": 0.0, "sick": 0.0}

    for request in requests:
        status_counts[request.Status.value] += 1
        absence_totals[request.AbsenceType.value] += float(request.TotalDays)

    balance_map: dict[str, BalanceTotals] = {}
    for balance in balances:
        key = balance.AbsenceType.value
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
    db: Session = Depends(get_db), _auth=Depends(require_authentication)
):
    rows = db.exec(select(TimeOffRequest)).all()
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
                item.AbsenceType.value,
                item.Status.value,
                item.TimeUnit.value,
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
    _auth=Depends(require_authentication),
):
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
