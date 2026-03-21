from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from api.dependencies import get_current_employee, get_current_employee_with_permissions
from main import app
from models.employees import Employees
from models.tickets import TicketPriority, TicketStatus, Tickets
from tests.conftest import create_test_record


@pytest.fixture
def current_employee(db_session: Session):
    emp = create_test_record(
        db_session, Employees, email="test@example.com", first_name="Test", last_name="User", display_name="Test User"
    )
    db_session.commit()
    return emp


@pytest.fixture
def other_employee(db_session: Session):
    emp = create_test_record(
        db_session, Employees, email="other@example.com", first_name="Other", last_name="User", display_name="Other User"
    )
    db_session.commit()
    return emp


@pytest.fixture
def auth_overrides(current_employee: Employees):
    # Override current employee
    def mock_get_current_employee():
        return current_employee

    # Override employee with permissions
    def mock_get_current_employee_with_permissions():
        return {
            "employee": {"employee_id": current_employee.employee_id, "email": current_employee.email},
            "permissions": [],  # Has no admin_actions by default
        }

    app.dependency_overrides[get_current_employee] = mock_get_current_employee
    app.dependency_overrides[get_current_employee_with_permissions] = mock_get_current_employee_with_permissions
    yield
    app.dependency_overrides.pop(get_current_employee, None)
    app.dependency_overrides.pop(get_current_employee_with_permissions, None)


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
