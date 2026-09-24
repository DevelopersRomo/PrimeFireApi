from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from sqlmodel import Session

from core import ticket_sla_scheduler as sla_job
from core.config import settings
from models.employees import Employees
from models.tenants import Tenants
from models.tickets import TicketSLA, TicketStatus, Tickets
from tests.conftest import create_test_record

NOW = datetime(2026, 3, 10, 12, 0, 0)  # noqa: DTZ001 - DB stores naive UTC


@pytest.fixture
def novu_enabled(monkeypatch):
    monkeypatch.setattr(settings, "NOVU_SECRET_KEY", "test-secret")


def _ticket(db: Session, creator: Employees, **overrides) -> Tickets:
    values = {
        "title": "Printer down",
        "status": TicketStatus.IN_PROGRESS,
        "sla": TicketSLA.HOURS_4,
        "created_by": creator.employee_id,
        "created_at": NOW - timedelta(days=2),  # irrelevant: only active/in_progress time counts
        "sla_running_since": NOW - timedelta(hours=3),  # 75% of a 4h SLA
    }
    values.update(overrides)
    ticket = create_test_record(db, Tickets, **values)
    db.commit()
    return ticket


def test_ticket_past_75_percent_of_sla_is_at_risk(db_session: Session, current_employee: Employees):
    at_risk = _ticket(db_session, current_employee)
    _ticket(db_session, current_employee, title="Too early", sla_running_since=NOW - timedelta(hours=2))

    assert [t.ticket_id for t in sla_job.find_tickets_at_risk(db_session, NOW)] == [at_risk.ticket_id]


@pytest.mark.parametrize(
    "overrides",
    [
        {"status": TicketStatus.TODO, "sla_running_since": None},  # never started: no time counted
        # paused at 90%: the clock is stopped, so it is not about to expire
        {"status": TicketStatus.ON_HOLD, "sla_running_since": None, "sla_elapsed_seconds": int(3.6 * 3600)},
        {"status": TicketStatus.DONE, "sla_running_since": None, "sla_elapsed_seconds": 4 * 3600},  # resolved
        {"sla": None},  # no SLA
        {"sla_warning_sent_at": NOW - timedelta(minutes=5)},  # already warned
    ],
)
def test_tickets_that_cannot_be_at_risk_are_ignored(db_session: Session, current_employee: Employees, overrides):
    _ticket(db_session, current_employee, **overrides)

    assert sla_job.find_tickets_at_risk(db_session, NOW) == []


def test_time_banked_before_a_pause_counts(db_session: Session, current_employee: Employees):
    # 2h worked before an on_hold, running again for 1h: 3h of 4h used
    ticket = _ticket(
        db_session, current_employee, sla_elapsed_seconds=2 * 3600, sla_running_since=NOW - timedelta(hours=1)
    )

    assert sla_job.find_tickets_at_risk(db_session, NOW) == [ticket]


def test_monthly_sla_is_a_30_day_budget(db_session: Session, current_employee: Employees):
    # With pauses the budget must be a fixed duration: 1m = 30 days, 75% = 22.5 days
    ticket = _ticket(db_session, current_employee, sla=TicketSLA.MONTH_1, sla_running_since=NOW - timedelta(days=22.5))

    assert sla_job.find_tickets_at_risk(db_session, NOW) == [ticket]
    assert sla_job.find_tickets_at_risk(db_session, NOW - timedelta(hours=1)) == []


def test_warning_goes_to_assignee_once(
    db_session: Session, current_employee: Employees, other_employee: Employees, novu_enabled
):
    ticket = _ticket(db_session, current_employee, assigned_to=other_employee.employee_id)

    with patch("core.ticket_sla_scheduler.novu.trigger") as trigger:
        assert sla_job.send_sla_warnings(db_session, "clienta", NOW) == 1
        assert sla_job.send_sla_warnings(db_session, "clienta", NOW) == 0

    trigger.assert_called_once()
    workflow_id, db_route, recipients, payload, transaction_id = trigger.call_args.args
    assert (workflow_id, db_route) == ("ticket-sla-at-risk", "clienta")
    assert [r.employee_id for r in recipients] == [other_employee.employee_id]
    assert payload["ticket_id"] == ticket.ticket_id
    assert payload["deadline"] == "2026-03-10T13:00:00Z"
    assert payload["minutes_left"] == 60
    assert payload["time_left"] == "1 hour"
    assert transaction_id == f"ticket-{ticket.ticket_id}-sla-at-risk"
    db_session.refresh(ticket)
    assert ticket.sla_warning_sent_at == NOW


def test_unassigned_ticket_warns_the_creator(db_session: Session, current_employee: Employees, novu_enabled):
    _ticket(db_session, current_employee)

    with patch("core.ticket_sla_scheduler.novu.trigger") as trigger:
        sla_job.send_sla_warnings(db_session, "main", NOW)

    assert [r.employee_id for r in trigger.call_args.args[2]] == [current_employee.employee_id]


def test_nothing_is_marked_while_novu_is_not_configured(
    db_session: Session, current_employee: Employees, monkeypatch
):
    monkeypatch.setattr(settings, "NOVU_SECRET_KEY", "")
    ticket = _ticket(db_session, current_employee)

    assert sla_job.send_sla_warnings(db_session, "main", NOW) == 0
    db_session.refresh(ticket)
    assert ticket.sla_warning_sent_at is None


def test_database_routes_cover_main_primefire_and_active_tenants(db_session: Session):
    create_test_record(db_session, Tenants, name="A", db_connection_key="clienta", is_active=True)
    create_test_record(db_session, Tenants, name="B", db_connection_key="clientb", is_active=False)
    # Same database as the "main" route: must not be scanned (and warned) twice
    create_test_record(db_session, Tenants, name="DevRomo", db_connection_key="MAIN", is_active=True)
    db_session.commit()
    main_engine, primefire_engine, tenant_engine = MagicMock(), MagicMock(), MagicMock()

    with (
        patch.object(sla_job, "main_engine", main_engine),
        patch.object(sla_job, "primefire_engine", primefire_engine),
        patch.object(sla_job.ConnectionManager, "get_engine", return_value=tenant_engine),
    ):
        routes = sla_job.database_routes(db_session)

    assert routes == [("main", main_engine), ("primefire", primefire_engine), ("clienta", tenant_engine)]


@pytest.mark.parametrize(
    ("minutes", "label"),
    [(0, "less than 1 minute"), (45, "45 minutes"), (61, "1 hour 1 minute"), (60 * 42, "1 day 18 hours")],
)
def test_time_left_label(minutes, label):
    assert sla_job.format_time_left(timedelta(minutes=minutes)) == label


def test_ticket_is_not_marked_when_novu_rejects_the_warning(
    db_session: Session, current_employee: Employees, novu_enabled
):
    """If the trigger fails (e.g. workflow not synced yet) the ticket must be retried next run,
    not silently marked as warned."""
    ticket = _ticket(db_session, current_employee)

    with patch("core.ticket_sla_scheduler.novu.trigger", return_value=False):
        assert sla_job.send_sla_warnings(db_session, "main", NOW) == 0

    db_session.refresh(ticket)
    assert ticket.sla_warning_sent_at is None
