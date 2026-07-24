"""Quotation number generation.

Two schemes coexist:
  * Q-IT-{year}-{sequence:06d}   internal draft number (assigned on create).
  * Q-{FIRST3}-{customer_id}-{seq:05d}  customer-scoped number assigned on
    first send. Counter lives in it.customer_quotation_sequences.
"""

import re
from datetime import datetime

from sqlalchemy import text
from sqlmodel import Session, func, select

from models.it.quotation_sequences import ITCustomerQuotationSequence
from models.it.quotations import ITQuotations

NUMBER_PREFIX = "Q-IT"


def format_quotation_number(year: int, sequence: int) -> str:
    return f"{NUMBER_PREFIX}-{year}-{sequence:06d}"


def next_quotation_number(db: Session) -> str:
    """Get the next internal quotation number (used on draft creation)."""
    year = datetime.utcnow().year
    dialect = db.get_bind().dialect.name

    if dialect == "mssql":
        sequence = db.exec(text("SELECT NEXT VALUE FOR it.quotation_sequence")).scalar()  # type: ignore[call-overload]
    else:
        max_id = db.exec(select(func.max(ITQuotations.quotation_id))).one()
        sequence = (max_id or 0) + 1

    return format_quotation_number(year, int(sequence))


def _customer_prefix(customer_name: str | None) -> str:
    """First 3 alphanumeric chars of the customer name, uppercased.

    Falls back to 'CUS' when the name has fewer than 3 usable characters.
    """
    letters = re.sub(r"[^A-Za-z0-9]", "", customer_name or "")
    prefix = letters[:3].upper()
    return prefix or "CUS"


def format_customer_quotation_number(
    customer_name: str | None, customer_id: int, sequence: int
) -> str:
    return f"Q-{_customer_prefix(customer_name)}-{customer_id}-{sequence:05d}"


def next_customer_quotation_number(
    db: Session,
    tenant_id: int,
    customer_id: int,
    customer_name: str | None,
) -> str:
    """Atomically bump the customer's counter and return the formatted number."""
    row = db.get(ITCustomerQuotationSequence, (tenant_id, customer_id))
    if row is None:
        row = ITCustomerQuotationSequence(
            tenant_id=tenant_id, customer_id=customer_id, last_number=1
        )
        db.add(row)
    else:
        row.last_number += 1
        row.updated_at = datetime.utcnow()
        db.add(row)

    db.flush()
    return format_customer_quotation_number(customer_name, customer_id, row.last_number)
