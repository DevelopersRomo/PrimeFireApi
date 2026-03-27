"""
Tests for the ticket recurrence scheduler.

The scheduler uses a module-level sync_engine from bd.connection.
These tests patch that engine to use the test database so they run
without a real SQL Server connection.
"""

from datetime import timedelta, timezone
from datetime import datetime as dt
from unittest.mock import patch

import pytest
from sqlmodel import Session, select

from models.tickets import TicketPriority, TicketRecurrenceConfig, TicketRecurrenceType, TicketStatus, Tickets
from tests.conftest import create_test_record


def _to_naive_utc(value: dt) -> dt:
    """Strip timezone info and convert to naive UTC datetime for SQLite compatibility."""
    if value.tzinfo is not None:
        value = value.replace(tzinfo=None) - value.utcoffset()  # type: ignore[assignment, arg-type]
    return value


@pytest.fixture
def scheduler_engine(db_session: Session):
    """
    Patch the scheduler's sync_engine so it uses the test DB session.

    The scheduler creates its own Session(engine) internally, so we need
    to intercept the engine reference and replace it with the test engine.
    We do this by patching the module-level engine reference.
    """
    global _test_engine

    import core.ticket_recurrence_scheduler as scheduler_module

    # The scheduler uses: from bd.connection import sync_engine as engine
    # So we need to patch it at the module where it's used (scheduler_module)
    with patch.object(scheduler_module, "engine", db_session.bind):
        yield db_session.bind


def _create_recurrence_config(
    db_session: Session,
    ticket_id: int,
    recurrence_type: TicketRecurrenceType,
    next_occurrence_delta: timedelta,
    is_active: bool = True,
) -> TicketRecurrenceConfig:
    """Helper to create a recurrence config with next_occurrence relative to now (naive UTC for SQLite)."""
    config = TicketRecurrenceConfig(
        ticket_id=ticket_id,
        recurrence_type=recurrence_type,
        next_occurrence=dt.utcnow() + next_occurrence_delta,
        is_active=is_active,
    )
    db_session.add(config)
    db_session.commit()
    return config


def test_scheduler_creates_child_ticket_when_due(
    client, auth_headers, current_employee, other_employee, db_session, auth_overrides, scheduler_engine
):
    """When next_occurrence is in the past, scheduler should create a child ticket."""
    from unittest.mock import patch as mock_patch

    from core.ticket_recurrence_scheduler import TicketRecurrenceScheduler

    with mock_patch("api.tickets.notify_ticket_created"):
        # Create parent ticket with recurrence
        payload = {
            "title": "Parent Recurring Ticket",
            "description": "Description",
            "status": "todo",
            "priority": "high",
            "recurrence_type": "weekly",
            "assigned_to": other_employee.employee_id,
        }
        resp = client.post("/tickets", json=payload, headers=auth_headers)
        assert resp.status_code == 200
        parent_id = resp.json()["ticket_id"]

    # Manually set next_occurrence to the past so the scheduler picks it up
    config = db_session.exec(
        select(TicketRecurrenceConfig).filter(TicketRecurrenceConfig.ticket_id == parent_id)
    ).first()
    config.next_occurrence = dt.utcnow() - timedelta(hours=1)
    db_session.commit()

    # Run scheduler
    scheduler = TicketRecurrenceScheduler()
    stats = scheduler.process_recurring_tickets()

    assert stats["processed"] == 1
    assert stats["created"] == 1
    assert stats["skipped"] == 0
    assert stats["errors"] == 0

    # Verify child ticket was created
    child_tickets = db_session.exec(select(Tickets).where(Tickets.ticket_id != parent_id)).all()
    assert len(child_tickets) == 1
    child = child_tickets[0]
    assert child.title == "Parent Recurring Ticket"
    assert child.status == TicketStatus.TODO
    assert child.priority == TicketPriority.HIGH
    assert child.ticket_type == resp.json()["ticket_type"]

    # Verify config was updated with new next_occurrence
    db_session.refresh(config)
    assert _to_naive_utc(config.next_occurrence) > dt.utcnow()
    assert config.parent_ticket_id == child.ticket_id


def test_scheduler_does_not_create_when_not_due(
    client, auth_headers, current_employee, other_employee, db_session, auth_overrides, scheduler_engine
):
    """When next_occurrence is in the future, scheduler should NOT create a child ticket."""
    from unittest.mock import patch as mock_patch

    from core.ticket_recurrence_scheduler import TicketRecurrenceScheduler

    with mock_patch("api.tickets.notify_ticket_created"):
        payload = {
            "title": "Future Ticket",
            "description": "Description",
            "status": "todo",
            "priority": "low",
            "recurrence_type": "daily",
            "assigned_to": other_employee.employee_id,
        }
        resp = client.post("/tickets", json=payload, headers=auth_headers)
        assert resp.status_code == 200

    # next_occurrence is already in the future (next_occurrence = now + 1 day by default)
    # No need to change anything — the scheduler should skip it
    scheduler = TicketRecurrenceScheduler()
    stats = scheduler.process_recurring_tickets()

    assert stats["processed"] == 0
    assert stats["created"] == 0

    # No extra tickets created
    tickets = db_session.exec(select(Tickets)).all()
    assert len(tickets) == 1


def test_scheduler_skips_inactive_config(
    client, auth_headers, current_employee, other_employee, db_session, auth_overrides, scheduler_engine
):
    """When is_active is False, scheduler should skip the config."""
    from unittest.mock import patch as mock_patch

    from core.ticket_recurrence_scheduler import TicketRecurrenceScheduler

    with mock_patch("api.tickets.notify_ticket_created"):
        payload = {
            "title": "Inactive Recurrence Ticket",
            "description": "Description",
            "status": "todo",
            "priority": "normal",
            "recurrence_type": "monthly",
            "assigned_to": other_employee.employee_id,
        }
        resp = client.post("/tickets", json=payload, headers=auth_headers)
        assert resp.status_code == 200

    # Manually set next_occurrence to past AND is_active to False
    config = db_session.exec(
        select(TicketRecurrenceConfig).filter(TicketRecurrenceConfig.ticket_id == resp.json()["ticket_id"])
    ).first()
    config.next_occurrence = dt.utcnow() - timedelta(hours=1)
    config.is_active = False
    db_session.commit()

    scheduler = TicketRecurrenceScheduler()
    stats = scheduler.process_recurring_tickets()

    assert stats["processed"] == 0  # Inactive configs filtered out by query
    assert stats["created"] == 0


def test_scheduler_deactivates_if_parent_closed(
    client, auth_headers, current_employee, other_employee, db_session, auth_overrides, scheduler_engine
):
    """If parent ticket status is closed/done, scheduler should deactivate config (not create child)."""
    from unittest.mock import patch as mock_patch

    from core.ticket_recurrence_scheduler import TicketRecurrenceScheduler

    with mock_patch("api.tickets.notify_ticket_created"):
        payload = {
            "title": "Parent Ticket",
            "description": "Description",
            "status": "todo",
            "priority": "high",
            "recurrence_type": "weekly",
            "assigned_to": other_employee.employee_id,
        }
        resp = client.post("/tickets", json=payload, headers=auth_headers)
        assert resp.status_code == 200
        parent_id = resp.json()["ticket_id"]

    # Set next_occurrence to past
    config = db_session.exec(select(TicketRecurrenceConfig).filter(TicketRecurrenceConfig.ticket_id == parent_id)).first()
    config.next_occurrence = dt.utcnow() - timedelta(hours=1)
    db_session.commit()

    # Close the parent ticket (status = done which exists in the enum but not in UI)
    parent = db_session.exec(select(Tickets).filter(Tickets.ticket_id == parent_id)).first()
    parent.status = TicketStatus.DONE
    db_session.commit()

    scheduler = TicketRecurrenceScheduler()
    stats = scheduler.process_recurring_tickets()

    assert stats["processed"] == 1
    assert stats["created"] == 0
    assert stats["skipped"] == 1

    # Config should be deactivated
    db_session.refresh(config)
    assert config.is_active is False
