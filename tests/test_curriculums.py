"""
Tests for Curriculums API endpoints.

Note: All tests that create files automatically clean up after themselves
to avoid leaving test artifacts in the uploads/curriculums directory.
"""

import io
from pathlib import Path

from sqlmodel import Session

from models.curriculums import Curriculums
from models.jobs import Jobs


class TestCurriculumsAPI:
    """Test cases for Curriculums API endpoints."""

    def test_get_curriculums_empty(self, client, auth_headers: dict) -> None:
        """Test GET /curriculums/ returns empty list when no curriculums exist."""
        response = client.get("/curriculums/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_create_curriculum_with_file(self, client, db_session: Session, auth_headers: dict) -> None:
        """Test POST /curriculums/upload creates a new curriculum with file upload."""
        # Create a test job first
        job = self._create_test_job(db_session)

        # Create a mock PDF file
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(Hello World) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000010 00000 n \n0000000053 00000 n \n0000000125 00000 n \n0000000205 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n297\n%%EOF"
        pdf_file = io.BytesIO(pdf_content)
        pdf_file.name = "test_resume.pdf"

        # Prepare form data
        form_data = {
            "job_id": str(job.job_id),
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1234567890",
            "cover_letter": "I am very interested in this position...",
            "status": "pending",
        }

        # Create files dict for the test
        files = {"resume_file": ("test_resume.pdf", pdf_file, "application/pdf")}

        response = client.post("/curriculums/upload", data=form_data, files=files, headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "John Doe"
        assert data["email"] == "john.doe@example.com"
        assert data["phone"] == "+1234567890"
        assert data["cover_letter"] == "I am very interested in this position..."
        assert data["status"] == "pending"
        assert data["job_id"] == job.job_id
        assert data["curriculum_id"] is not None
        assert data["curriculum_path"] is not None
        assert "curriculums" in data["curriculum_path"]

        # Cleanup: delete the uploaded file to avoid leaving test artifacts
        if data["curriculum_path"] and Path(data["curriculum_path"]).exists():
            Path(data["curriculum_path"]).unlink()

    def test_create_curriculum_simple(self, client, db_session: Session, auth_headers: dict) -> None:
        """Test POST /curriculums/ creates a new curriculum without file."""
        # Create a test job first
        job = self._create_test_job(db_session)

        curriculum_data = {
            "job_id": job.job_id,
            "name": "Jane Smith",
            "email": "jane.smith@example.com",
            "phone": "+0987654321",
            "cover_letter": "I am very interested in this position...",
            "status": "pending",
            "employee_id": None,
        }

        response = client.post("/curriculums/", json=curriculum_data, headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "Jane Smith"
        assert data["email"] == "jane.smith@example.com"
        assert data["phone"] == "+0987654321"
        assert data["cover_letter"] == "I am very interested in this position..."
        assert data["status"] == "pending"
        assert data["job_id"] == job.job_id
        assert data["curriculum_id"] is not None

    def test_get_curriculum_by_id(self, client, db_session: Session, auth_headers: dict) -> None:
        """Test GET /curriculums/{curriculum_id} returns specific curriculum."""
        # Create test data
        curriculum = self._create_test_curriculum(db_session)

        response = client.get(f"/curriculums/{curriculum.curriculum_id}", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["curriculum_id"] == curriculum.curriculum_id
        assert data["name"] == curriculum.name
        assert data["email"] == curriculum.email

    def test_get_curriculum_not_found(self, client, auth_headers: dict) -> None:
        """Test GET /curriculums/{curriculum_id} returns 404 for non-existent curriculum."""
        response = client.get("/curriculums/999", headers=auth_headers)
        assert response.status_code == 404
        data = response.json()
        assert "Curriculum not found" in data["detail"]

    def test_get_curriculums_by_job(self, client, db_session: Session, auth_headers: dict) -> None:
        """Test GET /curriculums/job/{job_id} returns curriculums for specific job."""
        # Create test job and curriculums
        job1 = self._create_test_job(db_session, "Job 1")
        job2 = self._create_test_job(db_session, "Job 2")

        self._create_test_curriculum(db_session, job1.job_id, "John Doe")
        self._create_test_curriculum(db_session, job1.job_id, "Jane Smith")
        self._create_test_curriculum(db_session, job2.job_id, "Bob Johnson")

        response = client.get(f"/curriculums/job/{job1.job_id}", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert all(c["job_id"] == job1.job_id for c in data)

        names = [c["name"] for c in data]
        assert "John Doe" in names
        assert "Jane Smith" in names

    def test_get_curriculums_by_status(self, client, db_session: Session, auth_headers: dict) -> None:
        """Test GET /curriculums/status/{status} returns curriculums by status."""
        # Create test data
        job = self._create_test_job(db_session)
        self._create_test_curriculum(db_session, job.job_id, "Pending Curriculum", "pending")
        self._create_test_curriculum(db_session, job.job_id, "Reviewed Curriculum", "reviewed")

        response = client.get("/curriculums/status/pending", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert all(c["status"] == "pending" for c in data)

    def test_update_curriculum(self, client, db_session: Session, auth_headers: dict) -> None:
        """Test PUT /curriculums/{curriculum_id} updates curriculum."""
        # Create test data
        curriculum = self._create_test_curriculum(db_session)

        update_data = {
            "name": "Updated Name",
            "email": "updated@example.com",
            "status": "reviewed",
            "cover_letter": "Updated cover letter",
        }

        response = client.put(f"/curriculums/{curriculum.curriculum_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["email"] == "updated@example.com"
        assert data["status"] == "reviewed"
        assert data["cover_letter"] == "Updated cover letter"

    def test_delete_curriculum(self, client, db_session: Session, auth_headers: dict) -> None:
        """Test DELETE /curriculums/{curriculum_id} deletes curriculum."""
        # Create test data
        curriculum = self._create_test_curriculum(db_session)

        # Verify curriculum exists
        response = client.get(f"/curriculums/{curriculum.curriculum_id}", headers=auth_headers)
        assert response.status_code == 200

        # Delete curriculum
        response = client.delete(f"/curriculums/{curriculum.curriculum_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "Curriculum deleted successfully" in data["detail"]

        # Verify curriculum is deleted
        response = client.get(f"/curriculums/{curriculum.curriculum_id}", headers=auth_headers)
        assert response.status_code == 404

    def _create_test_job(self, db_session: Session, title: str = "Test Job") -> Jobs:
        """Helper method to create a test job."""
        job = Jobs(
            title=title,
            description="Test description",
            requirements="Test requirements",
            location="Test location",
            salary_min=40000.0,
            salary_max=60000.0,
            status="active",
            employee_id=2,
        )
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)
        return job

    def _create_test_curriculum(
        self, db_session: Session, job_id: int | None = None, name: str = "Test Applicant", status: str = "pending"
    ) -> Curriculums:
        """Helper method to create a test curriculum."""
        if job_id is None:
            job = self._create_test_job(db_session)
            job_id = job.job_id

        curriculum = Curriculums(
            job_id=job_id,
            name=name,
            email=f"{name.lower().replace(' ', '.')}@example.com",
            phone="+1234567890",
            curriculum_path="/uploads/curriculums/test.pdf",
            cover_letter="Test cover letter",
            status=status,
            employee_id=None,
        )
        db_session.add(curriculum)
        db_session.commit()
        db_session.refresh(curriculum)
        return curriculum
