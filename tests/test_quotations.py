from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from sqlmodel import Session

from models.customers import CustomerTypeEnum, Customers
from models.quotations import Quotations


@pytest.fixture
def test_customer_for_quotation(db_session: Session) -> Customers:
    """Create a test customer for quotation tests."""
    customer = Customers(
        company_name="Test Company",
        first_name="John",
        last_name="Doe",
        customer_type=CustomerTypeEnum.COMMERCIAL,
        created_by=1,
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return customer


def test_create_quotation(client, auth_headers, db_session: Session, test_customer_for_quotation):
    """Test creating a new quotation."""
    payload = {
        "customer_id": test_customer_for_quotation.customer_id,
        "quote_date": datetime.now(UTC).isoformat(),
        "expiration_date": (datetime.now(UTC) + timedelta(days=30)).isoformat(),
        "subtotal": 100.00,
        "tax": 10.00,
        "discount": 5.00,
        "total": 105.00,
        "status": "pending",
        "notes": "Test quotation",
    }

    response = client.post("/quotations/", json=payload, headers=auth_headers)
    assert response.status_code in {200, 201}

    data = response.json()
    assert data["customer_id"] == test_customer_for_quotation.customer_id
    assert float(data["subtotal"]) == 100.00
    assert float(data["total"]) == 105.00
    assert data["status"] == "pending"


def test_list_quotations(client, auth_headers, db_session: Session, test_customer_for_quotation):
    """Test listing all quotations."""
    # Create a quotation first
    quotation = Quotations(
        customer_id=test_customer_for_quotation.customer_id,
        quote_date=datetime.now(UTC),
        subtotal=Decimal("200.00"),
        tax=Decimal("20.00"),
        total=Decimal("220.00"),
        status="pending",
    )
    db_session.add(quotation)
    db_session.commit()

    response = client.get("/quotations/", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_quotation_by_id(client, auth_headers, db_session: Session, test_customer_for_quotation):
    """Test getting a specific quotation by ID."""
    # Create a quotation first
    quotation = Quotations(
        customer_id=test_customer_for_quotation.customer_id,
        quote_date=datetime.now(UTC),
        subtotal=Decimal("150.00"),
        tax=Decimal("15.00"),
        total=Decimal("165.00"),
        status="approved",
    )
    db_session.add(quotation)
    db_session.commit()
    db_session.refresh(quotation)

    response = client.get(f"/quotations/{quotation.id}", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == quotation.id
    assert data["status"] == "approved"


def test_update_quotation(client, auth_headers, db_session: Session, test_customer_for_quotation):
    """Test updating a quotation."""
    # Create a quotation first
    quotation = Quotations(
        customer_id=test_customer_for_quotation.customer_id,
        quote_date=datetime.now(UTC),
        subtotal=Decimal("100.00"),
        tax=Decimal("10.00"),
        total=Decimal("110.00"),
        status="pending",
    )
    db_session.add(quotation)
    db_session.commit()
    db_session.refresh(quotation)

    # Update the quotation
    payload = {
        "status": "approved",
        "notes": "Updated notes",
    }

    response = client.patch(f"/quotations/{quotation.id}", json=payload, headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "approved"
    assert data["notes"] == "Updated notes"


def test_delete_quotation(client, auth_headers, db_session: Session, test_customer_for_quotation):
    """Test deleting a quotation."""
    # Create a quotation first
    quotation = Quotations(
        customer_id=test_customer_for_quotation.customer_id,
        quote_date=datetime.now(UTC),
        subtotal=Decimal("50.00"),
        tax=Decimal("5.00"),
        total=Decimal("55.00"),
        status="pending",
    )
    db_session.add(quotation)
    db_session.commit()
    db_session.refresh(quotation)
    quotation_id = quotation.id

    response = client.delete(f"/quotations/{quotation_id}", headers=auth_headers)
    assert response.status_code == 200

    # Verify it's deleted
    response = client.get(f"/quotations/{quotation_id}", headers=auth_headers)
    assert response.status_code == 404