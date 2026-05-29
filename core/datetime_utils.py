"""Utility helpers for datetime operations.

SQL Server DATETIME columns require naive (no tzinfo) datetimes without microseconds.
Use `utcnow()` everywhere instead of `datetime.now(UTC)` to avoid ODBC HY104 errors.
"""

from datetime import UTC, datetime


def utcnow() -> datetime:
    """Return current UTC time as a naive datetime (no tzinfo, no microseconds).

    Required for compatibility with SQL Server DATETIME columns via pyodbc/ODBC driver,
    which rejects timezone-aware datetimes and microsecond precision.
    """
    return datetime.now(UTC).replace(microsecond=0, tzinfo=None)
