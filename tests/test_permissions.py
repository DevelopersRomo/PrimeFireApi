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
        role = Roles(RoleName="Permission Role")
        db_session.add(role)
        module = Modules(ModuleName="Test Module", ModuleKey="test_module_key")
        db_session.add(module)
        db_session.commit()
        db_session.refresh(role)
        db_session.refresh(module)
        return role, module

    def test_create_permission(self, client: TestClient, db_session: Session, auth_headers: dict) -> None:
        """Test POST /permissions."""
        role, module = self._create_role_and_module(db_session)

        data = {
            "RoleId": role.RoleId,
            "ModuleId": module.ModuleId,
            "CanView": True,
            "CanCreate": True,
            "CanEdit": False,
            "CanDelete": False,
            "CanExport": False,
            "AdminActions": False,
            "OtherActions": False,
        }

        response = client.post("/permissions", json=data, headers=auth_headers)

        # Check if router uses trailing slash
        if response.status_code in {307, 404}:
            response = client.post("/permissions/", json=data, headers=auth_headers)

        assert response.status_code == 200
        resp_data = response.json()
        assert resp_data["RoleId"] == role.RoleId
        assert resp_data["ModuleId"] == module.ModuleId
        assert resp_data["CanView"] is True
        assert resp_data["CanCreate"] is True

    def test_create_permission_already_exists(
        self, client: TestClient, db_session: Session, auth_headers: dict
    ) -> None:
        """Test POST /permissions when it already exists."""
        role, module = self._create_role_and_module(db_session)
        rm = RoleModules(RoleId=role.RoleId, ModuleId=module.ModuleId, CanView=True)
        db_session.add(rm)
        db_session.commit()

        data = {"RoleId": role.RoleId, "ModuleId": module.ModuleId}
        response = client.post("/permissions", json=data, headers=auth_headers)
        if response.status_code in {307, 404}:
            response = client.post("/permissions/", json=data, headers=auth_headers)

        assert response.status_code == 400
        assert "Permission already exists" in response.json()["detail"]

    def test_get_all_permissions(self, client: TestClient, db_session: Session, auth_headers: dict) -> None:
        """Test GET /permissions."""
        role, module = self._create_role_and_module(db_session)
        rm = RoleModules(RoleId=role.RoleId, ModuleId=module.ModuleId, CanView=True)
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
        rm = RoleModules(RoleId=role.RoleId, ModuleId=module.ModuleId, CanView=True)
        db_session.add(rm)
        db_session.commit()

        response = client.get(f"/permissions/role/{role.RoleId}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["RoleId"] == role.RoleId
        assert data["RoleName"] == role.RoleName
        assert len(data["permissions"]) == 1

    def test_get_module_permissions(self, client: TestClient, db_session: Session, auth_headers: dict) -> None:
        """Test GET /permissions/module/{module_id}."""
        role, module = self._create_role_and_module(db_session)
        rm = RoleModules(RoleId=role.RoleId, ModuleId=module.ModuleId, CanView=True)
        db_session.add(rm)
        db_session.commit()

        response = client.get(f"/permissions/module/{module.ModuleId}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["RoleId"] == role.RoleId

    def test_get_specific_permission(self, client: TestClient, db_session: Session, auth_headers: dict) -> None:
        """Test GET /permissions/{role_id}/{module_id}."""
        role, module = self._create_role_and_module(db_session)
        rm = RoleModules(RoleId=role.RoleId, ModuleId=module.ModuleId, CanView=True)
        db_session.add(rm)
        db_session.commit()

        response = client.get(f"/permissions/{role.RoleId}/{module.ModuleId}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["RoleId"] == role.RoleId
        assert data["ModuleId"] == module.ModuleId

    def test_update_permission(self, client: TestClient, db_session: Session, auth_headers: dict) -> None:
        """Test PUT /permissions/{role_id}/{module_id}."""
        role, module = self._create_role_and_module(db_session)
        rm = RoleModules(RoleId=role.RoleId, ModuleId=module.ModuleId, CanView=True, CanEdit=False)
        db_session.add(rm)
        db_session.commit()

        update_data = {"CanEdit": True}
        response = client.put(f"/permissions/{role.RoleId}/{module.ModuleId}", json=update_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["CanEdit"] is True

        # Verify DB
        db_session.refresh(rm)
        assert rm.CanEdit is True

    def test_delete_permission(self, client: TestClient, db_session: Session, auth_headers: dict) -> None:
        """Test DELETE /permissions/{role_id}/{module_id}."""
        role, module = self._create_role_and_module(db_session)
        rm = RoleModules(RoleId=role.RoleId, ModuleId=module.ModuleId, CanView=True)
        db_session.add(rm)
        db_session.commit()

        response = client.delete(f"/permissions/{role.RoleId}/{module.ModuleId}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["detail"] == "Permission deleted successfully"

        # Verify DB
        deleted = db_session.get(RoleModules, (role.RoleId, module.ModuleId))
        assert deleted is None

    def test_bulk_update_permissions(self, client: TestClient, db_session: Session, auth_headers: dict) -> None:
        """Test POST /permissions/bulk-update."""
        role, module_1 = self._create_role_and_module(db_session)
        module_2 = Modules(ModuleName="Test Module 2", ModuleKey="test_module_key_2")
        db_session.add(module_2)
        db_session.commit()
        db_session.refresh(module_2)

        # Give an existing permission
        rm = RoleModules(RoleId=role.RoleId, ModuleId=module_1.ModuleId, CanView=True)
        db_session.add(rm)
        db_session.commit()

        # Update with new bulk request (this should replace the olds)
        bulk_data = {
            "RoleId": role.RoleId,
            "permissions": [{"RoleId": role.RoleId, "ModuleId": module_2.ModuleId, "CanView": True, "CanEdit": True}],
        }

        response = client.post("/permissions/bulk-update", json=bulk_data, headers=auth_headers)
        assert response.status_code == 200

        # Now DB should only have the module_2 permission
        db_perms = db_session.query(RoleModules).filter(RoleModules.RoleId == role.RoleId).all()
        assert len(db_perms) == 1
        assert db_perms[0].ModuleId == module_2.ModuleId
        assert db_perms[0].CanEdit is True

    def test_check_user_permission(self, client: TestClient, db_session: Session, auth_headers: dict) -> None:
        """Test GET /permissions/check/{module_key}/{action}."""
        module = Modules(ModuleName="Check Module", ModuleKey="check_key")
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
        mock_data = {"employee": {"EmployeeId": 1}, "roles": [], "permissions": [], "accessible_modules": []}

        # Override the dependency
        app.dependency_overrides[get_current_employee_with_permissions] = lambda: mock_data

        try:
            response = client.get("/permissions/me", headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert data["employee"]["EmployeeId"] == 1
        finally:
            # Clean up the override
            del app.dependency_overrides[get_current_employee_with_permissions]
