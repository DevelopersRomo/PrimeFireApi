import pytest
from fastapi import status

from models.employees import Employees
from models.tenants import TenantEmployees, TenantLogos, Tenants


@pytest.fixture(autouse=True)
def _grant_tenant_mutations(permission_override) -> None:
    permission_override("tenants", {"can_create", "can_edit", "can_delete"})


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
            TenantLogos(tenant_id=first.tenant_id, title="Zulu", path="/z", url="z.example"),
            TenantLogos(tenant_id=first.tenant_id, title="Alpha", path="/a", url="a.example"),
            TenantLogos(tenant_id=second.tenant_id, title="Other", path="/o", url="o.example"),
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
        ("post", "/tenants/logos", {"tenant_id": 1, "title": "Denied", "path": "/d", "url": "d"}),
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
        "path": "/some/path",
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
