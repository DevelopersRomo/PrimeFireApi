"""Novu in-app notifications.

Novu is optional: with no NOVU_SECRET_KEY every call is a no-op, and a Novu outage is
logged but never breaks the caller (closing a ticket must not fail because of Novu).
"""

import hashlib
import hmac
import logging
from dataclasses import dataclass

from novu_py import Novu, SubscriberPayloadDto, TriggerEventRequestDto

from core.config import settings
from models.employees import Employees

logger = logging.getLogger(__name__)

WORKFLOW_TICKET_CLOSED = "ticket-closed"
WORKFLOW_TICKET_SLA_AT_RISK = "ticket-sla-at-risk"


@dataclass(frozen=True)
class Recipient:
    """Plain copy of the employee fields Novu needs. Triggers run as background tasks, after the
    request's DB session is closed, so ORM instances cannot be passed to them.
    """

    employee_id: int
    email: str | None
    display_name: str | None

    @classmethod
    def from_employee(cls, employee: Employees) -> "Recipient":
        return cls(employee.employee_id, employee.email, employee.display_name)


def is_configured() -> bool:
    return bool(settings.NOVU_SECRET_KEY)


def subscriber_id(db_route: str, employee_id: int) -> str:
    """Novu subscriber for an employee. employee_id is only unique inside one database, so it is
    prefixed with the database route (tenant key, "primefire" or "main").
    """
    return f"{db_route}:{employee_id}"


def subscriber_hash(subscriber: str) -> str:
    """HMAC the Inbox needs so a user cannot open another subscriber's feed."""
    return hmac.new(settings.NOVU_SECRET_KEY.encode(), subscriber.encode(), hashlib.sha256).hexdigest()


def _client() -> Novu:
    # Novu Cloud US region (the SDK default)
    return Novu(secret_key=settings.NOVU_SECRET_KEY)


def trigger(
    workflow_id: str,
    db_route: str,
    recipients: list[Recipient],
    payload: dict,
    transaction_id: str,
) -> bool:
    """Trigger a workflow once per recipient. transaction_id makes retries idempotent in Novu.

    Never raises; returns whether Novu accepted every trigger, so callers can retry later.
    """
    if not is_configured() or not recipients:
        return False

    try:
        with _client() as client:
            for employee in recipients:
                subscriber = subscriber_id(db_route, employee.employee_id)
                client.trigger(
                    trigger_event_request_dto=TriggerEventRequestDto(
                        workflow_id=workflow_id,
                        to=SubscriberPayloadDto(
                            subscriber_id=subscriber,
                            email=employee.email,
                            first_name=employee.display_name,
                        ),
                        payload=payload,
                        transaction_id=f"{transaction_id}:{subscriber}",
                    )
                )
    except Exception:
        logger.exception(f"[NOVU] Failed to trigger {workflow_id} ({transaction_id})")
        return False
    return True
