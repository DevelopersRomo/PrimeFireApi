"""Regression coverage for how duplicate receipts reach the approver.

Two receipts of the same consumption are one exception, not two, and a report
never carries the same exception twice no matter how many extractions land at
once.
"""

from datetime import date
from decimal import Decimal

from sqlmodel import Session, select

from api.expenses import get_report
from models.employees import Employees
from models.expenses import (
    ExpenseReceiptExtractions,
    ExpenseReceipts,
    ExpenseReportFlags,
    ExpenseReports,
)
from services.expenses import policies

PLAIN_PERMISSIONS = {"permissions": [{"module_key": "expenses", "permissions": {"admin_actions": False}}]}


def _employee(db: Session, name: str) -> Employees:
    employee = Employees(first_name=name, last_name="Test", display_name=name, email=f"{name}@primefire.us")
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


def _report(db: Session, employee: Employees, suffix: int) -> ExpenseReports:
    report = ExpenseReports(
        folio=f"VIA-2026-{suffix:04d}",
        employee_id=employee.employee_id,
        title="Trip",
        status="draft",
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def _receipt(db: Session, report: ExpenseReports, file_name: str) -> ExpenseReceipts:
    receipt = ExpenseReceipts(report_id=report.report_id, file_name=file_name)
    db.add(receipt)
    db.commit()
    db.refresh(receipt)
    return receipt


def _same_consumption(db: Session, receipt: ExpenseReceipts) -> None:
    db.add(
        ExpenseReceiptExtractions(
            receipt_id=receipt.receipt_id,
            status="done",
            detected_merchant="Cafe Prime",
            detected_date=date(2026, 8, 20),
            detected_total=Decimal("25.00"),
        )
    )
    db.commit()


def test_duplicate_pair_raises_one_flag_naming_the_earlier_receipt(db_session: Session):
    owner = _employee(db_session, "dedupeowner")
    report = _report(db_session, owner, 91)
    first = _receipt(db_session, report, "first.pdf")
    second = _receipt(db_session, report, "second.pdf")
    _same_consumption(db_session, first)
    _same_consumption(db_session, second)

    policies.replace_flags(db_session, report)

    flags = db_session.exec(
        select(ExpenseReportFlags)
        .where(ExpenseReportFlags.report_id == report.report_id)
        .where(ExpenseReportFlags.code == "DUPLICATE_RECEIPT")
    ).all()

    assert len(flags) == 1
    assert "second.pdf" in flags[0].message
    assert f"receipt #{first.receipt_id}" in flags[0].message


def test_report_detail_reports_the_reading_status_of_each_receipt(db_session: Session):
    """Without it the capture form cannot tell which receipts still owe a line."""
    owner = _employee(db_session, "statusowner")
    report = _report(db_session, owner, 93)
    read = _receipt(db_session, report, "read.pdf")
    unread = _receipt(db_session, report, "unread.pdf")
    _same_consumption(db_session, read)
    db_session.add(ExpenseReceiptExtractions(receipt_id=unread.receipt_id, status="pending"))
    db_session.commit()

    detail = get_report(report.report_id, db_session, owner, PLAIN_PERMISSIONS)

    statuses = {item.receipt_id: item.extraction_status for item in detail.receipts}
    assert statuses[read.receipt_id] == "done"
    assert statuses[unread.receipt_id] == "pending"


def test_replace_flags_collapses_rows_two_evaluations_both_inserted(db_session: Session, monkeypatch):
    """Overlapping background extractions each insert the full set; keep one."""
    owner = _employee(db_session, "raceowner")
    report = _report(db_session, owner, 92)

    def _evaluated_twice(_db: Session, target: ExpenseReports) -> list[ExpenseReportFlags]:
        return [
            ExpenseReportFlags(
                report_id=target.report_id,
                code="DUPLICATE_RECEIPT",
                severity=policies.SEVERITY_CRITICAL,
                message="'second.pdf': Same merchant, date and amount as receipt #1",
            )
            for _ in range(2)
        ]

    monkeypatch.setattr(policies, "evaluate", _evaluated_twice)
    policies.replace_flags(db_session, report)

    flags = db_session.exec(
        select(ExpenseReportFlags).where(ExpenseReportFlags.report_id == report.report_id)
    ).all()

    assert len(flags) == 1
