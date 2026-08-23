"""Policy engine.

Turns a report into a short list of exceptions. The point is that an approver
reads three flags instead of forty receipts.

Rules are evaluated on submit and re-evaluated whenever lines change. Flags are
advisory: they colour the approver's screen, they never block a submission.
"""

import logging
from collections import defaultdict
from decimal import Decimal

from sqlmodel import Session, select

from models.expenses import (
    BASE_CURRENCY,
    ExpenseCategories,
    ExpenseReceiptExtractions,
    ExpenseReceipts,
    ExpenseReportFlags,
    ExpenseReportItems,
    ExpenseReports,
)
from services.expenses import dedupe

logger = logging.getLogger(__name__)

SEVERITY_CRITICAL = "critical"
SEVERITY_WARNING = "warning"
SEVERITY_INFO = "info"

LOW_CONFIDENCE_THRESHOLD = Decimal("0.5")
AMOUNT_MISMATCH_TOLERANCE = Decimal("0.02")


def _flag(report_id: int, code: str, severity: str, message: str, item_id: int | None = None) -> ExpenseReportFlags:
    return ExpenseReportFlags(
        report_id=report_id,
        item_id=item_id,
        code=code,
        severity=severity,
        message=message,
    )


def evaluate(db: Session, report: ExpenseReports) -> list[ExpenseReportFlags]:
    """Recompute every flag for a report. Replaces the previous set."""
    items = db.exec(select(ExpenseReportItems).where(ExpenseReportItems.report_id == report.report_id)).all()
    receipts = db.exec(select(ExpenseReceipts).where(ExpenseReceipts.report_id == report.report_id)).all()

    categories = {
        category.category_id: category
        for category in db.exec(select(ExpenseCategories)).all()
    }

    flags: list[ExpenseReportFlags] = []

    flags.extend(_check_unconverted(report, items))
    flags.extend(_check_caps(report, items, categories))
    flags.extend(_check_invoice_required(report, items, categories))
    flags.extend(_check_trip_dates(report, items))
    flags.extend(_check_extraction(db, report, items, receipts))
    flags.extend(_check_duplicates(db, report, receipts))

    return flags


def replace_flags(db: Session, report: ExpenseReports) -> list[ExpenseReportFlags]:
    """Evaluate and persist, clearing whatever the previous run produced."""
    existing = db.exec(select(ExpenseReportFlags).where(ExpenseReportFlags.report_id == report.report_id)).all()
    for flag in existing:
        db.delete(flag)

    flags = evaluate(db, report)
    for flag in flags:
        db.add(flag)

    db.commit()
    _drop_duplicate_rows(db, report.report_id)
    return flags


def _drop_duplicate_rows(db: Session, report_id: int) -> None:
    """Collapse rows that two overlapping evaluations both inserted.

    Extraction runs as a background task per upload, so uploading two receipts
    fires two replace_flags calls on the same report: each deletes a set the
    other has not committed yet, then both insert, and the approver reads every
    exception twice. Keep the first row of each identical (code, item, message).
    """
    seen: set[tuple[str, int | None, str]] = set()
    duplicated = False

    for flag in db.exec(
        select(ExpenseReportFlags)
        .where(ExpenseReportFlags.report_id == report_id)
        .order_by(ExpenseReportFlags.flag_id)  # type: ignore[arg-type]
    ).all():
        key = (flag.code, flag.item_id, flag.message)
        if key in seen:
            db.delete(flag)
            duplicated = True
        else:
            seen.add(key)

    if duplicated:
        db.commit()


def _check_unconverted(report, items) -> list[ExpenseReportFlags]:
    """A foreign line still sitting at rate 1 was never really converted.

    It matters beyond the total: the band that picks the approval chain and the
    category caps are all read in the base currency, so an unconverted line
    routes and caps against the wrong number. The approver has to see it.
    """
    flags = []
    for item in items:
        if not item.currency or item.currency.upper() == BASE_CURRENCY:
            continue
        if item.fx_rate == 1:
            flags.append(
                _flag(
                    report.report_id,
                    "FX_RATE_UNAVAILABLE",
                    SEVERITY_CRITICAL,
                    f"{item.amount_original:.2f} {item.currency} could not be converted to "
                    f"{BASE_CURRENCY}; it is counted at face value",
                    item.item_id,
                )
            )
    return flags


def _check_caps(report, items, categories) -> list[ExpenseReportFlags]:
    flags = []
    daily_totals: dict[tuple[int, object], Decimal] = defaultdict(Decimal)

    for item in items:
        category = categories.get(item.category_id)
        if category is None:
            continue

        if category.per_item_cap is not None and item.amount_base > category.per_item_cap:
            flags.append(
                _flag(
                    report.report_id,
                    "OVER_ITEM_CAP",
                    SEVERITY_CRITICAL,
                    f"{category.name}: {item.amount_base:.2f} exceeds the per-expense cap of {category.per_item_cap:.2f}",
                    item.item_id,
                )
            )

        if item.expense_date is not None:
            daily_totals[(category.category_id, item.expense_date)] += item.amount_base

    for (category_id, day), amount in daily_totals.items():
        category = categories.get(category_id)
        if category is None or category.daily_cap is None:
            continue
        if amount > category.daily_cap:
            flags.append(
                _flag(
                    report.report_id,
                    "OVER_DAILY_CAP",
                    SEVERITY_WARNING,
                    f"{category.name} on {day.isoformat()}: {amount:.2f} exceeds the daily cap of {category.daily_cap:.2f}",
                )
            )

    return flags


def _check_invoice_required(report, items, categories) -> list[ExpenseReportFlags]:
    flags = []
    for item in items:
        category = categories.get(item.category_id)
        if category is None or not category.requires_invoice:
            continue
        if not item.has_invoice:
            flags.append(
                _flag(
                    report.report_id,
                    "MISSING_INVOICE",
                    SEVERITY_CRITICAL,
                    f"{category.name} requires a fiscal invoice and none was attached",
                    item.item_id,
                )
            )
    return flags


def _check_trip_dates(report, items) -> list[ExpenseReportFlags]:
    if report.trip_start_date is None or report.trip_end_date is None:
        return []

    flags = []
    for item in items:
        if item.expense_date is None:
            continue
        if item.expense_date < report.trip_start_date or item.expense_date > report.trip_end_date:
            flags.append(
                _flag(
                    report.report_id,
                    "DATE_OUTSIDE_TRIP",
                    SEVERITY_WARNING,
                    f"Expense dated {item.expense_date.isoformat()} falls outside the trip "
                    f"({report.trip_start_date.isoformat()} to {report.trip_end_date.isoformat()})",
                    item.item_id,
                )
            )
    return flags


def _check_extraction(db, report, items, receipts) -> list[ExpenseReportFlags]:
    """Compare what was read off the receipt against what the employee typed."""
    if not receipts:
        return []

    extractions = db.exec(
        select(ExpenseReceiptExtractions).where(
            ExpenseReceiptExtractions.receipt_id.in_([r.receipt_id for r in receipts])  # type: ignore[attr-defined]
        )
    ).all()
    by_receipt = {extraction.receipt_id: extraction for extraction in extractions}
    items_by_id = {item.item_id: item for item in items}

    flags = []
    for receipt in receipts:
        extraction = by_receipt.get(receipt.receipt_id)
        if extraction is None or extraction.status != "done":
            continue

        if extraction.confidence < LOW_CONFIDENCE_THRESHOLD:
            flags.append(
                _flag(
                    report.report_id,
                    "LOW_CONFIDENCE",
                    SEVERITY_INFO,
                    f"'{receipt.file_name}' could not be read reliably; the amount was captured by hand",
                    receipt.item_id,
                )
            )
            continue

        item = items_by_id.get(receipt.item_id) if receipt.item_id else None
        if item is None or extraction.detected_total is None:
            continue

        if abs(item.amount_original - extraction.detected_total) > AMOUNT_MISMATCH_TOLERANCE:
            flags.append(
                _flag(
                    report.report_id,
                    "AMOUNT_MISMATCH",
                    SEVERITY_CRITICAL,
                    f"Captured amount {item.amount_original:.2f} does not match "
                    f"{extraction.detected_total:.2f} read from '{receipt.file_name}'",
                    item.item_id,
                )
            )

    return flags


def _check_duplicates(db, report, receipts) -> list[ExpenseReportFlags]:
    if not receipts:
        return []

    extractions = db.exec(
        select(ExpenseReceiptExtractions).where(
            ExpenseReceiptExtractions.receipt_id.in_([r.receipt_id for r in receipts])  # type: ignore[attr-defined]
        )
    ).all()
    by_receipt = {extraction.receipt_id: extraction for extraction in extractions}

    flags = []
    for receipt in receipts:
        reasons = dedupe.find_duplicates(db, report.employee_id, receipt, by_receipt.get(receipt.receipt_id))
        for reason in reasons:
            flags.append(
                _flag(
                    report.report_id,
                    "DUPLICATE_RECEIPT",
                    SEVERITY_CRITICAL,
                    f"'{receipt.file_name}': {reason}",
                    receipt.item_id,
                )
            )
    return flags
