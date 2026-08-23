"""Regression coverage for editable Expenses receipt and line deletion."""

from datetime import date
from decimal import Decimal

import pytest
from fastapi import HTTPException
from sqlmodel import Session, select

from api.expense_receipts import delete_report_receipt, router as expense_receipts_router
from api.expenses import delete_item, delete_report
from models.employees import Employees
from models.expenses import (
    ExpenseReceiptExtractions,
    ExpenseReceipts,
    ExpenseReportFlags,
    ExpenseReportItems,
    ExpenseReportMessages,
    ExpenseReports,
)
from services.expenses import policies

ADMIN_PERMISSIONS = {"permissions": [{"module_key": "expenses", "permissions": {"admin_actions": True}}]}
PLAIN_PERMISSIONS = {"permissions": [{"module_key": "expenses", "permissions": {"admin_actions": False}}]}


def _employee(db: Session, name: str) -> Employees:
    employee = Employees(first_name=name, last_name="Test", display_name=name, email=f"{name}@primefire.us")
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


def _report(db: Session, employee: Employees, suffix: int, status: str = "draft") -> ExpenseReports:
    report = ExpenseReports(
        folio=f"VIA-2026-{suffix:04d}",
        employee_id=employee.employee_id,
        title="Trip",
        status=status,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def _receipt(db: Session, report: ExpenseReports, item_id: int | None = None) -> ExpenseReceipts:
    receipt = ExpenseReceipts(report_id=report.report_id, item_id=item_id, file_name="receipt.pdf")
    db.add(receipt)
    db.commit()
    db.refresh(receipt)
    return receipt


def _duplicate_extraction(db: Session, receipt: ExpenseReceipts) -> None:
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


def test_owner_can_delete_receipt_and_recalculates_duplicate_flags(db_session: Session):
    owner = _employee(db_session, "owner")
    first_report = _report(db_session, owner, 1)
    second_report = _report(db_session, owner, 2)
    first_receipt = _receipt(db_session, first_report)
    second_receipt = _receipt(db_session, second_report)
    _duplicate_extraction(db_session, first_receipt)
    _duplicate_extraction(db_session, second_receipt)
    policies.replace_flags(db_session, first_report)
    policies.replace_flags(db_session, second_report)

    assert db_session.exec(select(ExpenseReportFlags).where(ExpenseReportFlags.report_id == second_report.report_id)).all()

    response = delete_report_receipt(
        first_report.report_id, first_receipt.receipt_id, db_session, owner, PLAIN_PERMISSIONS
    )

    assert response["success"] is True
    assert db_session.get(ExpenseReceipts, first_receipt.receipt_id) is None
    assert db_session.exec(
        select(ExpenseReceiptExtractions).where(ExpenseReceiptExtractions.receipt_id == first_receipt.receipt_id)
    ).first() is None
    assert db_session.exec(
        select(ExpenseReportFlags)
        .where(ExpenseReportFlags.report_id == second_report.report_id)
        .where(ExpenseReportFlags.code == "DUPLICATE_RECEIPT")
    ).all() == []


def test_global_receipt_deletion_route_is_not_exposed():
    assert not any(
        route.path == "/receipts/{receipt_id}" and "DELETE" in route.methods
        for route in expense_receipts_router.routes
    )


def test_delete_receipt_removes_metadata_when_file_cleanup_fails(db_session: Session, monkeypatch, tmp_path, caplog):
    owner = _employee(db_session, "owner")
    report = _report(db_session, owner, 1)
    file_path = tmp_path / "receipt.pdf"
    file_path.write_bytes(b"receipt")
    receipt = ExpenseReceipts(report_id=report.report_id, file_name="receipt.pdf", file_path=str(file_path))
    db_session.add(receipt)
    db_session.commit()
    db_session.refresh(receipt)
    _duplicate_extraction(db_session, receipt)

    def failing_unlink(*_args, **_kwargs):
        raise OSError("simulated cleanup failure")

    monkeypatch.setattr("api.expense_receipts.Path.unlink", failing_unlink)

    delete_report_receipt(report.report_id, receipt.receipt_id, db_session, owner, PLAIN_PERMISSIONS)

    assert db_session.get(ExpenseReceipts, receipt.receipt_id) is None
    assert db_session.exec(
        select(ExpenseReceiptExtractions).where(ExpenseReceiptExtractions.receipt_id == receipt.receipt_id)
    ).first() is None
    assert "Could not remove" in caplog.text


def test_admin_can_delete_another_employees_receipt(db_session: Session):
    owner = _employee(db_session, "owner")
    admin = _employee(db_session, "admin")
    report = _report(db_session, owner, 1)
    receipt = _receipt(db_session, report)

    delete_report_receipt(report.report_id, receipt.receipt_id, db_session, admin, ADMIN_PERMISSIONS)

    assert db_session.get(ExpenseReceipts, receipt.receipt_id) is None


def test_non_owner_cannot_delete_receipt(db_session: Session):
    owner = _employee(db_session, "owner")
    outsider = _employee(db_session, "outsider")
    report = _report(db_session, owner, 1)
    receipt = _receipt(db_session, report)

    with pytest.raises(HTTPException, match="belongs to another employee"):
        delete_report_receipt(report.report_id, receipt.receipt_id, db_session, outsider, PLAIN_PERMISSIONS)


def test_receipt_delete_rejects_non_editable_report_and_other_report_context(db_session: Session):
    owner = _employee(db_session, "owner")
    submitted = _report(db_session, owner, 1, status="submitted")
    draft = _report(db_session, owner, 2)
    receipt = _receipt(db_session, submitted)

    with pytest.raises(HTTPException, match="can no longer be edited"):
        delete_report_receipt(submitted.report_id, receipt.receipt_id, db_session, owner, PLAIN_PERMISSIONS)
    with pytest.raises(HTTPException, match="not found on this expense report"):
        delete_report_receipt(draft.report_id, receipt.receipt_id, db_session, owner, PLAIN_PERMISSIONS)


def test_deleting_a_receipt_removes_the_line_it_produced(db_session: Session):
    owner = _employee(db_session, "linkowner")
    report = _report(db_session, owner, 7)
    item = ExpenseReportItems(
        report_id=report.report_id,
        amount_original=Decimal("62.80"),
        amount_base=Decimal("62.80"),
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    receipt = _receipt(db_session, report, item.item_id)

    delete_report_receipt(report.report_id, receipt.receipt_id, db_session, owner, PLAIN_PERMISSIONS)

    assert db_session.get(ExpenseReceipts, receipt.receipt_id) is None
    assert db_session.get(ExpenseReportItems, item.item_id) is None
    db_session.refresh(report)
    assert report.total_requested == Decimal("0.00")


def test_a_line_backed_by_another_receipt_survives(db_session: Session):
    owner = _employee(db_session, "sharedowner")
    report = _report(db_session, owner, 8)
    item = ExpenseReportItems(
        report_id=report.report_id,
        amount_original=Decimal("62.80"),
        amount_base=Decimal("62.80"),
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    first = _receipt(db_session, report, item.item_id)
    _receipt(db_session, report, item.item_id)

    delete_report_receipt(report.report_id, first.receipt_id, db_session, owner, PLAIN_PERMISSIONS)

    assert db_session.get(ExpenseReportItems, item.item_id) is not None


def test_deleting_an_unlinked_receipt_leaves_the_lines_alone(db_session: Session):
    owner = _employee(db_session, "freeowner")
    report = _report(db_session, owner, 9)
    item = ExpenseReportItems(
        report_id=report.report_id,
        amount_original=Decimal("62.80"),
        amount_base=Decimal("62.80"),
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    unlinked = _receipt(db_session, report)

    delete_report_receipt(report.report_id, unlinked.receipt_id, db_session, owner, PLAIN_PERMISSIONS)

    assert db_session.get(ExpenseReportItems, item.item_id) is not None


def test_delete_draft_clears_every_row_that_references_it(db_session: Session, tmp_path):
    """The receipt FK from extractions used to abort the whole delete with a 500."""
    owner = _employee(db_session, "draftowner")
    report = _report(db_session, owner, 5)

    item = ExpenseReportItems(
        report_id=report.report_id,
        amount_original=Decimal("25.00"),
        amount_base=Decimal("25.00"),
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)

    file_path = tmp_path / "stored.pdf"
    file_path.write_bytes(b"receipt")
    receipt = ExpenseReceipts(
        report_id=report.report_id,
        item_id=item.item_id,
        file_name="receipt.pdf",
        file_path=str(file_path),
    )
    db_session.add(receipt)
    db_session.commit()
    db_session.refresh(receipt)
    _duplicate_extraction(db_session, receipt)

    db_session.add(
        ExpenseReportMessages(
            report_id=report.report_id,
            user_id=owner.employee_id,
            message_txt="Sending this tomorrow",
        )
    )
    db_session.commit()
    policies.replace_flags(db_session, report)

    response = delete_report(report.report_id, db_session, owner, PLAIN_PERMISSIONS)

    assert response["success"] is True
    assert db_session.get(ExpenseReports, report.report_id) is None
    assert db_session.get(ExpenseReportItems, item.item_id) is None
    assert db_session.get(ExpenseReceipts, receipt.receipt_id) is None
    assert db_session.exec(
        select(ExpenseReceiptExtractions).where(
            ExpenseReceiptExtractions.receipt_id == receipt.receipt_id
        )
    ).all() == []
    assert db_session.exec(
        select(ExpenseReportMessages).where(ExpenseReportMessages.report_id == report.report_id)
    ).all() == []
    assert db_session.exec(
        select(ExpenseReportFlags).where(ExpenseReportFlags.report_id == report.report_id)
    ).all() == []
    assert not file_path.exists()


def test_delete_draft_rejects_a_submitted_report(db_session: Session):
    owner = _employee(db_session, "submitowner")
    report = _report(db_session, owner, 6, status="submitted")

    with pytest.raises(HTTPException, match="Only a draft report can be deleted"):
        delete_report(report.report_id, db_session, owner, PLAIN_PERMISSIONS)


def test_delete_item_removes_duplicate_flag_before_fk_and_detaches_receipts(db_session: Session):
    owner = _employee(db_session, "owner")
    report = _report(db_session, owner, 1)
    item = ExpenseReportItems(
        report_id=report.report_id,
        amount_original=Decimal("25.00"),
        amount_base=Decimal("25.00"),
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    first_receipt = _receipt(db_session, report, item.item_id)
    second_receipt = _receipt(db_session, report)
    _duplicate_extraction(db_session, first_receipt)
    _duplicate_extraction(db_session, second_receipt)
    policies.replace_flags(db_session, report)

    assert db_session.exec(
        select(ExpenseReportFlags).where(ExpenseReportFlags.code == "DUPLICATE_RECEIPT")
    ).all()

    response = delete_item(item.item_id, db_session, owner, PLAIN_PERMISSIONS)

    assert response["success"] is True
    assert db_session.get(ExpenseReportItems, item.item_id) is None
    assert db_session.get(ExpenseReceipts, first_receipt.receipt_id).item_id is None
    assert db_session.exec(select(ExpenseReportFlags).where(ExpenseReportFlags.item_id == item.item_id)).all() == []
