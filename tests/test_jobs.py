"""
Tests for Jobs API endpoints.

Note: These tests use automatic rollback - all database changes are
automatically reverted after each test.
"""


class TestJobsAPI:
    """Test cases for Jobs API endpoints."""

    def test_get_jobs_empty(self, client, auth_headers) -> None:
        """Test GET /jobs/ returns empty list when no jobs exist."""
        response = client.get("/jobs/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_create_job(self, client, auth_headers) -> None:
        """Test POST /jobs/ creates a new job."""
        job_data = {
            "Title": "Software Developer",
            "Description": "We are looking for a skilled software developer",
            "Requirements": "Python, FastAPI, SQL experience required",
            "Location": "Remote",
            "SalaryMin": 50000.0,
            "SalaryMax": 70000.0,
            "Status": "active",
            "EmployeeId": 2,
        }

        response = client.post("/jobs/", json=job_data, headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["Title"] == "Software Developer"
        assert data["Description"] == "We are looking for a skilled software developer"
        assert data["Location"] == "Remote"
        assert data["SalaryMin"] == 50000.0  # noqa: RUF069
        assert data["SalaryMax"] == 70000.0  # noqa: RUF069
        assert data["Status"] == "active"
        assert data["JobId"] is not None

    def test_get_job_by_id(self, client, auth_headers) -> None:
        """Test GET /jobs/{job_id} returns specific job."""
        # Create test data using the API
        job_data = {
            "Title": "Test Job",
            "Description": "Test description",
            "Requirements": "Test requirements",
            "Location": "Test location",
            "SalaryMin": 40000.0,
            "SalaryMax": 60000.0,
            "Status": "active",
            "EmployeeId": 2,
        }

        create_response = client.post("/jobs/", json=job_data, headers=auth_headers)
        assert create_response.status_code == 200
        job_id = create_response.json()["JobId"]

        response = client.get(f"/jobs/{job_id}", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["JobId"] == job_id
        assert data["Title"] == "Test Job"
        assert data["Status"] == "active"

    def test_get_job_not_found(self, client, auth_headers) -> None:
        """Test GET /jobs/{job_id} returns 404 for non-existent job."""
        response = client.get("/jobs/999", headers=auth_headers)
        assert response.status_code == 404
        data = response.json()
        assert "Job not found" in data["detail"]

    def test_get_jobs_by_status(self, client, auth_headers) -> None:
        """Test GET /jobs/status/{status} returns jobs by status."""
        # Create test data using the API
        job_data_1 = {
            "Title": "Active Job",
            "Description": "Test description",
            "Requirements": "Test requirements",
            "Location": "Test location",
            "SalaryMin": 40000.0,
            "SalaryMax": 60000.0,
            "Status": "active",
            "EmployeeId": 2,
        }

        job_data_2 = {
            "Title": "Closed Job",
            "Description": "Test description",
            "Requirements": "Test requirements",
            "Location": "Test location",
            "SalaryMin": 40000.0,
            "SalaryMax": 60000.0,
            "Status": "closed",
            "EmployeeId": 2,
        }

        client.post("/jobs/", json=job_data_1, headers=auth_headers)
        client.post("/jobs/", json=job_data_2, headers=auth_headers)

        response = client.get("/jobs/status/active", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert all(j["Status"] == "active" for j in data)

    def test_update_job(self, client, auth_headers) -> None:
        """Test PUT /jobs/{job_id} updates job."""
        # Create test data using the API
        job_data = {
            "Title": "Test Job",
            "Description": "Test description",
            "Requirements": "Test requirements",
            "Location": "Test location",
            "SalaryMin": 40000.0,
            "SalaryMax": 60000.0,
            "Status": "active",
            "EmployeeId": 2,
        }

        create_response = client.post("/jobs/", json=job_data, headers=auth_headers)
        assert create_response.status_code == 200
        job_id = create_response.json()["JobId"]

        update_data = {
            "Title": "Senior Software Developer",
            "Description": "Updated description",
            "Status": "closed",
            "SalaryMin": 60000.0,
            "SalaryMax": 80000.0,
        }

        response = client.put(f"/jobs/{job_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["Title"] == "Senior Software Developer"
        assert data["Description"] == "Updated description"
        assert data["Status"] == "closed"
        assert data["SalaryMin"] == 60000.0  # noqa: RUF069
        assert data["SalaryMax"] == 80000.0  # noqa: RUF069

    def test_delete_job(self, client, auth_headers) -> None:
        """Test DELETE /jobs/{job_id} deletes job."""
        # Create test data using the API
        job_data = {
            "Title": "Test Job",
            "Description": "Test description",
            "Requirements": "Test requirements",
            "Location": "Test location",
            "SalaryMin": 40000.0,
            "SalaryMax": 60000.0,
            "Status": "active",
            "EmployeeId": 2,
        }

        create_response = client.post("/jobs/", json=job_data, headers=auth_headers)
        assert create_response.status_code == 200
        job_id = create_response.json()["JobId"]

        # Verify job exists
        response = client.get(f"/jobs/{job_id}", headers=auth_headers)
        assert response.status_code == 200

        # Delete job
        response = client.delete(f"/jobs/{job_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "Job deleted successfully" in data["detail"]

        # Verify job is deleted
        response = client.get(f"/jobs/{job_id}", headers=auth_headers)
        assert response.status_code == 404
