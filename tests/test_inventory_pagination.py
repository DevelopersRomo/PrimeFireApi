from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from models.inventory import InventoryMovementApprovals, InventoryMovements, Warehouses
from models.products import ProductCategories, ProductFamilies, Products
from tests.conftest import create_test_record


@pytest.fixture
def inventory_catalog(db_session):
    family = create_test_record(db_session, ProductFamilies, name="Safety")
    category = create_test_record(
        db_session,
        ProductCategories,
        family_id=family.id,
        name="Gloves",
    )
    warehouse = create_test_record(db_session, Warehouses, name="Main Warehouse", location="Mexico")
    other_warehouse = create_test_record(
        db_session,
        Warehouses,
        name="Inactive Warehouse",
        location="Canada",
        is_active=False,
    )
    first = create_test_record(
        db_session,
        Products,
        name="Alpha Glove",
        type="Product",
        code="SAFE-1",
        family_id=family.id,
        category_id=category.id,
        min_stock=Decimal(5),
    )
    second = create_test_record(
        db_session,
        Products,
        name="Beta Glove",
        type="Product",
        code="SAFE-2",
        family_id=family.id,
        category_id=category.id,
        min_stock=Decimal(1),
    )
    return family, category, warehouse, other_warehouse, first, second


def add_movement(db_session, product, warehouse, movement_type, quantity, movement_id=None):
    movement = InventoryMovements(
        movement_id=movement_id,
        product_id=product.id,
        warehouse_id=warehouse.warehouse_id,
        movement_type=movement_type,
        quantity=Decimal(str(quantity)),
        movement_date=date(2026, 7, 15),
        project="Server Filter Project",
        po_number="PO-42",
        notes="inventory predicate",
        created_by="Tester",
        created_at=datetime(2026, 7, 15, 12, tzinfo=UTC),
    )
    db_session.add(movement)
    db_session.commit()
    db_session.refresh(movement)
    return movement


def test_movement_metadata_filters_count_order_and_array_compatibility(
    client, auth_headers, db_session, inventory_catalog
):
    _, _, warehouse, other_warehouse, product, other_product = inventory_catalog
    first = add_movement(db_session, product, warehouse, "IN", 10)
    second = add_movement(db_session, product, warehouse, "IN", 5)
    add_movement(db_session, other_product, other_warehouse, "OUT", 1)
    params = {
        "with_meta": "true",
        "search": "predicate",
        "movement_type": "IN",
        "warehouse_id": warehouse.warehouse_id,
        "product_id": product.id,
        "start_date": "2026-07-15",
        "end_date": "2026-07-15",
        "limit": 1,
    }

    first_page = client.get("/inventory/movements", params=params, headers=auth_headers)
    second_page = client.get("/inventory/movements", params={**params, "skip": 1}, headers=auth_headers)
    compatible = client.get("/inventory/movements", params={"movement_type": "IN"}, headers=auth_headers)

    assert first_page.status_code == 200
    assert first_page.json()["total"] == 2
    assert first_page.json()["has_more"] is True
    assert second_page.json()["has_more"] is False
    assert first_page.json()["items"][0]["movement_id"] == max(first.movement_id, second.movement_id)
    assert second_page.json()["items"][0]["movement_id"] == min(first.movement_id, second.movement_id)
    assert isinstance(compatible.json(), list)
    assert len(compatible.json()) == 2


def test_stock_metadata_filters_metrics_order_and_array_compatibility(
    client, auth_headers, db_session, inventory_catalog
):
    family, category, warehouse, _, first, second = inventory_catalog
    add_movement(db_session, first, warehouse, "IN", 2)
    add_movement(db_session, second, warehouse, "IN", 3)
    params = {
        "with_meta": "true",
        "warehouse_id": warehouse.warehouse_id,
        "search": "glove",
        "family": family.name,
        "category": category.name,
        "status": "Low Stock",
        "sort_field": "name",
        "sort_direction": "asc",
        "limit": 1,
    }

    response = client.get("/inventory/stock", params=params, headers=auth_headers)
    compatible = client.get("/inventory/stock", params={"warehouse_id": warehouse.warehouse_id}, headers=auth_headers)
    metrics = client.get(
        "/inventory/stock-metrics", params={"warehouse_id": warehouse.warehouse_id}, headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["product_id"] == first.id
    assert isinstance(compatible.json(), list)
    assert metrics.json()["total_on_hand"] == "5.00"
    assert metrics.json()["low_stock_count"] == 1


def test_stock_product_filter_is_exact_and_preserves_pagination_metadata(
    client, auth_headers, db_session, inventory_catalog
):
    _, _, warehouse, _, product, other_product = inventory_catalog
    add_movement(db_session, product, warehouse, "IN", 2)
    add_movement(db_session, other_product, warehouse, "IN", 3)
    params = {
        "with_meta": "true",
        "warehouse_id": warehouse.warehouse_id,
        "product_id": product.id,
        "limit": 1,
    }

    first_page = client.get("/inventory/stock", params=params, headers=auth_headers)
    empty_page = client.get("/inventory/stock", params={**params, "skip": 1}, headers=auth_headers)

    assert first_page.status_code == 200
    assert first_page.json() == {
        "items": [first_page.json()["items"][0]],
        "total": 1,
        "skip": 0,
        "limit": 1,
        "has_more": False,
    }
    assert first_page.json()["items"][0]["product_id"] == product.id
    assert empty_page.json() == {
        "items": [],
        "total": 1,
        "skip": 1,
        "limit": 1,
        "has_more": False,
    }


def test_warehouse_metadata_filters_count_order_and_array_compatibility(client, auth_headers, inventory_catalog):
    _, _, warehouse, _, _, _ = inventory_catalog

    response = client.get(
        "/inventory/warehouses",
        params={"with_meta": "true", "search": "main", "active_only": "true", "limit": 1},
        headers=auth_headers,
    )
    compatible = client.get("/inventory/warehouses", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["warehouse_id"] == warehouse.warehouse_id
    assert isinstance(compatible.json(), list)
    assert len(compatible.json()) == 2


def test_approval_metadata_filters_count_order_and_array_compatibility(
    client, auth_headers, db_session, inventory_catalog
):
    _, _, warehouse, _, product, _ = inventory_catalog
    approvals = []
    for _ in range(2):
        approval = InventoryMovementApprovals(
            product_id=product.id,
            warehouse_id=warehouse.warehouse_id,
            movement_type="OUT",
            quantity=Decimal(1),
            status="PENDING",
            project="Approval Search",
            requested_by="Requester",
            created_at=datetime(2026, 7, 15, 12, tzinfo=UTC),
        )
        db_session.add(approval)
        db_session.commit()
        db_session.refresh(approval)
        approvals.append(approval)
    other_approval = InventoryMovementApprovals(
        product_id=inventory_catalog[5].id,
        warehouse_id=warehouse.warehouse_id,
        movement_type="OUT",
        quantity=Decimal(1),
        status="PENDING",
        project="Approval Search",
        requested_by="Requester",
        created_at=datetime(2026, 7, 15, 12, tzinfo=UTC),
    )
    db_session.add(other_approval)
    db_session.commit()

    response = client.get(
        "/inventory/movement-approvals",
        params={
            "with_meta": "true",
            "search": "approval",
            "status": "PENDING",
            "movement_type": "OUT",
            "warehouse_id": warehouse.warehouse_id,
            "product_id": product.id,
            "limit": 1,
        },
        headers=auth_headers,
    )
    second_page = client.get(
        "/inventory/movement-approvals",
        params={
            "with_meta": "true",
            "status": "PENDING",
            "product_id": product.id,
            "skip": 1,
            "limit": 1,
        },
        headers=auth_headers,
    )
    compatible = client.get("/inventory/movement-approvals", params={"status": "PENDING"}, headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["total"] == 2
    assert response.json()["skip"] == 0
    assert response.json()["limit"] == 1
    assert response.json()["has_more"] is True
    assert second_page.json()["total"] == 2
    assert second_page.json()["skip"] == 1
    assert second_page.json()["has_more"] is False
    assert {response.json()["items"][0]["product_id"], second_page.json()["items"][0]["product_id"]} == {
        product.id
    }
    assert response.json()["items"][0]["approval_id"] == max(item.approval_id for item in approvals)
    assert isinstance(compatible.json(), list)
    assert len(compatible.json()) == 3
