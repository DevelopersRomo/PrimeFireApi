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
        Email="manager@example.com",
        DisplayName="Manager User",
    )
    db_session.add(emp)
    db_session.commit()
    db_session.refresh(emp)
    return emp


@pytest.fixture
def emp_user(db_session: Session, emp_manager: Employees):
    emp = Employees(
        Email="user@example.com",
        DisplayName="Standard User",
        ManagerEmployeeId=emp_manager.EmployeeId,
    )
    db_session.add(emp)
    db_session.commit()
    db_session.refresh(emp)
    return emp


@pytest.fixture
def emp_other(db_session: Session):
    emp = Employees(
        Email="other@example.com",
        DisplayName="Other User",
    )
    db_session.add(emp)
    db_session.commit()
    db_session.refresh(emp)
    return emp


@pytest.fixture
def time_off_request(db_session: Session, emp_user: Employees):
    now_str = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
    req = TimeOffRequest(
        EmployeeId=emp_user.EmployeeId,
        AbsenceType=AbsenceTypeEnum.VACATION.value,
        Status=RequestStatusEnum.PENDING.value,
        TimeUnit=TimeUnitEnum.FULL_DAY.value,
        StartDate=(datetime.now(UTC) + timedelta(days=1)).strftime("%Y-%m-%d"),
        EndDate=(datetime.now(UTC) + timedelta(days=2)).strftime("%Y-%m-%d"),
        TotalDays="2.00",
        Reason="Need a break",
        CreatedAt=now_str,
        UpdatedAt=now_str,
    )
    db_session.add(req)

    balance = TimeOffBalance(
        EmployeeId=emp_user.EmployeeId,
        AbsenceType=AbsenceTypeEnum.VACATION.value,
        Year=datetime.now(UTC).year,
        EntitledDays="10.00",
        UsedDays="0.00",
        PendingDays="2.00",
        CarryoverDays="0.00",
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
    admin_perms = {"permissions": [{"module_key": "timeoff", "permissions": {"AdminActions": True}}]}
    override_deps(emp_user, admin_perms)

    response = client.get("/api/v1/requests")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(r["RequestId"] == time_off_request.RequestId for r in data)


def test_list_requests_manager(
    override_deps, client: TestClient, emp_manager: Employees, time_off_request: TimeOffRequest
):
    override_deps(emp_manager, {})

    response = client.get("/api/v1/requests")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(r["RequestId"] == time_off_request.RequestId for r in data)


def test_list_requests_user(override_deps, client: TestClient, emp_user: Employees, time_off_request: TimeOffRequest):
    override_deps(emp_user, {})

    response = client.get("/api/v1/requests")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(r["RequestId"] == time_off_request.RequestId for r in data)


def test_list_requests_other(override_deps, client: TestClient, emp_other: Employees, time_off_request: TimeOffRequest):
    override_deps(emp_other, {})

    response = client.get("/api/v1/requests")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


def test_get_request(override_deps, client: TestClient, emp_user: Employees, time_off_request: TimeOffRequest):
    override_deps(emp_user, {})

    response = client.get(f"/api/v1/requests/{time_off_request.RequestId}")
    assert response.status_code == 200
    data = response.json()
    assert data["RequestId"] == time_off_request.RequestId


def test_get_request_forbidden(
    override_deps, client: TestClient, emp_other: Employees, time_off_request: TimeOffRequest
):
    override_deps(emp_other, {})

    response = client.get(f"/api/v1/requests/{time_off_request.RequestId}")
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
        EmployeeId=emp_user.EmployeeId,
        AbsenceType=AbsenceTypeEnum.VACATION.value,
        Year=current_year,
        EntitledDays="10.00",
        UsedDays="0.00",
        PendingDays="0.00",
        CarryoverDays="0.00",
    )
    db_session.add(balance)
    db_session.commit()

    payload = {
        "AbsenceType": "vacation",
        "TimeUnit": "full_day",
        "StartDate": (datetime.now(UTC) + timedelta(days=1)).strftime("%Y-%m-%d"),
        "EndDate": (datetime.now(UTC) + timedelta(days=2)).strftime("%Y-%m-%d"),
        "Reason": "Test logic",
    }

    response = client.post("/api/v1/requests", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["TotalDays"] == "2.00"

    balance = db_session.exec(
        select(TimeOffBalance).where(
            TimeOffBalance.EmployeeId == emp_user.EmployeeId,
            TimeOffBalance.AbsenceType == "vacation",
            TimeOffBalance.Year == (datetime.now(UTC) + timedelta(days=1)).year,
        )
    ).first()
    assert balance.PendingDays == "2.00"
    mock_add_task.assert_called_once()


@patch("api.time_off.BackgroundTasks.add_task")
def test_create_request_hours(
    mock_add_task, override_deps, client: TestClient, db_session: Session, emp_user: Employees
):
    override_deps(emp_user, {})

    # Create time off balance for the employee
    current_year = datetime.now(UTC).year
    balance = TimeOffBalance(
        EmployeeId=emp_user.EmployeeId,
        AbsenceType=AbsenceTypeEnum.PERSONAL.value,
        Year=current_year,
        EntitledDays="5.00",
        UsedDays="0.00",
        PendingDays="0.00",
        CarryoverDays="0.00",
    )
    db_session.add(balance)
    db_session.commit()

    payload = {
        "AbsenceType": "personal",
        "TimeUnit": "hours",
        "StartDate": (datetime.now(UTC) + timedelta(days=1)).strftime("%Y-%m-%d"),
        "EndDate": (datetime.now(UTC) + timedelta(days=1)).strftime("%Y-%m-%d"),
        "StartTime": "10:00:00",
        "EndTime": "14:00:00",
        "Reason": "Doctor",
    }

    response = client.post("/api/v1/requests", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["TotalHours"] == "4.00"
    assert data["TotalDays"] == "0.50"


@patch("api.time_off.BackgroundTasks.add_task")
def test_approve_request_admin(
    mock_add_task, override_deps, client: TestClient, emp_other: Employees, time_off_request: TimeOffRequest
):
    admin_perms = {"permissions": [{"module_key": "timeoff", "permissions": {"AdminActions": True}}]}
    override_deps(emp_other, admin_perms)

    response = client.patch(f"/api/v1/requests/{time_off_request.RequestId}/approve", json={"ReviewNotes": "OK"})
    assert response.status_code == 200
    assert response.json()["Status"] == "approved"
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
        select(TimeOffBalance).where(TimeOffBalance.EmployeeId == time_off_request.EmployeeId)
    ).first()
    pending_before = Decimal(balance_before.PendingDays)

    response = client.patch(f"/api/v1/requests/{time_off_request.RequestId}/reject", json={"ReviewNotes": "No"})
    assert response.status_code == 200
    assert response.json()["Status"] == "rejected"
    mock_add_task.assert_called_once()

    db_session.refresh(balance_before)
    assert Decimal(balance_before.PendingDays) == pending_before - Decimal("2.00")


def test_approve_request_forbidden_own(
    override_deps, client: TestClient, emp_user: Employees, time_off_request: TimeOffRequest
):
    override_deps(emp_user, {})
    response = client.patch(
        f"/api/v1/requests/{time_off_request.RequestId}/approve", json={"ReviewNotes": "Self approval"}
    )
    assert response.status_code == 403
    assert "cannot approve or reject your own request" in response.json()["detail"]


def test_get_calendar(
    override_deps, client: TestClient, db_session: Session, emp_user: Employees, time_off_request: TimeOffRequest
):
    override_deps(emp_user, {})

    holiday = Holiday(Name="New Year", Date="2024-01-01", Year=2024)
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
    assert str(rows[0]["RequestId"]) == str(time_off_request.RequestId)


def test_get_balances(override_deps, client: TestClient, emp_user: Employees, time_off_request: TimeOffRequest):
    override_deps(emp_user, {})

    response = client.get(f"/api/v1/balances/{emp_user.EmployeeId}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["PendingDays"] == "2.00"


def test_get_balances_forbidden(
    override_deps, client: TestClient, emp_other: Employees, emp_user: Employees, time_off_request: TimeOffRequest
):
    override_deps(emp_other, {})

    response = client.get(f"/api/v1/balances/{emp_user.EmployeeId}")
    assert response.status_code == 403


def test_list_holidays(override_deps, client: TestClient, db_session: Session, emp_user: Employees):
    override_deps(emp_user, {})
    holiday = Holiday(Name="Xmas", Date="2024-12-25", Year=2024)
    db_session.add(holiday)
    db_session.commit()

    response = client.get("/api/v1/holidays")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_list_departments(override_deps, client: TestClient, db_session: Session, emp_user: Employees):
    override_deps(emp_user, {})
    dept = Department(Name="Engineering", Code="ENG")
    db_session.add(dept)
    db_session.commit()

    response = client.get("/api/v1/departments")
    assert response.status_code == 200
    assert len(response.json()) >= 1
