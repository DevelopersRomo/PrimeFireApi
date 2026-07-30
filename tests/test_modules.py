import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from models.employees import Roles
from models.modules import Modules


@pytest.fixture(autouse=True)
def _grant_module_mutations(permission_override) -> None:
    permission_override("modules", {"can_create", "can_edit", "can_delete"})


@pytest.fixture
def sample_module_data():
    """Sample module data for testing."""
    return {
        "module_name": "Test Module",
        "module_key": "test_module",
        "description": "A test module",
        "icon": "test_icon",
        "route_url": "/test",
        "display_order": 99,
        "is_active": True,
        "parent_module_id": None,
    }


@pytest.fixture
def sample_permission_data():
    """Sample permission data for testing."""
    return {
        "role_id": 1,
        "module_id": 1,
        "can_view": True,
        "can_create": True,
        "can_edit": True,
        "can_delete": False,
        "can_export": True,
        "admin_actions": False,
        "other_actions": False,
    }


@pytest.fixture
def test_role(db_session: Session):
    """Create a test role."""
    role = Roles(role_id=1, role_name="Admin", description="Admin role")
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)
    return role


@pytest.fixture
def test_module(db_session: Session):
    """Create a test module."""
    module = Modules(
        module_id=1,
        module_name="Dashboard",
        module_key="dashboard",
        description="Dashboard module",
        icon="dashboard",
        route_url="/dashboard",
        display_order=1,
        is_active=True,
    )
    db_session.add(module)
    db_session.commit()
    db_session.refresh(module)
    return module


@pytest.fixture
def test_role_user(db_session: Session):
    """Create a test user role."""
    role = Roles(role_id=3, role_name="User", description="Regular user role")
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
        assert data["module_name"] == sample_module_data["module_name"]
        assert data["module_key"] == sample_module_data["module_key"]
        assert "module_id" in data

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

    def test_get_modules_metadata_filters_inactive_and_includes_parent_name(
        self, client: TestClient, auth_headers: dict, db_session: Session
    ) -> None:
        parent = Modules(module_name="Parent", module_key="parent", display_order=1, is_active=True)
        db_session.add(parent)
        db_session.commit()
        db_session.refresh(parent)
        db_session.add_all(
            [
                Modules(
                    module_name="Child",
                    module_key="child",
                    display_order=2,
                    is_active=True,
                    parent_module_id=parent.module_id,
                ),
                Modules(module_name="Inactive", module_key="inactive", display_order=3, is_active=False),
            ]
        )
        db_session.commit()

        response = client.get("/modules?with_meta=true&skip=1&limit=1", headers=auth_headers)

        assert response.status_code == 200
        payload = response.json()
        assert payload["total"] == 2
        assert payload["items"][0]["module_name"] == "Child"
        assert payload["items"][0]["parent_module_name"] == "Parent"

    @pytest.mark.parametrize(
        ("method", "path"),
        [
            ("post", "/modules/"),
            ("put", "/modules/999"),
            ("delete", "/modules/999"),
            ("patch", "/modules/999/toggle-active"),
        ],
    )
    def test_module_mutations_require_matching_permission(
        self,
        client: TestClient,
        auth_headers: dict,
        sample_module_data: dict,
        permission_override,
        method: str,
        path: str,
    ) -> None:
        permission_override("modules", set())

        response = client.request(method, path, json=sample_module_data, headers=auth_headers)

        assert response.status_code == 403

    @pytest.mark.parametrize(
        ("endpoint", "is_active"),
        [("/modules", True), ("/modules?include_inactive=true", False)],
    )
    def test_get_modules_serializes_null_created_at(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session: Session,
        endpoint: str,
        is_active: bool,
    ) -> None:
        """Serialize legacy modules that do not have a creation timestamp."""
        module_key = f"null_created_at_{is_active}"
        db_session.add(
            Modules(
                module_name="Legacy Module",
                module_key=module_key,
                is_active=is_active,
                created_at=None,
            )
        )
        db_session.commit()

        response = client.get(endpoint, headers=auth_headers)

        assert response.status_code == 200
        serialized_module = next(module for module in response.json() if module["module_key"] == module_key)
        assert serialized_module["created_at"] is None

    def test_get_module_by_id(self, client: TestClient, auth_headers: dict, sample_module_data: dict) -> None:
        """Test getting a specific module by ID."""
        # Create module
        create_response = client.post("/modules/", json=sample_module_data, headers=auth_headers)
        module_id = create_response.json()["module_id"]

        # Get module
        response = client.get(f"/modules/{module_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["module_id"] == module_id
        assert data["module_name"] == sample_module_data["module_name"]

    def test_get_module_by_key(self, client: TestClient, auth_headers: dict, sample_module_data: dict) -> None:
        """Test getting a specific module by key."""
        # Create module
        client.post("/modules/", json=sample_module_data, headers=auth_headers)

        # Get module by key
        response = client.get(f"/modules/by-key/{sample_module_data['module_key']}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["module_key"] == sample_module_data["module_key"]

    def test_get_root_modules(self, client: TestClient, auth_headers: dict) -> None:
        """Test getting root modules."""
        response = client.get("/modules/root/all", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # All modules should have parent_module_id as None
        for module in data:
            assert module["parent_module_id"] is None

    def test_update_module(self, client: TestClient, auth_headers: dict, sample_module_data: dict) -> None:
        """Test updating a module."""
        # Create module
        create_response = client.post("/modules/", json=sample_module_data, headers=auth_headers)
        module_id = create_response.json()["module_id"]

        # Update module
        update_data = {"module_name": "Updated Module Name"}
        response = client.put(f"/modules/{module_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["module_name"] == "Updated Module Name"

    def test_toggle_module_active(self, client: TestClient, auth_headers: dict, sample_module_data: dict) -> None:
        """Test toggling module active status."""
        # Create module
        create_response = client.post("/modules/", json=sample_module_data, headers=auth_headers)
        module_id = create_response.json()["module_id"]
        original_status = create_response.json()["is_active"]

        # Toggle status
        response = client.patch(f"/modules/{module_id}/toggle-active", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] != original_status

    def test_delete_module(self, client: TestClient, auth_headers: dict, sample_module_data: dict) -> None:
        """Test deleting a module."""
        # Create module
        create_response = client.post("/modules/", json=sample_module_data, headers=auth_headers)
        module_id = create_response.json()["module_id"]

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
        parent_id = parent_response.json()["module_id"]

        # Create child module
        child_data = {**sample_module_data, "module_key": "child_module", "parent_module_id": parent_id}
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
        assert data["role_id"] == sample_permission_data["role_id"]
        assert data["module_id"] == sample_permission_data["module_id"]
        assert data["can_view"] == sample_permission_data["can_view"]

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
        assert data["role_id"] == role_id
        assert "role_name" in data
        assert "permissions" in data
        assert isinstance(data["permissions"], list)

    def test_get_module_permissions(
        self, client: TestClient, auth_headers: dict, db_session: Session, test_module
    ) -> None:
        """Test getting permissions for a specific module."""
        module_id = 1  # Dashboard module
        response = client.get(f"/permissions/module/{module_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_specific_permission(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session: Session,
        test_role,
        test_module,
        sample_permission_data,
    ) -> None:
        """Test getting a specific permission."""
        # First create the permission
        client.post("/permissions", json=sample_permission_data, headers=auth_headers)

        role_id = 1
        module_id = 1
        response = client.get(f"/permissions/{role_id}/{module_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["role_id"] == role_id
        assert data["module_id"] == module_id

    def test_update_permission(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session: Session,
        test_role,
        test_module,
        sample_permission_data,
    ) -> None:
        """Test updating a permission."""
        # First create the permission
        client.post("/permissions", json=sample_permission_data, headers=auth_headers)

        role_id = 1
        module_id = 1
        update_data = {"can_delete": False}

        response = client.put(f"/permissions/{role_id}/{module_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert not data["can_delete"]

    def test_delete_permission(
        self,
        client: TestClient,
        auth_headers: dict,
        sample_permission_data: dict,
        db_session: Session,
        test_role,
        test_module,
    ) -> None:
        """Test deleting a permission."""
        # Create permission
        create_response = client.post("/permissions", json=sample_permission_data, headers=auth_headers)
        role_id = create_response.json()["role_id"]
        module_id = create_response.json()["module_id"]

        # Delete permission
        response = client.delete(f"/permissions/{role_id}/{module_id}", headers=auth_headers)
        assert response.status_code == 200

        # Verify deletion
        get_response = client.get(f"/permissions/{role_id}/{module_id}", headers=auth_headers)
        assert get_response.status_code == 404

    def test_bulk_update_permissions(
        self, client: TestClient, auth_headers: dict, db_session: Session, test_role_user, test_module
    ) -> None:
        """Test bulk updating permissions for a role."""
        # Create second module for bulk test
        module2 = Modules(
            module_id=2,
            module_name="Settings",
            module_key="settings",
            description="Settings module",
            icon="settings",
            route_url="/settings",
            display_order=2,
            is_active=True,
        )
        db_session.add(module2)
        db_session.commit()

        bulk_data = {
            "role_id": 3,  # User role
            "permissions": [
                {
                    "role_id": 3,
                    "module_id": 1,
                    "can_view": True,
                    "can_create": False,
                    "can_edit": False,
                    "can_delete": False,
                    "can_export": False,
                    "admin_actions": False,
                    "other_actions": False,
                },
                {
                    "role_id": 3,
                    "module_id": 2,
                    "can_view": True,
                    "can_create": False,
                    "can_edit": False,
                    "can_delete": False,
                    "can_export": False,
                    "admin_actions": False,
                    "other_actions": False,
                },
            ],
        }

        response = client.post("/permissions/bulk-update", json=bulk_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["role_id"] == 3
        assert len(data["permissions"]) == 2

    def test_check_user_permission(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session: Session,
        test_role,
        test_module,
        sample_permission_data,
    ) -> None:
        """Test checking user permission."""
        # First create the permission
        client.post("/permissions", json=sample_permission_data, headers=auth_headers)

        response = client.get("/permissions/check/dashboard/view", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "module_key" in data
        assert "action" in data
        assert "allowed" in data
