import csv
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from io import StringIO
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from api.dependencies import (
    get_current_employee,
    get_current_employee_with_permissions,
    require_authentication,
)
from main import app
from models.employees import Employees
from models.time_off import (
    AbsenceTypeEnum,
    Department,
    Holiday,
    RequestStatusEnum,
    TimeOffBalance,
    TimeOffRequest,
    TimeUnitEnum,
)


@pytest.fixture
def emp_manager(db_session: Session):
    emp = Employees(
        email="manager@example.com",
        display_name="Manager User",
    )
    db_session.add(emp)
    db_session.commit()
    db_session.refresh(emp)
    return emp


@pytest.fixture
def emp_user(db_session: Session, emp_manager: Employees):
    emp = Employees(
        email="user@example.com",
        display_name="Standard User",
        manager_employee_id=emp_manager.employee_id,
    )
    db_session.add(emp)
    db_session.commit()
    db_session.refresh(emp)
    return emp


@pytest.fixture
def emp_other(db_session: Session):
    emp = Employees(
        email="other@example.com",
        display_name="Other User",
    )
    db_session.add(emp)
    db_session.commit()
    db_session.refresh(emp)
    return emp


@pytest.fixture
def time_off_request(db_session: Session, emp_user: Employees):
    now_str = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
    req = TimeOffRequest(
        employee_id=emp_user.employee_id,
        absence_type=AbsenceTypeEnum.VACATION.value,
        status=RequestStatusEnum.PENDING.value,
        time_unit=TimeUnitEnum.FULL_DAY.value,
        start_date=(datetime.now(UTC) + timedelta(days=1)).strftime("%Y-%m-%d"),
        end_date=(datetime.now(UTC) + timedelta(days=2)).strftime("%Y-%m-%d"),
        total_days="2.00",
        reason="Need a break",
        created_at=now_str,
        updated_at=now_str,
    )
    db_session.add(req)

    balance = TimeOffBalance(
        employee_id=emp_user.employee_id,
        absence_type=AbsenceTypeEnum.VACATION.value,
        year=datetime.now(UTC).year,
        entitled_days="10.00",
        used_days="0.00",
        pending_days="2.00",
        carryover_days="0.00",
    )
    db_session.add(balance)

    db_session.commit()
    db_session.refresh(req)
    return req


@pytest.fixture
def override_deps():
    def _override(user: Employees, permissions: dict | None = None):
        if permissions is None:
            permissions = {"permissions": []}

        app.dependency_overrides[get_current_employee] = lambda: user
        app.dependency_overrides[get_current_employee_with_permissions] = lambda: permissions
        app.dependency_overrides[require_authentication] = lambda: user

    yield _override

    app.dependency_overrides.pop(get_current_employee, None)
    app.dependency_overrides.pop(get_current_employee_with_permissions, None)
    app.dependency_overrides.pop(require_authentication, None)


def test_list_requests_admin(override_deps, client: TestClient, emp_user: Employees, time_off_request: TimeOffRequest):
    admin_perms = {"permissions": [{"module_key": "timeoff", "permissions": {"admin_actions": True}}]}
    override_deps(emp_user, admin_perms)

    response = client.get("/api/v1/requests")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(r["request_id"] == time_off_request.request_id for r in data)


def test_list_requests_manager(
    override_deps, client: TestClient, emp_manager: Employees, time_off_request: TimeOffRequest
):
    override_deps(emp_manager, {})

    response = client.get("/api/v1/requests")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(r["request_id"] == time_off_request.request_id for r in data)


def test_list_requests_user(override_deps, client: TestClient, emp_user: Employees, time_off_request: TimeOffRequest):
    override_deps(emp_user, {})

    response = client.get("/api/v1/requests")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(r["request_id"] == time_off_request.request_id for r in data)


def test_list_requests_other(override_deps, client: TestClient, emp_other: Employees, time_off_request: TimeOffRequest):
    override_deps(emp_other, {})

    response = client.get("/api/v1/requests")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


def test_get_request(override_deps, client: TestClient, emp_user: Employees, time_off_request: TimeOffRequest):
    override_deps(emp_user, {})

    response = client.get(f"/api/v1/requests/{time_off_request.request_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["request_id"] == time_off_request.request_id


def test_get_request_forbidden(
    override_deps, client: TestClient, emp_other: Employees, time_off_request: TimeOffRequest
):
    override_deps(emp_other, {})

    response = client.get(f"/api/v1/requests/{time_off_request.request_id}")
    assert response.status_code == 403


def test_get_request_404(override_deps, client: TestClient, emp_user: Employees):
    override_deps(emp_user, {})
    response = client.get("/api/v1/requests/99999")
    assert response.status_code == 404


@patch("api.time_off.BackgroundTasks.add_task")
def test_create_request_full_day(
    mock_add_task, override_deps, client: TestClient, db_session: Session, emp_user: Employees
):
    override_deps(emp_user, {})

    # Create time off balance for the employee
    current_year = datetime.now(UTC).year
    balance = TimeOffBalance(
        employee_id=emp_user.employee_id,
        absence_type=AbsenceTypeEnum.VACATION.value,
        year=current_year,
        entitled_days="10.00",
        used_days="0.00",
        pending_days="0.00",
        carryover_days="0.00",
    )
    db_session.add(balance)
    db_session.commit()

    payload = {
        "absence_type": "vacation",
        "time_unit": "full_day",
        "start_date": (datetime.now(UTC) + timedelta(days=1)).strftime("%Y-%m-%d"),
        "end_date": (datetime.now(UTC) + timedelta(days=2)).strftime("%Y-%m-%d"),
        "reason": "Test logic",
    }

    response = client.post("/api/v1/requests", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["total_days"] == "2.00"

    balance = db_session.exec(
        select(TimeOffBalance).where(
            TimeOffBalance.employee_id == emp_user.employee_id,
            TimeOffBalance.absence_type == "vacation",
            TimeOffBalance.year == (datetime.now(UTC) + timedelta(days=1)).year,
        )
    ).first()
    assert balance.pending_days == "2.00"
    mock_add_task.assert_called_once()


@patch("api.time_off.BackgroundTasks.add_task")
def test_create_request_hours(
    mock_add_task, override_deps, client: TestClient, db_session: Session, emp_user: Employees
):
    override_deps(emp_user, {})

    # Create time off balance for the employee
    current_year = datetime.now(UTC).year
    balance = TimeOffBalance(
        employee_id=emp_user.employee_id,
        absence_type=AbsenceTypeEnum.PERSONAL.value,
        year=current_year,
        entitled_days="5.00",
        used_days="0.00",
        pending_days="0.00",
        carryover_days="0.00",
    )
    db_session.add(balance)
    db_session.commit()

    payload = {
        "absence_type": "personal",
        "time_unit": "hours",
        "start_date": (datetime.now(UTC) + timedelta(days=1)).strftime("%Y-%m-%d"),
        "end_date": (datetime.now(UTC) + timedelta(days=1)).strftime("%Y-%m-%d"),
        "start_time": "10:00:00",
        "end_time": "14:00:00",
        "reason": "Doctor",
    }

    response = client.post("/api/v1/requests", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["total_hours"] == "4.00"
    assert data["total_days"] == "0.50"


@patch("api.time_off.BackgroundTasks.add_task")
def test_create_request_half_day_requires_single_day(
    _mock_add_task, override_deps, client: TestClient, emp_user: Employees
):
    override_deps(emp_user, {})

    payload = {
        "absence_type": "vacation",
        "time_unit": "half_day",
        "start_date": (datetime.now(UTC) + timedelta(days=1)).strftime("%Y-%m-%d"),
        "end_date": (datetime.now(UTC) + timedelta(days=2)).strftime("%Y-%m-%d"),
        "reason": "Invalid half-day range",
    }

    response = client.post("/api/v1/requests", json=payload)
    assert response.status_code == 400
    assert "half_day requests must use the same start_date and end_date" in response.json()["detail"]


@patch("api.time_off.BackgroundTasks.add_task")
def test_create_request_rejects_overlap_with_active_request(
    _mock_add_task, override_deps, client: TestClient, db_session: Session, emp_user: Employees
):
    override_deps(emp_user, {})

    start = (datetime.now(UTC) + timedelta(days=3)).strftime("%Y-%m-%d")
    end = (datetime.now(UTC) + timedelta(days=4)).strftime("%Y-%m-%d")
    now_str = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")

    existing = TimeOffRequest(
        employee_id=emp_user.employee_id,
        absence_type=AbsenceTypeEnum.VACATION.value,
        status=RequestStatusEnum.APPROVED.value,
        time_unit=TimeUnitEnum.FULL_DAY.value,
        start_date=start,
        end_date=end,
        total_days="2.00",
        reason="Existing approved request",
        created_at=now_str,
        updated_at=now_str,
    )
    db_session.add(existing)
    db_session.commit()

    payload = {
        "absence_type": "vacation",
        "time_unit": "full_day",
        "start_date": start,
        "end_date": end,
        "reason": "Should be blocked",
    }

    response = client.post("/api/v1/requests", json=payload)
    assert response.status_code == 400
    assert "overlaps with an existing pending or approved" in response.json()["detail"]


@patch("api.time_off.BackgroundTasks.add_task")
def test_approve_request_admin(
    mock_add_task, override_deps, client: TestClient, emp_other: Employees, time_off_request: TimeOffRequest
):
    admin_perms = {"permissions": [{"module_key": "timeoff", "permissions": {"admin_actions": True}}]}
    override_deps(emp_other, admin_perms)

    response = client.patch(f"/api/v1/requests/{time_off_request.request_id}/approve", json={"review_notes": "OK"})
    assert response.status_code == 200
    assert response.json()["status"] == "approved"
    mock_add_task.assert_called_once()


@patch("api.time_off.BackgroundTasks.add_task")
def test_reject_request_manager(
    mock_add_task,
    override_deps,
    client: TestClient,
    db_session: Session,
    emp_manager: Employees,
    time_off_request: TimeOffRequest,
):
    override_deps(emp_manager, {})

    balance_before = db_session.exec(
        select(TimeOffBalance).where(TimeOffBalance.employee_id == time_off_request.employee_id)
    ).first()
    pending_before = Decimal(balance_before.pending_days)

    response = client.patch(f"/api/v1/requests/{time_off_request.request_id}/reject", json={"review_notes": "No"})
    assert response.status_code == 200
    assert response.json()["status"] == "rejected"
    mock_add_task.assert_called_once()

    db_session.refresh(balance_before)
    assert Decimal(balance_before.pending_days) == pending_before - Decimal("2.00")


def test_approve_request_forbidden_own(
    override_deps, client: TestClient, emp_user: Employees, time_off_request: TimeOffRequest
):
    override_deps(emp_user, {})
    response = client.patch(
        f"/api/v1/requests/{time_off_request.request_id}/approve", json={"review_notes": "Self approval"}
    )
    assert response.status_code == 403
    assert "cannot approve or reject your own request" in response.json()["detail"]


def test_get_calendar(
    override_deps, client: TestClient, db_session: Session, emp_user: Employees, time_off_request: TimeOffRequest
):
    override_deps(emp_user, {})

    holiday = Holiday(name="New Year", date="2024-01-01", year=2024)
    db_session.add(holiday)
    db_session.commit()

    response = client.get("/api/v1/calendar")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


def test_get_report_summary(override_deps, client: TestClient, emp_user: Employees, time_off_request: TimeOffRequest):
    override_deps(emp_user, {})

    response = client.get("/api/v1/reports/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_requests"] == 1
    assert data["status"]["pending"] == 1


def test_export_requests_report(
    override_deps, client: TestClient, emp_user: Employees, time_off_request: TimeOffRequest
):
    override_deps(emp_user, {})

    response = client.get("/api/v1/reports/export")
    assert response.status_code == 200
    assert response.headers["Content-Disposition"] == "attachment; filename=time_off_requests.csv"
    assert response.headers.get("content-type", "").startswith("text/csv")

    reader = csv.DictReader(StringIO(response.text))
    rows = list(reader)
    assert len(rows) == 1
    assert str(rows[0]["request_id"]) == str(time_off_request.request_id)


def test_get_balances(override_deps, client: TestClient, emp_user: Employees, time_off_request: TimeOffRequest):
    override_deps(emp_user, {})

    response = client.get(f"/api/v1/balances/{emp_user.employee_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["pending_days"] == "2.00"


def test_get_balances_forbidden(
    override_deps, client: TestClient, emp_other: Employees, emp_user: Employees, time_off_request: TimeOffRequest
):
    override_deps(emp_other, {})

    response = client.get(f"/api/v1/balances/{emp_user.employee_id}")
    assert response.status_code == 403


def test_list_holidays(override_deps, client: TestClient, db_session: Session, emp_user: Employees):
    override_deps(emp_user, {})
    holiday = Holiday(name="Xmas", date="2024-12-25", year=2024)
    db_session.add(holiday)
    db_session.commit()

    response = client.get("/api/v1/holidays")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_list_departments(override_deps, client: TestClient, db_session: Session, emp_user: Employees):
    override_deps(emp_user, {})
    dept = Department(name="Engineering", code="ENG")
    db_session.add(dept)
    db_session.commit()

    response = client.get("/api/v1/departments")
    assert response.status_code == 200
    assert len(response.json()) >= 1
