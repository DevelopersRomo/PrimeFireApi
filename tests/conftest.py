"""
Pytest configuration with automatic rollback for tests.

This conftest provides fixtures that ensure each test runs in isolation
by wrapping all database operations in a transaction and rolling back
at the end of each test.
"""

import os
import tempfile
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine

from bd.dependencies import get_db, get_main_db
from main import app

# =============================================================================
# Test Database Configuration
# =============================================================================


def get_test_db_path():
    """Get a unique temporary database path for each test session."""
    temp_dir = tempfile.gettempdir()
    return os.path.join(temp_dir, "primefire_test.db")  # noqa: PTH118


TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", f"sqlite:///{get_test_db_path()}")

# Store engine globally to share between fixtures
_test_engine = None


@pytest.fixture(autouse=True)
def setup_and_cleanup():
    """
    Setup and cleanup for each test.
    Creates fresh database tables before test and drops after.
    """
    global _test_engine  # noqa: PLW0603

    # Create engine
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False} if "sqlite" in TEST_DATABASE_URL else {},
        echo=False,
    )

    # Remove schema from all models for SQLite compatibility
    if "sqlite" in TEST_DATABASE_URL:
        for table in SQLModel.metadata.tables.values():
            table.schema = None
            if hasattr(table, "_schema"):
                table._schema = None  # noqa: SLF001

    # Create all tables
    SQLModel.metadata.create_all(bind=engine)
    _test_engine = engine

    yield

    # Drop all tables after test
    SQLModel.metadata.drop_all(bind=engine)

    # Dispose engine connections
    engine.dispose()
    _test_engine = None


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Provide a database session for tests."""
    global _test_engine
    if _test_engine is None:
        raise RuntimeError("Test engine not initialized")

    connection = _test_engine.connect()
    # Autoflush must be True for typical usage, but autocommit False
    session = Session(bind=connection, autoflush=True, autocommit=False)

    try:
        yield session
    finally:
        session.close()
        connection.close()


@pytest.fixture(autouse=True)
def mock_upload_dirs(monkeypatch):
    """
    Override UPLOAD_DIR for tests that upload files so that no real files are created
    in the project's 'uploads' directory. All files are automatically rolled back.
    """
    from pathlib import Path

    import api.curriculums
    import api.customer_attachments
    import api.ticket_attachments

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        monkeypatch.setattr(api.customer_attachments, "UPLOAD_DIR", tmp_path / "customers")
        monkeypatch.setattr(api.ticket_attachments, "UPLOAD_DIR", tmp_path / "tickets")
        monkeypatch.setattr(api.curriculums, "UPLOAD_DIR", tmp_path / "curriculums")

        # Also ensure the mocked dirs exist
        (tmp_path / "customers").mkdir(parents=True, exist_ok=True)
        (tmp_path / "tickets").mkdir(parents=True, exist_ok=True)
        (tmp_path / "curriculums").mkdir(parents=True, exist_ok=True)

        yield


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """
    Create a test client for the FastAPI app.

    This fixture provides a test client that uses the shared test database.
    All changes persist during the test but are cleaned up automatically after.
    """
    global _test_engine  # noqa: PLW0602

    # Override the database dependency to use test database
    def override_get_db():
        if _test_engine is None:
            raise RuntimeError("Test engine not initialized")

        connection = _test_engine.connect()
        session = Session(bind=connection, autoflush=True, autocommit=False)

        try:
            yield session
        finally:
            session.rollback()
            session.close()
            connection.close()

    # Apply the override
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_main_db] = override_get_db

    # Create test client
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client

    # Clear overrides
    app.dependency_overrides.clear()

    # Rollback any remaining transactions
    if _test_engine:
        try:
            conn = _test_engine.connect()
            conn.rollback()
            conn.close()
        except Exception:
            pass


@pytest.fixture
def auth_headers(db_session: Session) -> dict:
    from sqlmodel import select

    from models.employees import Employees

    emp = db_session.exec(select(Employees).where(Employees.Email == "test@example.com")).first()
    if not emp:
        emp = Employees(Email="test@example.com", EmployeeId=1)
        db_session.add(emp)
        db_session.commit()

    """
    Generate authentication headers for API tests.

    This fixture provides a mock JWT token for testing protected endpoints.
    """
    from datetime import datetime, timedelta

    import jwt

    from core.config import settings

    SECRET_KEY = settings.BACKEND_CLIENT_SECRET or "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM = "HS256"

    # Create a test token with 'type': 'internal' as required by simple_token_validator
    payload = {
        "sub": "test@example.com",
        "user_id": 1,
        "role": "admin",
        "tenant_key": None,
        "type": "internal",  # Required for internal JWT validation
        "exp": datetime.utcnow() + timedelta(hours=24),  # noqa: DTZ003
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="session", autouse=True)
def setup_test_env() -> None:
    """
    Setup test environment variables.
    Run once per test session.
    """
    os.environ.setdefault("ENVIRONMENT", "test")
    # Cleanup


# =============================================================================
# Utilities for Tests
# =============================================================================


def create_test_record(session: Session, model_class, **kwargs):
    """
    Helper to create a test record without committing.

    Usage:
        employee = create_test_record(db_session, Employees, Name="John", Role="Dev")
    """
    if model_class.__name__ == "Customers":
        if "CustomerType" not in kwargs:
            kwargs["CustomerType"] = "commercial"
        if "CreatedBy" not in kwargs:
            kwargs["CreatedBy"] = 1
        if "CompanyName" not in kwargs:
            kwargs["CompanyName"] = "Test Company"
        kwargs.pop("Name", None)
        kwargs.pop("ContactName", None)
    record = model_class(**kwargs)
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def get_or_create(session: Session, model_class, defaults=None, **kwargs):
    """
    Get existing record or create new one without committing.

    Returns tuple (record, created).
    """
    from sqlmodel import select

    statement = select(model_class).where(*(getattr(model_class, k) == v for k, v in kwargs.items()))
    record = session.exec(statement).first()

    if record:
        return record, False

    defaults = defaults or {}

    if model_class.__name__ == "Customers":
        if "CustomerType" not in defaults:
            defaults["CustomerType"] = "commercial"
        if "CreatedBy" not in defaults:
            defaults["CreatedBy"] = 1
        if "CompanyName" not in defaults:
            defaults["CompanyName"] = "Test Company"
        if "Name" in defaults:
            del defaults["Name"]
        if "ContactName" in defaults:
            del defaults["ContactName"]
    defaults.update(kwargs)
    record = model_class(**defaults)
    session.add(record)
    session.commit()
    session.refresh(record)
    return record, True
