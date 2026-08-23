"""Expense report folio generation: VIA-YYYY-NNNN.

The counter restarts every year and is derived from the highest folio already
stored for that year, so it works identically on SQL Server and on the SQLite
engine the test suite uses.
"""

from sqlmodel import Session, select

from core.datetime_utils import utcnow
from models.expenses import ExpenseReports

FOLIO_PREFIX = "VIA"


def format_folio(year: int, sequence: int) -> str:
    return f"{FOLIO_PREFIX}-{year}-{sequence:04d}"


def next_folio(db: Session) -> str:
    """Return the next unused folio for the current year."""
    year = utcnow().year
    prefix = f"{FOLIO_PREFIX}-{year}-"

    existing = db.exec(select(ExpenseReports.folio).where(ExpenseReports.folio.startswith(prefix))).all()  # type: ignore[attr-defined]

    highest = 0
    for folio in existing:
        tail = (folio or "").rsplit("-", 1)[-1]
        if tail.isdigit():
            highest = max(highest, int(tail))

    return format_folio(year, highest + 1)
