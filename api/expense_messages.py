"""Per-report message thread.

Mirrors the ticket message pattern. Posting notifies the other side of the
conversation: the employee when an approver writes, the pending approvers when
the employee writes.
"""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlmodel import Session, select

from api.dependencies import (
    get_current_employee,
    get_request_app_url,
    require_module_permission,
)
from bd.dependencies import get_db
from models.employees import Employees
from models.expenses import ExpenseReportMessages, ExpenseReports
from schemas.expenses import ExpenseMessage, ExpenseMessageCreate
from services.expenses import approvals
from services.notifications.expenses import notify_expense_message

router = APIRouter()

MODULE_KEY = "expenses"


def _get_report_or_404(db: Session, report_id: int) -> ExpenseReports:
    report = db.get(ExpenseReports, report_id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense report not found")
    return report


def _assert_participant(
    db: Session, report: ExpenseReports, employee: Employees, user_permissions: dict
) -> None:
    if report.employee_id == employee.employee_id:
        return
    if approvals.has_admin_actions(user_permissions):
        return
    if approvals.can_review(db, report, employee, user_permissions):
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a participant in this report")


@router.get("/reports/{report_id}/messages", response_model=list[ExpenseMessage])
def list_messages(
    report_id: int,
    db: Session = Depends(get_db),
    current_employee: Employees = Depends(get_current_employee),
    user_permissions: dict = Depends(require_module_permission(MODULE_KEY, "can_view")),
):
    report = _get_report_or_404(db, report_id)
    _assert_participant(db, report, current_employee, user_permissions)

    messages = db.exec(
        select(ExpenseReportMessages)
        .where(ExpenseReportMessages.report_id == report_id)
        .order_by(ExpenseReportMessages.created_at)
    ).all()

    authors = {}
    if messages:
        rows = db.exec(
            select(Employees).where(Employees.employee_id.in_({m.user_id for m in messages}))  # type: ignore[attr-defined]
        ).all()
        authors = {row.employee_id: row for row in rows}

    return [
        ExpenseMessage(
            **message.model_dump(),
            user_name=(authors[message.user_id].display_name if message.user_id in authors else None),
            user_email=(authors[message.user_id].email if message.user_id in authors else None),
        )
        for message in messages
    ]


@router.post("/reports/{report_id}/messages", response_model=ExpenseMessage)
def create_message(
    report_id: int,
    payload: ExpenseMessageCreate,
    http_request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_employee: Employees = Depends(get_current_employee),
    user_permissions: dict = Depends(require_module_permission(MODULE_KEY, "can_view")),
):
    report = _get_report_or_404(db, report_id)
    _assert_participant(db, report, current_employee, user_permissions)

    text = (payload.message_txt or "").strip()
    if not text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Message cannot be empty")

    message = ExpenseReportMessages(
        report_id=report_id,
        user_id=current_employee.employee_id,
        message_txt=text,
    )
    db.add(message)
    db.commit()
    db.refresh(message)

    app_url = get_request_app_url(http_request)
    recipients: set[str] = set()

    if current_employee.employee_id == report.employee_id:
        step = approvals.current_step(db, report)
        if step:
            recipients.update(email for _name, email in approvals.approver_emails(db, step.role_id))
    else:
        owner = db.get(Employees, report.employee_id)
        if owner and owner.email:
            recipients.add(owner.email)

    for email in recipients:
        if email == current_employee.email:
            continue
        background_tasks.add_task(
            notify_expense_message,
            report_id=report_id,
            folio=report.folio,
            to_email=email,
            author_name=current_employee.display_name or current_employee.email,
            author_email=current_employee.email,
            message_txt=text,
            app_url=app_url,
        )

    return ExpenseMessage(
        **message.model_dump(),
        user_name=current_employee.display_name,
        user_email=current_employee.email,
    )
