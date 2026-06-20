from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from fastapi import status
from sqlmodel import Session, select

from api.dependencies import get_current_employee, get_current_employee_with_permissions
from main import app
from models.customers import CustomerTypeEnum, Customers
from models.timesheet import (
    TimeSheetPunch,
    TimeSheetPunchStatusEnum,
    TimeSheetSettings,
)


# Set up defaults for overrides
class MockEmployee:
    def __init__(self, employee_id=1, email="john@example.com", first_name="John", last_name="Doe"):
        self.employee_id = employee_id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name


def mock_get_current_employee():
    return MockEmployee()


def mock_get_current_admin_permissions():
    return {
        "employee": {"employee_id": 1, "first_name": "John", "last_name": "Doe"},
        "permissions": [{"module_key": "timesheet", "permissions": {"admin_actions": True}}],
    }


@pytest.fixture(autouse=True)
def setup_dependencies():
    app.dependency_overrides[get_current_employee] = mock_get_current_employee
    app.dependency_overrides[get_current_employee_with_permissions] = mock_get_current_admin_permissions
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def mock_httpx_get():
    with patch("httpx.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "ip": "1.2.3.4",
            "latitude": "10.0",
            "longitude": "20.0",
            "city": "TestCity",
            "state_prov": "TestState",
            "country_name": "TestCountry",
            "time_zone": {"name": "UTC"},
        }
        mock_get.return_value = mock_response
        yield mock_get


@pytest.fixture
def mock_ipgeolocation_settings():
    with patch("api.timesheet.settings.IPGEOLOCATION_API_KEY", "test-api-key"):
        yield mock_httpx_get()


@pytest.fixture
def mock_background_task():
    with patch("api.timesheet.notify_timesheet_hours") as mock_notify:
        mock_notify.return_value = MagicMock(success=True)
        yield mock_notify


@pytest.fixture
def mock_asyncio_run():
    with patch("api.timesheet.asyncio.run") as mock_run:
        mock_run.return_value = MagicMock(success=True)
        yield mock_run


@pytest.fixture
def test_customer(db_session: Session) -> Customers:
    customer = Customers(
        company_name="Test Company",
        first_name="Test",
        last_name="Cust",
        customer_type=CustomerTypeEnum.COMMERCIAL,
        created_by=1,
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return customer


@pytest.fixture
def base_settings(db_session: Session) -> TimeSheetSettings:
    settings = TimeSheetSettings(
        overtime_daily_hours="8.00",
        overtime_weekly_hours="40.00",
        max_overtime_daily_hours="8.00",
        is_active=True,
        created_at=datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
        updated_at=datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
    )
    db_session.add(settings)
    db_session.commit()
    db_session.refresh(settings)
    return settings


def create_punch(
    db_session: Session,
    employee_id: int,
    customer_id: int,
    status: str,
    clock_in: str | None = None,
    clock_out: str | None = None,
    worked_minutes: int = 0,
) -> TimeSheetPunch:
    """Helper to create a TimeSheetPunch with required fields."""
    now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
    punch = TimeSheetPunch(
        employee_id=employee_id,
        customer_id=customer_id,
        status=status,
        clock_in_at=clock_in or now,
        clock_out_at=clock_out,
        worked_minutes=worked_minutes,
        created_at=now,
        updated_at=now,
    )
    db_session.add(punch)
    db_session.commit()
    db_session.refresh(punch)
    return punch


# --- Tests ---


def test_clock_in(client, db_session: Session, test_customer, base_settings, mock_httpx_get, mock_asyncio_run):
    payload = {
        "customer_id": test_customer.customer_id,
        "note": "Starting work",
        "use_location": True,
        "latitude": "11.1",
        "longitude": "22.2",
        "gps_accuracy": "10m",
    }

    response = client.post("/api/v1/timesheet/clock-in", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["status"] == TimeSheetPunchStatusEnum.OPEN.value
    assert data["note"] == "Starting work"

    # Verify db
    punch = db_session.exec(select(TimeSheetPunch).where(TimeSheetPunch.punch_id == data["punch_id"])).first()
    assert punch is not None
    assert punch.clock_out_at is None

    # Try to clock in again should fail due to conflict
    response = client.post("/api/v1/timesheet/clock-in", json=payload)
    assert response.status_code == status.HTTP_409_CONFLICT


def test_clock_out(client, db_session: Session, test_customer, base_settings, mock_httpx_get):
    # Setup open punch
    create_punch(db_session, 1, test_customer.customer_id, TimeSheetPunchStatusEnum.OPEN.value, "2023-01-01 08:00:00")

    payload = {"note": "Done for the day", "use_location": False}

    response = client.post("/api/v1/timesheet/clock-out", json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == TimeSheetPunchStatusEnum.CLOSED.value
    assert data["note"] == "Done for the day"
    assert data["clock_out_at"] is not None


def test_list_timesheet(client, db_session: Session, test_customer, base_settings):
    create_punch(
        db_session,
        1,
        test_customer.customer_id,
        TimeSheetPunchStatusEnum.CLOSED.value,
        "2023-01-01 08:00:00",
        "2023-01-01 16:00:00",
        480,
    )

    response = client.get("/api/v1/timesheet?view=month&start_date=2023-01-01&end_date=2023-01-31")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "totals" in data
    assert data["totals"]["total_hours"] == 8.0


def test_get_open_punch(client, db_session: Session, test_customer):
    response = client.get("/api/v1/timesheet/open")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["punch"] is None

    create_punch(db_session, 1, test_customer.customer_id, TimeSheetPunchStatusEnum.OPEN.value, "2023-01-01 08:00:00")

    response = client.get("/api/v1/timesheet/open")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["punch"]["punch_id"] is not None


def test_export_timesheet(client, db_session: Session, test_customer):
    response = client.get("/api/v1/timesheet/export?view=week&start_date=2023-01-01&end_date=2023-01-07")
    assert response.status_code == status.HTTP_200_OK
    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in response.headers["content-type"]


def test_get_location(client, db_session: Session, mock_httpx_get):
    # Mock the API key so the ipgeolocation call is made
    with patch("api.timesheet.settings") as mock_settings:
        mock_settings.IPGEOLOCATION_API_KEY = "test-api-key"
        response = client.get("/api/v1/timesheet/location")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["ip_address"] == "1.2.3.4"
        assert data["city"] == "TestCity"


def test_admin_list_punches(client, db_session: Session, test_customer):
    create_punch(
        db_session,
        2,
        test_customer.customer_id,
        TimeSheetPunchStatusEnum.CLOSED.value,
        "2023-01-01 08:00:00",
        "2023-01-01 16:00:00",
        480,
    )

    response = client.get("/api/v1/timesheet/admin?employee_id=2")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["employee_id"] == 2


def test_admin_export_punches(client, db_session: Session):
    response = client.get("/api/v1/timesheet/admin/export?start_date=2023-01-01&end_date=2023-01-07")
    assert response.status_code == status.HTTP_200_OK
    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in response.headers["content-type"]


def test_update_punch(client, db_session: Session, test_customer):
    punch = create_punch(
        db_session,
        1,
        test_customer.customer_id,
        TimeSheetPunchStatusEnum.CLOSED.value,
        "2023-01-01 08:00:00",
        "2023-01-01 16:00:00",
        480,
    )

    payload = {"note": "Updated Note"}

    response = client.patch(f"/api/v1/timesheet/{punch.punch_id}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["note"] == "Updated Note"


def test_update_punch_converts_timezone_to_utc(client, db_session: Session, test_customer):
    punch = create_punch(
        db_session,
        1,
        test_customer.customer_id,
        TimeSheetPunchStatusEnum.CLOSED.value,
        "2023-01-01 08:00:00",
        "2023-01-01 16:00:00",
        480,
    )

    # Admin in America/Mexico_City (UTC-6) submits local times with offset
    payload = {
        "clock_in_at": "2023-01-01T02:00:00-06:00",
        "clock_out_at": "2023-01-01T10:00:00-06:00",
    }

    response = client.patch(
        f"/api/v1/timesheet/{punch.punch_id}",
        json=payload,
        headers={"X-Timezone": "America/Mexico_City"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["clock_in_at"] == "2023-01-01 08:00:00"
    assert data["clock_out_at"] == "2023-01-01 16:00:00"


def test_approve_reject_punch(client, db_session: Session, test_customer):
    punch = create_punch(
        db_session,
        2,
        test_customer.customer_id,
        TimeSheetPunchStatusEnum.CLOSED.value,
        "2023-01-01 08:00:00",
        "2023-01-01 16:00:00",
    )

    response = client.post(f"/api/v1/timesheet/{punch.punch_id}/approve")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == TimeSheetPunchStatusEnum.APPROVED.value
    assert response.json()["approved_by"] == 1

    response = client.post(f"/api/v1/timesheet/{punch.punch_id}/reject")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == TimeSheetPunchStatusEnum.REJECTED.value


def test_check_notifications(client, db_session: Session, test_customer):
    response = client.get("/api/v1/timesheet/notifications/check")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["has_open_punch"] is False

    now_dt = datetime.now(UTC)
    past_dt = now_dt - timedelta(hours=9)
    create_punch(
        db_session,
        1,
        test_customer.customer_id,
        TimeSheetPunchStatusEnum.OPEN.value,
        past_dt.strftime("%Y-%m-%d %H:%M:%S"),
    )

    response = client.get("/api/v1/timesheet/notifications/check")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["has_open_punch"] is True
    assert response.json()["should_notify_regular"] is True


def test_clock_out_auto(client, db_session: Session, test_customer, mock_asyncio_run):
    now_dt = datetime.now(UTC)
    past_dt = now_dt - timedelta(hours=17)
    create_punch(
        db_session,
        1,
        test_customer.customer_id,
        TimeSheetPunchStatusEnum.OPEN.value,
        past_dt.strftime("%Y-%m-%d %H:%M:%S"),
    )

    response = client.post("/api/v1/timesheet/clock-out-auto")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == TimeSheetPunchStatusEnum.CLOSED.value
    assert data["clock_out_at"] is not None


def test_notify_hours(client, db_session: Session, test_customer, mock_asyncio_run):
    from models.employees import Employees

    # Create employee record for the mock employee
    emp = Employees(employee_id=1, first_name="John", last_name="Doe", email="john@example.com")
    db_session.add(emp)
    db_session.commit()

    create_punch(db_session, 1, test_customer.customer_id, TimeSheetPunchStatusEnum.OPEN.value, "2023-01-01 08:00:00")

    # Patch asyncio.run to return success
    with patch("api.timesheet.asyncio.run") as mock_run:
        mock_result = MagicMock()
        mock_result.success = True
        mock_run.return_value = mock_result

        response = client.post("/api/v1/timesheet/notify-hours?notification_type=regular")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["success"] is True