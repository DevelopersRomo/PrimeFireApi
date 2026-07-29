import io
import zipfile
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

import api.agreements as agreements_api
from api.dependencies import get_current_employee_with_permissions
from main import app
from models.agreements import AgreementAttachments, Agreements
from models.customers import Customers
from models.employees import Employees

FULL_PERMISSIONS = {
    "can_view": True,
    "can_create": True,
    "can_edit": True,
    "can_delete": True,
    "admin_actions": True,
}


def test_module_seed_repairs_legacy_data_and_uses_customer_permissions() -> None:
    sql = (Path(__file__).parents[1] / "bd" / "sql" / "CREATE_AGREEMENTS_MODULE.sql").read_text(encoding="utf-8")

    assert "UPDATE dbo.modules\nSET created_at = @now\nWHERE created_at IS NULL;" in sql
    assert "FROM dbo.role_modules AS customer_permissions" in sql
    assert "INNER JOIN dbo.role_modules AS parent_permissions" in sql
    assert "agreements_permissions.can_view = parent_permissions.can_view" in sql


@pytest.fixture
def agreement_context(db_session: Session):
    employee = Employees(email="agreements@example.com", display_name="Agreement Owner")
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)
    customer = Customers(customer_type="commercial", company_name="Legal Customer", created_by=employee.employee_id)
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)

    def permissions():
        return {
            "employee": {"employee_id": employee.employee_id},
            "permissions": [{"module_key": "agreements", "permissions": FULL_PERMISSIONS}],
        }

    app.dependency_overrides[get_current_employee_with_permissions] = permissions
    yield employee, customer
    app.dependency_overrides.pop(get_current_employee_with_permissions, None)


def pdf_bytes(label: bytes = b"agreement") -> bytes:
    return b"%PDF-1.4\n" + label + b"\n%%EOF"


def office_bytes(required_entry: str) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("[Content_Types].xml", "<Types />")
        archive.writestr(required_entry, "<document />")
    return buffer.getvalue()


def create_payload(employee: Employees, customer: Customers) -> dict[str, str]:
    today = datetime.now(UTC).date()
    return {
        "title": "Fire Protection Services",
        "agreement_type": "SERVICE_AGREEMENT",
        "customer_id": str(customer.customer_id),
        "counterparty_name": "Legal Customer LLC",
        "owner_employee_id": str(employee.employee_id),
        "effective_date": today.isoformat(),
        "expiration_date": (today + timedelta(days=365)).isoformat(),
    }


def test_create_requires_valid_primary_and_returns_active_lifecycle(
    client: TestClient, db_session: Session, agreement_context
):
    employee, customer = agreement_context
    response = client.post(
        "/agreements",
        data=create_payload(employee, customer),
        files={"primary_file": ("service.pdf", pdf_bytes(), "application/pdf")},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["lifecycle_status"] == "ACTIVE"
    assert body["counterparty_name"] == "Legal Customer LLC"
    assert body["current_primary"]["version_number"] == 1
    assert body["current_primary"]["sha256"]
    assert db_session.exec(select(Agreements)).one().agreement_id == body["agreement_id"]


def test_rejects_spoofed_document_without_creating_record(client: TestClient, db_session: Session, agreement_context):
    employee, customer = agreement_context
    response = client.post(
        "/agreements",
        data=create_payload(employee, customer),
        files={"primary_file": ("service.pdf", b"not a pdf", "application/pdf")},
    )

    assert response.status_code == 400
    assert db_session.exec(select(Agreements)).first() is None


def test_rejects_openxml_container_missing_required_document(
    client: TestClient, db_session: Session, agreement_context
):
    employee, customer = agreement_context
    response = client.post(
        "/agreements",
        data=create_payload(employee, customer),
        files={
            "primary_file": (
                "service.docx",
                office_bytes("xl/workbook.xml"),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )

    assert response.status_code == 400
    assert db_session.exec(select(Agreements)).first() is None


def test_accepts_valid_openxml_and_rejects_macro_extension(client: TestClient, agreement_context):
    employee, customer = agreement_context
    response = client.post(
        "/agreements",
        data=create_payload(employee, customer),
        files={
            "primary_file": (
                "service.docx",
                office_bytes("word/document.xml"),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert response.status_code == 201

    rejected = client.post(
        "/agreements",
        data={**create_payload(employee, customer), "title": "Macro"},
        files={"primary_file": ("macro.docm", office_bytes("word/document.xml"), "application/octet-stream")},
    )
    assert rejected.status_code == 400


def test_primary_replacement_retains_version_history(client: TestClient, db_session: Session, agreement_context):
    employee, customer = agreement_context
    created = client.post(
        "/agreements",
        data=create_payload(employee, customer),
        files={"primary_file": ("service.pdf", pdf_bytes(b"v1"), "application/pdf")},
    ).json()

    response = client.post(
        f"/agreements/{created['agreement_id']}/attachments/primary",
        data={"replacement_reason": "Executed amendment"},
        files={"file": ("service-v2.pdf", pdf_bytes(b"v2"), "application/pdf")},
    )

    assert response.status_code == 201
    assert response.json()["version_number"] == 2
    rows = db_session.exec(
        select(AgreementAttachments).where(AgreementAttachments.agreement_id == created["agreement_id"])
    ).all()
    assert len(rows) == 2
    assert sum(row.is_current for row in rows) == 1
    assert {row.version_number for row in rows} == {1, 2}


def test_archive_restore_and_termination_are_separate(client: TestClient, agreement_context):
    employee, customer = agreement_context
    agreement_id = client.post(
        "/agreements",
        data=create_payload(employee, customer),
        files={"primary_file": ("service.pdf", pdf_bytes(), "application/pdf")},
    ).json()["agreement_id"]

    archived = client.delete(f"/agreements/{agreement_id}")
    assert archived.status_code == 200
    assert archived.json()["archived_at"] is not None
    assert archived.json()["lifecycle_status"] == "ACTIVE"

    restored = client.post(f"/agreements/{agreement_id}/restore")
    assert restored.status_code == 200
    assert restored.json()["archived_at"] is None

    terminated = client.patch(
        f"/agreements/{agreement_id}/termination",
        json={
            "terminated_on": datetime.now(UTC).date().isoformat(),
            "termination_reason": "Completed by mutual agreement",
        },
    )
    assert terminated.status_code == 200
    assert terminated.json()["lifecycle_status"] == "TERMINATED"


def test_permission_is_required(client: TestClient, agreement_context):
    app.dependency_overrides[get_current_employee_with_permissions] = lambda: {
        "employee": {"employee_id": agreement_context[0].employee_id},
        "permissions": [],
    }
    response = client.get("/agreements")
    assert response.status_code == 403


def test_upcoming_and_expired_lifecycle_boundaries(agreement_context):
    employee, _customer = agreement_context
    today = datetime.now(UTC).date()
    upcoming = Agreements(
        title="Upcoming",
        agreement_type="OTHER",
        counterparty_name="Future Counterparty",
        owner_employee_id=employee.employee_id,
        effective_date=today + timedelta(days=1),
        created_by=employee.employee_id,
    )
    expired = Agreements(
        title="Expired",
        agreement_type="OTHER",
        counterparty_name="Past Counterparty",
        owner_employee_id=employee.employee_id,
        effective_date=today - timedelta(days=2),
        expiration_date=today - timedelta(days=1),
        created_by=employee.employee_id,
    )

    assert agreements_api._lifecycle(upcoming, today) == "UPCOMING"  # noqa: SLF001
    assert agreements_api._lifecycle(expired, today) == "EXPIRED"  # noqa: SLF001


def test_interrupted_write_removes_temporary_and_partial_files(monkeypatch, agreement_context):
    real_open = agreements_api.Path.open

    class InterruptedWriter:
        def __init__(self, path):
            self.path = path
            self.handle = None

        def __enter__(self):
            self.handle = real_open(self.path, "xb")
            return self

        def write(self, content):
            self.handle.write(content[:4])
            raise OSError("simulated interrupted write")

        def __exit__(self, exc_type, exc_value, traceback):
            self.handle.close()
            return False

    def interrupted_open(path, mode="r", *args, **kwargs):
        if mode == "xb" and path.name.endswith(".tmp"):
            return InterruptedWriter(path)
        return real_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(agreements_api.Path, "open", interrupted_open)

    with pytest.raises(OSError, match="simulated interrupted write"):
        agreements_api._write_file(1, ".pdf", pdf_bytes())  # noqa: SLF001

    assert not list(agreements_api.UPLOAD_DIR.rglob("*.tmp"))
    assert not [path for path in agreements_api.UPLOAD_DIR.rglob("*") if path.is_file()]


def test_cleanup_failure_does_not_raise(monkeypatch, tmp_path):
    path = tmp_path / "cleanup.pdf"
    path.write_bytes(pdf_bytes())

    def failing_unlink(*_args, **_kwargs):
        raise OSError("simulated cleanup failure")

    monkeypatch.setattr(agreements_api.Path, "unlink", failing_unlink)

    agreements_api._remove_file(path)  # noqa: SLF001


def test_creation_refresh_failure_rolls_back_metadata_and_file(
    client: TestClient, db_session: Session, agreement_context, monkeypatch
):
    employee, customer = agreement_context
    real_refresh = Session.refresh

    def failing_refresh(session, instance, *args, **kwargs):
        if isinstance(instance, Agreements):
            raise OSError("simulated pre-commit refresh failure")
        return real_refresh(session, instance, *args, **kwargs)

    monkeypatch.setattr(Session, "refresh", failing_refresh)
    response = client.post(
        "/agreements",
        data=create_payload(employee, customer),
        files={"primary_file": ("service.pdf", pdf_bytes(), "application/pdf")},
    )

    assert response.status_code == 500
    assert db_session.exec(select(Agreements)).first() is None
    assert not [path for path in agreements_api.UPLOAD_DIR.rglob("*") if path.is_file()]


def test_attachment_refresh_failure_keeps_existing_version_and_removes_new_file(
    client: TestClient, db_session: Session, agreement_context, monkeypatch
):
    employee, customer = agreement_context
    created = client.post(
        "/agreements",
        data=create_payload(employee, customer),
        files={"primary_file": ("service.pdf", pdf_bytes(b"v1"), "application/pdf")},
    ).json()
    real_refresh = Session.refresh

    def failing_refresh(session, instance, *args, **kwargs):
        if isinstance(instance, AgreementAttachments):
            raise OSError("simulated attachment refresh failure")
        return real_refresh(session, instance, *args, **kwargs)

    monkeypatch.setattr(Session, "refresh", failing_refresh)
    response = client.post(
        f"/agreements/{created['agreement_id']}/attachments/primary",
        data={"replacement_reason": "Failed replacement"},
        files={"file": ("service-v2.pdf", pdf_bytes(b"v2"), "application/pdf")},
    )

    assert response.status_code == 500
    rows = db_session.exec(
        select(AgreementAttachments).where(AgreementAttachments.agreement_id == created["agreement_id"])
    ).all()
    assert len(rows) == 1
    assert rows[0].is_current is True
    assert len([path for path in agreements_api.UPLOAD_DIR.rglob("*") if path.is_file()]) == 1


def test_post_commit_detail_failure_keeps_committed_metadata_and_file(
    client: TestClient, db_session: Session, agreement_context, monkeypatch
):
    employee, customer = agreement_context

    def failing_detail(_db, _agreement):
        raise RuntimeError("simulated response failure")

    monkeypatch.setattr(agreements_api, "_detail", failing_detail)
    response = client.post(
        "/agreements",
        data=create_payload(employee, customer),
        files={"primary_file": ("service.pdf", pdf_bytes(), "application/pdf")},
    )

    assert response.status_code == 500
    assert db_session.exec(select(Agreements)).first() is not None
    assert db_session.exec(select(AgreementAttachments)).first() is not None
    assert len([path for path in agreements_api.UPLOAD_DIR.rglob("*") if path.is_file()]) == 1
