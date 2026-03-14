from fastapi import status

from models.employees import Employees
from models.tenants import TenantEmployees, TenantLogos, Tenants


def test_list_all_tenants(client, db_session, auth_headers):
    """Test listing all tenants."""
    # Create test tenants
    t1 = Tenants(Name="Tenant 1", DbConnectionKey="t1_key", IsActive=True)
    t2 = Tenants(Name="Tenant 2", DbConnectionKey="t2_key", IsActive=False)
    db_session.add(t1)
    db_session.add(t2)
    db_session.commit()

    response = client.get("/tenants/list-all", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) >= 2
    names = [t["Name"] for t in data]
    assert "Tenant 1" in names
    assert "Tenant 2" in names


def test_create_tenant(client, db_session, auth_headers):
    """Test creating a new tenant."""
    emp = Employees(Email="test@example.com", PasswordHash="hash", Title="Dev")
    db_session.add(emp)
    db_session.commit()

    payload = {
        "Name": "New Tenant",
        "DbConnectionKey": "new_key",
        "Description": "new.com",
        "IsActive": True,
    }
    response = client.post("/tenants/", json=payload, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data["Name"] == "New Tenant"
    assert data["DbConnectionKey"] == "new_key"
    assert data["IsActive"] is True


def test_list_my_tenants(client, db_session, auth_headers):
    """Test listing my tenants based on auth_headers and Employee/TenantEmployee."""
    emp = Employees(Email="test@example.com", PasswordHash="hash", Title="Dev")
    db_session.add(emp)

    t1 = Tenants(Name="My Tenant", DbConnectionKey="my_key", IsActive=True)
    t2 = Tenants(Name="Not My", DbConnectionKey="not_my", IsActive=True)
    db_session.add(t1)
    db_session.add(t2)
    db_session.commit()

    link = TenantEmployees(Email="test@example.com", TenantId=t1.TenantId, PasswordHash="hash")
    db_session.add(link)
    db_session.commit()

    response = client.get("/tenants/my-tenants", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) >= 1
    assert any(d["Name"] == "My Tenant" for d in data)


def test_list_pending_users(client, db_session, auth_headers):
    """Test listing pending users."""
    response = client.get("/tenants/pending-users", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert isinstance(data, list)


def test_approve_external_user(client, db_session, auth_headers):
    """Test approving external user."""
    ext_user = TenantEmployees(Email="approve@example.com", PasswordHash="hash", TenantId=None)
    db_session.add(ext_user)
    t = Tenants(Name="Approve Tenant", DbConnectionKey="key", IsActive=True)
    db_session.add(t)
    db_session.commit()

    emp = Employees(Email="test@example.com", PasswordHash="hash", Title="Dev")
    db_session.add(emp)
    db_session.commit()

    payload = {"TenantEmployeeId": ext_user.Id, "TenantId": t.TenantId}
    response = client.post("/tenants/approve-user", json=payload, headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["message"] == "User approved and assigned to tenant"
    assert data["tenant_id"] == t.TenantId

    new_employee = db_session.query(Employees).filter_by(Email="approve@example.com").first()
    assert new_employee is not None


def test_approve_tenant_request(client, db_session, auth_headers):
    """Test approve tenant."""
    t = Tenants(Name="InActiveTenant", DbConnectionKey="key", IsActive=False)
    db_session.add(t)

    emp = Employees(Email="test@example.com", PasswordHash="hash", Title="Dev")
    db_session.add(emp)
    db_session.commit()

    response = client.post("/tenants/approve", json={"TenantId": t.TenantId}, headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["IsActive"] is True


def test_tenant_logos_crud(client, db_session, auth_headers):
    """Test CRUD operations on tenant logos."""
    t = Tenants(Name="LogoTenant", DbConnectionKey="key", IsActive=True)
    db_session.add(t)
    db_session.commit()

    emp = Employees(Email="test@example.com", PasswordHash="hash", Title="Dev")
    db_session.add(emp)
    db_session.commit()

    create_payload = {
        "TenantId": t.TenantId,
        "Url": "https://example.com/logo",
        "Title": "Logo title",
        "Path": "/some/path",
    }
    response = client.post("/tenants/logos", json=create_payload, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    logo_id = data["LogoId"] if "LogoId" in data else data.get("Id", None)
    # Use whatever primary key id logo returns
    logo_id = data.get("LogoId", data.get("Id"))

    response = client.get("/tenants/logos", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK

    response = client.get(f"/tenants/logos/{logo_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK

    db_session.query(TenantLogos).filter_by(LogoId=logo_id).update({"Url": "mycustomurl"})
    db_session.commit()

    response = client.get("/tenants/logos/by-url/mycustomurl", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["Url"] == "mycustomurl"

    update_payload = {"Title": "New title logo"}
    response = client.put(f"/tenants/logos/{logo_id}", json=update_payload, headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK

    response = client.delete(f"/tenants/logos/{logo_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = client.get(f"/tenants/logos/{logo_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_and_update_tenant(client, db_session, auth_headers):
    """Test getting and updating a specific tenant."""
    t = Tenants(Name="SingleTenant", DbConnectionKey="key", IsActive=True)
    db_session.add(t)

    emp = Employees(Email="test@example.com", PasswordHash="hash", Title="Dev")
    db_session.add(emp)
    db_session.commit()

    response = client.get(f"/tenants/{t.TenantId}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["Name"] == "SingleTenant"

    update_payload = {"Name": "Updated Tenant"}
    response = client.put(f"/tenants/{t.TenantId}", json=update_payload, headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["Name"] == "Updated Tenant"
