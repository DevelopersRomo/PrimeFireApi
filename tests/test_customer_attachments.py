from pathlib import Path

from fastapi.testclient import TestClient
from sqlmodel import Session

from models.customers import CustomerAttachments, Customers
from tests.conftest import create_test_record


def test_create_customer_attachment(client: TestClient, db_session: Session, auth_headers: dict):
    customer = create_test_record(
        db_session, Customers, CustomerType="commercial", CompanyName="Test Customer", FirstName="Bob", CreatedBy=1
    )

    files = {"file": ("test.txt", b"hello world", "text/plain")}

    response = client.post(f"/customers/{customer.customer_id}/attachments", files=files, headers=auth_headers)
    assert response.status_code in {200, 201}
    data = response.json()
    assert data["file_name"] == "test.txt"
    assert data["file_type"] == "text/plain"
    assert "file_path" in data
    assert data["customer_id"] == customer.customer_id


def test_list_customer_attachments(client: TestClient, db_session: Session, auth_headers: dict):
    customer = create_test_record(
        db_session, Customers, CustomerType="commercial", CompanyName="Test Customer", FirstName="Bob", CreatedBy=1
    )

    # Upload first
    client.post(
        f"/customers/{customer.customer_id}/attachments",
        files={"file": ("test1.txt", b"hello", "text/plain")},
        headers=auth_headers,
    )
    client.post(
        f"/customers/{customer.customer_id}/attachments",
        files={"file": ("test2.pdf", b"fake pdf", "application/pdf")},
        headers=auth_headers,
    )

    # List
    response = client.get(f"/customers/{customer.customer_id}/attachments", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    filenames = [d["file_name"] for d in data]
    assert "test1.txt" in filenames
    assert "test2.pdf" in filenames


def test_get_customer_attachment(client: TestClient, db_session: Session, auth_headers: dict):
    customer = create_test_record(
        db_session, Customers, CustomerType="commercial", CompanyName="Test Cust", FirstName="Bob", CreatedBy=1
    )
    upload_res = client.post(
        f"/customers/{customer.customer_id}/attachments",
        files={"file": ("test_get.txt", b"get me", "text/plain")},
        headers=auth_headers,
    )

    att_id = upload_res.json()["customer_attachment_id"]

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
        f"/customers/{customer.customer_id}/attachments",
        files={"file": ("test_del.txt", b"delete me", "text/plain")},
        headers=auth_headers,
    )

    att_id = upload_res.json()["customer_attachment_id"]

    del_res = client.delete(f"/customers/attachments/{att_id}", headers=auth_headers)
    assert del_res.status_code in {200, 204}

    # Verify deletion
    get_res = client.get(f"/customers/{customer.customer_id}/attachments", headers=auth_headers)
    assert len(get_res.json()) == 0


MAIN_PY = Path(__file__).resolve().parents[1] / "main.py"


def _customer(db_session: Session) -> Customers:
    return create_test_record(
        db_session, Customers, CustomerType="commercial", CompanyName="Test Cust", FirstName="Bob", CreatedBy=1
    )


def test_create_customer_attachment_rejects_client_file_path(
    client: TestClient, db_session: Session, auth_headers: dict
):
    customer = _customer(db_session)

    for file_path in ("../../main.py", str(MAIN_PY)):
        response = client.post(
            f"/customers/{customer.customer_id}/attachments",
            data={"file_path": file_path, "file_name": "main.py", "file_type": "text/plain"},
            headers=auth_headers,
        )
        assert response.status_code == 400
        att_id = response.json().get("customer_attachment_id", 0)
        served = client.get(f"/customers/attachments/{att_id}", headers=auth_headers)
        assert MAIN_PY.read_bytes() not in served.content

    listed = client.get(f"/customers/{customer.customer_id}/attachments", headers=auth_headers).json()
    assert listed == []


def test_get_customer_attachment_outside_upload_root_returns_404(
    client: TestClient, db_session: Session, auth_headers: dict
):
    customer = _customer(db_session)
    for file_path in ("../../main.py", str(MAIN_PY)):
        att = create_test_record(
            db_session,
            CustomerAttachments,
            customer_id=customer.customer_id,
            file_name="main.py",
            file_path=file_path,
            created_by=1,
        )
        db_session.commit()

        response = client.get(f"/customers/attachments/{att.customer_attachment_id}", headers=auth_headers)
        assert response.status_code == 404
        assert MAIN_PY.read_bytes() not in response.content


def test_delete_customer_attachment_removes_stored_file(client: TestClient, db_session: Session, auth_headers: dict):
    customer = _customer(db_session)
    upload_res = client.post(
        f"/customers/{customer.customer_id}/attachments",
        files={"file": ("gone.txt", b"bye", "text/plain")},
        headers=auth_headers,
    )
    stored = Path(upload_res.json()["file_path"])
    assert stored.exists()

    att_id = upload_res.json()["customer_attachment_id"]
    del_res = client.delete(f"/customers/attachments/{att_id}", headers=auth_headers)
    assert del_res.status_code == 200
    assert not stored.exists()


def test_delete_customer_attachment_with_missing_file_succeeds(
    client: TestClient, db_session: Session, auth_headers: dict
):
    customer = _customer(db_session)
    upload_res = client.post(
        f"/customers/{customer.customer_id}/attachments",
        files={"file": ("missing.txt", b"x", "text/plain")},
        headers=auth_headers,
    )
    Path(upload_res.json()["file_path"]).unlink()

    att_id = upload_res.json()["customer_attachment_id"]
    del_res = client.delete(f"/customers/attachments/{att_id}", headers=auth_headers)
    assert del_res.status_code == 200


def test_delete_customer_attachment_never_unlinks_outside_upload_root(
    client: TestClient, db_session: Session, auth_headers: dict, tmp_path: Path
):
    outside = tmp_path / "keep.txt"
    outside.write_bytes(b"keep")
    customer = _customer(db_session)
    att = create_test_record(
        db_session,
        CustomerAttachments,
        customer_id=customer.customer_id,
        file_name="keep.txt",
        file_path=str(outside),
        created_by=1,
    )
    db_session.commit()

    del_res = client.delete(f"/customers/attachments/{att.customer_attachment_id}", headers=auth_headers)
    assert del_res.status_code == 200
    assert outside.exists()
