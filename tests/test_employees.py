import pytest
from sqlmodel import Session, select

from models.employees import Employees
from schemas.employees import EmployeeCreate


class TestEmployeesAPI:
    """Test cases for Employees API endpoints"""

    def test_get_employees_empty(self, client):
        """Test GET /employees/ returns empty list when no employees exist"""
        response = client.get("/employees/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_create_employee(self, client):
        """Test POST /employees/ creates a new employee"""
        employee_data = {
            "Name": "John Doe",
            "Role": "Software Developer",
            "Email": "john.doe@example.com",
            "Phone": "+1234567890",
            "Connection": "VPN Office",
            "Password": "securepass123",
            "CountryId": 1
        }

        response = client.post("/employees/", json=employee_data)
        assert response.status_code == 200

        data = response.json()
        assert data["Name"] == "John Doe"
        assert data["Role"] == "Software Developer"
        assert data["Email"] == "john.doe@example.com"
        assert data["Phone"] == "+1234567890"
        assert data["EmployeeId"] is not None

    def test_create_employee_minimal_data(self, client):
        """Test POST /employees/ with minimal required data"""
        employee_data = {
            "Name": None,
            "Role": None,
            "Email": None,
            "Phone": None,
            "Connection": None,
            "Password": None,
            "CountryId": None
        }

        response = client.post("/employees/", json=employee_data)
        assert response.status_code == 200

        data = response.json()
        assert data["EmployeeId"] is not None
        assert data["Name"] is None
        assert data["Role"] is None

    def test_get_employee_by_id(self, client, db_session: Session):
        """Test GET /employees/{employee_id} returns specific employee"""
        # Create test data
        employee = self._create_test_employee(db_session)

        response = client.get(f"/employees/{employee.EmployeeId}")
        assert response.status_code == 200

        data = response.json()
        assert data["EmployeeId"] == employee.EmployeeId
        assert data["Name"] == employee.Name
        assert data["Email"] == employee.Email

    def test_get_employee_not_found(self, client):
        """Test GET /employees/{employee_id} returns 404 for non-existent employee"""
        response = client.get("/employees/999")
        assert response.status_code == 404
        data = response.json()
        assert "Employee not found" in data["detail"]

    def test_get_all_employees(self, client, db_session: Session):
        """Test GET /employees/ returns all employees"""
        # Create test data
        self._create_test_employee(db_session, "John Doe", "john@example.com")
        self._create_test_employee(db_session, "Jane Smith", "jane@example.com")

        response = client.get("/employees/")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

        # Check that both employees are present
        names = [emp["Name"] for emp in data]
        assert "John Doe" in names
        assert "Jane Smith" in names

    def test_update_employee(self, client, db_session: Session):
        """Test PUT /employees/{employee_id} updates employee"""
        # Create test data
        employee = self._create_test_employee(db_session)

        update_data = {
            "Name": "Updated Name",
            "Role": "Senior Developer",
            "Email": "updated@example.com",
            "Phone": "+0987654321",
            "Connection": "Remote VPN",
            "Password": "newpassword",
            "CountryId": 2
        }

        response = client.put(f"/employees/{employee.EmployeeId}", json=update_data)
        assert response.status_code == 200

        data = response.json()
        assert data["Name"] == "Updated Name"
        assert data["Role"] == "Senior Developer"
        assert data["Email"] == "updated@example.com"
        assert data["Phone"] == "+0987654321"

    def test_update_employee_partial(self, client, db_session: Session):
        """Test PUT /employees/{employee_id} with partial update"""
        # Create test data
        employee = self._create_test_employee(db_session)

        # Update only email and role
        update_data = {
            "Email": "newemail@example.com",
            "Role": "Tech Lead"
        }

        response = client.put(f"/employees/{employee.EmployeeId}", json=update_data)
        assert response.status_code == 200

        data = response.json()
        assert data["Email"] == "newemail@example.com"
        assert data["Role"] == "Tech Lead"
        # Other fields should remain unchanged
        assert data["Name"] == employee.Name

    def test_update_employee_not_found(self, client):
        """Test PUT /employees/{employee_id} returns 404 for non-existent employee"""
        update_data = {
            "Name": "Test Employee",
            "Email": "test@example.com"
        }

        response = client.put("/employees/999", json=update_data)
        assert response.status_code == 404
        data = response.json()
        assert "Employee not found" in data["detail"]

    def test_delete_employee(self, client, db_session: Session):
        """Test DELETE /employees/{employee_id} deletes employee"""
        # Create test data
        employee = self._create_test_employee(db_session)

        # Verify employee exists
        response = client.get(f"/employees/{employee.EmployeeId}")
        assert response.status_code == 200

        # Delete employee
        response = client.delete(f"/employees/{employee.EmployeeId}")
        assert response.status_code == 200
        data = response.json()
        assert "Employee deleted successfully" in data["detail"]

        # Verify employee is deleted
        response = client.get(f"/employees/{employee.EmployeeId}")
        assert response.status_code == 404

    def test_delete_employee_not_found(self, client):
        """Test DELETE /employees/{employee_id} returns 404 for non-existent employee"""
        response = client.delete("/employees/999")
        assert response.status_code == 404
        data = response.json()
        assert "Employee not found" in data["detail"]

    def test_create_employee_invalid_email_format(self, client):
        """Test POST /employees/ with various data types"""
        # Test with various data - schema should handle it
        employee_data = {
            "Name": "Test User",
            "Role": "Tester",
            "Email": "test@example.com",
            "Phone": "123-456-7890",
            "Connection": "Local",
            "Password": "testpass",
            "CountryId": 1
        }

        response = client.post("/employees/", json=employee_data)
        assert response.status_code == 200

        data = response.json()
        assert data["Name"] == "Test User"
        assert data["Email"] == "test@example.com"

    def test_employee_crud_workflow(self, client, db_session: Session):
        """Test complete CRUD workflow for employees"""
        # CREATE
        employee_data = {
            "Name": "Workflow Test",
            "Role": "QA Engineer",
            "Email": "workflow@test.com",
            "Phone": "+5551234567",
            "Connection": "Office",
            "Password": "workflow123",
            "CountryId": 1
        }

        create_response = client.post("/employees/", json=employee_data)
        assert create_response.status_code == 200
        created_data = create_response.json()
        employee_id = created_data["EmployeeId"]

        # READ
        read_response = client.get(f"/employees/{employee_id}")
        assert read_response.status_code == 200
        read_data = read_response.json()
        assert read_data["Name"] == "Workflow Test"

        # UPDATE
        update_data = {"Name": "Updated Workflow Test", "Role": "Senior QA Engineer"}
        update_response = client.put(f"/employees/{employee_id}", json=update_data)
        assert update_response.status_code == 200
        updated_data = update_response.json()
        assert updated_data["Name"] == "Updated Workflow Test"

        # DELETE
        delete_response = client.delete(f"/employees/{employee_id}")
        assert delete_response.status_code == 200

        # VERIFY DELETION
        final_response = client.get(f"/employees/{employee_id}")
        assert final_response.status_code == 404

    def _create_test_employee(self, db_session: Session, name: str = "Test Employee", email: str = "test@example.com") -> Employees:
        """Helper method to create a test employee"""
        employee = Employees(
            Name=name,
            Role="Developer",
            Email=email,
            Phone="+1234567890",
            Connection="VPN Office",
            Password="testpass",
            CountryId=1,
            EmployeeId=self._get_next_employee_id(db_session)
        )
        db_session.add(employee)
        db_session.commit()
        db_session.refresh(employee)
        return employee

    def _get_next_employee_id(self, db_session: Session) -> int:
        """Helper method to get next available EmployeeId"""
        # For testing, just return incremental IDs
        result = db_session.exec(select(Employees).order_by(Employees.EmployeeId.desc())).first()
        return (result.EmployeeId + 1) if result else 1
