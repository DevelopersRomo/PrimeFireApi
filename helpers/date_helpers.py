"""Date and time helper functions."""

from datetime import date, datetime
from decimal import Decimal


def format_display_date(value: date | datetime | str | None) -> str | None:
    """Format a date/datetime to display format 'May 21, 2026'.

    Args:
        value: date, datetime, ISO string, or None

    Returns:
        Formatted string like 'May 21, 2026' or None if input is None
    """
    if value is None:
        return None

    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return value

    if isinstance(value, datetime):
        return value.strftime("%b %d, %Y").replace(" 0", " ")

    if isinstance(value, date):
        return value.strftime("%b %d, %Y").replace(" 0", " ")

    return str(value)


def format_hours_minutes(minutes: int) -> str:
    """Format minutes as 'xx hours xx min'.

    Args:
        minutes: Total minutes to format

    Returns:
        String in format 'xx hours xx min'
    """
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours} hours {mins} min"


def calculate_regular_overtime(worked_minutes: int, overtime_daily_minutes: int = 480) -> tuple[int, int]:
    """Calculate regular and overtime minutes based on daily limit.

    Args:
        worked_minutes: Total minutes worked
        overtime_daily_minutes: Daily limit in minutes (default 480 = 8 hours)

    Returns:
        Tuple of (regular_minutes, overtime_minutes)
    """
    if worked_minutes <= overtime_daily_minutes:
        return worked_minutes, 0
    return overtime_daily_minutes, worked_minutes - overtime_daily_minutes


def minutes_to_hours(minutes: int | None) -> float:
    """Convert minutes to hours as float.

    Args:
        minutes: Minutes to convert

    Returns:
        Hours as float
    """
    if minutes is None:
        return 0.0
    return float(Decimal(minutes) / Decimal(60))


def hours_to_minutes(hours: float) -> int:
    """Convert hours to minutes.

    Args:
        hours: Hours to convert

    Returns:
        Minutes as integer
    """
    return int(hours * 60)
