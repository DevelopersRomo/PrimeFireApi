"""Tests for Employees API endpoints."""

from unittest.mock import AsyncMock, patch

from models.employees import Employees, Roles


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

    def test_create_and_get_employee(self, client, auth_headers, db_session) -> None:
        """Test GET /employees/{id} successfully returns an employee."""
        emp = Employees(FirstName="Test", LastName="User", Email="test@primefire.com")
        db_session.add(emp)
        db_session.commit()
        db_session.refresh(emp)

        response = client.get(f"/employees/{emp.EmployeeId}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["FirstName"] == "Test"
        assert data["Email"] == "test@primefire.com"

    def test_get_employee_not_found(self, client, auth_headers) -> None:
        """Test GET /employees/{id} returns 404 when not found."""
        response = client.get("/employees/999999", headers=auth_headers)
        assert response.status_code == 404

    @patch("api.employees.graph_client")
    def test_update_employee(self, mock_graph, client, auth_headers, db_session) -> None:
        """Test PATCH /employees/{id} updates employee and pushes to Microsoft Graph if AzureOid exists."""
        mock_graph.map_employee_to_graph_user.return_value = {"givenName": "Updated"}
        mock_graph.update_user = AsyncMock()

        emp = Employees(FirstName="Old", LastName="Name", Email="update@primefire.com", AzureOid="some-oid-123")
        db_session.add(emp)
        db_session.commit()
        db_session.refresh(emp)

        update_data = {"FirstName": "Updated"}
        response = client.patch(f"/employees/{emp.EmployeeId}", json=update_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["FirstName"] == "Updated"
        mock_graph.update_user.assert_called_once()

    def test_assign_and_remove_role(self, client, auth_headers, db_session) -> None:
        """Test assigning a role, getting roles, and removing a role."""
        emp = Employees(FirstName="Role", LastName="Test")
        role = Roles(RoleName="MockRole", Description="A mock role")
        db_session.add(emp)
        db_session.add(role)
        db_session.commit()
        db_session.refresh(emp)
        db_session.refresh(role)

        # 1. Assign role
        assignment_data = {"RoleId": role.RoleId}
        res_assign = client.post(f"/employees/{emp.EmployeeId}/roles", json=assignment_data, headers=auth_headers)
        assert res_assign.status_code == 200

        # 2. Prevent duplicate role assignment
        res_assign_duplicate = client.post(
            f"/employees/{emp.EmployeeId}/roles", json=assignment_data, headers=auth_headers
        )
        assert res_assign_duplicate.status_code == 400

        # 3. Verify roles collection
        res_roles = client.get(f"/employees/{emp.EmployeeId}/roles", headers=auth_headers)
        assert res_roles.status_code == 200
        roles_data = res_roles.json()
        assert len(roles_data) == 1
        assert roles_data[0]["RoleName"] == "MockRole"

        # 4. Remove role
        res_remove = client.delete(f"/employees/{emp.EmployeeId}/roles/{role.RoleId}", headers=auth_headers)
        assert res_remove.status_code == 200

        # 5. Verify role was removed
        res_empty = client.get(f"/employees/{emp.EmployeeId}/roles", headers=auth_headers)
        assert len(res_empty.json()) == 0

    @patch("api.employees.graph_client")
    def test_sync_from_microsoft(self, mock_graph, client, auth_headers, db_session) -> None:
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
            "AzureOid": "mock-oid-abc",
            "AzureUpn": "testsync@primefire.com",
            "Email": "testsync@primefire.com",
            "DisplayName": "Sync User",
            "FirstName": "Sync",
            "LastName": "User",
        }

        response = client.get("/employees/sync/from-microsoft", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        # Verify that only the user we successfully parsed is returned
        sync_user = next((u for u in data if u["AzureOid"] == "mock-oid-abc"), None)
        assert sync_user is not None
        assert sync_user["Email"] == "testsync@primefire.com"

    @patch("api.employees.graph_client")
    def test_sync_employee_to_microsoft(self, mock_graph, client, auth_headers, db_session) -> None:
        """Test PUT /employees/{id}/sync-to-microsoft."""
        emp = Employees(FirstName="Old", LastName="Name", Email="update@primefire.com", AzureOid="some-oid-456")
        db_session.add(emp)
        db_session.commit()
        db_session.refresh(emp)

        mock_graph.map_employee_to_graph_user.return_value = {"givenName": "Old"}
        mock_graph.update_user = AsyncMock()

        response = client.put(f"/employees/{emp.EmployeeId}/sync-to-microsoft", headers=auth_headers)
        assert response.status_code == 200
        mock_graph.update_user.assert_called_once()

    @patch("api.employees.graph_client")
    def test_sync_single_employee_from_microsoft(self, mock_graph, client, auth_headers, db_session) -> None:
        """Test GET /employees/{id}/sync-from-microsoft."""
        emp = Employees(FirstName="Old", LastName="Name", Email="update@primefire.com", AzureOid="some-oid-789")
        db_session.add(emp)
        db_session.commit()
        db_session.refresh(emp)

        mock_ms_user = {"id": "some-oid-789", "givenName": "NewName"}
        mock_graph.get_user = AsyncMock(return_value=mock_ms_user)
        mock_graph.map_graph_user_to_employee.return_value = {"FirstName": "NewName"}

        response = client.get(f"/employees/{emp.EmployeeId}/sync-from-microsoft", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["FirstName"] == "NewName"

    def test_trigger_sync(self, client, auth_headers) -> None:
        """Test POST /employees/sync/trigger."""
        response = client.post("/employees/sync/trigger", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Sync triggered successfully"

    def test_sync_status(self, client, auth_headers) -> None:
        """Test GET /employees/sync/status."""
        response = client.get("/employees/sync/status", headers=auth_headers)
        assert response.status_code == 200
        assert "is_running" in response.json()
