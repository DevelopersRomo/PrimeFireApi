import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from api.dependencies import get_current_employee_with_permissions
from main import app
from models.employees import Employees
from models.ticket_messages import TicketAttachments
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
    def mock_get_current_employee_with_permissions():
        return {
            "employee": {"EmployeeId": current_employee.EmployeeId, "Email": current_employee.Email},
            "permissions": [{"module_key": "tickets", "permissions": {"AdminActions": True}}],
        }

    app.dependency_overrides[get_current_employee_with_permissions] = mock_get_current_employee_with_permissions

    yield
    app.dependency_overrides.pop(get_current_employee_with_permissions, None)


def test_create_attachment(client: TestClient, auth_headers: dict, test_ticket: Tickets, auth_overrides):
    files = {"file": ("test.txt", b"hello world", "text/plain")}

    response = client.post(f"/tickets/{test_ticket.TicketId}/attachments", files=files, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["FileName"] == "test.txt"
    assert data["TicketId"] == test_ticket.TicketId


def test_get_attachments_for_ticket(client: TestClient, auth_headers: dict, test_ticket: Tickets, db_session: Session):
    create_test_record(db_session, TicketAttachments, TicketId=test_ticket.TicketId, FileName="test1.txt")
    create_test_record(db_session, TicketAttachments, TicketId=test_ticket.TicketId, FileName="test2.txt")
    db_session.commit()

    response = client.get(f"/tickets/{test_ticket.TicketId}/attachments", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    filenames = [a["FileName"] for a in data]
    assert "test1.txt" in filenames
    assert "test2.txt" in filenames


def test_get_attachment(client: TestClient, auth_headers: dict, test_ticket: Tickets, db_session: Session):
    att = create_test_record(db_session, TicketAttachments, TicketId=test_ticket.TicketId, FileName="single.txt")
    db_session.commit()

    response = client.get(f"/attachments/{att.TicketAttachmentId}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["FileName"] == "single.txt"


def test_delete_attachment(
    client: TestClient, auth_headers: dict, test_ticket: Tickets, db_session: Session, auth_overrides
):
    att = create_test_record(db_session, TicketAttachments, TicketId=test_ticket.TicketId, FileName="delete_me.txt")
    db_session.commit()

    response = client.delete(f"/attachments/{att.TicketAttachmentId}", headers=auth_headers)
    assert response.status_code == 200

    response = client.get(f"/attachments/{att.TicketAttachmentId}", headers=auth_headers)
    assert response.status_code == 404
