from fastapi.testclient import TestClient
from sqlmodel import Session

from models.customers import Customers
from tests.conftest import create_test_record


def test_debug(client: TestClient, db_session: Session, auth_headers: dict):
    """Debug test - verifies attachment upload works correctly."""
    customer = create_test_record(
        db_session, Customers, customer_type="commercial", company_name="Test Customer", first_name="Bob"
    )
    response = client.post(
        f"/customers/{customer.customer_id}/attachments",
        files={"file": ("t.txt", b"test content", "text/plain")},
        headers=auth_headers,
    )
    assert response.status_code == 200
