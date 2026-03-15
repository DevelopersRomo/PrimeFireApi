from unittest.mock import AsyncMock, patch

import pytest

from api.dependencies import get_current_employee, get_current_employee_with_permissions
from main import app


# Set up defaults for overrides
class MockEmployee:
    def __init__(self, employee_id=1, email="test@example.com", first_name="Test", last_name="User"):
        self.EmployeeId = employee_id
        self.Email = email
        self.FirstName = first_name
        self.LastName = last_name


def mock_get_current_employee():
    return MockEmployee()


def mock_get_current_admin_permissions():
    return {
        "employee": {"EmployeeId": 1, "FirstName": "Test", "LastName": "User"},
        "permissions": [{"module_key": "notifications", "permissions": {"AdminActions": True}}],
    }


@pytest.fixture(autouse=True)
def setup_dependencies():
    app.dependency_overrides[get_current_employee] = mock_get_current_employee
    app.dependency_overrides[get_current_employee_with_permissions] = mock_get_current_admin_permissions
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def mock_send_custom():
    with patch("api.notifications.send_custom_notification", new_callable=AsyncMock) as mock:
        yield mock


@pytest.fixture
def mock_time_off_approved():
    with patch("api.notifications.notify_time_off_approved", new_callable=AsyncMock) as mock:
        yield mock


@pytest.fixture
def mock_ticket_created():
    with patch("api.notifications.notify_ticket_created", new_callable=AsyncMock) as mock:
        yield mock


@pytest.fixture
def mock_contact_primefire():
    with patch("api.notifications.send_contact_primefire_notification", new_callable=AsyncMock) as mock:
        yield mock


def test_send_custom_notification(client, auth_headers, mock_send_custom):
    mock_send_custom.return_value = {"success": True, "message_id": "12345"}

    payload = {
        "notification_type": "custom",
        "custom": {
            "title": "Test Title",
            "message_body": "This is a test notification",
            "to_email": "test@example.com",
        },
    }

    response = client.post("/notifications/send", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message_id"] == "12345"
    mock_send_custom.assert_called_once()


def test_send_time_off_approved(client, auth_headers, mock_time_off_approved):
    mock_time_off_approved.return_value = {"success": True, "message_id": "12345"}

    payload = {
        "notification_type": "time_off_approved",
        "time_off_approved": {
            "request_id": 1,
            "employee_id": 100,
            "employee_name": "Test User",
            "employee_email": "test@example.com",
            "absence_type": "Vacation",
            "start_date": "2026-03-20T00:00:00.000000",
            "end_date": "2026-03-25T00:00:00.000000",
            "total_days": "5.0",
            "total_hours": "40.0",
            "reason": "Family vacation",
            "reviewed_by_name": "Manager",
            "reviewed_by_email": "manager@example.com",
        },
    }

    response = client.post("/notifications/send", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    mock_time_off_approved.assert_called_once()


def test_send_invalid_notification_type(client, auth_headers):
    payload = {"notification_type": "unknown_type"}
    response = client.post("/notifications/send", json=payload, headers=auth_headers)
    # Pydantic returns 422 for invalid enum values, not 400
    assert response.status_code == 422


def test_send_contact_primefire(client):
    from unittest.mock import MagicMock

    # Required fields: name, email, phone
    payload = {
        "name": "John Doe",
        "email": "johndoe@example.com",
        "phone": "1234567890",
        "subject": "Inquiry",
        "message": "Hello PrimeFire",
    }

    # Patch settings token
    with patch("api.notifications.settings.CONTACT_PRIMEFIRE_API_TOKEN", "valid-token"):
        with patch("api.notifications.send_contact_primefire_notification", new_callable=AsyncMock) as mock_contact:
            mock_ret = MagicMock()
            mock_ret.success = True
            mock_ret.message_id = "msg_123"
            mock_contact.return_value = mock_ret

            headers = {"Authorization": "Bearer valid-token"}
            response = client.post("/notifications/send/contact-primefire", json=payload, headers=headers)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["message_id"] == "msg_123"


def test_send_contact_primefire_unauthorized(client):
    # Required fields: name, email, phone
    payload = {
        "name": "John Doe",
        "email": "johndoe@example.com",
        "phone": "1234567890",
        "subject": "Inquiry",
        "message": "Hello PrimeFire",
    }

    # Without valid token
    with patch("api.notifications.settings.CONTACT_PRIMEFIRE_API_TOKEN", "valid-token"):
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.post("/notifications/send/contact-primefire", json=payload, headers=headers)

        assert response.status_code == 401
