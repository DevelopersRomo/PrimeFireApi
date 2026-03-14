from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from api.dependencies import get_current_employee
from main import app
from models.employees import Employees
from models.ticket_messages import TicketMessages
from models.tickets import TicketStatus, Tickets
from tests.conftest import create_test_record


@pytest.fixture
def current_employee(db_session: Session):
    emp = create_test_record(
        db_session, Employees, Email="test@example.com", FirstName="Test", LastName="User", DisplayName="Test User"
    )
    db_session.commit()
    return emp


@pytest.fixture
def test_ticket(db_session: Session, current_employee: Employees):
    ticket = create_test_record(
        db_session,
        Tickets,
        Title="Test Ticket",
        Description="Desc",
        Status=TicketStatus.TODO,
        CreatedBy=current_employee.EmployeeId,
    )
    db_session.commit()
    return ticket


@pytest.fixture
def auth_overrides(current_employee: Employees):
    def mock_get_current_employee():
        return current_employee

    app.dependency_overrides[get_current_employee] = mock_get_current_employee

    yield
    app.dependency_overrides.pop(get_current_employee, None)


def test_create_message(
    client: TestClient, auth_headers: dict, test_ticket: Tickets, current_employee: Employees, auth_overrides
):
    with patch("api.ticket_messages.notify_ticket_message") as mock_notify:
        payload = {"MessageTxt": "This is a test message", "TicketId": test_ticket.TicketId}

        response = client.post(f"/tickets/{test_ticket.TicketId}/messages", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["MessageTxt"] == "This is a test message"
        assert data["TicketId"] == test_ticket.TicketId

        mock_notify.assert_called_once()


def test_get_messages_for_ticket(
    client: TestClient, auth_headers: dict, test_ticket: Tickets, current_employee: Employees, db_session: Session
):
    create_test_record(
        db_session,
        TicketMessages,
        TicketId=test_ticket.TicketId,
        UserId=current_employee.EmployeeId,
        MessageTxt="Message 1",
    )
    create_test_record(
        db_session,
        TicketMessages,
        TicketId=test_ticket.TicketId,
        UserId=current_employee.EmployeeId,
        MessageTxt="Message 2",
    )
    db_session.commit()

    response = client.get(f"/tickets/{test_ticket.TicketId}/messages", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    messages = [m["MessageTxt"] for m in data]
    assert "Message 1" in messages
    assert "Message 2" in messages


def test_get_message(
    client: TestClient, auth_headers: dict, test_ticket: Tickets, current_employee: Employees, db_session: Session
):
    msg = create_test_record(
        db_session,
        TicketMessages,
        TicketId=test_ticket.TicketId,
        UserId=current_employee.EmployeeId,
        MessageTxt="Single Message",
    )
    db_session.commit()

    response = client.get(f"/messages/{msg.TicketMessageId}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["MessageTxt"] == "Single Message"
