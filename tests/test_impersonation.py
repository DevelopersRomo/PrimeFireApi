"""Tests for admin impersonation via signed, expiring grants."""

from datetime import UTC, datetime, timedelta

import pytest
from jose import jwt as jose_jwt
from sqlmodel import select

from api.dependencies import (
    ALGORITHM,
    IMPERSONATION_GRANT_TYPE,
    IMPERSONATION_HEADER,
    SECRET_KEY,
    issue_impersonation_grant,
)
from models.employees import EmployeeRoles, Employees, Roles
from tests.conftest import create_test_record


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


def sign(claims: dict) -> str:
    return jose_jwt.encode(claims, SECRET_KEY, algorithm=ALGORITHM)


# --- Issuing -----------------------------------------------------------------


def test_admin_can_start_impersonation(client, auth_headers, db_session, caller, other_employee):
    make_admin(db_session, caller)

    response = client.post(
        "/impersonation/start",
        headers=auth_headers,
        json={"employee_id": other_employee.employee_id},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["employee_id"] == other_employee.employee_id
    assert body["grant"]
    assert body["expires_at"]


def test_non_admin_cannot_start_impersonation(client, auth_headers, db_session, caller, other_employee):
    response = client.post(
        "/impersonation/start",
        headers=auth_headers,
        json={"employee_id": other_employee.employee_id},
    )

    assert response.status_code == 403
    assert "Admin" in response.json()["detail"]


def test_cannot_start_against_unknown_employee(client, auth_headers, db_session, caller):
    make_admin(db_session, caller)

    response = client.post("/impersonation/start", headers=auth_headers, json={"employee_id": 999999})

    assert response.status_code == 404


def test_grant_expires_in_one_hour(db_session, caller, other_employee):
    _grant, expires_at = issue_impersonation_grant(caller.employee_id, other_employee.employee_id)

    remaining = expires_at - datetime.now(UTC)
    assert timedelta(minutes=55) < remaining <= timedelta(hours=1)


# --- Using -------------------------------------------------------------------


def test_grant_swaps_the_employee(client, auth_headers, db_session, caller, other_employee):
    make_admin(db_session, caller)
    grant, _ = issue_impersonation_grant(caller.employee_id, other_employee.employee_id)

    response = client.get("/permissions/me", headers={**auth_headers, IMPERSONATION_HEADER: grant})

    assert response.status_code == 200, response.text
    assert response.json()["employee"]["employee_id"] == other_employee.employee_id


def test_no_grant_means_no_impersonation(client, auth_headers, db_session, caller):
    make_admin(db_session, caller)

    response = client.get("/permissions/me", headers=auth_headers)

    assert response.status_code == 200, response.text
    assert response.json()["employee"]["employee_id"] == caller.employee_id


def test_expired_grant_is_rejected(client, auth_headers, db_session, caller, other_employee):
    """The whole point of signing: the client cannot extend its own session."""
    make_admin(db_session, caller)
    expired = sign(
        {
            "type": IMPERSONATION_GRANT_TYPE,
            "act": caller.employee_id,
            "sub": str(other_employee.employee_id),
            "exp": datetime.now(UTC) - timedelta(minutes=1),
        }
    )

    response = client.get("/permissions/me", headers={**auth_headers, IMPERSONATION_HEADER: expired})

    assert response.status_code == 403
    assert "expired" in response.json()["detail"].lower()


def test_forged_grant_is_rejected(client, auth_headers, db_session, caller, other_employee):
    make_admin(db_session, caller)
    forged = jose_jwt.encode(
        {
            "type": IMPERSONATION_GRANT_TYPE,
            "act": caller.employee_id,
            "sub": str(other_employee.employee_id),
            "exp": datetime.now(UTC) + timedelta(hours=1),
        },
        "not-the-real-secret",
        algorithm=ALGORITHM,
    )

    response = client.get("/permissions/me", headers={**auth_headers, IMPERSONATION_HEADER: forged})

    assert response.status_code == 403


def test_grant_issued_for_somebody_else_is_rejected(
    client, auth_headers, db_session, caller, other_employee, manager_employee
):
    """A leaked grant is useless: it only works for the actor it names."""
    make_admin(db_session, caller)
    grant, _ = issue_impersonation_grant(manager_employee.employee_id, other_employee.employee_id)

    response = client.get("/permissions/me", headers={**auth_headers, IMPERSONATION_HEADER: grant})

    assert response.status_code == 403
    assert "another user" in response.json()["detail"].lower()


def test_ordinary_access_token_is_not_a_grant(client, auth_headers, db_session, caller):
    """Signed with the same secret, but the wrong type must not be accepted."""
    make_admin(db_session, caller)
    not_a_grant = sign(
        {
            "type": "internal",
            "act": caller.employee_id,
            "sub": "test@example.com",
            "exp": datetime.now(UTC) + timedelta(hours=1),
        }
    )

    response = client.get("/permissions/me", headers={**auth_headers, IMPERSONATION_HEADER: not_a_grant})

    assert response.status_code == 403


def test_grant_stops_working_when_admin_role_is_revoked(client, auth_headers, db_session, caller, other_employee):
    """Authority is re-checked per request, not frozen at issue time."""
    make_admin(db_session, caller)
    grant, _ = issue_impersonation_grant(caller.employee_id, other_employee.employee_id)

    for link in db_session.exec(select(EmployeeRoles).where(EmployeeRoles.employee_id == caller.employee_id)).all():
        db_session.delete(link)
    db_session.commit()

    response = client.get("/permissions/me", headers={**auth_headers, IMPERSONATION_HEADER: grant})

    assert response.status_code == 403
    assert "Admin" in response.json()["detail"]


# --- Context -----------------------------------------------------------------


def test_context_reports_admin_can_impersonate(client, auth_headers, db_session, caller):
    make_admin(db_session, caller)

    response = client.get("/impersonation/context", headers=auth_headers)

    assert response.status_code == 200, response.text
    assert response.json()["can_impersonate"] is True


def test_context_denies_non_admin(client, auth_headers, db_session, caller):
    response = client.get("/impersonation/context", headers=auth_headers)

    assert response.status_code == 200, response.text
    assert response.json()["can_impersonate"] is False


def test_context_stays_reachable_while_impersonating(client, auth_headers, db_session, caller, other_employee):
    """The switch must resolve from the real caller, not the impersonated one."""
    make_admin(db_session, caller)
    grant, _ = issue_impersonation_grant(caller.employee_id, other_employee.employee_id)

    response = client.get("/impersonation/context", headers={**auth_headers, IMPERSONATION_HEADER: grant})

    assert response.status_code == 200, response.text
    assert response.json()["can_impersonate"] is True
    assert response.json()["real_employee_id"] == caller.employee_id
