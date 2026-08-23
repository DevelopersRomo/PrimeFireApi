"""Pulling a sent report back to draft.

A typo in a date used to mean asking an approver to reject the report, which
records a rejection that never really happened. Recall exists so the owner can
fix their own mistake — but only while nobody has decided anything.
"""

from decimal import Decimal

import pytest
from fastapi import HTTPException
from sqlmodel import Session, select

from api.expenses import recall_report
from models.employees import Employees
from models.expenses import ExpenseReportApprovals, ExpenseReportItems, ExpenseReports

ADMIN_PERMISSIONS = {"permissions": [{"module_key": "expenses", "permissions": {"admin_actions": True}}]}
PLAIN_PERMISSIONS = {"permissions": [{"module_key": "expenses", "permissions": {"admin_actions": False}}]}


def _employee(db: Session, name: str) -> Employees:
    employee = Employees(first_name=name, last_name="Test", display_name=name, email=f"{name}@primefire.us")
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


def _submitted(db: Session, owner: Employees, suffix: int, status: str = "submitted") -> ExpenseReports:
    report = ExpenseReports(
        folio=f"VIA-2026-{suffix:04d}",
        employee_id=owner.employee_id,
        title="Trip",
        status=status,
        current_level=1,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    item = ExpenseReportItems(
        report_id=report.report_id,
        amount_original=Decimal("62.80"),
        amount_base=Decimal("62.80"),
    )
    db.add(item)
    for level in (1, 2):
        db.add(ExpenseReportApprovals(report_id=report.report_id, level=level, decision="pending"))
    db.commit()
    db.refresh(report)
    return report


def test_the_owner_can_pull_an_untouched_report_back_to_draft(db_session: Session):
    owner = _employee(db_session, "recallowner")
    report = _submitted(db_session, owner, 41)

    detail = recall_report(report.report_id, db_session, owner, PLAIN_PERMISSIONS)

    assert detail.status == "draft"
    assert detail.submitted_at is None
    assert detail.current_level == 0


def test_the_chain_is_cleared_so_the_next_submit_rebuilds_it(db_session: Session):
    owner = _employee(db_session, "recallchain")
    report = _submitted(db_session, owner, 42)

    recall_report(report.report_id, db_session, owner, PLAIN_PERMISSIONS)

    assert db_session.exec(
        select(ExpenseReportApprovals).where(ExpenseReportApprovals.report_id == report.report_id)
    ).all() == []


def test_a_report_already_decided_at_one_level_cannot_be_pulled_back(db_session: Session):
    owner = _employee(db_session, "recalldecided")
    approver = _employee(db_session, "recallapprover")
    report = _submitted(db_session, owner, 43, status="in_review")
    step = db_session.exec(
        select(ExpenseReportApprovals)
        .where(ExpenseReportApprovals.report_id == report.report_id)
        .where(ExpenseReportApprovals.level == 1)
    ).first()
    step.decision = "approved"
    step.approver_id = approver.employee_id
    db_session.add(step)
    db_session.commit()

    with pytest.raises(HTTPException) as raised:
        recall_report(report.report_id, db_session, owner, PLAIN_PERMISSIONS)

    assert raised.value.status_code == 409
    assert "already been reviewed" in raised.value.detail
    # The recorded decision survives the refusal.
    db_session.refresh(step)
    assert step.decision == "approved"


def test_a_draft_cannot_be_recalled(db_session: Session):
    owner = _employee(db_session, "recalldraft")
    report = _submitted(db_session, owner, 44, status="draft")

    with pytest.raises(HTTPException) as raised:
        recall_report(report.report_id, db_session, owner, PLAIN_PERMISSIONS)

    assert raised.value.status_code == 400


def test_a_paid_report_cannot_be_recalled(db_session: Session):
    owner = _employee(db_session, "recallpaid")
    report = _submitted(db_session, owner, 45, status="paid")

    with pytest.raises(HTTPException) as raised:
        recall_report(report.report_id, db_session, owner, PLAIN_PERMISSIONS)

    assert raised.value.status_code == 400


def test_a_colleague_cannot_recall_someone_elses_report(db_session: Session):
    owner = _employee(db_session, "recallmine")
    outsider = _employee(db_session, "recallthief")
    report = _submitted(db_session, owner, 46)

    with pytest.raises(HTTPException) as raised:
        recall_report(report.report_id, db_session, outsider, PLAIN_PERMISSIONS)

    assert raised.value.status_code == 403


def test_an_administrator_can_recall_on_the_owners_behalf(db_session: Session):
    owner = _employee(db_session, "recallhelped")
    admin = _employee(db_session, "recalladmin")
    report = _submitted(db_session, owner, 47)

    detail = recall_report(report.report_id, db_session, admin, ADMIN_PERMISSIONS)

    assert detail.status == "draft"


def test_a_recalled_report_becomes_editable_again(db_session: Session):
    from api.expenses import _assert_editable

    owner = _employee(db_session, "recalledit")
    report = _submitted(db_session, owner, 48)

    recall_report(report.report_id, db_session, owner, PLAIN_PERMISSIONS)

    db_session.refresh(report)
    _assert_editable(report)  # raises if the status still locks editing
