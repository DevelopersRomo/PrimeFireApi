from sqlmodel import Session

from models.products import Products


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
    assert data["unit_price"] == 150.00


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