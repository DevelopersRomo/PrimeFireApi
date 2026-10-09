from pathlib import Path

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
    def mock_get_current_employee_with_permissions():
        return {
            "employee": {"employee_id": current_employee.employee_id, "email": current_employee.email},
            "permissions": [{"module_key": "tickets", "permissions": {"admin_actions": True}}],
        }

    app.dependency_overrides[get_current_employee_with_permissions] = mock_get_current_employee_with_permissions

    yield
    app.dependency_overrides.pop(get_current_employee_with_permissions, None)


def test_create_attachment(client: TestClient, auth_headers: dict, test_ticket: Tickets, auth_overrides):
    files = {"file": ("test.txt", b"hello world", "text/plain")}

    response = client.post(f"/tickets/{test_ticket.ticket_id}/attachments", files=files, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["file_name"] == "test.txt"
    assert data["ticket_id"] == test_ticket.ticket_id


def test_get_attachments_for_ticket(client: TestClient, auth_headers: dict, test_ticket: Tickets, db_session: Session):
    create_test_record(db_session, TicketAttachments, ticket_id=test_ticket.ticket_id, file_name="test1.txt")
    create_test_record(db_session, TicketAttachments, ticket_id=test_ticket.ticket_id, file_name="test2.txt")
    db_session.commit()

    response = client.get(f"/tickets/{test_ticket.ticket_id}/attachments", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    filenames = [a["file_name"] for a in data]
    assert "test1.txt" in filenames
    assert "test2.txt" in filenames


def test_get_attachment(client: TestClient, auth_headers: dict, test_ticket: Tickets, db_session: Session):
    att = create_test_record(db_session, TicketAttachments, ticket_id=test_ticket.ticket_id, file_name="single.txt")
    db_session.commit()

    response = client.get(f"/attachments/{att.ticket_attachment_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["file_name"] == "single.txt"


def test_delete_attachment(
    client: TestClient, auth_headers: dict, test_ticket: Tickets, db_session: Session, auth_overrides
):
    att = create_test_record(db_session, TicketAttachments, ticket_id=test_ticket.ticket_id, file_name="delete_me.txt")
    db_session.commit()

    response = client.delete(f"/attachments/{att.ticket_attachment_id}", headers=auth_headers)
    assert response.status_code == 200

    response = client.get(f"/attachments/{att.ticket_attachment_id}", headers=auth_headers)
    assert response.status_code == 404


MAIN_PY = Path(__file__).resolve().parents[1] / "main.py"


def test_create_attachment_rejects_client_file_path(
    client: TestClient, auth_headers: dict, test_ticket: Tickets, auth_overrides
):
    for file_path in ("../../main.py", str(MAIN_PY)):
        response = client.post(
            f"/tickets/{test_ticket.ticket_id}/attachments",
            data={"file_path": file_path, "file_name": "main.py", "file_type": "text/plain"},
            headers=auth_headers,
        )
        assert response.status_code == 400
        att_id = response.json().get("ticket_attachment_id", 0)
        served = client.get(f"/attachments/{att_id}", headers=auth_headers)
        assert MAIN_PY.read_bytes() not in served.content

    listed = client.get(f"/tickets/{test_ticket.ticket_id}/attachments", headers=auth_headers).json()
    assert listed == []


def test_get_attachment_outside_upload_root_returns_404(
    client: TestClient, auth_headers: dict, test_ticket: Tickets, db_session: Session
):
    for file_path in ("../../main.py", "main.py", str(MAIN_PY)):
        att = create_test_record(
            db_session, TicketAttachments, ticket_id=test_ticket.ticket_id, file_name="main.py", file_path=file_path
        )
        db_session.commit()

        response = client.get(f"/attachments/{att.ticket_attachment_id}", headers=auth_headers)
        assert response.status_code == 404
        assert MAIN_PY.read_bytes() not in response.content


def test_uploaded_attachment_downloads(client: TestClient, auth_headers: dict, test_ticket: Tickets, auth_overrides):
    upload_res = client.post(
        f"/tickets/{test_ticket.ticket_id}/attachments",
        files={"file": ("dl.txt", b"download me", "text/plain")},
        headers=auth_headers,
    )
    response = client.get(f"/attachments/{upload_res.json()['ticket_attachment_id']}", headers=auth_headers)
    assert response.status_code == 200
    assert response.content == b"download me"


def test_delete_attachment_removes_stored_file(
    client: TestClient, auth_headers: dict, test_ticket: Tickets, auth_overrides
):
    upload_res = client.post(
        f"/tickets/{test_ticket.ticket_id}/attachments",
        files={"file": ("gone.txt", b"bye", "text/plain")},
        headers=auth_headers,
    )
    stored = Path(upload_res.json()["file_path"])
    assert stored.exists()

    response = client.delete(f"/attachments/{upload_res.json()['ticket_attachment_id']}", headers=auth_headers)
    assert response.status_code == 200
    assert not stored.exists()


def test_delete_attachment_with_missing_file_succeeds(
    client: TestClient, auth_headers: dict, test_ticket: Tickets, auth_overrides
):
    upload_res = client.post(
        f"/tickets/{test_ticket.ticket_id}/attachments",
        files={"file": ("missing.txt", b"x", "text/plain")},
        headers=auth_headers,
    )
    Path(upload_res.json()["file_path"]).unlink()

    response = client.delete(f"/attachments/{upload_res.json()['ticket_attachment_id']}", headers=auth_headers)
    assert response.status_code == 200


def test_delete_attachment_never_unlinks_outside_upload_root(
    client: TestClient, auth_headers: dict, test_ticket: Tickets, db_session: Session, auth_overrides, tmp_path: Path
):
    outside = tmp_path / "keep.txt"
    outside.write_bytes(b"keep")
    att = create_test_record(
        db_session, TicketAttachments, ticket_id=test_ticket.ticket_id, file_name="keep.txt", file_path=str(outside)
    )
    db_session.commit()

    response = client.delete(f"/attachments/{att.ticket_attachment_id}", headers=auth_headers)
    assert response.status_code == 200
    assert outside.exists()
