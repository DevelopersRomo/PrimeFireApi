from fastapi.testclient import TestClient
from sqlmodel import Session

from models.customers import Customers
from tests.conftest import create_test_record


def test_create_customer_attachment(client: TestClient, db_session: Session, auth_headers: dict):
    customer = create_test_record(
        db_session, Customers, CustomerType="commercial", CompanyName="Test Customer", FirstName="Bob", CreatedBy=1
    )

    files = {"file": ("test.txt", b"hello world", "text/plain")}

    response = client.post(f"/customers/{customer.CustomerId}/attachments", files=files, headers=auth_headers)
    assert response.status_code in {200, 201}
    data = response.json()
    assert data["FileName"] == "test.txt"
    assert data["FileType"] == "text/plain"
    assert "FilePath" in data
    assert data["CustomerId"] == customer.CustomerId


def test_list_customer_attachments(client: TestClient, db_session: Session, auth_headers: dict):
    customer = create_test_record(
        db_session, Customers, CustomerType="commercial", CompanyName="Test Customer", FirstName="Bob", CreatedBy=1
    )

    # Upload first
    client.post(
        f"/customers/{customer.CustomerId}/attachments",
        files={"file": ("test1.txt", b"hello", "text/plain")},
        headers=auth_headers,
    )
    client.post(
        f"/customers/{customer.CustomerId}/attachments",
        files={"file": ("test2.pdf", b"fake pdf", "application/pdf")},
        headers=auth_headers,
    )

    # List
    response = client.get(f"/customers/{customer.CustomerId}/attachments", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    filenames = [d["FileName"] for d in data]
    assert "test1.txt" in filenames
    assert "test2.pdf" in filenames


def test_get_customer_attachment(client: TestClient, db_session: Session, auth_headers: dict):
    customer = create_test_record(
        db_session, Customers, CustomerType="commercial", CompanyName="Test Cust", FirstName="Bob", CreatedBy=1
    )
    upload_res = client.post(
        f"/customers/{customer.CustomerId}/attachments",
        files={"file": ("test_get.txt", b"get me", "text/plain")},
        headers=auth_headers,
    )

    att_id = upload_res.json()["CustomerAttachmentId"]

    # Get attachment record or download? If it returns file, it should be 200 and have content.
    # The route might return the file directly using FileResponse if it's get_attachment
    response = client.get(f"/customers/attachments/{att_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.content == b"get me"


def test_delete_customer_attachment(client: TestClient, db_session: Session, auth_headers: dict):
    customer = create_test_record(
        db_session, Customers, CustomerType="commercial", CompanyName="Test Cust", FirstName="Bob", CreatedBy=1
    )
    upload_res = client.post(
        f"/customers/{customer.CustomerId}/attachments",
        files={"file": ("test_del.txt", b"delete me", "text/plain")},
        headers=auth_headers,
    )

    att_id = upload_res.json()["CustomerAttachmentId"]

    del_res = client.delete(f"/customers/attachments/{att_id}", headers=auth_headers)
    assert del_res.status_code in {200, 204}

    # Verify deletion
    get_res = client.get(f"/customers/{customer.CustomerId}/attachments", headers=auth_headers)
    assert len(get_res.json()) == 0
