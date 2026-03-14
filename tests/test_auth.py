from fastapi.testclient import TestClient
from jose import jwt
from sqlmodel import Session, select

from api.auth import ALGORITHM, SECRET_KEY
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

    user = db_session.exec(select(TenantEmployees).where(TenantEmployees.Email == "pending@example.com")).first()
    assert user is not None
    assert user.TenantId is None


def test_register_user_with_tenant(client: TestClient, db_session: Session):
    """Test registering a user with a valid tenant."""
    # Setup Tenant
    tenant = Tenants(Name="Test Tenant", DbConnectionKey="TEST_TENANT", IsActive=True)
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)

    response = client.post(
        "/auth/register",
        json={
            "email": "tenantuser@example.com",
            "password": "securepassword123",
            "first_name": "Tenant",
            "last_name": "User",
            "tenant_key": "TEST_TENANT",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

    payload = _verify_token(data["access_token"])
    assert payload["sub"] == "tenantuser@example.com"
    assert payload["tenant_key"] == "TEST_TENANT"


def test_register_with_invalid_tenant(client: TestClient, db_session: Session):
    response = client.post(
        "/auth/register",
        json={
            "email": "badtenant@example.com",
            "password": "securepassword123",
            "first_name": "Bad",
            "last_name": "Tenant",
            "tenant_key": "NON_EXISTENT",
        },
    )
    assert response.status_code == 404


def test_token_login_success(client: TestClient, db_session: Session):
    tenant = Tenants(Name="Active Tenant", DbConnectionKey="ACTIVE", IsActive=True)
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)

    from api.auth import get_password_hash

    hashed_pw = get_password_hash("securepassword")
    user = TenantEmployees(Email="login_user@example.com", PasswordHash=hashed_pw, TenantId=tenant.TenantId)
    db_session.add(user)
    db_session.commit()

    response = client.post("/auth/token", data={"username": "login_user@example.com", "password": "securepassword"})

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_token_login_pending_user(client: TestClient, db_session: Session):
    from api.auth import get_password_hash

    user = TenantEmployees(Email="pend_login@example.com", PasswordHash=get_password_hash("pass"), TenantId=None)
    db_session.add(user)
    db_session.commit()

    response = client.post("/auth/token", data={"username": "pend_login@example.com", "password": "pass"})

    assert response.status_code == 403
    assert "pending approval" in response.json()["detail"].lower()


def test_token_login_invalid_password(client: TestClient, db_session: Session):
    from api.auth import get_password_hash

    user = TenantEmployees(Email="wrong_pw@example.com", PasswordHash=get_password_hash("pass"), TenantId=None)
    db_session.add(user)
    db_session.commit()

    response = client.post("/auth/token", data={"username": "wrong_pw@example.com", "password": "wrongpassword"})
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


def test_refresh_token_success(client: TestClient, db_session: Session):
    # Setup Tenant and directly generate token to test refresh
    tenant = Tenants(Name="Refresh Tenant", DbConnectionKey="REFRESH_T", IsActive=True)
    db_session.add(tenant)
    db_session.commit()

    response = client.post(
        "/auth/register",
        json={
            "email": "refresh_user@example.com",
            "password": "my_password",
            "first_name": "Refresh",
            "last_name": "User",
            "tenant_key": "REFRESH_T",
        },
    )
    refresh_token = response.json()["refresh_token"]

    response = client.post("/auth/refresh", json={"refresh_token": refresh_token})

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_refresh_token_invalid(client: TestClient):
    response = client.post("/auth/refresh", json={"refresh_token": "invalid_or_expired_refresh_token"})
    assert response.status_code in {400, 401}
