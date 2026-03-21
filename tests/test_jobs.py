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
            "title": "Software Developer",
            "description": "We are looking for a skilled software developer",
            "requirements": "Python, FastAPI, SQL experience required",
            "location": "Remote",
            "salary_min": 50000.0,
            "salary_max": 70000.0,
            "status": "active",
            "employee_id": 2,
        }

        response = client.post("/jobs/", json=job_data, headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["title"] == "Software Developer"
        assert data["description"] == "We are looking for a skilled software developer"
        assert data["location"] == "Remote"
        assert data["salary_min"] == 50000.0  # noqa: RUF069
        assert data["salary_max"] == 70000.0  # noqa: RUF069
        assert data["status"] == "active"
        assert data["job_id"] is not None

    def test_get_job_by_id(self, client, auth_headers) -> None:
        """Test GET /jobs/{job_id} returns specific job."""
        # Create test data using the API
        job_data = {
            "title": "Test Job",
            "description": "Test description",
            "requirements": "Test requirements",
            "location": "Test location",
            "salary_min": 40000.0,
            "salary_max": 60000.0,
            "status": "active",
            "employee_id": 2,
        }

        create_response = client.post("/jobs/", json=job_data, headers=auth_headers)
        assert create_response.status_code == 200
        job_id = create_response.json()["job_id"]

        response = client.get(f"/jobs/{job_id}", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["job_id"] == job_id
        assert data["title"] == "Test Job"
        assert data["status"] == "active"

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
            "title": "Active Job",
            "description": "Test description",
            "requirements": "Test requirements",
            "location": "Test location",
            "salary_min": 40000.0,
            "salary_max": 60000.0,
            "status": "active",
            "employee_id": 2,
        }

        job_data_2 = {
            "title": "Closed Job",
            "description": "Test description",
            "requirements": "Test requirements",
            "location": "Test location",
            "salary_min": 40000.0,
            "salary_max": 60000.0,
            "status": "closed",
            "employee_id": 2,
        }

        client.post("/jobs/", json=job_data_1, headers=auth_headers)
        client.post("/jobs/", json=job_data_2, headers=auth_headers)

        response = client.get("/jobs/status/active", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert all(j["status"] == "active" for j in data)

    def test_update_job(self, client, auth_headers) -> None:
        """Test PUT /jobs/{job_id} updates job."""
        # Create test data using the API
        job_data = {
            "title": "Test Job",
            "description": "Test description",
            "requirements": "Test requirements",
            "location": "Test location",
            "salary_min": 40000.0,
            "salary_max": 60000.0,
            "status": "active",
            "employee_id": 2,
        }

        create_response = client.post("/jobs/", json=job_data, headers=auth_headers)
        assert create_response.status_code == 200
        job_id = create_response.json()["job_id"]

        update_data = {
            "title": "Senior Software Developer",
            "description": "Updated description",
            "status": "closed",
            "salary_min": 60000.0,
            "salary_max": 80000.0,
        }

        response = client.put(f"/jobs/{job_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["title"] == "Senior Software Developer"
        assert data["description"] == "Updated description"
        assert data["status"] == "closed"
        assert data["salary_min"] == 60000.0  # noqa: RUF069
        assert data["salary_max"] == 80000.0  # noqa: RUF069

    def test_delete_job(self, client, auth_headers) -> None:
        """Test DELETE /jobs/{job_id} deletes job."""
        # Create test data using the API
        job_data = {
            "title": "Test Job",
            "description": "Test description",
            "requirements": "Test requirements",
            "location": "Test location",
            "salary_min": 40000.0,
            "salary_max": 60000.0,
            "status": "active",
            "employee_id": 2,
        }

        create_response = client.post("/jobs/", json=job_data, headers=auth_headers)
        assert create_response.status_code == 200
        job_id = create_response.json()["job_id"]

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
