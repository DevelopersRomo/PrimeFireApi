import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from models.modules import Modules
from models.employees import Roles


@pytest.fixture
def sample_module_data():
    """Sample module data for testing."""
    return {
        "ModuleName": "Test Module",
        "ModuleKey": "test_module",
        "Description": "A test module",
        "Icon": "test_icon",
        "RouteUrl": "/test",
        "DisplayOrder": 99,
        "IsActive": True,
        "ParentModuleId": None,
    }


@pytest.fixture
def sample_permission_data():
    """Sample permission data for testing."""
    return {
        "RoleId": 1,
        "ModuleId": 1,
        "CanView": True,
        "CanCreate": True,
        "CanEdit": True,
        "CanDelete": False,
        "CanExport": True,
        "AdminActions": False,
        "OtherActions": False,
    }


@pytest.fixture
def test_role(db_session: Session):
    """Create a test role."""
    role = Roles(RoleId=1, RoleName="Admin", Description="Admin role")
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)
    return role


@pytest.fixture
def test_module(db_session: Session):
    """Create a test module."""
    module = Modules(
        ModuleId=1,
        ModuleName="Dashboard",
        ModuleKey="dashboard",
        Description="Dashboard module",
        Icon="dashboard",
        RouteUrl="/dashboard",
        DisplayOrder=1,
        IsActive=True,
    )
    db_session.add(module)
    db_session.commit()
    db_session.refresh(module)
    return module


@pytest.fixture
def test_role_user(db_session: Session):
    """Create a test user role."""
    role = Roles(RoleId=3, RoleName="User", Description="Regular user role")
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)
    return role


class TestModules:
    """Test suite for Modules endpoints."""

    def test_create_module(self, client: TestClient, auth_headers: dict, sample_module_data: dict) -> None:
        """Test creating a new module."""
        response = client.post("/modules/", json=sample_module_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["ModuleName"] == sample_module_data["ModuleName"]
        assert data["ModuleKey"] == sample_module_data["ModuleKey"]
        assert "ModuleId" in data

    def test_create_module_duplicate_key(
        self, client: TestClient, auth_headers: dict, sample_module_data: dict
    ) -> None:
        """Test creating a module with duplicate key fails."""
        # Create first module
        client.post("/modules/", json=sample_module_data, headers=auth_headers)

        # Try to create duplicate
        response = client.post("/modules/", json=sample_module_data, headers=auth_headers)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_get_modules(self, client: TestClient, auth_headers: dict) -> None:
        """Test getting all modules."""
        response = client.get("/modules/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_module_by_id(self, client: TestClient, auth_headers: dict, sample_module_data: dict) -> None:
        """Test getting a specific module by ID."""
        # Create module
        create_response = client.post("/modules/", json=sample_module_data, headers=auth_headers)
        module_id = create_response.json()["ModuleId"]

        # Get module
        response = client.get(f"/modules/{module_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["ModuleId"] == module_id
        assert data["ModuleName"] == sample_module_data["ModuleName"]

    def test_get_module_by_key(self, client: TestClient, auth_headers: dict, sample_module_data: dict) -> None:
        """Test getting a specific module by key."""
        # Create module
        client.post("/modules/", json=sample_module_data, headers=auth_headers)

        # Get module by key
        response = client.get(f"/modules/by-key/{sample_module_data['ModuleKey']}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["ModuleKey"] == sample_module_data["ModuleKey"]

    def test_get_root_modules(self, client: TestClient, auth_headers: dict) -> None:
        """Test getting root modules."""
        response = client.get("/modules/root/all", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # All modules should have ParentModuleId as None
        for module in data:
            assert module["ParentModuleId"] is None

    def test_update_module(self, client: TestClient, auth_headers: dict, sample_module_data: dict) -> None:
        """Test updating a module."""
        # Create module
        create_response = client.post("/modules/", json=sample_module_data, headers=auth_headers)
        module_id = create_response.json()["ModuleId"]

        # Update module
        update_data = {"ModuleName": "Updated Module Name"}
        response = client.put(f"/modules/{module_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["ModuleName"] == "Updated Module Name"

    def test_toggle_module_active(self, client: TestClient, auth_headers: dict, sample_module_data: dict) -> None:
        """Test toggling module active status."""
        # Create module
        create_response = client.post("/modules/", json=sample_module_data, headers=auth_headers)
        module_id = create_response.json()["ModuleId"]
        original_status = create_response.json()["IsActive"]

        # Toggle status
        response = client.patch(f"/modules/{module_id}/toggle-active", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["IsActive"] != original_status

    def test_delete_module(self, client: TestClient, auth_headers: dict, sample_module_data: dict) -> None:
        """Test deleting a module."""
        # Create module
        create_response = client.post("/modules/", json=sample_module_data, headers=auth_headers)
        module_id = create_response.json()["ModuleId"]

        # Delete module
        response = client.delete(f"/modules/{module_id}", headers=auth_headers)
        assert response.status_code == 200

        # Verify deletion
        get_response = client.get(f"/modules/{module_id}", headers=auth_headers)
        assert get_response.status_code == 404

    def test_delete_module_with_children_fails(
        self, client: TestClient, auth_headers: dict, sample_module_data: dict
    ) -> None:
        """Test that deleting a module with children fails."""
        # Create parent module
        parent_response = client.post("/modules/", json=sample_module_data, headers=auth_headers)
        parent_id = parent_response.json()["ModuleId"]

        # Create child module
        child_data = {**sample_module_data, "ModuleKey": "child_module", "ParentModuleId": parent_id}
        client.post("/modules/", json=child_data, headers=auth_headers)

        # Try to delete parent
        response = client.delete(f"/modules/{parent_id}", headers=auth_headers)
        assert response.status_code == 400
        assert "children" in response.json()["detail"].lower()


class TestPermissions:
    """Test suite for Permissions endpoints."""

    def test_create_permission(
        self,
        client: TestClient,
        auth_headers: dict,
        sample_permission_data: dict,
        db_session: Session,
        test_role,
        test_module,
    ) -> None:
        """Test creating a new permission."""
        response = client.post("/permissions", json=sample_permission_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["RoleId"] == sample_permission_data["RoleId"]
        assert data["ModuleId"] == sample_permission_data["ModuleId"]
        assert data["CanView"] == sample_permission_data["CanView"]

    def test_get_all_permissions(self, client: TestClient, auth_headers: dict) -> None:
        """Test getting all permissions."""
        response = client.get("/permissions", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_role_permissions(self, client: TestClient, auth_headers: dict, db_session: Session, test_role) -> None:
        """Test getting permissions for a specific role."""
        role_id = 1  # Admin role
        response = client.get(f"/permissions/role/{role_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["RoleId"] == role_id
        assert "RoleName" in data
        assert "permissions" in data
        assert isinstance(data["permissions"], list)

    def test_get_module_permissions(self, client: TestClient, auth_headers: dict, db_session: Session, test_module) -> None:
        """Test getting permissions for a specific module."""
        module_id = 1  # Dashboard module
        response = client.get(f"/permissions/module/{module_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_specific_permission(self, client: TestClient, auth_headers: dict, db_session: Session, test_role, test_module, sample_permission_data) -> None:
        """Test getting a specific permission."""
        # First create the permission
        client.post("/permissions", json=sample_permission_data, headers=auth_headers)

        role_id = 1
        module_id = 1
        response = client.get(f"/permissions/{role_id}/{module_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["RoleId"] == role_id
        assert data["ModuleId"] == module_id

    def test_update_permission(self, client: TestClient, auth_headers: dict, db_session: Session, test_role, test_module, sample_permission_data) -> None:
        """Test updating a permission."""
        # First create the permission
        client.post("/permissions", json=sample_permission_data, headers=auth_headers)

        role_id = 1
        module_id = 1
        update_data = {"CanDelete": False}

        response = client.put(f"/permissions/{role_id}/{module_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert not data["CanDelete"]

    def test_delete_permission(self, client: TestClient, auth_headers: dict, sample_permission_data: dict, db_session: Session, test_role, test_module) -> None:
        """Test deleting a permission."""
        # Create permission
        create_response = client.post("/permissions", json=sample_permission_data, headers=auth_headers)
        role_id = create_response.json()["RoleId"]
        module_id = create_response.json()["ModuleId"]

        # Delete permission
        response = client.delete(f"/permissions/{role_id}/{module_id}", headers=auth_headers)
        assert response.status_code == 200

        # Verify deletion
        get_response = client.get(f"/permissions/{role_id}/{module_id}", headers=auth_headers)
        assert get_response.status_code == 404

    def test_bulk_update_permissions(self, client: TestClient, auth_headers: dict, db_session: Session, test_role_user, test_module) -> None:
        """Test bulk updating permissions for a role."""
        # Create second module for bulk test
        module2 = Modules(
            ModuleId=2,
            ModuleName="Settings",
            ModuleKey="settings",
            Description="Settings module",
            Icon="settings",
            RouteUrl="/settings",
            DisplayOrder=2,
            IsActive=True,
        )
        db_session.add(module2)
        db_session.commit()

        bulk_data = {
            "RoleId": 3,  # User role
            "permissions": [
                {
                    "RoleId": 3,
                    "ModuleId": 1,
                    "CanView": True,
                    "CanCreate": False,
                    "CanEdit": False,
                    "CanDelete": False,
                    "CanExport": False,
                    "AdminActions": False,
                    "OtherActions": False,
                },
                {
                    "RoleId": 3,
                    "ModuleId": 2,
                    "CanView": True,
                    "CanCreate": False,
                    "CanEdit": False,
                    "CanDelete": False,
                    "CanExport": False,
                    "AdminActions": False,
                    "OtherActions": False,
                },
            ],
        }

        response = client.post("/permissions/bulk-update", json=bulk_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["RoleId"] == 3
        assert len(data["permissions"]) == 2

    def test_check_user_permission(self, client: TestClient, auth_headers: dict, db_session: Session, test_role, test_module, sample_permission_data) -> None:
        """Test checking user permission."""
        # First create the permission
        client.post("/permissions", json=sample_permission_data, headers=auth_headers)

        response = client.get("/permissions/check/dashboard/view", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "module_key" in data
        assert "action" in data
        assert "allowed" in data
