"""Separation-of-duty rules for the two-level expense approval chain.

The chain is Manager (level 1) then Accountant (level 2). Two levels only mean
something if two different people sign them, so these tests pin the rules that
enforce that — including against administrators.
"""

from decimal import Decimal

import pytest
from sqlmodel import Session

from models.employees import EmployeeRoles, Employees, Roles
from models.expenses import ExpenseApprovalRules, ExpenseReportApprovals, ExpenseReportItems, ExpenseReports
from services.expenses import approvals

ADMIN_PERMISSIONS = {"permissions": [{"module_key": "expenses", "permissions": {"admin_actions": True}}]}
PLAIN_PERMISSIONS = {"permissions": [{"module_key": "expenses", "permissions": {"admin_actions": False}}]}


def _employee(db: Session, name: str, email: str) -> Employees:
    employee = Employees(first_name=name, last_name="T", display_name=name, email=email)
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


def _role(db: Session, name: str) -> Roles:
    role = Roles(role_name=name)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def _assign(db: Session, employee: Employees, role: Roles) -> None:
    db.add(EmployeeRoles(employee_id=employee.employee_id, role_id=role.role_id))
    db.commit()


def _report(db: Session, employee: Employees, total: str = "5000.00") -> ExpenseReports:
    report = ExpenseReports(
        folio=f"VIA-2026-{employee.employee_id:04d}",
        employee_id=employee.employee_id,
        title="Trip",
        total_requested=Decimal(total),
        status="submitted",
        current_level=1,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def _chain(db: Session, report: ExpenseReports, manager: Roles, accountant: Roles) -> None:
    db.add(ExpenseReportApprovals(report_id=report.report_id, level=1, role_id=manager.role_id))
    db.add(ExpenseReportApprovals(report_id=report.report_id, level=2, role_id=accountant.role_id))
    db.commit()


@pytest.fixture
def chain_setup(db_session: Session):
    """A submitted report with a Manager -> Accountant chain and three people."""
    manager_role = _role(db_session, "Manager")
    accountant_role = _role(db_session, "Accountant")

    requester = _employee(db_session, "Requester", "requester@primefire.us")
    manager = _employee(db_session, "Manager", "manager@primefire.us")
    accountant = _employee(db_session, "Accountant", "accountant@primefire.us")

    _assign(db_session, manager, manager_role)
    _assign(db_session, accountant, accountant_role)

    report = _report(db_session, requester)
    _chain(db_session, report, manager_role, accountant_role)

    return {
        "db": db_session,
        "report": report,
        "requester": requester,
        "manager": manager,
        "accountant": accountant,
        "manager_role": manager_role,
        "accountant_role": accountant_role,
    }


# --- Chain construction -----------------------------------------------------


def test_single_band_covers_every_amount(db_session: Session):
    """One band from 0 to unbounded means no threshold to maintain."""
    manager_role = _role(db_session, "Manager")
    accountant_role = _role(db_session, "Accountant")
    db_session.add(ExpenseApprovalRules(min_amount=Decimal(0), max_amount=None, level=1, role_id=manager_role.role_id))
    db_session.add(
        ExpenseApprovalRules(min_amount=Decimal(0), max_amount=None, level=2, role_id=accountant_role.role_id)
    )
    db_session.commit()

    for amount in ("1.00", "9999.99", "250000.00"):
        rules = approvals.rules_for_amount(db_session, Decimal(amount))
        assert [rule.level for rule in rules] == [1, 2], f"amount {amount} did not resolve two levels"


def test_build_chain_creates_two_pending_levels(db_session: Session):
    manager_role = _role(db_session, "Manager")
    accountant_role = _role(db_session, "Accountant")
    db_session.add(ExpenseApprovalRules(min_amount=Decimal(0), max_amount=None, level=1, role_id=manager_role.role_id))
    db_session.add(
        ExpenseApprovalRules(min_amount=Decimal(0), max_amount=None, level=2, role_id=accountant_role.role_id)
    )
    db_session.commit()

    requester = _employee(db_session, "Requester", "r@primefire.us")
    report = _report(db_session, requester)

    chain = approvals.build_chain(db_session, report)
    db_session.commit()

    assert [step.level for step in chain] == [1, 2]
    assert [step.role_id for step in chain] == [manager_role.role_id, accountant_role.role_id]
    assert all(step.decision == "pending" for step in chain)


def test_recalculate_totals_uses_usd_base_amounts_for_mxn_and_dop_lines(chain_setup):
    """Report totals are consolidated from USD base amounts, never original line currencies."""
    db = chain_setup["db"]
    report = chain_setup["report"]
    report.currency = "MXN"
    db.add(report)
    db.add_all(
        [
            ExpenseReportItems(
                report_id=report.report_id,
                currency="MXN",
                amount_original=Decimal("2000.00"),
                fx_rate=Decimal("0.05"),
                amount_base=Decimal("100.00"),
                status="approved",
                approved_amount=Decimal("90.00"),
            ),
            ExpenseReportItems(
                report_id=report.report_id,
                currency="DOP",
                amount_original=Decimal("5000.00"),
                fx_rate=Decimal("0.02"),
                amount_base=Decimal("100.00"),
                status="pending",
            ),
        ]
    )
    db.commit()

    approvals.recalculate_totals(db, report)

    assert report.total_requested == Decimal("200.00")
    assert report.total_approved == Decimal("90.00")


# --- Who may act ------------------------------------------------------------


def test_manager_can_review_level_one(chain_setup):
    assert approvals.can_review(
        chain_setup["db"], chain_setup["report"], chain_setup["manager"], PLAIN_PERMISSIONS
    )


def test_accountant_cannot_review_before_level_one_is_done(chain_setup):
    """Level 2 does not open until level 1 has decided."""
    assert not approvals.can_review(
        chain_setup["db"], chain_setup["report"], chain_setup["accountant"], PLAIN_PERMISSIONS
    )


def test_accountant_can_review_once_level_one_is_approved(chain_setup):
    db = chain_setup["db"]
    step = approvals.current_step(db, chain_setup["report"])
    step.decision = "approved"
    step.approver_id = chain_setup["manager"].employee_id
    db.add(step)
    db.commit()

    assert approvals.can_review(db, chain_setup["report"], chain_setup["accountant"], PLAIN_PERMISSIONS)


# --- Separation of duty -----------------------------------------------------


def test_requester_cannot_review_own_report(chain_setup):
    assert not approvals.can_review(
        chain_setup["db"], chain_setup["report"], chain_setup["requester"], PLAIN_PERMISSIONS
    )


def test_admin_cannot_review_own_report(chain_setup):
    """Admin rights are a wildcard for other people's reports, never your own."""
    assert not approvals.can_review(
        chain_setup["db"], chain_setup["report"], chain_setup["requester"], ADMIN_PERMISSIONS
    )


def test_same_person_cannot_approve_both_levels(chain_setup):
    """An admin who stands in for the manager cannot also sign as accountant."""
    db = chain_setup["db"]
    stand_in = chain_setup["accountant"]

    step = approvals.current_step(db, chain_setup["report"])
    step.decision = "approved"
    step.approver_id = stand_in.employee_id
    db.add(step)
    db.commit()

    assert approvals.has_already_decided(db, chain_setup["report"], stand_in.employee_id)
    assert not approvals.can_review(db, chain_setup["report"], stand_in, ADMIN_PERMISSIONS)


def test_a_different_accountant_can_still_close_the_chain(chain_setup):
    """Blocking one person must not deadlock the report."""
    db = chain_setup["db"]
    first = chain_setup["accountant"]
    second = _employee(db, "Second", "second@primefire.us")
    _assign(db, second, chain_setup["accountant_role"])

    step = approvals.current_step(db, chain_setup["report"])
    step.decision = "approved"
    step.approver_id = first.employee_id
    db.add(step)
    db.commit()

    assert not approvals.can_review(db, chain_setup["report"], first, PLAIN_PERMISSIONS)
    assert approvals.can_review(db, chain_setup["report"], second, PLAIN_PERMISSIONS)


def test_unrelated_role_cannot_review(chain_setup):
    db = chain_setup["db"]
    outsider = _employee(db, "Outsider", "outsider@primefire.us")
    _assign(db, outsider, _role(db, "Technician"))

    assert not approvals.can_review(db, chain_setup["report"], outsider, PLAIN_PERMISSIONS)


# --- Approver visibility ----------------------------------------------------


def test_approver_sees_reports_waiting_on_their_role(chain_setup):
    """The list endpoint relies on this: an invisible queue is a stalled queue."""
    db = chain_setup["db"]
    visible = approvals.reviewable_report_ids(db, chain_setup["manager"])

    assert chain_setup["report"].report_id in visible


def test_accountant_does_not_see_the_report_while_level_one_is_pending(chain_setup):
    db = chain_setup["db"]
    visible = approvals.reviewable_report_ids(db, chain_setup["accountant"])

    assert chain_setup["report"].report_id not in visible


def test_employee_without_roles_sees_no_queue(chain_setup):
    db = chain_setup["db"]

    assert approvals.reviewable_report_ids(db, chain_setup["requester"]) == []
