"""Amount-tiered approval chain.

On submit the report total selects a band in `expense_approval_rules`, and one
approval row is created per level in that band. Approving level n advances the
report to level n+1; approving the last level closes the chain. A rejection at
any level terminates it immediately.

Holding `admin_actions` on the expenses module bypasses the chain entirely,
matching how Admin already behaves in the inventory approval flow.
"""

import logging
from decimal import Decimal

from sqlmodel import Session, select

from models.employees import EmployeeRoles, Employees, Roles
from models.expenses import ExpenseApprovalRules, ExpenseReportApprovals, ExpenseReportItems, ExpenseReports

logger = logging.getLogger(__name__)

MODULE_KEY = "expenses"


def has_admin_actions(user_permissions: dict) -> bool:
    for perm in user_permissions.get("permissions", []):
        if perm.get("module_key") == MODULE_KEY:
            return bool(perm.get("permissions", {}).get("admin_actions"))
    return False


def rules_for_amount(db: Session, amount: Decimal) -> list[ExpenseApprovalRules]:
    """Active rules whose band contains `amount`, ordered by level."""
    rules = db.exec(select(ExpenseApprovalRules).where(ExpenseApprovalRules.is_active == True)).all()  # noqa: E712

    matching = [
        rule
        for rule in rules
        if rule.min_amount <= amount and (rule.max_amount is None or amount <= rule.max_amount)
    ]
    matching.sort(key=lambda rule: rule.level)
    return matching


def build_chain(db: Session, report: ExpenseReports) -> list[ExpenseReportApprovals]:
    """Create the approval rows for a freshly submitted report.

    With no rule configured the report still needs a decision, so a single
    level-1 approval with no role restriction is created and anyone holding
    `admin_actions` can act on it.
    """
    existing = db.exec(
        select(ExpenseReportApprovals).where(ExpenseReportApprovals.report_id == report.report_id)
    ).all()
    for row in existing:
        db.delete(row)

    rules = rules_for_amount(db, report.total_requested)

    if not rules:
        chain = [ExpenseReportApprovals(report_id=report.report_id, level=1, role_id=None)]
    else:
        chain = [
            ExpenseReportApprovals(report_id=report.report_id, level=rule.level, role_id=rule.role_id)
            for rule in rules
        ]

    for row in chain:
        db.add(row)

    return chain


def has_already_decided(db: Session, report: ExpenseReports, employee_id: int) -> bool:
    """True when this employee already decided one of the report's levels."""
    decided = db.exec(
        select(ExpenseReportApprovals.approver_id)
        .where(ExpenseReportApprovals.report_id == report.report_id)
        .where(ExpenseReportApprovals.decision != "pending")
    ).all()
    return employee_id in decided


def employee_role_ids(db: Session, employee_id: int) -> list[int]:
    return db.exec(select(EmployeeRoles.role_id).where(EmployeeRoles.employee_id == employee_id)).all()


def can_review(db: Session, report: ExpenseReports, employee: Employees, user_permissions: dict) -> bool:
    """True when this employee may act on the report's current level.

    The two separation-of-duty rules below are checked before the admin
    override on purpose: a chain with two levels only means something if two
    different people sign it, and nobody approves their own money.
    """
    # Nobody signs off on their own claim, administrators included.
    if report.employee_id == employee.employee_id:
        return False

    pending = current_step(db, report)
    if pending is None:
        return False

    # One person cannot be both approvers of the same report.
    if has_already_decided(db, report, employee.employee_id):
        return False

    # Admins act as a wildcard so a chain never deadlocks on an absent approver.
    if has_admin_actions(user_permissions):
        return True

    if pending.role_id is None:
        return False

    return pending.role_id in employee_role_ids(db, employee.employee_id)


def reviewable_report_ids(db: Session, employee: Employees) -> list[int]:
    """Reports whose *current* level is assigned to one of this employee's roles.

    Used by the list endpoint so an approver sees the queue they are expected to
    act on, not only their own claims. Only the lowest pending level counts: a
    level-2 approver has no business seeing a report still sitting at level 1.
    """
    role_ids = set(employee_role_ids(db, employee.employee_id))
    if not role_ids:
        return []

    pending = db.exec(
        select(ExpenseReportApprovals).where(ExpenseReportApprovals.decision == "pending")
    ).all()

    current_by_report: dict[int, ExpenseReportApprovals] = {}
    for step in pending:
        held = current_by_report.get(step.report_id)
        if held is None or step.level < held.level:
            current_by_report[step.report_id] = step

    return [
        report_id
        for report_id, step in current_by_report.items()
        if step.role_id is not None and step.role_id in role_ids
    ]


def current_step(db: Session, report: ExpenseReports) -> ExpenseReportApprovals | None:
    """The approval row waiting on a decision, if any."""
    steps = db.exec(
        select(ExpenseReportApprovals)
        .where(ExpenseReportApprovals.report_id == report.report_id)
        .where(ExpenseReportApprovals.decision == "pending")
    ).all()
    if not steps:
        return None
    return min(steps, key=lambda step: step.level)


def next_level(db: Session, report: ExpenseReports, after_level: int) -> int | None:
    """Level that follows `after_level`, or None when the chain is complete."""
    levels = db.exec(
        select(ExpenseReportApprovals.level)
        .where(ExpenseReportApprovals.report_id == report.report_id)
        .where(ExpenseReportApprovals.decision == "pending")
    ).all()
    remaining = sorted(level for level in levels if level > after_level)
    return remaining[0] if remaining else None


def recalculate_totals(db: Session, report: ExpenseReports) -> None:
    """Refresh requested and approved totals from the report's lines."""
    items = db.exec(select(ExpenseReportItems).where(ExpenseReportItems.report_id == report.report_id)).all()

    report.total_requested = sum((item.amount_base for item in items), Decimal(0))
    report.total_approved = sum(
        (
            (item.approved_amount if item.approved_amount is not None else item.amount_base)
            for item in items
            if item.status == "approved"
        ),
        Decimal(0),
    )


def settle_status(db: Session, report: ExpenseReports) -> str:
    """Final status once the last level has approved.

    Any rejected line, or any line approved for less than it claimed, makes the
    whole report partially approved rather than approved.
    """
    items = db.exec(select(ExpenseReportItems).where(ExpenseReportItems.report_id == report.report_id)).all()
    if not items:
        return "approved"

    if any(item.status == "rejected" for item in items):
        return "partially_approved"
    if any(
        item.approved_amount is not None and item.approved_amount < item.amount_base
        for item in items
    ):
        return "partially_approved"
    return "approved"


def approver_emails(db: Session, role_id: int | None) -> list[tuple[str, str]]:
    """(display_name, email) for everyone who can act on a level."""
    if role_id is None:
        return []

    employee_ids = db.exec(select(EmployeeRoles.employee_id).where(EmployeeRoles.role_id == role_id)).all()
    if not employee_ids:
        return []

    employees = db.exec(select(Employees).where(Employees.employee_id.in_(employee_ids))).all()  # type: ignore[attr-defined]
    return [(emp.display_name or emp.email, emp.email) for emp in employees if emp.email]


def role_name(db: Session, role_id: int | None) -> str | None:
    if role_id is None:
        return None
    role = db.get(Roles, role_id)
    return role.role_name if role else None
