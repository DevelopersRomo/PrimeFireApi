import pytest
from sqlmodel import select

from models.employees import EmployeeRoles, Employees, Roles
from models.products import Products
from models.inventory import Warehouses
from tests.conftest import create_test_record


@pytest.fixture(autouse=True)
def disable_notifications(monkeypatch):
    from core.config import settings

    monkeypatch.setattr(settings, "SEND_NOTIFICATIONS", False, raising=False)


@pytest.fixture
def product(db_session):
    return create_test_record(db_session, Products, name="Test Product", code="TP-001")


@pytest.fixture
def warehouse(db_session):
    return create_test_record(db_session, Warehouses, name="Main Warehouse")


def assign_roles(db_session, email: str, role_names: list[str]) -> None:
    employee = db_session.exec(select(Employees).where(Employees.email == email)).first()
    for role_name in role_names:
        role = db_session.exec(select(Roles).where(Roles.role_name == role_name)).first()
        if not role:
            role = create_test_record(db_session, Roles, role_name=role_name)
        db_session.add(EmployeeRoles(employee_id=employee.employee_id, role_id=role.role_id))
    db_session.commit()


def seed_stock(client, auth_headers, product, warehouse, quantity=10):
    response = client.post(
        "/inventory/entries",
        headers=auth_headers,
        json={
            "product_id": product.id,
            "warehouse_id": warehouse.warehouse_id,
            "movement_type": "IN",
            "quantity": quantity,
        },
    )
    assert response.status_code == 200, response.text


def request_output(client, auth_headers, product, warehouse, quantity=4):
    return client.post(
        "/inventory/outputs",
        headers=auth_headers,
        json={
            "product_id": product.id,
            "warehouse_id": warehouse.warehouse_id,
            "movement_type": "OUT",
            "quantity": quantity,
        },
    )


def test_output_without_approver_roles_creates_pending_request(
    client, auth_headers, db_session, product, warehouse
):
    seed_stock(client, auth_headers, product, warehouse)

    response = request_output(client, auth_headers, product, warehouse)

    assert response.status_code == 200, response.text
    result = response.json()
    assert result["requires_approval"] is True
    assert result["movement"] is None
    assert result["approval"]["status"] == "PENDING"
    assert result["approval"]["movement_type"] == "OUT"

    movements = client.get("/inventory/movements", headers=auth_headers).json()
    assert all(m["movement_type"] != "OUT" for m in movements)


def test_adjustment_without_approver_roles_creates_pending_request(
    client, auth_headers, db_session, product, warehouse
):
    response = client.post(
        "/inventory/adjustments",
        headers=auth_headers,
        json={
            "product_id": product.id,
            "warehouse_id": warehouse.warehouse_id,
            "movement_type": "ADJUSTMENT",
            "quantity": -2,
        },
    )

    assert response.status_code == 200, response.text
    result = response.json()
    assert result["requires_approval"] is True
    assert result["approval"]["status"] == "PENDING"


def test_output_requires_approval_even_for_approvers(client, auth_headers, db_session, product, warehouse):
    """Approver roles grant review rights, not a bypass: their own outputs still go through approval."""
    seed_stock(client, auth_headers, product, warehouse)
    assign_roles(db_session, "test@example.com", ["Admin", "Project Manager", "Business Proposals"])

    response = request_output(client, auth_headers, product, warehouse)

    assert response.status_code == 200, response.text
    result = response.json()
    assert result["requires_approval"] is True
    assert result["movement"] is None
    assert result["approval"]["status"] == "PENDING"

    movements = client.get("/inventory/movements", headers=auth_headers).json()
    assert all(m["movement_type"] != "OUT" for m in movements)


def test_approve_executes_movement(client, auth_headers, db_session, product, warehouse):
    seed_stock(client, auth_headers, product, warehouse)
    approval = request_output(client, auth_headers, product, warehouse).json()["approval"]

    assign_roles(db_session, "test@example.com", ["Project Manager", "Business Proposals"])

    response = client.post(
        f"/inventory/movement-approvals/{approval['approval_id']}/approve",
        headers=auth_headers,
        json={"note": "Looks good"},
    )

    assert response.status_code == 200, response.text
    reviewed = response.json()
    assert reviewed["status"] == "APPROVED"
    assert reviewed["review_note"] == "Looks good"
    assert reviewed["movement_id"] is not None

    movements = client.get("/inventory/movements", headers=auth_headers).json()
    assert any(m["movement_id"] == reviewed["movement_id"] and m["movement_type"] == "OUT" for m in movements)

    # A reviewed request cannot be reviewed again
    again = client.post(
        f"/inventory/movement-approvals/{approval['approval_id']}/approve",
        headers=auth_headers,
        json={"note": None},
    )
    assert again.status_code == 400, again.text


def test_reject_does_not_execute_movement(client, auth_headers, db_session, product, warehouse):
    seed_stock(client, auth_headers, product, warehouse)
    approval = request_output(client, auth_headers, product, warehouse).json()["approval"]

    assign_roles(db_session, "test@example.com", ["Project Manager", "Business Proposals"])

    response = client.post(
        f"/inventory/movement-approvals/{approval['approval_id']}/reject",
        headers=auth_headers,
        json={"note": "Not justified"},
    )

    assert response.status_code == 200, response.text
    reviewed = response.json()
    assert reviewed["status"] == "REJECTED"
    assert reviewed["review_note"] == "Not justified"
    assert reviewed["movement_id"] is None

    movements = client.get("/inventory/movements", headers=auth_headers).json()
    assert all(m["movement_type"] != "OUT" for m in movements)


def test_review_requires_approver_roles(client, auth_headers, db_session, product, warehouse):
    seed_stock(client, auth_headers, product, warehouse)
    approval = request_output(client, auth_headers, product, warehouse).json()["approval"]

    response = client.post(
        f"/inventory/movement-approvals/{approval['approval_id']}/approve",
        headers=auth_headers,
        json={"note": None},
    )

    assert response.status_code == 403, response.text


def test_approve_revalidates_stock(client, auth_headers, db_session, product, warehouse):
    seed_stock(client, auth_headers, product, warehouse, quantity=10)
    big_request = request_output(client, auth_headers, product, warehouse, quantity=8).json()["approval"]
    small_request = request_output(client, auth_headers, product, warehouse, quantity=5).json()["approval"]

    assign_roles(db_session, "test@example.com", ["Project Manager", "Business Proposals"])

    # Approving the small request consumes stock so the big one no longer fits
    small_approve = client.post(
        f"/inventory/movement-approvals/{small_request['approval_id']}/approve",
        headers=auth_headers,
        json={"note": None},
    )
    assert small_approve.status_code == 200, small_approve.text

    response = client.post(
        f"/inventory/movement-approvals/{big_request['approval_id']}/approve",
        headers=auth_headers,
        json={"note": None},
    )

    assert response.status_code == 400, response.text

    listing = client.get("/inventory/movement-approvals?status=PENDING", headers=auth_headers).json()
    assert any(item["approval_id"] == big_request["approval_id"] for item in listing)


def test_list_movement_approvals_filters_by_status(client, auth_headers, db_session, product, warehouse):
    seed_stock(client, auth_headers, product, warehouse)
    request_output(client, auth_headers, product, warehouse)

    pending = client.get("/inventory/movement-approvals?status=PENDING", headers=auth_headers)
    assert pending.status_code == 200, pending.text
    assert len(pending.json()) == 1

    approved = client.get("/inventory/movement-approvals?status=APPROVED", headers=auth_headers)
    assert approved.status_code == 200, approved.text
    assert approved.json() == []
