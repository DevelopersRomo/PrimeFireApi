"""Quotation number generation: Q-IT-{year}-{sequence:06d}."""

from datetime import datetime

from sqlalchemy import text
from sqlmodel import Session, func, select

from models.it.quotations import ITQuotations

NUMBER_PREFIX = "Q-IT"


def format_quotation_number(year: int, sequence: int) -> str:
    return f"{NUMBER_PREFIX}-{year}-{sequence:06d}"


def next_quotation_number(db: Session) -> str:
    """Get the next quotation number.

    Uses the it.quotation_sequence SEQUENCE on SQL Server. Other dialects
    (SQLite in tests) fall back to MAX(quotation_id) + 1.
    """
    year = datetime.utcnow().year
    dialect = db.get_bind().dialect.name

    if dialect == "mssql":
        sequence = db.exec(text("SELECT NEXT VALUE FOR it.quotation_sequence")).scalar()  # type: ignore[call-overload]
    else:
        max_id = db.exec(select(func.max(ITQuotations.quotation_id))).one()
        sequence = (max_id or 0) + 1

    return format_quotation_number(year, int(sequence))
