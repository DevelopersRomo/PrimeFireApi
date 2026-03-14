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
        db_session, Employees, Email="test@example.com", FirstName="Test", LastName="User", DisplayName="Test User"
    )
    db_session.commit()
    return emp


@pytest.fixture
def other_employee(db_session: Session):
    emp = create_test_record(
        db_session, Employees, Email="other@example.com", FirstName="Other", LastName="User", DisplayName="Other User"
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
            "employee": {"EmployeeId": current_employee.EmployeeId, "Email": current_employee.Email},
            "permissions": [],  # Has no AdminActions by default
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
            "Title": "Test Ticket",
            "Description": "This is a test ticket",
            "Status": "todo",
            "Priority": "high",
            "SLA": "24h",
            "AssignedTo": other_employee.EmployeeId,
        }

        response = client.post("/tickets", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["Title"] == "Test Ticket"
        assert data["Status"] == "todo"
        assert data["Priority"] == "high"
        assert data["SLA"] == "24h"
        assert data["CreatedBy"] == current_employee.EmployeeId
        assert data["AssignedTo"] == other_employee.EmployeeId

        mock_notify.assert_called_once()


def test_get_tickets(
    client: TestClient, auth_headers: dict, current_employee: Employees, db_session: Session, auth_overrides
):
    create_test_record(
        db_session,
        Tickets,
        Title="Test Ticket 1",
        Description="Desc 1",
        Status=TicketStatus.TODO,
        Priority=TicketPriority.LOW,
        CreatedBy=current_employee.EmployeeId,
    )
    create_test_record(
        db_session,
        Tickets,
        Title="Test Ticket 2",
        Description="Desc 2",
        Status=TicketStatus.DONE,
        Priority=TicketPriority.HIGH,
        CreatedBy=current_employee.EmployeeId,
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
    assert all(t["Status"] == "done" for t in data)


def test_get_ticket(
    client: TestClient, auth_headers: dict, current_employee: Employees, db_session: Session, auth_overrides
):
    ticket = create_test_record(
        db_session, Tickets, Title="Test Ticket", Status=TicketStatus.TODO, CreatedBy=current_employee.EmployeeId
    )
    db_session.commit()

    response = client.get(f"/tickets/{ticket.TicketId}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["Title"] == "Test Ticket"


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
            db_session, Tickets, Title="Test Ticket", Status=TicketStatus.TODO, CreatedBy=current_employee.EmployeeId
        )
        db_session.commit()

        payload = {"Status": "in_progress", "AssignedTo": other_employee.EmployeeId}

        response = client.patch(f"/tickets/{ticket.TicketId}", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["Status"] == "in_progress"
        assert data["AssignedTo"] == other_employee.EmployeeId

        mock_notify.assert_called_once()


def test_delete_ticket(
    client: TestClient, auth_headers: dict, current_employee: Employees, db_session: Session, auth_overrides
):
    ticket = create_test_record(
        db_session, Tickets, Title="Test Ticket", Status=TicketStatus.TODO, CreatedBy=current_employee.EmployeeId
    )
    db_session.commit()

    response = client.delete(f"/tickets/{ticket.TicketId}", headers=auth_headers)
    assert response.status_code == 200

    response = client.get(f"/tickets/{ticket.TicketId}", headers=auth_headers)
    assert response.status_code == 404
