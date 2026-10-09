from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlmodel import Session, select

import api.auth
from api.auth import ALGORITHM, SECRET_KEY, get_password_hash
from core.datetime_utils import utcnow
from models.auth_tokens import AuthToken
from models.employees import Employees
from models.tenants import TenantEmployees, Tenants


def _verify_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def test_register_pending_user(client: TestClient, db_session: Session):
    """Test registering a user without a tenant. Should be returned 202."""
    response = client.post(
        "/auth/register",
        json={
            "email": "pending@example.com",
            "password": "securepassword123",
            "first_name": "Pending",
            "last_name": "User",
        },
    )

    assert response.status_code == 202
    assert "pending approval" in response.json()["detail"].lower()

    user = db_session.exec(select(TenantEmployees).where(TenantEmployees.email == "pending@example.com")).first()
    assert user is not None
    assert user.tenant_id is None


@pytest.mark.parametrize("tenant_key", ["TEST_TENANT", "NON_EXISTENT"])
def test_register_ignores_tenant_key_and_stays_pending(client: TestClient, db_session: Session, tenant_key: str):
    """A client-supplied tenant_key must not join a tenant; only /tenants/approve-user assigns one."""
    tenant = Tenants(name="Test Tenant", db_connection_key="TEST_TENANT", is_active=True)
    db_session.add(tenant)
    db_session.commit()

    response = client.post(
        "/auth/register",
        json={
            "email": "tenantuser@example.com",
            "password": "securepassword123",
            "first_name": "Tenant",
            "last_name": "User",
            "tenant_key": tenant_key,
        },
    )

    assert response.status_code == 202
    assert "access_token" not in response.json()
    user = db_session.exec(select(TenantEmployees).where(TenantEmployees.email == "tenantuser@example.com")).first()
    assert user is not None
    assert user.tenant_id is None
    assert db_session.exec(select(Employees).where(Employees.email == "tenantuser@example.com")).first() is None


@pytest.mark.parametrize("tenant_key", ["COLLIDE_TENANT", None])
def test_register_rejects_email_of_existing_employee(client: TestClient, db_session: Session, tenant_key):
    """Registration must never take over an existing local account (with or without tenant_key)."""
    original_hash = get_password_hash("victim-password")
    victim = Employees(email="victim@example.com", password_hash=original_hash, azure_oid="victim-oid")
    db_session.add(victim)
    db_session.commit()

    payload = {
        "email": "victim@example.com",
        "password": "attacker-password",
        "first_name": "Attacker",
        "last_name": "User",
    }
    if tenant_key:
        payload["tenant_key"] = tenant_key
    response = client.post("/auth/register", json=payload)

    assert response.status_code == 400
    db_session.expire_all()
    stored = db_session.exec(select(Employees).where(Employees.email == "victim@example.com")).one()
    assert stored.password_hash == original_hash
    assert db_session.exec(select(TenantEmployees).where(TenantEmployees.email == "victim@example.com")).first() is None


def test_token_login_success(client: TestClient, db_session: Session):
    tenant = Tenants(name="Active Tenant", db_connection_key="ACTIVE", is_active=True)
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)

    from api.auth import get_password_hash

    hashed_pw = get_password_hash("securepassword")
    user = TenantEmployees(email="login_user@example.com", password_hash=hashed_pw, tenant_id=tenant.tenant_id)
    db_session.add(user)
    db_session.commit()

    response = client.post("/auth/token", data={"username": "login_user@example.com", "password": "securepassword"})

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_token_login_pending_user(client: TestClient, db_session: Session):
    from api.auth import get_password_hash

    user = TenantEmployees(email="pend_login@example.com", password_hash=get_password_hash("pass"), tenant_id=None)
    db_session.add(user)
    db_session.commit()

    response = client.post("/auth/token", data={"username": "pend_login@example.com", "password": "pass"})

    assert response.status_code == 403
    assert "pending approval" in response.json()["detail"].lower()


def test_token_login_invalid_password(client: TestClient, db_session: Session):
    from api.auth import get_password_hash

    user = TenantEmployees(email="wrong_pw@example.com", password_hash=get_password_hash("pass"), tenant_id=None)
    db_session.add(user)
    db_session.commit()

    response = client.post("/auth/token", data={"username": "wrong_pw@example.com", "password": "wrongpassword"})
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


def test_refresh_token_success(client: TestClient, db_session: Session):
    # An approved tenant user signs in to obtain a refresh token
    tenant = Tenants(name="Refresh Tenant", db_connection_key="REFRESH_T", is_active=True)
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    db_session.add(
        TenantEmployees(
            email="refresh_user@example.com", password_hash=get_password_hash("my_password"), tenant_id=tenant.tenant_id
        )
    )
    db_session.commit()

    response = client.post("/auth/token", data={"username": "refresh_user@example.com", "password": "my_password"})
    refresh_token = response.json()["refresh_token"]

    response = client.post("/auth/refresh", json={"refresh_token": refresh_token})

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_refresh_token_invalid(client: TestClient):
    response = client.post("/auth/refresh", json={"refresh_token": "invalid_or_expired_refresh_token"})
    assert response.status_code in {400, 401}


# =============================================================================
# Magic link and password recovery
# =============================================================================


@pytest.fixture
def captured_emails(monkeypatch) -> list[dict]:
    """Capture auth emails instead of sending them, and expose the delivered token."""
    sent: list[dict] = []

    async def _capture(*, to_email: str, token: str, app_url: str | None = None, tenant_title: str = "PrimeFire"):
        sent.append({"to_email": to_email, "token": token})
        return True, None

    monkeypatch.setattr(api.auth, "send_magic_link_email", _capture)
    monkeypatch.setattr(api.auth, "send_password_recovery_email", _capture)
    return sent


@pytest.fixture
def local_auth_user(db_session: Session) -> TenantEmployees:
    """Tenant user with a local password — the only kind allowed to use magic links."""
    tenant = Tenants(name="Magic Tenant", db_connection_key="MAGIC_T", is_active=True)
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)

    user = TenantEmployees(
        email="magic_user@example.com",
        password_hash=get_password_hash("original_password"),
        tenant_id=tenant.tenant_id,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _request_token(client: TestClient, captured_emails: list[dict], endpoint: str, email: str) -> str:
    """Trigger an auth email and return the token that reached the user's inbox."""
    response = client.post(endpoint, json={"email": email})
    assert response.status_code == 200, response.text
    return captured_emails[-1]["token"]


def _force_expired(db_session: Session, token: str) -> None:
    """Move a token's expiry into the past, reproducing a stale link."""
    row = db_session.exec(select(AuthToken).where(AuthToken.token == token)).first()
    assert row is not None
    row.expires_at = utcnow() - timedelta(minutes=1)
    db_session.add(row)
    db_session.commit()


def test_magic_link_verify_returns_tokens(
    client: TestClient, local_auth_user: TenantEmployees, captured_emails: list[dict]
):
    """A fresh magic link must sign the user in, not fail comparing stored and current time."""
    email = local_auth_user.email
    token = _request_token(client, captured_emails, "/auth/magic-link", email)

    response = client.get("/auth/magic-link/verify", params={"token": token})

    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert _verify_token(data["access_token"])["sub"] == email


@pytest.mark.parametrize("state", ["pending", "inactive_tenant"])
def test_magic_link_verify_applies_login_approval_checks(
    client: TestClient, db_session: Session, captured_emails: list[dict], state: str
):
    """A magic link must not sign in an account that /auth/token would refuse."""
    tenant_id = None
    if state == "inactive_tenant":
        tenant = Tenants(name="Inactive Tenant", db_connection_key="INACTIVE_T", is_active=False)
        db_session.add(tenant)
        db_session.commit()
        db_session.refresh(tenant)
        tenant_id = tenant.tenant_id
    email = f"{state}_magic@example.com"
    db_session.add(TenantEmployees(email=email, password_hash=get_password_hash("pw"), tenant_id=tenant_id))
    db_session.commit()
    token = _request_token(client, captured_emails, "/auth/magic-link", email)

    response = client.get("/auth/magic-link/verify", params={"token": token})

    assert response.status_code == 403, response.text
    assert "access_token" not in response.json()


def test_magic_link_verify_rejects_expired_token(
    client: TestClient, db_session: Session, local_auth_user: TenantEmployees, captured_emails: list[dict]
):
    """An expired link must be refused with 400, not crash while checking the expiry."""
    token = _request_token(client, captured_emails, "/auth/magic-link", local_auth_user.email)
    _force_expired(db_session, token)

    response = client.get("/auth/magic-link/verify", params={"token": token})

    assert response.status_code == 400, response.text
    assert "expired" in response.json()["detail"].lower()


def test_magic_link_cannot_be_used_twice(
    client: TestClient, local_auth_user: TenantEmployees, captured_emails: list[dict]
):
    token = _request_token(client, captured_emails, "/auth/magic-link", local_auth_user.email)
    assert client.get("/auth/magic-link/verify", params={"token": token}).status_code == 200

    response = client.get("/auth/magic-link/verify", params={"token": token})

    assert response.status_code == 400
    assert "already been used" in response.json()["detail"].lower()


def test_requesting_magic_link_invalidates_the_previous_one(
    client: TestClient, local_auth_user: TenantEmployees, captured_emails: list[dict]
):
    email = local_auth_user.email
    first_token = _request_token(client, captured_emails, "/auth/magic-link", email)
    second_token = _request_token(client, captured_emails, "/auth/magic-link", email)

    assert client.get("/auth/magic-link/verify", params={"token": first_token}).status_code == 400
    assert client.get("/auth/magic-link/verify", params={"token": second_token}).status_code == 200


def test_magic_link_verify_rejects_unknown_token(client: TestClient):
    response = client.get("/auth/magic-link/verify", params={"token": "not-a-real-token"})

    assert response.status_code == 400


def test_magic_link_for_unknown_email_sends_nothing(client: TestClient, captured_emails: list[dict]):
    """Enumeration guard: same 200 answer, but no email leaves the system."""
    response = client.post("/auth/magic-link", json={"email": "nobody@example.com"})

    assert response.status_code == 200
    assert captured_emails == []


def test_reset_password_allows_login_with_the_new_password(
    client: TestClient, local_auth_user: TenantEmployees, captured_emails: list[dict]
):
    """Full recovery round trip: the reset must land and the normal login must honour it."""
    email = local_auth_user.email
    token = _request_token(client, captured_emails, "/auth/password-recovery", email)

    response = client.post("/auth/reset-password", json={"token": token, "new_password": "brand_new_password"})
    assert response.status_code == 200, response.text

    old = client.post("/auth/token", data={"username": email, "password": "original_password"})
    assert old.status_code == 401

    new = client.post("/auth/token", data={"username": email, "password": "brand_new_password"})
    assert new.status_code == 200
    assert "access_token" in new.json()


def test_reset_password_rejects_expired_token(
    client: TestClient, db_session: Session, local_auth_user: TenantEmployees, captured_emails: list[dict]
):
    """An expired recovery token must be refused with 400, not crash while checking the expiry."""
    token = _request_token(client, captured_emails, "/auth/password-recovery", local_auth_user.email)
    _force_expired(db_session, token)

    response = client.post("/auth/reset-password", json={"token": token, "new_password": "brand_new_password"})

    assert response.status_code == 400, response.text
    assert "expired" in response.json()["detail"].lower()


def test_reset_password_cannot_be_used_twice(
    client: TestClient, local_auth_user: TenantEmployees, captured_emails: list[dict]
):
    token = _request_token(client, captured_emails, "/auth/password-recovery", local_auth_user.email)
    first = client.post("/auth/reset-password", json={"token": token, "new_password": "first_new_password"})
    assert first.status_code == 200

    response = client.post("/auth/reset-password", json={"token": token, "new_password": "second_new_password"})

    assert response.status_code == 400
    assert "already been used" in response.json()["detail"].lower()


def test_password_recovery_for_unknown_email_sends_nothing(client: TestClient, captured_emails: list[dict]):
    response = client.post("/auth/password-recovery", json={"email": "nobody@example.com"})

    assert response.status_code == 200
    assert captured_emails == []
