"""Tests for the local-only employee impersonation header."""

import pytest
from sqlmodel import select

from api.dependencies import IMPERSONATION_HEADER
from core.config import EnvironmentMode, settings
from models.employees import EmployeeRoles, Employees, Roles
from tests.conftest import create_test_record


@pytest.fixture
def local_environment(monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", EnvironmentMode.LOCAL)


@pytest.fixture
def caller(db_session, auth_headers) -> Employees:
    """The employee the auth_headers token actually resolves to."""
    return db_session.exec(select(Employees).where(Employees.email == "test@example.com")).first()


def make_admin(db_session, employee: Employees) -> None:
    role = db_session.exec(select(Roles).where(Roles.role_name == "Admin")).first()
    if not role:
        role = create_test_record(db_session, Roles, role_name="Admin")
    db_session.add(EmployeeRoles(employee_id=employee.employee_id, role_id=role.role_id))
    db_session.commit()


def test_admin_impersonates_another_employee(
    client, auth_headers, db_session, caller, other_employee, local_environment
):
    make_admin(db_session, caller)

    response = client.get(
        "/permissions/me",
        headers={**auth_headers, IMPERSONATION_HEADER: str(other_employee.employee_id)},
    )

    assert response.status_code == 200, response.text
    assert response.json()["employee"]["employee_id"] == other_employee.employee_id


def test_non_admin_cannot_impersonate(client, auth_headers, db_session, caller, other_employee, local_environment):
    response = client.get(
        "/permissions/me",
        headers={**auth_headers, IMPERSONATION_HEADER: str(other_employee.employee_id)},
    )

    assert response.status_code == 403
    assert "Admin" in response.json()["detail"]


def test_header_is_ignored_outside_local(client, auth_headers, db_session, caller, other_employee, monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", EnvironmentMode.PROD)
    make_admin(db_session, caller)

    response = client.get(
        "/permissions/me",
        headers={**auth_headers, IMPERSONATION_HEADER: str(other_employee.employee_id)},
    )

    assert response.status_code == 200, response.text
    assert response.json()["employee"]["employee_id"] == caller.employee_id


def test_unknown_target_is_rejected(client, auth_headers, db_session, caller, local_environment):
    make_admin(db_session, caller)

    response = client.get(
        "/permissions/me",
        headers={**auth_headers, IMPERSONATION_HEADER: "999999"},
    )

    assert response.status_code == 404


def test_non_numeric_target_is_rejected(client, auth_headers, db_session, caller, local_environment):
    make_admin(db_session, caller)

    response = client.get(
        "/permissions/me",
        headers={**auth_headers, IMPERSONATION_HEADER: "not-an-id"},
    )

    assert response.status_code == 400


def test_context_reports_admin_can_impersonate(client, auth_headers, db_session, caller, local_environment):
    make_admin(db_session, caller)

    response = client.get("/impersonation/context", headers=auth_headers)

    assert response.status_code == 200, response.text
    assert response.json()["can_impersonate"] is True


def test_context_denies_non_admin(client, auth_headers, db_session, caller, local_environment):
    response = client.get("/impersonation/context", headers=auth_headers)

    assert response.status_code == 200, response.text
    assert response.json()["can_impersonate"] is False


def test_context_denies_outside_local(client, auth_headers, db_session, caller, monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", EnvironmentMode.PROD)
    make_admin(db_session, caller)

    response = client.get("/impersonation/context", headers=auth_headers)

    assert response.status_code == 200, response.text
    assert response.json()["can_impersonate"] is False


def test_context_stays_reachable_while_impersonating(
    client, auth_headers, db_session, caller, other_employee, local_environment
):
    """The switch must resolve from the real caller, not the impersonated one."""
    make_admin(db_session, caller)

    response = client.get(
        "/impersonation/context",
        headers={**auth_headers, IMPERSONATION_HEADER: str(other_employee.employee_id)},
    )

    assert response.status_code == 200, response.text
    assert response.json()["can_impersonate"] is True
    assert response.json()["real_employee_id"] == caller.employee_id
