from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from models.employees import Employees
from models.tickets import TicketPriority, TicketRecurrenceConfig, TicketRecurrenceType, TicketStatus, Tickets
from tests.conftest import create_test_record


# Fixtures (current_employee, other_employee, auth_overrides) are defined in conftest.py
# They are automatically injected by pytest — no import needed.
current_employee: Employees
other_employee: Employees


def test_create_ticket(
    client: TestClient, auth_headers: dict, current_employee: Employees, other_employee: Employees, auth_overrides
):
    with patch("api.tickets.notify_ticket_created") as mock_notify:
        payload = {
            "title": "Test Ticket",
            "description": "This is a test ticket",
            "status": "todo",
            "priority": "high",
            "sla": "24h",
            "assigned_to": other_employee.employee_id,
        }

        response = client.post("/tickets", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Ticket"
        assert data["status"] == "todo"
        assert data["priority"] == "high"
        assert data["sla"] == "24h"
        assert data["created_by"] == current_employee.employee_id
        assert data["assigned_to"] == other_employee.employee_id

        mock_notify.assert_called_once()


def test_get_tickets(
    client: TestClient, auth_headers: dict, current_employee: Employees, db_session: Session, auth_overrides
):
    create_test_record(
        db_session,
        Tickets,
        title="Test Ticket 1",
        description="Desc 1",
        status=TicketStatus.TODO,
        priority=TicketPriority.LOW,
        created_by=current_employee.employee_id,
    )
    create_test_record(
        db_session,
        Tickets,
        title="Test Ticket 2",
        description="Desc 2",
        status=TicketStatus.DONE,
        priority=TicketPriority.HIGH,
        created_by=current_employee.employee_id,
    )
    db_session.commit()

    response = client.get("/tickets", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2

    # test filtering
    response = client.get("/tickets?status=done", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert all(t["status"] == "done" for t in data)


def test_get_ticket(
    client: TestClient, auth_headers: dict, current_employee: Employees, db_session: Session, auth_overrides
):
    ticket = create_test_record(
        db_session, Tickets, title="Test Ticket", status=TicketStatus.TODO, created_by=current_employee.employee_id
    )
    db_session.commit()

    response = client.get(f"/tickets/{ticket.ticket_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Ticket"


def test_update_ticket(
    client: TestClient,
    auth_headers: dict,
    current_employee: Employees,
    other_employee: Employees,
    db_session: Session,
    auth_overrides,
):
    with patch("api.tickets.send_ticket_assigned_notification") as mock_notify:
        ticket = create_test_record(
            db_session, Tickets, title="Test Ticket", status=TicketStatus.TODO, created_by=current_employee.employee_id
        )
        db_session.commit()

        payload = {"status": "in_progress", "assigned_to": other_employee.employee_id}

        response = client.patch(f"/tickets/{ticket.ticket_id}", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "in_progress"
        assert data["assigned_to"] == other_employee.employee_id

        mock_notify.assert_called_once()


def test_delete_ticket(
    client: TestClient, auth_headers: dict, current_employee: Employees, db_session: Session, auth_overrides
):
    ticket = create_test_record(
        db_session, Tickets, title="Test Ticket", status=TicketStatus.TODO, created_by=current_employee.employee_id
    )
    db_session.commit()

    response = client.delete(f"/tickets/{ticket.ticket_id}", headers=auth_headers)
    assert response.status_code == 200

    response = client.get(f"/tickets/{ticket.ticket_id}", headers=auth_headers)
    assert response.status_code == 404


# =============================================================================
# Recurrence Tests
# =============================================================================


def test_create_ticket_with_recurrence(
    client: TestClient,
    auth_headers: dict,
    current_employee: Employees,
    other_employee: Employees,
    db_session: Session,
    auth_overrides,
):
    """Creating a ticket with recurrence_type should create a TicketRecurrenceConfig."""
    with patch("api.tickets.notify_ticket_created"):
        payload = {
            "title": "Recurring Ticket",
            "description": "Test recurring ticket",
            "status": "todo",
            "priority": "high",
            "recurrence_type": "weekly",
            "assigned_to": other_employee.employee_id,
        }

        response = client.post("/tickets", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["recurrence_type"] == "weekly"

        # Verify config was created in DB
        config = db_session.exec(
            select(TicketRecurrenceConfig).filter(TicketRecurrenceConfig.ticket_id == data["ticket_id"])
        ).first()
        assert config is not None
        assert config.recurrence_type == TicketRecurrenceType.WEEKLY
        assert config.is_active is True
        assert config.next_occurrence is not None


def test_create_ticket_without_recurrence(
    client: TestClient,
    auth_headers: dict,
    current_employee: Employees,
    other_employee: Employees,
    db_session: Session,
    auth_overrides,
):
    """Creating a ticket without recurrence_type should NOT create a TicketRecurrenceConfig."""
    with patch("api.tickets.notify_ticket_created"):
        payload = {
            "title": "Normal Ticket",
            "description": "No recurrence",
            "status": "todo",
            "priority": "low",
            "assigned_to": other_employee.employee_id,
        }

        response = client.post("/tickets", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["recurrence_type"] is None

        # Verify no config was created
        config = db_session.exec(
            select(TicketRecurrenceConfig).filter(TicketRecurrenceConfig.ticket_id == data["ticket_id"])
        ).first()
        assert config is None


def test_update_ticket_recurrence_type(
    client: TestClient,
    auth_headers: dict,
    current_employee: Employees,
    db_session: Session,
    auth_overrides,
):
    """Updating recurrence_type on an existing ticket should create/update the config."""
    ticket = create_test_record(
        db_session,
        Tickets,
        title="Test Ticket",
        status=TicketStatus.TODO,
        created_by=current_employee.employee_id,
    )
    db_session.commit()

    # Update with recurrence
    payload = {"recurrence_type": "monthly"}
    response = client.patch(f"/tickets/{ticket.ticket_id}", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["recurrence_type"] == "monthly"

    db_session.expire_all()  # Force re-fetch so we see DB state, not identity-map cache
    config = db_session.exec(
        select(TicketRecurrenceConfig).filter(TicketRecurrenceConfig.ticket_id == ticket.ticket_id)
    ).first()
    assert config is not None
    assert config.recurrence_type == TicketRecurrenceType.MONTHLY

    # Update recurrence type
    payload = {"recurrence_type": "biweekly"}
    response = client.patch(f"/tickets/{ticket.ticket_id}", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["recurrence_type"] == "biweekly"

    db_session.expire_all()  # Force re-fetch after second update
    config = db_session.exec(
        select(TicketRecurrenceConfig).filter(TicketRecurrenceConfig.ticket_id == ticket.ticket_id)
    ).first()
    assert config is not None
    assert config.recurrence_type == TicketRecurrenceType.BIWEEKLY


def test_update_recurrence_type_to_none_deletes_config(
    client: TestClient,
    auth_headers: dict,
    current_employee: Employees,
    db_session: Session,
    auth_overrides,
):
    """Setting recurrence_type to 'none' should DELETE the TicketRecurrenceConfig."""
    ticket = create_test_record(
        db_session,
        Tickets,
        title="Test Ticket",
        status=TicketStatus.TODO,
        created_by=current_employee.employee_id,
    )
    db_session.commit()

    # First add recurrence
    client.patch(f"/tickets/{ticket.ticket_id}", json={"recurrence_type": "weekly"}, headers=auth_headers)

    config = db_session.exec(
        select(TicketRecurrenceConfig).filter(TicketRecurrenceConfig.ticket_id == ticket.ticket_id)
    ).first()
    assert config is not None

    # Now clear recurrence
    response = client.patch(f"/tickets/{ticket.ticket_id}", json={"recurrence_type": "none"}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["recurrence_type"] is None

    config = db_session.exec(
        select(TicketRecurrenceConfig).filter(TicketRecurrenceConfig.ticket_id == ticket.ticket_id)
    ).first()
    assert config is None  # Deleted, not just inactive


def test_update_status_to_inactive_deletes_recurrence_config(
    client: TestClient,
    auth_headers: dict,
    current_employee: Employees,
    db_session: Session,
    auth_overrides,
):
    """Setting status to 'inactive' should DELETE the TicketRecurrenceConfig."""
    ticket = create_test_record(
        db_session,
        Tickets,
        title="Test Ticket",
        status=TicketStatus.TODO,
        created_by=current_employee.employee_id,
    )
    db_session.commit()

    # First add recurrence
    client.patch(f"/tickets/{ticket.ticket_id}", json={"recurrence_type": "daily"}, headers=auth_headers)

    config = db_session.exec(
        select(TicketRecurrenceConfig).filter(TicketRecurrenceConfig.ticket_id == ticket.ticket_id)
    ).first()
    assert config is not None

    # Now set to inactive
    response = client.patch(
        f"/tickets/{ticket.ticket_id}", json={"status": "inactive", "recurrence_type": "none"}, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "inactive"

    config = db_session.exec(
        select(TicketRecurrenceConfig).filter(TicketRecurrenceConfig.ticket_id == ticket.ticket_id)
    ).first()
    assert config is None  # Deleted


def test_delete_ticket_deletes_recurrence_config(
    client: TestClient,
    auth_headers: dict,
    current_employee: Employees,
    db_session: Session,
    auth_overrides,
):
    """Deleting a ticket should also DELETE its TicketRecurrenceConfig."""
    ticket = create_test_record(
        db_session,
        Tickets,
        title="Test Ticket",
        status=TicketStatus.TODO,
        created_by=current_employee.employee_id,
    )
    db_session.commit()
    ticket_id = ticket.ticket_id

    # First add recurrence
    client.patch(f"/tickets/{ticket_id}", json={"recurrence_type": "yearly"}, headers=auth_headers)

    config = db_session.exec(
        select(TicketRecurrenceConfig).filter(TicketRecurrenceConfig.ticket_id == ticket_id)
    ).first()
    assert config is not None

    # Delete the ticket
    response = client.delete(f"/tickets/{ticket_id}", headers=auth_headers)
    assert response.status_code == 200

    # Config should be gone too
    config = db_session.exec(
        select(TicketRecurrenceConfig).filter(TicketRecurrenceConfig.ticket_id == ticket_id)
    ).first()
    assert config is None


def test_stop_recurrence_endpoint(
    client: TestClient,
    auth_headers: dict,
    current_employee: Employees,
    db_session: Session,
    auth_overrides,
):
    """POST /tickets/{id}/stop-recurrence should delete the recurrence config."""
    ticket = create_test_record(
        db_session,
        Tickets,
        title="Test Ticket",
        status=TicketStatus.TODO,
        created_by=current_employee.employee_id,
    )
    db_session.commit()

    # First add recurrence
    client.patch(f"/tickets/{ticket.ticket_id}", json={"recurrence_type": "weekly"}, headers=auth_headers)

    db_session.expire_all()
    config = db_session.exec(
        select(TicketRecurrenceConfig).filter(TicketRecurrenceConfig.ticket_id == ticket.ticket_id)
    ).first()
    assert config is not None

    # Stop recurrence
    response = client.post(f"/tickets/{ticket.ticket_id}/stop-recurrence", headers=auth_headers)
    assert response.status_code == 200

    db_session.expire_all()  # Force re-fetch after deletion
    config = db_session.exec(
        select(TicketRecurrenceConfig).filter(TicketRecurrenceConfig.ticket_id == ticket.ticket_id)
    ).first()
    assert config is None
