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
            "Software": "Visual Studio Code",
            "Version": "1.85.0",
            "ExpiryDate": "2024-12-31",
            "Key": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
            "Account": "license@company.com",
            "Password": "password123",
            "EmployeeId": 1,
        }

        response = client.post("/licenses/", json=license_data, headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["Software"] == "Visual Studio Code"
        assert data["Version"] == "1.85.0"
        assert data["Key"] == "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX"
        assert data["Account"] == "license@company.com"
        assert data["EmployeeId"] == 1
        assert "LicenseId" in data
        assert "CreatedAt" in data

    def test_get_license_by_id(self, client, auth_headers) -> None:
        """Test GET /licenses/{license_id} returns specific license."""
        # Create test data using the API
        license_data = {
            "Software": "Visual Studio Code",
            "Version": "1.85.0",
            "ExpiryDate": "2024-12-31",
            "Key": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
            "Account": "license@company.com",
            "Password": "password123",
            "EmployeeId": 1,
        }

        create_response = client.post("/licenses/", json=license_data, headers=auth_headers)
        assert create_response.status_code == 200
        license_id = create_response.json()["LicenseId"]

        response = client.get(f"/licenses/{license_id}", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["LicenseId"] == license_id
        assert data["Software"] == "Visual Studio Code"

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
            "Software": "Visual Studio Code",
            "Version": "1.85.0",
            "ExpiryDate": "2024-12-31",
            "Key": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
            "Account": "license@company.com",
            "Password": "password123",
            "EmployeeId": 1,
        }

        license_data_2 = {
            "Software": "Office 365",
            "Version": "2024",
            "ExpiryDate": "2025-12-31",
            "Key": "YYYYY-YYYYY-YYYYY-YYYYY-YYYYY",
            "Account": "office@company.com",
            "Password": "password456",
            "EmployeeId": 1,
        }

        client.post("/licenses/", json=license_data_1, headers=auth_headers)
        client.post("/licenses/", json=license_data_2, headers=auth_headers)

        response = client.get("/licenses/", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

        software_names = [license["Software"] for license in data]  # noqa: A001
        assert "Visual Studio Code" in software_names
        assert "Office 365" in software_names

    def test_update_license(self, client, auth_headers) -> None:
        """Test PUT /licenses/{license_id} updates license."""
        # Create test data using the API
        license_data = {
            "Software": "Visual Studio Code",
            "Version": "1.85.0",
            "ExpiryDate": "2024-12-31",
            "Key": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
            "Account": "license@company.com",
            "Password": "password123",
            "EmployeeId": 1,
        }

        create_response = client.post("/licenses/", json=license_data, headers=auth_headers)
        assert create_response.status_code == 200
        license_id = create_response.json()["LicenseId"]

        update_data = {
            "Software": "Updated Software",
            "Version": "2.0.0",
            "Key": "YYYYY-YYYYY-YYYYY-YYYYY-YYYYY",
            "Account": "updated@company.com",
            "Password": "newpassword",
            "EmployeeId": 1,
        }

        response = client.put(f"/licenses/{license_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["Software"] == "Updated Software"
        assert data["Version"] == "2.0.0"
        assert data["Key"] == "YYYYY-YYYYY-YYYYY-YYYYY-YYYYY"

    def test_update_license_not_found(self, client, auth_headers) -> None:
        """Test PUT /licenses/{license_id} returns 404 for non-existent license."""
        update_data = {
            "Software": "Test",
            "Version": "1.0",
            "Key": "TEST-KEY",
            "Account": "test@test.com",
            "Password": "test",
            "EmployeeId": 1,
        }

        response = client.put("/licenses/999", json=update_data, headers=auth_headers)
        assert response.status_code == 404
        data = response.json()
        assert "License not found" in data["detail"]

    def test_delete_license(self, client, auth_headers) -> None:
        """Test DELETE /licenses/{license_id} deletes license."""
        # Create test data using the API
        license_data = {
            "Software": "Visual Studio Code",
            "Version": "1.85.0",
            "ExpiryDate": "2024-12-31",
            "Key": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
            "Account": "license@company.com",
            "Password": "password123",
            "EmployeeId": 1,
        }

        create_response = client.post("/licenses/", json=license_data, headers=auth_headers)
        assert create_response.status_code == 200
        license_id = create_response.json()["LicenseId"]

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
            "Software": "",  # Empty software name
            "Version": "1.0",
            "Key": "TEST",
            "Account": "test@test.com",
            "Password": "test",
            # Missing EmployeeId
        }

        response = client.post("/licenses/", json=invalid_data, headers=auth_headers)
        # Should return validation error
        assert response.status_code == 422
