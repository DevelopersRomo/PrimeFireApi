import pytest
from datetime import date
from sqlmodel import Session

from models.licenses import Licences
from schemas.licenses import LicenceCreate


class TestLicensesAPI:
    """Test cases for Licenses API endpoints"""

    def test_get_licenses_empty(self, client):
        """Test GET /licenses/ returns empty list when no licenses exist"""
        response = client.get("/licenses/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_create_license(self, client, db_session: Session):
        """Test POST /licenses/ creates a new license"""
        # First create an employee (required for license)
        from models.employees import Employees
        employee = Employees(
            Name="Test Employee",
            Role="Developer",
            Email="test@example.com",
            EmployeeId=1
        )
        db_session.add(employee)
        db_session.commit()

        license_data = {
            "Software": "Visual Studio Code",
            "Version": "1.85.0",
            "ExpiryDate": "2024-12-31",
            "Key": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
            "Account": "license@company.com",
            "Password": "password123",
            "EmployeeId": 1
        }

        response = client.post("/licenses/", json=license_data)
        assert response.status_code == 200

        data = response.json()
        assert data["Software"] == "Visual Studio Code"
        assert data["Version"] == "1.85.0"
        assert data["Key"] == "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX"
        assert data["Account"] == "license@company.com"
        assert data["EmployeeId"] == 1
        assert "LicenceId" in data
        assert "CreatedAt" in data

    def test_get_license_by_id(self, client, db_session: Session):
        """Test GET /licenses/{license_id} returns specific license"""
        # Create test data
        employee = self._create_test_employee(db_session)
        license_obj = self._create_test_license(db_session, employee.EmployeeId)

        response = client.get(f"/licenses/{license_obj.LicenceId}")
        assert response.status_code == 200

        data = response.json()
        assert data["LicenceId"] == license_obj.LicenceId
        assert data["Software"] == license_obj.Software

    def test_get_license_not_found(self, client):
        """Test GET /licenses/{license_id} returns 404 for non-existent license"""
        response = client.get("/licenses/999")
        assert response.status_code == 404
        data = response.json()
        assert "License not found" in data["detail"]

    def test_get_all_licenses(self, client, db_session: Session):
        """Test GET /licenses/ returns all licenses"""
        # Create test data
        employee = self._create_test_employee(db_session)
        self._create_test_license(db_session, employee.EmployeeId)
        self._create_test_license(db_session, employee.EmployeeId, software="Office 365")

        response = client.get("/licenses/")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

        # Check that both licenses are present
        software_names = [license["Software"] for license in data]
        assert "Visual Studio Code" in software_names
        assert "Office 365" in software_names

    def test_update_license(self, client, db_session: Session):
        """Test PUT /licenses/{license_id} updates license"""
        # Create test data
        employee = self._create_test_employee(db_session)
        license_obj = self._create_test_license(db_session, employee.EmployeeId)

        update_data = {
            "Software": "Updated Software",
            "Version": "2.0.0",
            "Key": "YYYYY-YYYYY-YYYYY-YYYYY-YYYYY",
            "Account": "updated@company.com",
            "Password": "newpassword",
            "EmployeeId": 1
        }

        response = client.put(f"/licenses/{license_obj.LicenceId}", json=update_data)
        assert response.status_code == 200

        data = response.json()
        assert data["Software"] == "Updated Software"
        assert data["Version"] == "2.0.0"
        assert data["Key"] == "YYYYY-YYYYY-YYYYY-YYYYY-YYYYY"

    def test_update_license_not_found(self, client):
        """Test PUT /licenses/{license_id} returns 404 for non-existent license"""
        update_data = {
            "Software": "Test",
            "Version": "1.0",
            "Key": "TEST-KEY",
            "Account": "test@test.com",
            "Password": "test",
            "EmployeeId": 1
        }

        response = client.put("/licenses/999", json=update_data)
        assert response.status_code == 404
        data = response.json()
        assert "License not found" in data["detail"]

    def test_delete_license(self, client, db_session: Session):
        """Test DELETE /licenses/{license_id} deletes license"""
        # Create test data
        employee = self._create_test_employee(db_session)
        license_obj = self._create_test_license(db_session, employee.EmployeeId)

        # Verify license exists
        response = client.get(f"/licenses/{license_obj.LicenceId}")
        assert response.status_code == 200

        # Delete license
        response = client.delete(f"/licenses/{license_obj.LicenceId}")
        assert response.status_code == 200
        data = response.json()
        assert "License deleted successfully" in data["message"]

        # Verify license is deleted
        response = client.get(f"/licenses/{license_obj.LicenceId}")
        assert response.status_code == 404

    def test_delete_license_not_found(self, client):
        """Test DELETE /licenses/{license_id} returns 404 for non-existent license"""
        response = client.delete("/licenses/999")
        assert response.status_code == 404
        data = response.json()
        assert "License not found" in data["detail"]

    def test_create_license_invalid_data(self, client):
        """Test POST /licenses/ with invalid data"""
        invalid_data = {
            "Software": "",  # Empty software name
            "Version": "1.0",
            "Key": "TEST",
            "Account": "test@test.com",
            "Password": "test"
            # Missing EmployeeId
        }

        response = client.post("/licenses/", json=invalid_data)
        # Should return validation error
        assert response.status_code == 422

    def _create_test_employee(self, db_session: Session) -> object:
        """Helper method to create a test employee"""
        from models.employees import Employees

        employee = Employees(
            Name="Test Employee",
            Role="Developer",
            Email="test@example.com",
            EmployeeId=1
        )
        db_session.add(employee)
        db_session.commit()
        db_session.refresh(employee)
        return employee

    def _create_test_license(self, db_session: Session, employee_id: int, software: str = "Visual Studio Code") -> Licences:
        """Helper method to create a test license"""
        license_obj = Licences(
            Software=software,
            Version="1.85.0",
            ExpiryDate=date(2024, 12, 31),
            Key="XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
            Account="license@company.com",
            Password="password123",
            EmployeeId=employee_id
        )
        db_session.add(license_obj)
        db_session.commit()
        db_session.refresh(license_obj)
        return license_obj
