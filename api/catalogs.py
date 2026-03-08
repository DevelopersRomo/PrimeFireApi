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


def _quantize(value: Decimal | float | int | None) -> str:
    if value is None:
        value = Decimal("0")
    if not isinstance(value, Decimal):
        value = Decimal(value)
    return str(value.quantize(DECIMAL_PLACES))


def _has_admin_actions(user_permissions: dict) -> bool:
    for perm in user_permissions.get("permissions", []):
        if perm.get("module_key") == "timesheet":
            return perm.get("permissions", {}).get("AdminActions", False)
    return False


def _get_or_create_settings(db: Session) -> TimeSheetSettings:
    settings_row = db.exec(
        select(TimeSheetSettings)
        .where(TimeSheetSettings.IsActive == True)  # noqa: E712
        .order_by(TimeSheetSettings.SettingId.desc())
    ).first()
    if settings_row:
        return settings_row
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
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
    if payload.OvertimeDailyHours is not None:
        settings_row.OvertimeDailyHours = _quantize(payload.OvertimeDailyHours)
    if payload.OvertimeWeeklyHours is not None:
        settings_row.OvertimeWeeklyHours = _quantize(payload.OvertimeWeeklyHours)
    if payload.MaxOvertimeDailyHours is not None:
        settings_row.MaxOvertimeDailyHours = _quantize(payload.MaxOvertimeDailyHours)
    if payload.RoundToMinutes is not None:
        settings_row.RoundToMinutes = payload.RoundToMinutes
    if payload.IsActive is not None:
        settings_row.IsActive = payload.IsActive
    settings_row.UpdatedAt = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    db.add(settings_row)
    db.commit()
    db.refresh(settings_row)
    return settings_row
