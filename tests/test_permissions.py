"""Tests for Permissions API endpoints."""

from fastapi.testclient import TestClient
from sqlmodel import Session

from api.dependencies import get_current_employee_with_permissions
from main import app
from models.employees import Roles
from models.modules import Modules, RoleModules


class TestPermissionsAPI:
    """Test cases for Permissions API endpoints."""

    def _create_role_and_module(self, db_session: Session):
        """Helper to create a role and module."""
        role = Roles(role_name="Permission Role")
        db_session.add(role)
        module = Modules(module_name="Test Module", module_key="test_module_key")
        db_session.add(module)
        db_session.commit()
        db_session.refresh(role)
        db_session.refresh(module)
        return role, module

    def test_create_permission(self, client: TestClient, db_session: Session, auth_headers: dict) -> None:
        """Test POST /permissions."""
        role, module = self._create_role_and_module(db_session)

        data = {
            "role_id": role.role_id,
            "module_id": module.module_id,
            "can_view": True,
            "can_create": True,
            "can_edit": False,
            "can_delete": False,
            "can_export": False,
            "admin_actions": False,
            "other_actions": False,
        }

        response = client.post("/permissions", json=data, headers=auth_headers)

        # Check if router uses trailing slash
        if response.status_code in {307, 404}:
            response = client.post("/permissions/", json=data, headers=auth_headers)

        assert response.status_code == 200
        resp_data = response.json()
        assert resp_data["role_id"] == role.role_id
        assert resp_data["module_id"] == module.module_id
        assert resp_data["can_view"] is True
        assert resp_data["can_create"] is True

    def test_create_permission_already_exists(
        self, client: TestClient, db_session: Session, auth_headers: dict
    ) -> None:
        """Test POST /permissions when it already exists."""
        role, module = self._create_role_and_module(db_session)
        rm = RoleModules(role_id=role.role_id, module_id=module.module_id, can_view=True)
        db_session.add(rm)
        db_session.commit()

        data = {"role_id": role.role_id, "module_id": module.module_id}
        response = client.post("/permissions", json=data, headers=auth_headers)
        if response.status_code in {307, 404}:
            response = client.post("/permissions/", json=data, headers=auth_headers)

        assert response.status_code == 400
        assert "Permission already exists" in response.json()["detail"]

    def test_get_all_permissions(self, client: TestClient, db_session: Session, auth_headers: dict) -> None:
        """Test GET /permissions."""
        role, module = self._create_role_and_module(db_session)
        rm = RoleModules(role_id=role.role_id, module_id=module.module_id, can_view=True)
        db_session.add(rm)
        db_session.commit()

        response = client.get("/permissions", headers=auth_headers)
        if response.status_code in {307, 404}:
            response = client.get("/permissions/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["role_name"] is not None
        assert data[0]["module_name"] is not None

    def test_get_role_permissions(self, client: TestClient, db_session: Session, auth_headers: dict) -> None:
        """Test GET /permissions/role/{role_id}."""
        role, module = self._create_role_and_module(db_session)
        rm = RoleModules(role_id=role.role_id, module_id=module.module_id, can_view=True)
        db_session.add(rm)
        db_session.commit()

        response = client.get(f"/permissions/role/{role.role_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["role_id"] == role.role_id
        assert data["role_name"] == role.role_name
        assert len(data["permissions"]) == 1

    def test_get_module_permissions(self, client: TestClient, db_session: Session, auth_headers: dict) -> None:
        """Test GET /permissions/module/{module_id}."""
        role, module = self._create_role_and_module(db_session)
        rm = RoleModules(role_id=role.role_id, module_id=module.module_id, can_view=True)
        db_session.add(rm)
        db_session.commit()

        response = client.get(f"/permissions/module/{module.module_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["role_id"] == role.role_id

    def test_get_specific_permission(self, client: TestClient, db_session: Session, auth_headers: dict) -> None:
        """Test GET /permissions/{role_id}/{module_id}."""
        role, module = self._create_role_and_module(db_session)
        rm = RoleModules(role_id=role.role_id, module_id=module.module_id, can_view=True)
        db_session.add(rm)
        db_session.commit()

        response = client.get(f"/permissions/{role.role_id}/{module.module_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["role_id"] == role.role_id
        assert data["module_id"] == module.module_id

    def test_update_permission(self, client: TestClient, db_session: Session, auth_headers: dict) -> None:
        """Test PUT /permissions/{role_id}/{module_id}."""
        role, module = self._create_role_and_module(db_session)
        rm = RoleModules(role_id=role.role_id, module_id=module.module_id, can_view=True, can_edit=False)
        db_session.add(rm)
        db_session.commit()

        update_data = {"can_edit": True}
        response = client.put(f"/permissions/{role.role_id}/{module.module_id}", json=update_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["can_edit"] is True

        # Verify DB
        db_session.refresh(rm)
        assert rm.can_edit is True

    def test_delete_permission(self, client: TestClient, db_session: Session, auth_headers: dict) -> None:
        """Test DELETE /permissions/{role_id}/{module_id}."""
        role, module = self._create_role_and_module(db_session)
        rm = RoleModules(role_id=role.role_id, module_id=module.module_id, can_view=True)
        db_session.add(rm)
        db_session.commit()

        response = client.delete(f"/permissions/{role.role_id}/{module.module_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["detail"] == "Permission deleted successfully"

        # Verify DB
        deleted = db_session.get(RoleModules, (role.role_id, module.module_id))
        assert deleted is None

    def test_bulk_update_permissions(self, client: TestClient, db_session: Session, auth_headers: dict) -> None:
        """Test POST /permissions/bulk-update."""
        role, module_1 = self._create_role_and_module(db_session)
        module_2 = Modules(module_name="Test Module 2", module_key="test_module_key_2")
        db_session.add(module_2)
        db_session.commit()
        db_session.refresh(module_2)

        # Give an existing permission
        rm = RoleModules(role_id=role.role_id, module_id=module_1.module_id, can_view=True)
        db_session.add(rm)
        db_session.commit()

        # Update with new bulk request (this should replace the olds)
        bulk_data = {
            "role_id": role.role_id,
            "permissions": [{"role_id": role.role_id, "module_id": module_2.module_id, "can_view": True, "can_edit": True}],
        }

        response = client.post("/permissions/bulk-update", json=bulk_data, headers=auth_headers)
        assert response.status_code == 200

        # Now DB should only have the module_2 permission
        db_perms = db_session.query(RoleModules).filter(RoleModules.role_id == role.role_id).all()
        assert len(db_perms) == 1
        assert db_perms[0].module_id == module_2.module_id
        assert db_perms[0].can_edit is True

    def test_check_user_permission(self, client: TestClient, db_session: Session, auth_headers: dict) -> None:
        """Test GET /permissions/check/{module_key}/{action}."""
        module = Modules(module_name="Check Module", module_key="check_key")
        db_session.add(module)
        db_session.commit()

        response = client.get("/permissions/check/check_key/view", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["module_key"] == "check_key"
        assert data["action"] == "view"
        assert data["allowed"] is True

    def test_get_current_user_permissions(self, client: TestClient, auth_headers: dict) -> None:
        """Test GET /permissions/me."""
        mock_data = {"employee": {"employee_id": 1}, "roles": [], "permissions": [], "accessible_modules": []}

        # Override the dependency
        app.dependency_overrides[get_current_employee_with_permissions] = lambda: mock_data

        try:
            response = client.get("/permissions/me", headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert data["employee"]["employee_id"] == 1
        finally:
            # Clean up the override
            del app.dependency_overrides[get_current_employee_with_permissions]