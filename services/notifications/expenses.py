"""Expense reimbursement notifications.

Thin wrappers over `send_custom_notification`, one per state transition, so the
API layer only ever passes primitives into `background_tasks.add_task`.
"""

import logging

from services.notifications.notifications import send_custom_notification
from services.notifications.schemas import NotificationField, NotificationResponse

logger = logging.getLogger(__name__)


def _money(amount, currency: str = "USD") -> str:
    return f"${amount:,.2f} {currency}"


def _report_url(app_url: str | None, report_id: int) -> str | None:
    if not app_url:
        return None
    return f"{app_url.rstrip('/')}/expenses/detail/{report_id}"


def _base_fields(
    folio: str,
    employee_name: str,
    total: float,
    currency: str,
    destination: str | None,
    job_name: str | None,
) -> list[NotificationField]:
    fields = [
        NotificationField(label="Folio", value=folio),
        NotificationField(label="Employee", value=employee_name),
        NotificationField(label="Total requested", value=_money(total, currency)),
    ]
    if destination:
        fields.append(NotificationField(label="Destination", value=destination))
    if job_name:
        fields.append(NotificationField(label="Job / Project", value=job_name))
    return fields


async def notify_expense_submitted(
    report_id: int,
    folio: str,
    employee_name: str,
    total: float,
    currency: str,
    to_email: str,
    destination: str | None = None,
    job_name: str | None = None,
    level: int = 1,
    app_url: str | None = None,
) -> NotificationResponse:
    """Tell an approver a report is waiting on them."""
    return await send_custom_notification(
        title="Expense report awaiting your approval",
        sub_title=f"{folio} - {employee_name}",
        message_body=(
            f"{employee_name} submitted an expense report for "
            f"{_money(total, currency)}. It is waiting for your approval at level {level}."
        ),
        action_type="submitted",
        to_email=to_email,
        fields=_base_fields(folio, employee_name, total, currency, destination, job_name),
        action_url=_report_url(app_url, report_id),
        action_text="Review report",
    )


async def notify_expense_approved(
    report_id: int,
    folio: str,
    employee_name: str,
    total_approved: float,
    currency: str,
    to_email: str,
    reviewed_by_name: str | None = None,
    reviewed_by_email: str | None = None,
    note: str | None = None,
    app_url: str | None = None,
) -> NotificationResponse:
    fields = [
        NotificationField(label="Folio", value=folio),
        NotificationField(label="Approved amount", value=_money(total_approved, currency)),
    ]
    if note:
        fields.append(NotificationField(label="Note", value=note))

    return await send_custom_notification(
        title="Your expense report was approved",
        sub_title=folio,
        message_body=(
            f"Your expense report {folio} was approved for {_money(total_approved, currency)}. "
            "Finance will process the reimbursement."
        ),
        action_type="approved",
        to_email=to_email,
        performed_by_name=reviewed_by_name,
        performed_by_email=reviewed_by_email,
        fields=fields,
        action_url=_report_url(app_url, report_id),
        action_text="View report",
    )


async def notify_expense_partially_approved(
    report_id: int,
    folio: str,
    employee_name: str,
    total_requested: float,
    total_approved: float,
    currency: str,
    to_email: str,
    reviewed_by_name: str | None = None,
    reviewed_by_email: str | None = None,
    note: str | None = None,
    rejected_lines: int = 0,
    app_url: str | None = None,
) -> NotificationResponse:
    """A partial approval always carries the reason: the employee is owed one."""
    fields = [
        NotificationField(label="Folio", value=folio),
        NotificationField(label="Requested", value=_money(total_requested, currency)),
        NotificationField(label="Approved", value=_money(total_approved, currency)),
    ]
    if rejected_lines:
        fields.append(NotificationField(label="Lines not approved", value=str(rejected_lines)))
    if note:
        fields.append(NotificationField(label="Reason", value=note))

    return await send_custom_notification(
        title="Your expense report was partially approved",
        sub_title=folio,
        message_body=(
            f"Your expense report {folio} was approved for {_money(total_approved, currency)} "
            f"out of the {_money(total_requested, currency)} claimed. "
            "Open the report to see the reason for each line."
        ),
        action_type="pending",
        to_email=to_email,
        performed_by_name=reviewed_by_name,
        performed_by_email=reviewed_by_email,
        fields=fields,
        action_url=_report_url(app_url, report_id),
        action_text="View details",
    )


async def notify_expense_rejected(
    report_id: int,
    folio: str,
    employee_name: str,
    total: float,
    currency: str,
    to_email: str,
    reviewed_by_name: str | None = None,
    reviewed_by_email: str | None = None,
    note: str | None = None,
    app_url: str | None = None,
) -> NotificationResponse:
    fields = [
        NotificationField(label="Folio", value=folio),
        NotificationField(label="Amount", value=_money(total, currency)),
        NotificationField(label="Reason", value=note or "No reason provided"),
    ]

    return await send_custom_notification(
        title="Your expense report was rejected",
        sub_title=folio,
        message_body=(
            f"Your expense report {folio} for {_money(total, currency)} was rejected. "
            "You can reply in the report thread if you need to discuss it."
        ),
        action_type="rejected",
        to_email=to_email,
        performed_by_name=reviewed_by_name,
        performed_by_email=reviewed_by_email,
        fields=fields,
        action_url=_report_url(app_url, report_id),
        action_text="View report",
    )


async def notify_expense_paid(
    report_id: int,
    folio: str,
    amount: float,
    currency: str,
    to_email: str,
    payment_method: str | None = None,
    reference: str | None = None,
    paid_by_name: str | None = None,
    paid_by_email: str | None = None,
    app_url: str | None = None,
) -> NotificationResponse:
    fields = [
        NotificationField(label="Folio", value=folio),
        NotificationField(label="Reimbursed", value=_money(amount, currency)),
    ]
    if payment_method:
        fields.append(NotificationField(label="Method", value=payment_method))
    if reference:
        fields.append(NotificationField(label="Reference", value=reference))

    return await send_custom_notification(
        title="Your reimbursement was processed",
        sub_title=folio,
        message_body=f"A reimbursement of {_money(amount, currency)} was processed for report {folio}.",
        action_type="approved",
        to_email=to_email,
        performed_by_name=paid_by_name,
        performed_by_email=paid_by_email,
        fields=fields,
        action_url=_report_url(app_url, report_id),
        action_text="View report",
    )


async def notify_expense_message(
    report_id: int,
    folio: str,
    to_email: str,
    author_name: str,
    author_email: str | None,
    message_txt: str,
    app_url: str | None = None,
) -> NotificationResponse:
    preview = message_txt if len(message_txt) <= 400 else f"{message_txt[:400]}..."

    return await send_custom_notification(
        title=f"New message on expense report {folio}",
        sub_title=folio,
        message_body=preview,
        action_type="commented",
        to_email=to_email,
        performed_by_name=author_name,
        performed_by_email=author_email,
        fields=[NotificationField(label="Folio", value=folio)],
        action_url=_report_url(app_url, report_id),
        action_text="Open thread",
    )
