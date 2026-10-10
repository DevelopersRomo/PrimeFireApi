from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from api.dependencies import get_current_employee
from main import app
from models.employees import Employees
from models.ticket_messages import TicketAttachments, TicketMessages
from models.tickets import TicketStatus, Tickets
from tests.conftest import create_test_record


@pytest.fixture
def current_employee(db_session: Session):
    emp = create_test_record(
        db_session, Employees, email="test@example.com", first_name="Test", last_name="User", display_name="Test User"
    )
    db_session.commit()
    return emp


@pytest.fixture
def test_ticket(db_session: Session, current_employee: Employees):
    ticket = create_test_record(
        db_session,
        Tickets,
        title="Test Ticket",
        description="Desc",
        status=TicketStatus.TODO,
        created_by=current_employee.employee_id,
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
        payload = {"message_txt": "This is a test message", "ticket_id": test_ticket.ticket_id}

        response = client.post(f"/tickets/{test_ticket.ticket_id}/messages", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["message_txt"] == "This is a test message"
        assert data["ticket_id"] == test_ticket.ticket_id

        mock_notify.assert_called_once()


def test_ticket_message_routes_enforce_visibility_scope(
    client: TestClient,
    auth_headers: dict,
    db_session: Session,
    other_employee: Employees,
    permission_override,
    tmp_path,
    monkeypatch,
):
    from api import ticket_attachments
    from models.tickets import TicketPriority

    monkeypatch.setattr(ticket_attachments, "UPLOAD_DIR", tmp_path)

    permission_override("tickets", {"can_view"})
    ticket = create_test_record(
        db_session,
        Tickets,
        title="Out of scope ticket",
        description="Private",
        status=TicketStatus.TODO,
        priority=TicketPriority.LOW,
        created_by=other_employee.employee_id,
        assigned_to=other_employee.employee_id,
    )
    message = create_test_record(
        db_session,
        TicketMessages,
        ticket_id=ticket.ticket_id,
        user_id=other_employee.employee_id,
        message_txt="Private message",
    )
    attachment_path = tmp_path / "private.txt"
    attachment_path.write_bytes(b"private attachment")
    attachment = create_test_record(
        db_session,
        TicketAttachments,
        ticket_id=ticket.ticket_id,
        file_name="private.txt",
        file_type="text/plain",
        file_path=str(attachment_path.relative_to(tmp_path)),
    )
    db_session.commit()

    responses = [
        client.get(f"/tickets/{ticket.ticket_id}/messages", headers=auth_headers),
        client.get(f"/messages/{message.ticket_message_id}", headers=auth_headers),
        client.get(f"/attachments/{attachment.ticket_attachment_id}", headers=auth_headers),
        client.post(
            f"/tickets/{ticket.ticket_id}/messages",
            json={"message_txt": "Attempted reply", "ticket_id": ticket.ticket_id},
            headers=auth_headers,
        ),
        client.patch(
            f"/messages/{message.ticket_message_id}", json={"message_txt": "Changed"}, headers=auth_headers
        ),
        client.delete(f"/messages/{message.ticket_message_id}", headers=auth_headers),
        client.post(
            f"/tickets/{ticket.ticket_id}/attachments",
            files={"file": ("attempt.txt", b"attempt", "text/plain")},
            headers=auth_headers,
        ),
        client.delete(f"/attachments/{attachment.ticket_attachment_id}", headers=auth_headers),
        client.patch(f"/tickets/{ticket.ticket_id}", json={"title": "Changed"}, headers=auth_headers),
        client.post(f"/tickets/{ticket.ticket_id}/stop-recurrence", headers=auth_headers),
        client.delete(f"/tickets/{ticket.ticket_id}", headers=auth_headers),
    ]

    assert [response.status_code for response in responses] == [404] * len(responses)


def test_get_messages_for_ticket(
    client: TestClient,
    auth_headers: dict,
    test_ticket: Tickets,
    current_employee: Employees,
    db_session: Session,
    auth_overrides,
):
    create_test_record(
        db_session,
        TicketMessages,
        ticket_id=test_ticket.ticket_id,
        user_id=current_employee.employee_id,
        message_txt="Message 1",
    )
    create_test_record(
        db_session,
        TicketMessages,
        ticket_id=test_ticket.ticket_id,
        user_id=current_employee.employee_id,
        message_txt="Message 2",
    )
    db_session.commit()

    response = client.get(f"/tickets/{test_ticket.ticket_id}/messages", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    messages = [m["message_txt"] for m in data]
    assert "Message 1" in messages
    assert "Message 2" in messages


def test_get_message(
    client: TestClient,
    auth_headers: dict,
    test_ticket: Tickets,
    current_employee: Employees,
    db_session: Session,
    auth_overrides,
):
    msg = create_test_record(
        db_session,
        TicketMessages,
        ticket_id=test_ticket.ticket_id,
        user_id=current_employee.employee_id,
        message_txt="Single Message",
    )
    db_session.commit()

    response = client.get(f"/messages/{msg.ticket_message_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["message_txt"] == "Single Message"
