"""
Tests for Licenses API endpoints.

Note: These tests use automatic rollback - all database changes are
automatically reverted after each test.
"""


class TestLicensesAPI:
    """Test cases for Licenses API endpoints."""

    def test_get_licenses_empty(self, client, auth_headers) -> None:
        """Test GET /licenses/ returns empty list when no licenses exist."""
        response = client.get("/licenses/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_create_license(self, client, auth_headers) -> None:
        """Test POST /licenses/ creates a new license."""
        license_data = {
            "software": "Visual Studio Code",
            "version": "1.85.0",
            "expiry_date": "2024-12-31",
            "key": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
            "account": "license@company.com",
            "password": "password123",
            "employee_id": 1,
        }

        response = client.post("/licenses/", json=license_data, headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["software"] == "Visual Studio Code"
        assert data["version"] == "1.85.0"
        assert data["key"] == "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX"
        assert data["account"] == "license@company.com"
        assert data["employee_id"] == 1
        assert "license_id" in data
        assert "created_at" in data

    def test_get_license_by_id(self, client, auth_headers) -> None:
        """Test GET /licenses/{license_id} returns specific license."""
        # Create test data using the API
        license_data = {
            "software": "Visual Studio Code",
            "version": "1.85.0",
            "expiry_date": "2024-12-31",
            "key": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
            "account": "license@company.com",
            "password": "password123",
            "employee_id": 1,
        }

        create_response = client.post("/licenses/", json=license_data, headers=auth_headers)
        assert create_response.status_code == 200
        license_id = create_response.json()["license_id"]

        response = client.get(f"/licenses/{license_id}", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["license_id"] == license_id
        assert data["software"] == "Visual Studio Code"

    def test_get_license_not_found(self, client, auth_headers) -> None:
        """Test GET /licenses/{license_id} returns 404 for non-existent license."""
        response = client.get("/licenses/999", headers=auth_headers)
        assert response.status_code == 404
        data = response.json()
        assert "License not found" in data["detail"]

    def test_get_all_licenses(self, client, auth_headers) -> None:
        """Test GET /licenses/ returns all licenses."""
        # Create test data using the API
        license_data_1 = {
            "software": "Visual Studio Code",
            "version": "1.85.0",
            "expiry_date": "2024-12-31",
            "key": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
            "account": "license@company.com",
            "password": "password123",
            "employee_id": 1,
        }

        license_data_2 = {
            "software": "Office 365",
            "version": "2024",
            "expiry_date": "2025-12-31",
            "key": "YYYYY-YYYYY-YYYYY-YYYYY-YYYYY",
            "account": "office@company.com",
            "password": "password456",
            "employee_id": 1,
        }

        client.post("/licenses/", json=license_data_1, headers=auth_headers)
        client.post("/licenses/", json=license_data_2, headers=auth_headers)

        response = client.get("/licenses/", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

        software_names = [license["software"] for license in data]  # noqa: A001
        assert "Visual Studio Code" in software_names
        assert "Office 365" in software_names

    def test_update_license(self, client, auth_headers) -> None:
        """Test PUT /licenses/{license_id} updates license."""
        # Create test data using the API
        license_data = {
            "software": "Visual Studio Code",
            "version": "1.85.0",
            "expiry_date": "2024-12-31",
            "key": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
            "account": "license@company.com",
            "password": "password123",
            "employee_id": 1,
        }

        create_response = client.post("/licenses/", json=license_data, headers=auth_headers)
        assert create_response.status_code == 200
        license_id = create_response.json()["license_id"]

        update_data = {
            "software": "Updated Software",
            "version": "2.0.0",
            "key": "YYYYY-YYYYY-YYYYY-YYYYY-YYYYY",
            "account": "updated@company.com",
            "password": "newpassword",
            "employee_id": 1,
        }

        response = client.put(f"/licenses/{license_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["software"] == "Updated Software"
        assert data["version"] == "2.0.0"
        assert data["key"] == "YYYYY-YYYYY-YYYYY-YYYYY-YYYYY"

    def test_update_license_not_found(self, client, auth_headers) -> None:
        """Test PUT /licenses/{license_id} returns 404 for non-existent license."""
        update_data = {
            "software": "Test",
            "version": "1.0",
            "key": "TEST-KEY",
            "account": "test@test.com",
            "password": "test",
            "employee_id": 1,
        }

        response = client.put("/licenses/999", json=update_data, headers=auth_headers)
        assert response.status_code == 404
        data = response.json()
        assert "License not found" in data["detail"]

    def test_delete_license(self, client, auth_headers) -> None:
        """Test DELETE /licenses/{license_id} deletes license."""
        # Create test data using the API
        license_data = {
            "software": "Visual Studio Code",
            "version": "1.85.0",
            "expiry_date": "2024-12-31",
            "key": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
            "account": "license@company.com",
            "password": "password123",
            "employee_id": 1,
        }

        create_response = client.post("/licenses/", json=license_data, headers=auth_headers)
        assert create_response.status_code == 200
        license_id = create_response.json()["license_id"]

        # Verify license exists
        response = client.get(f"/licenses/{license_id}", headers=auth_headers)
        assert response.status_code == 200

        # Delete license
        response = client.delete(f"/licenses/{license_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "License deleted successfully" in data["message"]

        # Verify license is deleted
        response = client.get(f"/licenses/{license_id}", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_license_not_found(self, client, auth_headers) -> None:
        """Test DELETE /licenses/{license_id} returns 404 for non-existent license."""
        response = client.delete("/licenses/999", headers=auth_headers)
        assert response.status_code == 404
        data = response.json()
        assert "License not found" in data["detail"]

    def test_create_license_invalid_data(self, client, auth_headers) -> None:
        """Test POST /licenses/ with invalid data."""
        invalid_data = {
            "software": "",  # Empty software name
            "version": "1.0",
            "key": "TEST",
            "account": "test@test.com",
            "password": "test",
            # Missing employee_id
        }

        response = client.post("/licenses/", json=invalid_data, headers=auth_headers)
        # Should return validation error
        assert response.status_code == 422
