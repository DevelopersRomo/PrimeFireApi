from decimal import Decimal

import pytest
from sqlmodel import select

from models.countries import Countries
from models.employees import EmployeeRoles, Employees, Roles
from models.inventory import InventoryMovementApprovals, InventoryMovements, Warehouses
from models.products import Products
from tests.conftest import create_test_record


@pytest.fixture(autouse=True)
def inventory_permissions(permission_override):
    permission_override("inventory", {"can_view", "can_create"})


@pytest.fixture
def scoped_inventory_data(db_session):
    country = create_test_record(db_session, Countries, name="United States")
    employee = db_session.exec(select(Employees).where(Employees.email == "test@example.com")).first()
    employee.city = " CityA "
    employee.country_id = country.country_id
    db_session.add(employee)
    db_session.flush()
    role_names = db_session.exec(select(Roles)).all()
    scoped_role = next((role for role in role_names if role.role_name == "Scoped Inventory User"), None)
    if not scoped_role:
        scoped_role = create_test_record(db_session, Roles, role_name="Scoped Inventory User")
    db_session.add(EmployeeRoles(employee_id=employee.employee_id, role_id=scoped_role.role_id))

    warehouse_a = create_test_record(db_session, Warehouses, name="cityA", location="us")
    warehouse_b = create_test_record(db_session, Warehouses, name="CityB", location="United States")
    product = create_test_record(db_session, Products, name="Scoped Product", code="SCOPE-1", type="Product")
    for warehouse in (warehouse_a, warehouse_b):
        db_session.add(
            InventoryMovements(
                product_id=product.id,
                warehouse_id=warehouse.warehouse_id,
                movement_type="IN",
                quantity=Decimal(10),
            )
        )
        db_session.add(
            InventoryMovementApprovals(
                product_id=product.id,
                warehouse_id=warehouse.warehouse_id,
                movement_type="OUT",
                quantity=Decimal(1),
                requested_by_email="requester@example.com",
            )
        )
    db_session.commit()
    return employee, warehouse_a, warehouse_b, product


def assign_roles(db_session, employee, role_names):
    for role_name in role_names:
        role = db_session.exec(select(Roles).where(Roles.role_name == role_name)).first()
        if not role:
            role = create_test_record(db_session, Roles, role_name=role_name)
        db_session.add(EmployeeRoles(employee_id=employee.employee_id, role_id=role.role_id))
    db_session.commit()


def test_scoped_reads_are_forced_to_matching_warehouse(client, auth_headers, scoped_inventory_data):
    _, warehouse_a, warehouse_b, product = scoped_inventory_data
    for path in ("/inventory/movements", "/inventory/movement-approvals"):
        response = client.get(path, headers=auth_headers)
        assert response.status_code == 200, response.text
        assert {row["warehouse_id"] for row in response.json()} == {warehouse_a.warehouse_id}
        mismatch = client.get(path, params={"warehouse_id": warehouse_b.warehouse_id}, headers=auth_headers)
        assert mismatch.status_code == 403

    stock = client.get("/inventory/stock", headers=auth_headers)
    assert stock.status_code == 200, stock.text
    assert stock.json()[0]["stock_on_hand"] == "10.00"
    assert client.get("/inventory/stock/" + str(product.id), headers=auth_headers).json()["stock_on_hand"] == "10.00"
    metrics = client.get("/inventory/stock-metrics", headers=auth_headers)
    assert metrics.json()["total_on_hand"] == "10.00"
    assert client.get(
        "/inventory/stock", params={"warehouse_id": warehouse_b.warehouse_id}, headers=auth_headers
    ).status_code == 403


@pytest.mark.parametrize("warehouse_id", [None, "other"])
def test_scoped_writes_reject_null_or_other_warehouse(client, auth_headers, scoped_inventory_data, warehouse_id):
    _, _, warehouse_b, product = scoped_inventory_data
    requested_warehouse = None if warehouse_id is None else warehouse_b.warehouse_id
    response = client.post(
        "/inventory/entries",
        headers=auth_headers,
        json={"product_id": product.id, "warehouse_id": requested_warehouse, "movement_type": "IN", "quantity": 1},
    )
    assert response.status_code == 403


@pytest.mark.parametrize("roles", [["Admin"], ["Project Manager", "Business Proposals"]])
def test_approvers_keep_unrestricted_reads_and_writes(client, auth_headers, scoped_inventory_data, db_session, roles):
    employee, warehouse_a, warehouse_b, product = scoped_inventory_data
    assign_roles(db_session, employee, roles)

    for warehouse in (warehouse_a, warehouse_b):
        movements = client.get("/inventory/movements", params={"warehouse_id": warehouse.warehouse_id}, headers=auth_headers)
        assert movements.status_code == 200, movements.text
        assert {row["warehouse_id"] for row in movements.json()} == {warehouse.warehouse_id}
        write = client.post(
            "/inventory/entries",
            headers=auth_headers,
            json={"product_id": product.id, "warehouse_id": warehouse.warehouse_id, "movement_type": "IN", "quantity": 1},
        )
        assert write.status_code == 200, write.text


def test_scoped_user_without_matching_warehouse_sees_empty_and_cannot_write(
    client, auth_headers, scoped_inventory_data, db_session
):
    employee, _, _, product = scoped_inventory_data
    employee.city = "Nowhere"
    db_session.add(employee)
    db_session.commit()
    for path in ("/inventory/movements", "/inventory/movement-approvals", "/inventory/stock"):
        response = client.get(path, headers=auth_headers)
        assert response.status_code == 200, response.text
        assert response.json() == []
    assert client.get("/inventory/stock-metrics", headers=auth_headers).json() == {
        "total_on_hand": "0",
        "low_stock_count": 0,
    }
    assert client.get(f"/inventory/stock/{product.id}", headers=auth_headers).status_code == 404
    response = client.post(
        "/inventory/entries",
        headers=auth_headers,
        json={"product_id": product.id, "warehouse_id": 1, "movement_type": "IN", "quantity": 1},
    )
    assert response.status_code == 403
