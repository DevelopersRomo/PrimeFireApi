from sqlmodel import Session

from models.products import Products


def test_create_product(client, auth_headers, db_session: Session):
    """Test creating a new product."""
    payload = {
        "Name": "Test Product",
        "Description": "Test product description",
        "Type": "Product",
        "SKU": "TEST-001",
        "UnitPrice": 100.00,
        "Cost": 50.00,
        "TaxRate": 10.0,
        "Unit": "pieza",
        "StockQuantity": 10,
        "IsActive": True,
    }

    response = client.post("/products", json=payload, headers=auth_headers)
    assert response.status_code in (200, 201)

    data = response.json()
    assert data["Name"] == "Test Product"
    assert data["Type"] == "Product"
    assert data["SKU"] == "TEST-001"


def test_list_products(client, auth_headers, db_session: Session):
    """Test listing all products."""
    # Create a product first
    product = Products(
        Name="Test Product",
        Description="Test description",
        Type="Product",
        SKU="LIST-001",
        UnitPrice=100.00,
        Cost=50.00,
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
        Name="Get Test Product",
        Description="Get test description",
        Type="Product",
        SKU="GET-001",
        UnitPrice=200.00,
        Cost=100.00,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    response = client.get(f"/products/{product.Id}", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["Id"] == product.Id
    assert data["Name"] == "Get Test Product"


def test_update_product(client, auth_headers, db_session: Session):
    """Test updating a product."""
    # Create a product first
    product = Products(
        Name="Update Test Product",
        Description="Original description",
        Type="Product",
        SKU="UPDATE-001",
        UnitPrice=100.00,
        Cost=50.00,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    # Update the product
    payload = {
        "Name": "Updated Product Name",
        "UnitPrice": 150.00,
    }

    response = client.patch(f"/products/{product.Id}", json=payload, headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["Name"] == "Updated Product Name"
    assert data["UnitPrice"] == 150.00


def test_delete_product(client, auth_headers, db_session: Session):
    """Test deleting a product."""
    # Create a product first
    product = Products(
        Name="Delete Test Product",
        Description="To be deleted",
        Type="Product",
        SKU="DELETE-001",
        UnitPrice=50.00,
        Cost=25.00,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    product_id = product.Id

    response = client.delete(f"/products/{product_id}", headers=auth_headers)
    assert response.status_code in (200, 204)

    # Verify it's deleted
    response = client.get(f"/products/{product_id}", headers=auth_headers)
    assert response.status_code == 404


def test_product_not_found(client, auth_headers):
    """Test getting a non-existent product returns 404."""
    response = client.get("/products/99999", headers=auth_headers)
    assert response.status_code == 404