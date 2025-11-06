import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
import os

from main import app
from bd.connection import engine
from bd.dependencies import get_db

# Import models to register them with SQLModel metadata
from models.employees import Employees
from models.licenses import Licenses


# Test database URL (using SQLite for tests)
TEST_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})


@pytest.fixture(scope="function")
def db_session():
    """
    Create a fresh database session for each test.
    """
    # Create all tables
    SQLModel.metadata.create_all(bind=test_engine)

    # Create a new session
    with Session(test_engine) as db:
        try:
            yield db
        finally:
            db.rollback()

    # Drop all tables after test
    SQLModel.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client():
    """
    Create a test client for the FastAPI app.
    """
    # Create all tables before test
    SQLModel.metadata.create_all(bind=test_engine)
    
    # Override the database dependency to use test database
    def override_get_db():
        with Session(test_engine) as db:
            try:
                yield db
            finally:
                db.rollback()

    # Override the database dependency in the app
    app.dependency_overrides[get_db] = override_get_db

    # Create test client
    with TestClient(app) as test_client:
        yield test_client

    # Clear overrides after test
    app.dependency_overrides.clear()
    
    # Drop all tables after test
    SQLModel.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Setup and teardown for the entire test session.
    """
    # Create test database tables
    SQLModel.metadata.create_all(bind=test_engine)

    yield

    # Clean up test database file
    try:
        if os.path.exists("./test.db"):
            os.remove("./test.db")
    except PermissionError:
        # If we can't delete it now, try again later
        pass
