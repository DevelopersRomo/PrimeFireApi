"""Tests for Roles API endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from models.employees import Roles


@pytest.fixture(autouse=True)
def _grant_role_mutations(permission_override) -> None:
    permission_override("roles", {"can_create", "can_edit", "can_delete"})


class TestRolesAPI:
    """Test cases for Roles API endpoints."""

    def test_create_role(self, client: TestClient, db_session: Session, auth_headers: dict) -> None:
        """Test POST /roles."""
        role_data = {"role_name": "Admin Role", "description": "Administrator role with full access"}
        response = client.post("/roles", json=role_data, headers=auth_headers)

        # In case the prefix in main.py is different or there's a trailing slash issue,
        # we'll use "/roles" assuming it's correctly mapped.
        if response.status_code in {307, 404}:
            response = client.post("/roles/", json=role_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["role_name"] == "Admin Role"
        assert data["description"] == "Administrator role with full access"
        assert "role_id" in data

        # Verify in DB
        db_role = db_session.get(Roles, data["role_id"])
        assert db_role is not None
        assert db_role.role_name == "Admin Role"

    def test_get_roles(self, client: TestClient, db_session: Session, auth_headers: dict) -> None:
        """Test GET /roles."""
        role1 = Roles(role_name="Role 1", description="First role")
        role2 = Roles(role_name="Role 2", description="Second role")
        db_session.add(role1)
        db_session.add(role2)
        db_session.commit()

        response = client.get("/roles", headers=auth_headers)
        if response.status_code in {307, 404}:
            response = client.get("/roles/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        role_names = [r["role_name"] for r in data]
        assert "Role 1" in role_names
        assert "Role 2" in role_names

    def test_get_roles_metadata_is_ordered_and_truthful(
        self, client: TestClient, db_session: Session, auth_headers: dict
    ) -> None:
        db_session.add_all([Roles(role_name="Zulu"), Roles(role_name="Alpha")])
        db_session.commit()

        response = client.get("/roles?with_meta=true&skip=0&limit=1", headers=auth_headers)

        assert response.status_code == 200
        payload = response.json()
        assert payload["total"] == 2
        assert payload["has_more"] is True
        assert payload["items"][0]["role_name"] == "Alpha"

    @pytest.mark.parametrize(
        ("method", "path", "payload"),
        [
            ("post", "/roles", {"role_name": "Denied"}),
            ("put", "/roles/999", {"role_name": "Denied"}),
            ("delete", "/roles/999", None),
        ],
    )
    def test_role_mutations_require_matching_permission(
        self, client: TestClient, auth_headers: dict, permission_override, method, path, payload
    ) -> None:
        permission_override("roles", set())

        response = client.request(method, path, json=payload, headers=auth_headers)

        assert response.status_code == 403

    def test_get_role(self, client: TestClient, db_session: Session, auth_headers: dict) -> None:
        """Test GET /roles/{role_id}."""
        role = Roles(role_name="Specific Role", description="Specific description")
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)

        response = client.get(f"/roles/{role.role_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["role_name"] == "Specific Role"
        assert data["role_id"] == role.role_id

    def test_get_role_not_found(self, client: TestClient, auth_headers: dict) -> None:
        """Test GET /roles/{role_id} for a non-existent role."""
        response = client.get("/roles/9999", headers=auth_headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "Role not found"

    def test_update_role(self, client: TestClient, db_session: Session, auth_headers: dict) -> None:
        """Test PUT /roles/{role_id}."""
        role = Roles(role_name="Old Role", description="Old description")
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)

        update_data = {"role_name": "Updated Role", "description": "Updated description"}
        response = client.put(f"/roles/{role.role_id}", json=update_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["role_name"] == "Updated Role"
        assert data["description"] == "Updated description"

        # Verify in DB
        db_session.refresh(role)
        assert role.role_name == "Updated Role"

    def test_update_role_not_found(self, client: TestClient, auth_headers: dict) -> None:
        """Test PUT /roles/{role_id} for a non-existent role."""
        update_data = {"role_name": "Ghost Role"}
        response = client.put("/roles/9999", json=update_data, headers=auth_headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "Role not found"

    def test_delete_role(self, client: TestClient, db_session: Session, auth_headers: dict) -> None:
        """Test DELETE /roles/{role_id}."""
        role = Roles(role_name="Role to delete", description="To be deleted")
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)

        response = client.delete(f"/roles/{role.role_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["detail"] == "Role deleted successfully"

    def test_delete_role_not_found(self, client: TestClient, auth_headers: dict) -> None:
        """Test DELETE /roles/{role_id} for a non-existent role."""
        response = client.delete("/roles/9999", headers=auth_headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "Role not found"
