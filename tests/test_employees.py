"""Tests for Employees API endpoints."""

from unittest.mock import AsyncMock, patch

import pytest

from main import app
from models.employees import Employees, Roles


def _override_employee_permissions(permissions: dict):
    from api.dependencies import get_current_employee_with_permissions

    def mock_permissions():
        return {
            "employee": {"employee_id": 1, "email": "test@example.com"},
            "permissions": [{"module_key": "employees", "permissions": permissions}],
        }

    app.dependency_overrides[get_current_employee_with_permissions] = mock_permissions


@pytest.fixture
def employees_editor_overrides():
    """Caller with can_edit on the employees module (no admin_actions)."""
    from api.dependencies import get_current_employee_with_permissions

    _override_employee_permissions({"can_edit": True})
    yield
    app.dependency_overrides.pop(get_current_employee_with_permissions, None)


@pytest.fixture
def employees_admin_overrides():
    """Caller with can_edit + admin_actions on the employees module."""
    from api.dependencies import get_current_employee_with_permissions

    _override_employee_permissions({"can_edit": True, "admin_actions": True})
    yield
    app.dependency_overrides.pop(get_current_employee_with_permissions, None)


class TestEmployeesAPI:
    """Test cases for Employees API endpoints."""

    def test_get_employees_empty(self, client, auth_headers) -> None:
        """Test GET /employees/ returns an empty list or list of existing employees."""
        # Using /employees since router is usually prefixed
        response = client.get("/employees/", headers=auth_headers)
        # If there's a routing redirect it might be 307 or 200 depending on trailing slash.
        # Let's try without trailing slash if it hits 404/307. We will handle both safely.
        if response.status_code in {307, 404}:
            response = client.get("/employees", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_search_metadata_uses_filtered_total(self, client, auth_headers, db_session) -> None:
        db_session.add(Employees(first_name="Needle", last_name="Employee", email="needle@example.com"))
        db_session.add(Employees(first_name="Other", last_name="Employee", email="other@example.com"))
        db_session.commit()

        response = client.get("/employees?with_meta=true&search=Needle", headers=auth_headers)

        assert response.status_code == 200
        assert response.json()["total"] == 1
        assert response.json()["items"][0]["first_name"] == "Needle"

    def test_create_and_get_employee(self, client, auth_headers, db_session) -> None:
        """Test GET /employees/{id} successfully returns an employee."""
        emp = Employees(first_name="Test", last_name="User", email="test@primefire.com")
        db_session.add(emp)
        db_session.commit()
        db_session.refresh(emp)

        response = client.get(f"/employees/{emp.employee_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Test"
        assert data["email"] == "test@primefire.com"

    def test_get_employee_not_found(self, client, auth_headers) -> None:
        """Test GET /employees/{id} returns 404 when not found."""
        response = client.get("/employees/999999", headers=auth_headers)
        assert response.status_code == 404

    def test_get_employees_invalidates_cache_when_db_marker_changes(self, client, auth_headers, db_session) -> None:
        """GET /employees should detect inserts without explicit cache invalidation."""
        cached_emp = Employees(first_name="Cached", last_name="User", email="cached@primefire.com")
        db_session.add(cached_emp)
        db_session.commit()
        db_session.refresh(cached_emp)

        first_response = client.get("/employees", headers=auth_headers)
        assert first_response.status_code == 200

        later_emp = Employees(first_name="Later", last_name="User", email="later@primefire.com")
        db_session.add(later_emp)
        db_session.commit()
        db_session.refresh(later_emp)

        fresh_response = client.get("/employees", headers=auth_headers)
        fresh_ids = {item["employee_id"] for item in fresh_response.json()}
        assert cached_emp.employee_id in fresh_ids
        assert later_emp.employee_id in fresh_ids

    @patch("api.employees.graph_client")
    def test_update_employee(self, mock_graph, client, auth_headers, db_session, employees_editor_overrides) -> None:
        """Test PATCH /employees/{id} updates employee and pushes to Microsoft Graph if azure_oid exists."""
        mock_graph.map_employee_to_graph_user.return_value = {"givenName": "Updated"}
        mock_graph.update_user = AsyncMock()

        emp = Employees(first_name="Old", last_name="Name", email="update@primefire.com", azure_oid="some-oid-123")
        db_session.add(emp)
        db_session.commit()
        db_session.refresh(emp)

        update_data = {"first_name": "Updated"}
        response = client.patch(f"/employees/{emp.employee_id}", json=update_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Updated"
        mock_graph.update_user.assert_called_once()

    @patch("api.employees.graph_client")
    def test_update_employee_fails_when_graph_sync_fails(
        self, mock_graph, client, auth_headers, db_session, employees_editor_overrides
    ) -> None:
        """PATCH must not report success when Microsoft Graph rejects the update."""
        mock_graph.map_employee_to_graph_user.return_value = {"givenName": "Updated"}
        mock_graph.update_user = AsyncMock(side_effect=RuntimeError("Graph rejected update"))

        emp = Employees(first_name="Old", last_name="Name", email="update@primefire.com", azure_oid="some-oid-123")
        db_session.add(emp)
        db_session.commit()
        db_session.refresh(emp)

        response = client.patch(f"/employees/{emp.employee_id}", json={"first_name": "Updated"}, headers=auth_headers)

        assert response.status_code == 502
        db_session.refresh(emp)
        assert emp.first_name == "Old"

    @patch("api.employees.graph_client")
    def test_update_employee_syncs_cleared_graph_fields(
        self, mock_graph, client, auth_headers, db_session, employees_editor_overrides
    ) -> None:
        """PATCH must send explicitly cleared fields to Microsoft Graph, not silently drop them."""

        def map_employee_to_graph_user(data):
            title = data.get("title")
            return {"jobTitle": None if isinstance(title, str) and title == "" else title}

        mock_graph.map_employee_to_graph_user.side_effect = map_employee_to_graph_user
        mock_graph.update_user = AsyncMock()

        emp = Employees(first_name="Old", last_name="Name", title="Engineer", azure_oid="some-oid-123")
        db_session.add(emp)
        db_session.commit()
        db_session.refresh(emp)

        response = client.patch(f"/employees/{emp.employee_id}", json={"title": ""}, headers=auth_headers)

        assert response.status_code == 200
        mock_graph.update_user.assert_called_once_with("some-oid-123", {"jobTitle": None})

    def test_assign_and_remove_role(self, client, auth_headers, db_session, employees_admin_overrides) -> None:
        """Test assigning a role, getting roles, and removing a role."""
        emp = Employees(first_name="Role", last_name="Test")
        role = Roles(role_name="MockRole", description="A mock role")
        db_session.add(emp)
        db_session.add(role)
        db_session.commit()
        db_session.refresh(emp)
        db_session.refresh(role)

        # 1. Assign role
        assignment_data = {"role_id": role.role_id}
        res_assign = client.post(f"/employees/{emp.employee_id}/roles", json=assignment_data, headers=auth_headers)
        assert res_assign.status_code == 200

        # 2. Prevent duplicate role assignment
        res_assign_duplicate = client.post(
            f"/employees/{emp.employee_id}/roles", json=assignment_data, headers=auth_headers
        )
        assert res_assign_duplicate.status_code == 400

        # 3. Verify roles collection
        res_roles = client.get(f"/employees/{emp.employee_id}/roles", headers=auth_headers)
        assert res_roles.status_code == 200
        roles_data = res_roles.json()
        assert len(roles_data) == 1
        assert roles_data[0]["role_name"] == "MockRole"

        # 4. Remove role
        res_remove = client.delete(f"/employees/{emp.employee_id}/roles/{role.role_id}", headers=auth_headers)
        assert res_remove.status_code == 200

        # 5. Verify role was removed
        res_empty = client.get(f"/employees/{emp.employee_id}/roles", headers=auth_headers)
        assert len(res_empty.json()) == 0

    @patch("api.employees.graph_client")
    def test_sync_from_microsoft(self, mock_graph, client, auth_headers, db_session, employees_admin_overrides) -> None:
        """Test GET /employees/sync/from-microsoft endpoints logic."""
        mock_ms_users = [
            {
                "id": "mock-oid-abc",
                "userPrincipalName": "testsync@primefire.com",
                "mail": "testsync@primefire.com",
                "displayName": "Sync User",
                "givenName": "Sync",
                "surname": "User",
                "country": "US",
            }
        ]

        mock_graph.get_all_users = AsyncMock(return_value=mock_ms_users)
        mock_graph.map_graph_user_to_employee.return_value = {
            "azure_oid": "mock-oid-abc",
            "azure_upn": "testsync@primefire.com",
            "email": "testsync@primefire.com",
            "display_name": "Sync User",
            "first_name": "Sync",
            "last_name": "User",
        }

        response = client.get("/employees/sync/from-microsoft", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        # Verify that only the user we successfully parsed is returned
        sync_user = next((u for u in data if u["azure_oid"] == "mock-oid-abc"), None)
        assert sync_user is not None
        assert sync_user["email"] == "testsync@primefire.com"

    @patch("api.employees.graph_client")
    def test_sync_employee_to_microsoft(
        self, mock_graph, client, auth_headers, db_session, employees_editor_overrides
    ) -> None:
        """Test PUT /employees/{id}/sync-to-microsoft."""
        emp = Employees(first_name="Old", last_name="Name", email="update@primefire.com", azure_oid="some-oid-456")
        db_session.add(emp)
        db_session.commit()
        db_session.refresh(emp)

        mock_graph.map_employee_to_graph_user.return_value = {"givenName": "Old"}
        mock_graph.update_user = AsyncMock()

        response = client.put(f"/employees/{emp.employee_id}/sync-to-microsoft", headers=auth_headers)
        assert response.status_code == 200
        mock_graph.update_user.assert_called_once()

    @patch("api.employees.graph_client")
    def test_sync_single_employee_from_microsoft(
        self, mock_graph, client, auth_headers, db_session, employees_editor_overrides
    ) -> None:
        """Test GET /employees/{id}/sync-from-microsoft."""
        emp = Employees(first_name="Old", last_name="Name", email="update@primefire.com", azure_oid="some-oid-789")
        db_session.add(emp)
        db_session.commit()
        db_session.refresh(emp)

        mock_ms_user = {"id": "some-oid-789", "givenName": "NewName"}
        mock_graph.get_user = AsyncMock(return_value=mock_ms_user)
        mock_graph.map_graph_user_to_employee.return_value = {"first_name": "NewName"}

        response = client.get(f"/employees/{emp.employee_id}/sync-from-microsoft", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["first_name"] == "NewName"

    def test_trigger_sync(self, client, auth_headers, employees_admin_overrides) -> None:
        """Test POST /employees/sync/trigger."""
        response = client.post("/employees/sync/trigger", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Sync triggered successfully"

    def test_sync_status(self, client, auth_headers) -> None:
        """Test GET /employees/sync/status."""
        response = client.get("/employees/sync/status", headers=auth_headers)
        assert response.status_code == 200
        assert "is_running" in response.json()


class TestEmployeesPermissions:
    """Authenticated callers without employees-module permissions must get 403 on mutations."""

    @pytest.fixture
    def target_employee(self, db_session):
        emp = Employees(first_name="Target", last_name="User", email="target@primefire.com")
        db_session.add(emp)
        db_session.commit()
        db_session.refresh(emp)
        return emp

    def test_patch_requires_can_edit(self, client, auth_headers, target_employee) -> None:
        response = client.patch(
            f"/employees/{target_employee.employee_id}", json={"first_name": "Hacked"}, headers=auth_headers
        )
        assert response.status_code == 403

    def test_assign_role_requires_admin_actions(self, client, auth_headers, target_employee, db_session) -> None:
        role = Roles(role_name="Admin", description="Admin role")
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)

        response = client.post(
            f"/employees/{target_employee.employee_id}/roles", json={"role_id": role.role_id}, headers=auth_headers
        )
        assert response.status_code == 403

    def test_remove_role_requires_admin_actions(self, client, auth_headers, target_employee) -> None:
        response = client.delete(f"/employees/{target_employee.employee_id}/roles/1", headers=auth_headers)
        assert response.status_code == 403

    def test_assign_role_rejects_editor_without_admin_actions(
        self, client, auth_headers, target_employee, db_session, employees_editor_overrides
    ) -> None:
        role = Roles(role_name="Admin", description="Admin role")
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)

        response = client.post(
            f"/employees/{target_employee.employee_id}/roles", json={"role_id": role.role_id}, headers=auth_headers
        )
        assert response.status_code == 403

    def test_bulk_sync_requires_admin_actions(self, client, auth_headers) -> None:
        response = client.get("/employees/sync/from-microsoft", headers=auth_headers)
        assert response.status_code == 403

    def test_trigger_sync_requires_admin_actions(self, client, auth_headers) -> None:
        response = client.post("/employees/sync/trigger", headers=auth_headers)
        assert response.status_code == 403

    def test_sync_to_microsoft_requires_can_edit(self, client, auth_headers, target_employee) -> None:
        response = client.put(f"/employees/{target_employee.employee_id}/sync-to-microsoft", headers=auth_headers)
        assert response.status_code == 403

    def test_sync_single_from_microsoft_requires_can_edit(self, client, auth_headers, target_employee) -> None:
        response = client.get(f"/employees/{target_employee.employee_id}/sync-from-microsoft", headers=auth_headers)
        assert response.status_code == 403

    def test_patch_allows_editor(self, client, auth_headers, target_employee, employees_editor_overrides) -> None:
        response = client.patch(f"/employees/{target_employee.employee_id}", json={}, headers=auth_headers)
        assert response.status_code == 200
