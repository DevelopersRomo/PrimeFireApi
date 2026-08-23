"""Who may reach a receipt.

Receipts are addressed by a bare integer id and hold invoices, bank references
and tax ids. Module-level `can_view` is held by every requester in the company,
so these endpoints have to answer the same question the report itself does:
owner, administrator, or the approver whose level the report is sitting at.
"""

import pytest
from fastapi import HTTPException
from sqlmodel import Session

from api.expense_receipts import download_receipt, get_extraction, list_receipts, upload_receipt
from models.employees import Employees
from models.expenses import ExpenseReceipts, ExpenseReports

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


def _receipt(db: Session, report: ExpenseReports) -> ExpenseReceipts:
    receipt = ExpenseReceipts(report_id=report.report_id, file_name="receipt.pdf")
    db.add(receipt)
    db.commit()
    db.refresh(receipt)
    return receipt


def test_a_colleague_cannot_download_another_employees_receipt(db_session: Session):
    owner = _employee(db_session, "downowner")
    outsider = _employee(db_session, "downoutsider")
    receipt = _receipt(db_session, _report(db_session, owner, 21))

    with pytest.raises(HTTPException) as raised:
        download_receipt(receipt.receipt_id, db_session, outsider, PLAIN_PERMISSIONS)

    assert raised.value.status_code == 403


def test_an_administrator_can_download_any_receipt(db_session: Session):
    owner = _employee(db_session, "adminowner")
    admin = _employee(db_session, "adminreader")
    receipt = _receipt(db_session, _report(db_session, owner, 22))

    # No file on disk, so it stops at 404 — never at the ownership gate.
    with pytest.raises(HTTPException) as raised:
        download_receipt(receipt.receipt_id, db_session, admin, ADMIN_PERMISSIONS)

    assert raised.value.status_code == 404


def test_a_colleague_cannot_read_another_employees_extraction(db_session: Session):
    owner = _employee(db_session, "extowner")
    outsider = _employee(db_session, "extoutsider")
    receipt = _receipt(db_session, _report(db_session, owner, 23))

    with pytest.raises(HTTPException) as raised:
        get_extraction(receipt.receipt_id, db_session, outsider, PLAIN_PERMISSIONS)

    assert raised.value.status_code == 403


def test_a_colleague_cannot_list_another_employees_receipts(db_session: Session):
    owner = _employee(db_session, "listowner")
    outsider = _employee(db_session, "listoutsider")
    report = _report(db_session, owner, 24)

    with pytest.raises(HTTPException) as raised:
        list_receipts(report.report_id, db_session, outsider, PLAIN_PERMISSIONS)

    assert raised.value.status_code == 403


def test_an_owner_lists_their_own_receipts(db_session: Session):
    owner = _employee(db_session, "selflist")
    report = _report(db_session, owner, 25)
    _receipt(db_session, report)

    assert len(list_receipts(report.report_id, db_session, owner, PLAIN_PERMISSIONS)) == 1


def test_a_colleague_cannot_attach_a_receipt_to_another_employees_report(db_session: Session):
    owner = _employee(db_session, "uploadowner")
    outsider = _employee(db_session, "uploadoutsider")
    report = _report(db_session, owner, 26)

    with pytest.raises(HTTPException) as raised:
        upload_receipt(report.report_id, None, None, None, db_session, outsider, PLAIN_PERMISSIONS)

    assert raised.value.status_code == 403


def test_no_receipt_can_be_attached_to_a_submitted_report(db_session: Session):
    owner = _employee(db_session, "lockedowner")
    report = _report(db_session, owner, 27, status="submitted")

    with pytest.raises(HTTPException) as raised:
        upload_receipt(report.report_id, None, None, None, db_session, owner, PLAIN_PERMISSIONS)

    assert raised.value.status_code == 400
