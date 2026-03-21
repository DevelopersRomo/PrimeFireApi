from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from api.dependencies import get_current_employee_with_permissions, require_authentication
from bd.dependencies import get_db
from models.timesheet import TimeSheetSettings
from schemas.timesheet import TimeSheetSettingsRead, TimeSheetSettingsUpdate

router = APIRouter(prefix="/api/v1", tags=["catalogs"])

DECIMAL_PLACES = Decimal("0.01")


def _quantize(value: Decimal | float | None) -> str:
    if value is None:
        value = Decimal(0)
    if not isinstance(value, Decimal):
        value = Decimal(value)
    return str(value.quantize(DECIMAL_PLACES))


def _has_admin_actions(user_permissions: dict) -> bool:
    for perm in user_permissions.get("permissions", []):
        if perm.get("module_key") == "timesheet":
            return perm.get("permissions", {}).get("admin_actions", False)
    return False


def _get_or_create_settings(db: Session) -> TimeSheetSettings:
    settings_row = db.exec(
        select(TimeSheetSettings)
        .where(TimeSheetSettings.is_active == True)  # noqa: E712
        .order_by(TimeSheetSettings.setting_id.desc())
    ).first()
    if settings_row:
        return settings_row
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")  # noqa: DTZ003
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


@router.get("/catalogs/timesheet", response_model=TimeSheetSettingsRead)
def get_timesheet_settings(
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    return _get_or_create_settings(db)


@router.put("/catalogs/timesheet", response_model=TimeSheetSettingsRead)
def upsert_timesheet_settings(
    payload: TimeSheetSettingsUpdate,
    user_permissions: dict = Depends(get_current_employee_with_permissions),
    db: Session = Depends(get_db),
):
    if not _has_admin_actions(user_permissions):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    settings_row = _get_or_create_settings(db)
    if payload.overtime_daily_hours is not None:
        settings_row.overtime_daily_hours = _quantize(payload.overtime_daily_hours)
    if payload.overtime_weekly_hours is not None:
        settings_row.overtime_weekly_hours = _quantize(payload.overtime_weekly_hours)
    if payload.max_overtime_daily_hours is not None:
        settings_row.max_overtime_daily_hours = _quantize(payload.max_overtime_daily_hours)
    if payload.round_to_minutes is not None:
        settings_row.round_to_minutes = payload.round_to_minutes
    if payload.is_active is not None:
        settings_row.is_active = payload.is_active
    settings_row.updated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")  # noqa: DTZ003

    db.add(settings_row)
    db.commit()
    db.refresh(settings_row)
    return settings_row
