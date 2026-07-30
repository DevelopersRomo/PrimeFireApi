import pytest
from sqlmodel import Session, select

from api.products import product_to_read
from models.products import ProductCatalog, ProductCategories, ProductFamilies, ProductSpecifications, Products


@pytest.fixture(autouse=True)
def _grant_product_mutations(permission_override) -> None:
    permission_override("products", {"can_create", "can_edit", "can_delete"})


def test_create_product(client, auth_headers, db_session: Session):
    """Test creating a new product."""
    payload = {
        "name": "Test Product",
        "description": "Test product description",
        "type": "Product",
        "sku": "TEST-001",
        "unit_price": 100.00,
        "cost": 50.00,
        "tax_rate": 10.0,
        "unit": "pieza",
        "stock_quantity": 10,
        "is_active": True,
    }

    response = client.post("/products", json=payload, headers=auth_headers)
    assert response.status_code in {200, 201}

    data = response.json()
    assert data["name"] == "Test Product"
    assert data["type"] == "Product"
    assert data["sku"] == "TEST-001"


def test_product_search_metadata_uses_matching_predicates(client, auth_headers, db_session: Session):
    db_session.add(Products(name="Needle Product", type="Product", sku="NEEDLE"))
    db_session.add(Products(name="Other Product", type="Product", sku="OTHER"))
    db_session.commit()

    response = client.get("/products?with_meta=true&search=Needle", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["name"] == "Needle Product"


def test_product_filters_by_family_and_category(client, auth_headers, db_session: Session):
    family = ProductFamilies(name="Detection")
    other_family = ProductFamilies(name="Suppression")
    db_session.add(family)
    db_session.add(other_family)
    db_session.commit()

    category = ProductCategories(family_id=family.id, name="Smoke")
    other_category = ProductCategories(family_id=family.id, name="Heat")
    db_session.add(category)
    db_session.add(other_category)
    db_session.commit()

    db_session.add(Products(name="Smoke Detector", type="Product", family_id=family.id, category_id=category.id))
    db_session.add(Products(name="Heat Detector", type="Product", family_id=family.id, category_id=other_category.id))
    db_session.add(Products(name="Sprinkler", type="Product", family_id=other_family.id))
    db_session.commit()

    by_family = client.get(f"/products?family_id={family.id}", headers=auth_headers)
    assert by_family.status_code == 200
    assert {item["name"] for item in by_family.json()} == {"Smoke Detector", "Heat Detector"}

    by_category = client.get(f"/products?category_id={category.id}", headers=auth_headers)
    assert by_category.status_code == 200
    assert [item["name"] for item in by_category.json()] == ["Smoke Detector"]


def test_product_filters_by_type_and_status(client, auth_headers, db_session: Session):
    db_session.add(Products(name="Active Product", type="Product", is_active=True))
    db_session.add(Products(name="Inactive Product", type="Product", is_active=False))
    db_session.add(Products(name="Active Service", type="Service", is_active=True))
    db_session.commit()

    by_type = client.get("/products?type=Service", headers=auth_headers)
    assert by_type.status_code == 200
    assert [item["name"] for item in by_type.json()] == ["Active Service"]

    inactive = client.get("/products?is_active=false", headers=auth_headers)
    assert inactive.status_code == 200
    assert [item["name"] for item in inactive.json()] == ["Inactive Product"]

    active_products = client.get("/products?type=Product&is_active=true", headers=auth_headers)
    assert active_products.status_code == 200
    assert [item["name"] for item in active_products.json()] == ["Active Product"]


def test_product_filter_metadata_total_respects_filters(client, auth_headers, db_session: Session):
    db_session.add(Products(name="Kept Service", type="Service", is_active=True))
    db_session.add(Products(name="Dropped Product", type="Product", is_active=True))
    db_session.commit()

    response = client.get("/products?with_meta=true&type=Service", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["has_more"] is False
    assert [item["name"] for item in body["items"]] == ["Kept Service"]


def test_product_catalog_dynamic_selects_and_create(client, auth_headers, db_session: Session):
    family = ProductFamilies(name="Fire Alarm")
    db_session.add(family)
    db_session.commit()
    db_session.refresh(family)

    category = ProductCategories(family_id=family.id, name="Device")
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    families_response = client.get("/products/families", headers=auth_headers)
    assert families_response.status_code == 200, families_response.text
    assert any(item["name"] == "Fire Alarm" for item in families_response.json())

    categories_response = client.get(f"/products/categories?family_id={family.id}", headers=auth_headers)
    assert categories_response.status_code == 200, categories_response.text
    assert categories_response.json()[0]["name"] == "Device"

    payload = {
        "name": "Pull Station",
        "description": "Fire alarm pull station",
        "type": "Product",
        "sku": "NBG-12LX",
        "code": "NBG-12LX",
        "family_id": family.id,
        "category_id": category.id,
        "size": "EA",
        "material_type": "Electronic",
        "specification": "Addressable",
        "manufacturer": "Notifier",
        "model": "NBG-12LX",
        "unit_price": 100.00,
        "cost": 50.00,
        "tax_rate": 10.0,
        "unit": "pieza",
        "min_stock": 2,
        "needed_quantity": 5,
        "stock_quantity": 10,
        "is_active": True,
    }

    response = client.post("/products", json=payload, headers=auth_headers)
    assert response.status_code in {200, 201}, response.text

    data = response.json()
    assert data["code"] == "NBG-12LX"
    assert data["family_name"] == "Fire Alarm"
    assert data["category_name"] == "Device"
    assert data["size"] == "EA"
    assert data["material_type"] == "Electronic"

    catalog_item = db_session.exec(select(ProductCatalog).where(ProductCatalog.code == "NBG-12LX")).first()
    assert catalog_item is not None
    assert catalog_item.family_id == family.id

    catalog_spec = db_session.exec(
        select(ProductSpecifications).where(ProductSpecifications.product_id == catalog_item.id)
    ).first()
    assert catalog_spec is not None
    assert catalog_spec.material == "Electronic"


def test_product_category_must_belong_to_family(client, auth_headers, db_session: Session):
    fire_alarm = ProductFamilies(name="Fire Alarm")
    plumbing = ProductFamilies(name="Plumbing")
    db_session.add(fire_alarm)
    db_session.add(plumbing)
    db_session.commit()
    db_session.refresh(fire_alarm)
    db_session.refresh(plumbing)

    category = ProductCategories(family_id=plumbing.id, name="Valve")
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    response = client.post(
        "/products",
        headers=auth_headers,
        json={
            "name": "Invalid Product",
            "type": "Product",
            "family_id": fire_alarm.id,
            "category_id": category.id,
        },
    )

    assert response.status_code == 400, response.text
    assert response.json()["detail"] == "Product category does not belong to selected family"


def test_duplicate_product_category_returns_conflict(client, auth_headers, db_session: Session):
    family = ProductFamilies(name="Duplicate Category Family")
    db_session.add(family)
    db_session.commit()
    db_session.refresh(family)

    category = ProductCategories(family_id=family.id, name="Device")
    db_session.add(category)
    db_session.commit()

    response = client.post(
        "/products/categories",
        headers=auth_headers,
        json={
            "family_id": family.id,
            "name": "Device",
            "description": "Duplicate name in the same family",
        },
    )

    assert response.status_code == 409, response.text
    assert response.json()["detail"] == "Product category already exists for this family"


def test_delete_family_without_products_deletes_its_categories(client, auth_headers, db_session: Session):
    family = ProductFamilies(name="Unused Family")
    db_session.add(family)
    db_session.commit()
    db_session.refresh(family)

    category = ProductCategories(family_id=family.id, name="Unused Category")
    db_session.add(category)
    db_session.commit()
    category_id = category.id
    family_id = family.id

    response = client.delete(f"/products/families/{family_id}", headers=auth_headers)

    assert response.status_code == 200, response.text
    db_session.expire_all()
    assert db_session.get(ProductCategories, category_id) is None
    assert db_session.get(ProductFamilies, family_id) is None


def test_delete_product_removes_synced_catalog_item(client, auth_headers, db_session: Session):
    family = ProductFamilies(name="Delete Sync Family")
    db_session.add(family)
    db_session.commit()
    db_session.refresh(family)

    category = ProductCategories(family_id=family.id, name="Delete Sync Category")
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    create_response = client.post(
        "/products",
        headers=auth_headers,
        json={
            "name": "Synced Delete Product",
            "type": "Product",
            "sku": "SYNC-DELETE-001",
            "code": "SYNC-DELETE-001",
            "family_id": family.id,
            "category_id": category.id,
            "unit_price": 10,
            "unit": "pieza",
            "stock_quantity": 0,
            "is_active": True,
        },
    )
    assert create_response.status_code == 200, create_response.text
    product_id = create_response.json()["id"]

    assert db_session.exec(select(ProductCatalog).where(ProductCatalog.code == "SYNC-DELETE-001")).first() is not None

    delete_response = client.delete(f"/products/{product_id}", headers=auth_headers)

    assert delete_response.status_code == 200, delete_response.text
    db_session.expire_all()
    assert db_session.exec(select(ProductCatalog).where(ProductCatalog.code == "SYNC-DELETE-001")).first() is None

    category_delete_response = client.delete(f"/products/categories/{category.id}", headers=auth_headers)
    assert category_delete_response.status_code == 200, category_delete_response.text


def test_list_product_specification_options(client, auth_headers, db_session: Session):
    catalog_item = ProductCatalog(code="SPEC-001", name="Spec Product")
    db_session.add(catalog_item)
    db_session.commit()
    db_session.refresh(catalog_item)

    db_session.add(
        ProductSpecifications(
            product_id=catalog_item.id,
            specification="Addressable",
            size="EA",
            material="Electronic",
            manufacturer="Notifier",
            model="NBG-12LX",
        )
    )
    db_session.add(ProductSpecifications(product_id=catalog_item.id, specification="Conventional"))
    db_session.commit()

    response = client.get("/products/specifications?search=address", headers=auth_headers)

    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 1
    assert isinstance(data[0]["id"], int)
    assert data[0] == {
        "id": data[0]["id"],
        "product_id": catalog_item.id,
        "specification": "Addressable",
        "size": "EA",
        "material": "Electronic",
        "manufacturer": "Notifier",
        "model": "NBG-12LX",
        "notes": None,
    }


def test_create_update_delete_global_product_specification(client, auth_headers):
    create_response = client.post(
        "/products/specifications",
        headers=auth_headers,
        json={
            "specification": "Global Preset",
            "size": "EA",
            "material": "Electronic",
            "manufacturer": "Notifier",
            "model": "NBG-12LX",
            "notes": "Reusable setup value",
        },
    )

    assert create_response.status_code == 200, create_response.text
    created = create_response.json()
    assert created["product_id"] is None
    assert created["specification"] == "Global Preset"

    update_response = client.patch(
        f"/products/specifications/{created['id']}",
        headers=auth_headers,
        json={"model": "NBG-12LX-UPDATED"},
    )

    assert update_response.status_code == 200, update_response.text
    assert update_response.json()["model"] == "NBG-12LX-UPDATED"

    delete_response = client.delete(f"/products/specifications/{created['id']}", headers=auth_headers)

    assert delete_response.status_code == 200, delete_response.text
    assert delete_response.json()["message"] == "Product specification deleted successfully"


def test_list_products(client, auth_headers, db_session: Session):
    """Test listing all products."""
    # Create a product first
    product = Products(
        name="Test Product",
        description="Test description",
        type="Product",
        sku="LIST-001",
        unit_price=100.00,
        cost=50.00,
    )
    db_session.add(product)
    db_session.commit()

    response = client.get("/products", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_product_read_does_not_expose_inventory_min_stock(db_session: Session):
    product = Products(
        name="Legacy Product",
        description="Legacy product with null min stock",
        type="Product",
        sku="LEGACY-001",
        unit_price=100.00,
        cost=50.00,
    )
    product.min_stock = None

    data = product_to_read(db_session, product)

    assert "min_stock" not in data.model_dump()


def test_get_product_by_id(client, auth_headers, db_session: Session):
    """Test getting a specific product by ID."""
    # Create a product first
    product = Products(
        name="Get Test Product",
        description="Get test description",
        type="Product",
        sku="GET-001",
        unit_price=200.00,
        cost=100.00,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    response = client.get(f"/products/{product.id}", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == product.id
    assert data["name"] == "Get Test Product"


def test_update_product(client, auth_headers, db_session: Session):
    """Test updating a product."""
    # Create a product first
    product = Products(
        name="Update Test Product",
        description="Original description",
        type="Product",
        sku="UPDATE-001",
        unit_price=100.00,
        cost=50.00,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    # Update the product
    payload = {
        "name": "Updated Product Name",
        "unit_price": 150.00,
    }

    response = client.patch(f"/products/{product.id}", json=payload, headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Updated Product Name"
    assert data["unit_price"] == 150


def test_delete_product(client, auth_headers, db_session: Session):
    """Test deleting a product."""
    # Create a product first
    product = Products(
        name="Delete Test Product",
        description="To be deleted",
        type="Product",
        sku="DELETE-001",
        unit_price=50.00,
        cost=25.00,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    product_id = product.id

    response = client.delete(f"/products/{product_id}", headers=auth_headers)
    assert response.status_code in {200, 204}

    # Verify it's deleted
    response = client.get(f"/products/{product_id}", headers=auth_headers)
    assert response.status_code == 404


def test_product_not_found(client, auth_headers):
    """Test getting a non-existent product returns 404."""
    response = client.get("/products/99999", headers=auth_headers)
    assert response.status_code == 404
