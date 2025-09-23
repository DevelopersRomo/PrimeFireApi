import pytest
from sqlmodel import Session, select

from models.jobs import Jobs
from schemas.jobs import JobCreate


class TestJobsAPI:
    """Test cases for Jobs API endpoints"""

    def test_get_jobs_empty(self, client):
        """Test GET /jobs/ returns empty list when no jobs exist"""
        response = client.get("/jobs/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_create_job(self, client):
        """Test POST /jobs/ creates a new job"""
        job_data = {
            "Title": "Software Developer",
            "Description": "We are looking for a skilled software developer",
            "Requirements": "Python, FastAPI, SQL experience required",
            "Location": "Remote",
            "SalaryMin": 50000.0,
            "SalaryMax": 70000.0,
            "Status": "active",
            "EmployeeId": 2
        }

        response = client.post("/jobs/", json=job_data)
        assert response.status_code == 200

        data = response.json()
        assert data["Title"] == "Software Developer"
        assert data["Description"] == "We are looking for a skilled software developer"
        assert data["Location"] == "Remote"
        assert data["SalaryMin"] == 50000.0
        assert data["SalaryMax"] == 70000.0
        assert data["Status"] == "active"
        assert data["JobId"] is not None

    def test_get_job_by_id(self, client, db_session: Session):
        """Test GET /jobs/{job_id} returns specific job"""
        # Create test data
        job = self._create_test_job(db_session)

        response = client.get(f"/jobs/{job.JobId}")
        assert response.status_code == 200

        data = response.json()
        assert data["JobId"] == job.JobId
        assert data["Title"] == job.Title
        assert data["Status"] == job.Status

    def test_get_job_not_found(self, client):
        """Test GET /jobs/{job_id} returns 404 for non-existent job"""
        response = client.get("/jobs/999")
        assert response.status_code == 404
        data = response.json()
        assert "Job not found" in data["detail"]

    def test_get_jobs_by_status(self, client, db_session: Session):
        """Test GET /jobs/status/{status} returns jobs by status"""
        # Create test data
        self._create_test_job(db_session, "Active Job", "active")
        self._create_test_job(db_session, "Closed Job", "closed")

        response = client.get("/jobs/status/active")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert all(j["Status"] == "active" for j in data)

    def test_update_job(self, client, db_session: Session):
        """Test PUT /jobs/{job_id} updates job"""
        # Create test data
        job = self._create_test_job(db_session)

        update_data = {
            "Title": "Senior Software Developer",
            "Description": "Updated description",
            "Status": "closed",
            "SalaryMin": 60000.0,
            "SalaryMax": 80000.0
        }

        response = client.put(f"/jobs/{job.JobId}", json=update_data)
        assert response.status_code == 200

        data = response.json()
        assert data["Title"] == "Senior Software Developer"
        assert data["Description"] == "Updated description"
        assert data["Status"] == "closed"
        assert data["SalaryMin"] == 60000.0
        assert data["SalaryMax"] == 80000.0

    def test_delete_job(self, client, db_session: Session):
        """Test DELETE /jobs/{job_id} deletes job"""
        # Create test data
        job = self._create_test_job(db_session)

        # Verify job exists
        response = client.get(f"/jobs/{job.JobId}")
        assert response.status_code == 200

        # Delete job
        response = client.delete(f"/jobs/{job.JobId}")
        assert response.status_code == 200
        data = response.json()
        assert "Job deleted successfully" in data["detail"]

        # Verify job is deleted
        response = client.get(f"/jobs/{job.JobId}")
        assert response.status_code == 404

    def _create_test_job(self, db_session: Session, title: str = "Test Job", status: str = "active") -> Jobs:
        """Helper method to create a test job"""
        job = Jobs(
            Title=title,
            Description="Test description",
            Requirements="Test requirements",
            Location="Test location",
            SalaryMin=40000.0,
            SalaryMax=60000.0,
            Status=status,
            EmployeeId=2
        )
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)
        return job

