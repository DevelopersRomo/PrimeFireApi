import pytest
from fastapi import status

from api.auth import get_password_hash
from api.dependencies import get_current_employee_with_permissions
from main import app
from models.employees import Employees
from models.tenants import TenantEmployees, TenantLogos, Tenants


@pytest.fixture(autouse=True)
def _grant_tenant_mutations(permission_override) -> None:
    permission_override("tenants", {"can_view", "can_create", "can_edit", "can_delete"})


def test_list_all_tenants(client, db_session, auth_headers):
    """Test listing all tenants."""
    # Create test tenants
    t1 = Tenants(name="Tenant 1", db_connection_key="t1_key", is_active=True)
    t2 = Tenants(name="Tenant 2", db_connection_key="t2_key", is_active=False)
    db_session.add(t1)
    db_session.add(t2)
    db_session.commit()

    response = client.get("/tenants/list-all", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) >= 2
    names = [t["name"] for t in data]
    assert "Tenant 1" in names
    assert "Tenant 2" in names


def test_tenant_lists_metadata_are_truthful_and_stably_ordered(client, db_session, auth_headers):
    db_session.add_all(
        [
            Tenants(name="Zulu Tenant", db_connection_key="z"),
            Tenants(name="Alpha Tenant", db_connection_key="a"),
            TenantEmployees(email="later@example.com", tenant_id=None),
            TenantEmployees(email="earlier@example.com", tenant_id=None),
        ]
    )
    db_session.commit()

    tenants = client.get("/tenants/list-all?with_meta=true&skip=0&limit=1", headers=auth_headers)
    pending = client.get("/tenants/pending-users?with_meta=true&skip=0&limit=1", headers=auth_headers)

    assert tenants.status_code == 200
    assert tenants.json()["total"] == 2
    assert tenants.json()["items"][0]["name"] == "Alpha Tenant"
    assert pending.status_code == 200
    assert pending.json()["total"] == 2
    assert pending.json()["has_more"] is True
    assert pending.json()["items"][0]["email"] == "earlier@example.com"


def test_logos_metadata_filters_tenant_and_preserves_public_read(client, db_session):
    first = Tenants(name="First", db_connection_key="first")
    second = Tenants(name="Second", db_connection_key="second")
    db_session.add_all([first, second])
    db_session.commit()
    db_session.add_all(
        [
            TenantLogos(
                tenant_id=first.tenant_id,
                title="Zulu",
                logo_dark="/z-dark",
                logo_light="/z-light",
                url="z.example",
            ),
            TenantLogos(
                tenant_id=first.tenant_id,
                title="Alpha",
                logo_dark="/a-dark",
                logo_light="/a-light",
                url="a.example",
            ),
            TenantLogos(
                tenant_id=second.tenant_id,
                title="Other",
                logo_dark="/o-dark",
                logo_light="/o-light",
                url="o.example",
            ),
        ]
    )
    db_session.commit()

    response = client.get(f"/tenants/logos?tenant_id={first.tenant_id}&with_meta=true&limit=1")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 2
    assert payload["items"][0]["title"] == "Alpha"
    assert payload["has_more"] is True


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        ("post", "/tenants/", {"name": "Denied", "db_connection_key": "denied"}),
        ("post", "/tenants/approve-user", {"tenant_employee_id": 1, "tenant_id": 1}),
        ("post", "/tenants/approve", {"tenant_id": 1}),
        (
            "post",
            "/tenants/logos",
            {
                "tenant_id": 1,
                "title": "Denied",
                "logo_dark": "/d-dark",
                "logo_light": "/d-light",
                "url": "d",
            },
        ),
        ("put", "/tenants/1", {"name": "Denied"}),
        ("put", "/tenants/logos/1", {"title": "Denied"}),
        ("delete", "/tenants/1", None),
        ("delete", "/tenants/logos/1", None),
    ],
)
def test_tenant_mutations_require_matching_permission(
    client, auth_headers, permission_override, method, path, payload
):
    permission_override("tenants", set())

    response = client.request(method, path, headers=auth_headers, json=payload)

    assert response.status_code == 403


def test_create_tenant(client, db_session, auth_headers):
    """Test creating a new tenant."""
    emp = Employees(email="test@example.com", password_hash="hash", title="Dev")
    db_session.add(emp)
    db_session.commit()

    payload = {
        "name": "New Tenant",
        "db_connection_key": "new_key",
        "description": "new.com",
        "is_active": True,
    }
    response = client.post("/tenants/", json=payload, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data["name"] == "New Tenant"
    assert data["db_connection_key"] == "new_key"
    assert data["is_active"] is True


def test_list_my_tenants(client, db_session, auth_headers):
    """Test listing my tenants based on auth_headers and Employee/TenantEmployee."""
    emp = Employees(email="test@example.com", password_hash="hash", title="Dev")
    db_session.add(emp)

    t1 = Tenants(name="My Tenant", db_connection_key="my_key", is_active=True)
    t2 = Tenants(name="Not My", db_connection_key="not_my", is_active=True)
    db_session.add(t1)
    db_session.add(t2)
    db_session.commit()

    link = TenantEmployees(email="test@example.com", tenant_id=t1.tenant_id, password_hash="hash")
    db_session.add(link)
    db_session.commit()

    response = client.get("/tenants/my-tenants", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) >= 1
    assert any(d["name"] == "My Tenant" for d in data)


def test_list_pending_users(client, db_session, auth_headers):
    """Test listing pending users."""
    response = client.get("/tenants/pending-users", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert isinstance(data, list)


def test_approve_external_user(client, db_session, auth_headers):
    """Test approving external user."""
    ext_user = TenantEmployees(email="approve@example.com", password_hash="hash", tenant_id=None)
    db_session.add(ext_user)
    t = Tenants(name="Approve Tenant", db_connection_key="key", is_active=True)
    db_session.add(t)
    db_session.commit()

    emp = Employees(email="test@example.com", password_hash="hash", title="Dev")
    db_session.add(emp)
    db_session.commit()

    payload = {"tenant_employee_id": ext_user.id, "tenant_id": t.tenant_id}
    response = client.post("/tenants/approve-user", json=payload, headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["message"] == "User approved and assigned to tenant"
    assert data["tenant_id"] == t.tenant_id

    new_employee = db_session.query(Employees).filter_by(email="approve@example.com").first()
    assert new_employee is not None


def test_approve_pending_user_rejects_email_of_existing_employee(client, db_session, auth_headers):
    """Approving a pending registration must not take over an existing employee account."""
    ext_user = TenantEmployees(email="collide@example.com", password_hash="registrant-hash", tenant_id=None)
    t = Tenants(name="Collide Tenant", db_connection_key="key", is_active=True)
    victim = Employees(email="collide@example.com", password_hash="victim-hash", title="Dev")
    db_session.add_all([ext_user, t, victim])
    db_session.commit()

    payload = {"tenant_employee_id": ext_user.id, "tenant_id": t.tenant_id}
    response = client.post("/tenants/approve-user", json=payload, headers=auth_headers)

    assert response.status_code == status.HTTP_409_CONFLICT
    db_session.expire_all()
    assert db_session.get(Employees, victim.employee_id).password_hash == "victim-hash"
    assert db_session.get(TenantEmployees, ext_user.id).tenant_id is None


def test_reassigning_approved_user_keeps_existing_employee_hash(client, db_session, auth_headers):
    """Moving an already-approved user to another tenant must not rewrite their main-DB credential."""
    old_t = Tenants(name="Old Tenant", db_connection_key="key", is_active=True)
    new_t = Tenants(name="New Tenant", db_connection_key="key2", is_active=True)
    db_session.add_all([old_t, new_t])
    db_session.commit()
    ext_user = TenantEmployees(email="moved@example.com", password_hash="current-hash", tenant_id=old_t.tenant_id)
    shadow = Employees(email="moved@example.com", password_hash="shadow-hash", title="External User")
    db_session.add_all([ext_user, shadow])
    db_session.commit()

    payload = {"tenant_employee_id": ext_user.id, "tenant_id": new_t.tenant_id}
    response = client.post("/tenants/approve-user", json=payload, headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    db_session.expire_all()
    assert db_session.get(TenantEmployees, ext_user.id).tenant_id == new_t.tenant_id
    assert db_session.get(Employees, shadow.employee_id).password_hash == "shadow-hash"


def test_approve_tenant_request(client, db_session, auth_headers):
    """Test approve tenant."""
    t = Tenants(name="InActiveTenant", db_connection_key="key", is_active=False)
    db_session.add(t)

    emp = Employees(email="test@example.com", password_hash="hash", title="Dev")
    db_session.add(emp)
    db_session.commit()

    response = client.post("/tenants/approve", json={"tenant_id": t.tenant_id}, headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["is_active"] is True


def test_tenant_logos_crud(client, db_session, auth_headers):
    """Test CRUD operations on tenant logos."""
    t = Tenants(name="LogoTenant", db_connection_key="key", is_active=True)
    db_session.add(t)
    db_session.commit()

    emp = Employees(email="test@example.com", password_hash="hash", title="Dev")
    db_session.add(emp)
    db_session.commit()

    create_payload = {
        "tenant_id": t.tenant_id,
        "url": "https://example.com/logo",
        "title": "Logo title",
        "logo_dark": "/some/path-dark",
        "logo_light": "/some/path-light",
    }
    response = client.post("/tenants/logos", json=create_payload, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    logo_id = data["logo_id"] if "logo_id" in data else data.get("id", None)
    # Use whatever primary key id logo returns
    logo_id = data.get("logo_id", data.get("id"))

    response = client.get("/tenants/logos", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK

    response = client.get(f"/tenants/logos/{logo_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK

    db_session.query(TenantLogos).filter_by(logo_id=logo_id).update({"url": "mycustomurl"})
    db_session.commit()

    response = client.get("/tenants/logos/by-url/mycustomurl", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["url"] == "mycustomurl"

    update_payload = {"title": "New title logo"}
    response = client.put(f"/tenants/logos/{logo_id}", json=update_payload, headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK

    response = client.delete(f"/tenants/logos/{logo_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = client.get(f"/tenants/logos/{logo_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_and_update_tenant(client, db_session, auth_headers):
    """Test getting and updating a specific tenant."""
    t = Tenants(name="SingleTenant", db_connection_key="key", is_active=True)
    db_session.add(t)

    emp = Employees(email="test@example.com", password_hash="hash", title="Dev")
    db_session.add(emp)
    db_session.commit()

    response = client.get(f"/tenants/{t.tenant_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "SingleTenant"

    update_payload = {"name": "Updated Tenant"}
    response = client.put(f"/tenants/{t.tenant_id}", json=update_payload, headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Updated Tenant"


def _approved_external_user(db_session, email: str, password: str) -> Tenants:
    """An active tenant with one approved external user: link plus main-DB shadow, as /approve-user leaves it."""
    tenant = Tenants(name=f"Tenant of {email}", db_connection_key=f"KEY_{email}", is_active=True)
    db_session.add(tenant)
    db_session.commit()
    hashed = get_password_hash(password)
    db_session.add_all(
        [
            TenantEmployees(email=email, password_hash=hashed, tenant_id=tenant.tenant_id),
            Employees(email=email, password_hash=hashed, title="External User"),
        ]
    )
    db_session.commit()
    return tenant


def _deactivate_and_delete(client, db_session, tenant: Tenants, auth_headers) -> None:
    tenant.is_active = False
    db_session.add(tenant)
    db_session.commit()
    response = client.delete(f"/tenants/{tenant.tenant_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_deleted_tenant_member_cannot_log_in(client, db_session, auth_headers):
    """Deleting a tenant must not leave its members a password login through the main-DB shadow employee."""
    tenant = _approved_external_user(db_session, "gone@example.com", "pw-gone")

    _deactivate_and_delete(client, db_session, tenant, auth_headers)

    response = client.post("/auth/token", data={"username": "gone@example.com", "password": "pw-gone"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    db_session.expire_all()
    shadow = db_session.query(Employees).filter_by(email="gone@example.com").first()
    assert shadow is not None
    assert shadow.password_hash is None


def test_deleted_tenant_member_cannot_refresh(client, db_session, auth_headers):
    """A refresh token issued while the tenant existed must stop working once the tenant is deleted."""
    tenant = _approved_external_user(db_session, "stale@example.com", "pw-stale")
    login = client.post("/auth/token", data={"username": "stale@example.com", "password": "pw-stale"})
    assert login.status_code == status.HTTP_200_OK
    refresh_token = login.json()["refresh_token"]

    _deactivate_and_delete(client, db_session, tenant, auth_headers)

    response = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize("path", ["/tenants/list-all", "/tenants/pending-users"])
def test_tenant_admin_listings_reject_anonymous_callers(client, db_session, path):
    """Tenant directory (with db_connection_key) and pending registrants are not public."""
    db_session.add_all([Tenants(name="Secret Tenant", db_connection_key="SECRET"), TenantEmployees(email="p@x.com")])
    db_session.commit()
    app.dependency_overrides.pop(get_current_employee_with_permissions, None)

    response = client.get(path)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "SECRET" not in response.text


@pytest.mark.parametrize("path", ["/tenants/list-all", "/tenants/pending-users"])
def test_tenant_admin_listings_require_tenants_can_view(client, auth_headers, permission_override, path):
    permission_override("tenants", set())

    response = client.get(path, headers=auth_headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN
