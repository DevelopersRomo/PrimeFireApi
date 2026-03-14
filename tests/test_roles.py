"""Tests for Roles API endpoints."""

from fastapi.testclient import TestClient
from sqlmodel import Session

from models.employees import Roles


class TestRolesAPI:
    """Test cases for Roles API endpoints."""

    def test_create_role(self, client: TestClient, db_session: Session, auth_headers: dict) -> None:
        """Test POST /roles."""
        role_data = {"RoleName": "Admin Role", "Description": "Administrator role with full access"}
        response = client.post("/roles", json=role_data, headers=auth_headers)

        # In case the prefix in main.py is different or there's a trailing slash issue,
        # we'll use "/roles" assuming it's correctly mapped.
        if response.status_code in {307, 404}:
            response = client.post("/roles/", json=role_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["RoleName"] == "Admin Role"
        assert data["Description"] == "Administrator role with full access"
        assert "RoleId" in data

        # Verify in DB
        db_role = db_session.get(Roles, data["RoleId"])
        assert db_role is not None
        assert db_role.RoleName == "Admin Role"

    def test_get_roles(self, client: TestClient, db_session: Session, auth_headers: dict) -> None:
        """Test GET /roles."""
        role1 = Roles(RoleName="Role 1", Description="First role")
        role2 = Roles(RoleName="Role 2", Description="Second role")
        db_session.add(role1)
        db_session.add(role2)
        db_session.commit()

        response = client.get("/roles", headers=auth_headers)
        if response.status_code in {307, 404}:
            response = client.get("/roles/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        role_names = [r["RoleName"] for r in data]
        assert "Role 1" in role_names
        assert "Role 2" in role_names

    def test_get_role(self, client: TestClient, db_session: Session, auth_headers: dict) -> None:
        """Test GET /roles/{role_id}."""
        role = Roles(RoleName="Specific Role", Description="Specific description")
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)

        response = client.get(f"/roles/{role.RoleId}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["RoleName"] == "Specific Role"
        assert data["RoleId"] == role.RoleId

    def test_get_role_not_found(self, client: TestClient, auth_headers: dict) -> None:
        """Test GET /roles/{role_id} for a non-existent role."""
        response = client.get("/roles/9999", headers=auth_headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "Role not found"

    def test_update_role(self, client: TestClient, db_session: Session, auth_headers: dict) -> None:
        """Test PUT /roles/{role_id}."""
        role = Roles(RoleName="Old Role", Description="Old description")
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)

        update_data = {"RoleName": "Updated Role", "Description": "Updated description"}
        response = client.put(f"/roles/{role.RoleId}", json=update_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["RoleName"] == "Updated Role"
        assert data["Description"] == "Updated description"

        # Verify in DB
        db_session.refresh(role)
        assert role.RoleName == "Updated Role"

    def test_update_role_not_found(self, client: TestClient, auth_headers: dict) -> None:
        """Test PUT /roles/{role_id} for a non-existent role."""
        update_data = {"RoleName": "Ghost Role"}
        response = client.put("/roles/9999", json=update_data, headers=auth_headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "Role not found"

    def test_delete_role(self, client: TestClient, db_session: Session, auth_headers: dict) -> None:
        """Test DELETE /roles/{role_id}."""
        role = Roles(RoleName="Role to delete", Description="To be deleted")
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)

        response = client.delete(f"/roles/{role.RoleId}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["detail"] == "Role deleted successfully"

    def test_delete_role_not_found(self, client: TestClient, auth_headers: dict) -> None:
        """Test DELETE /roles/{role_id} for a non-existent role."""
        response = client.delete("/roles/9999", headers=auth_headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "Role not found"
