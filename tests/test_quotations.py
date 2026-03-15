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
        CompanyName="Test Company",
        FirstName="John",
        LastName="Doe",
        CustomerType=CustomerTypeEnum.COMMERCIAL,
        CreatedBy=1,
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return customer


def test_create_quotation(client, auth_headers, db_session: Session, test_customer_for_quotation):
    """Test creating a new quotation."""
    payload = {
        "CustomerId": test_customer_for_quotation.CustomerId,
        "QuoteDate": datetime.now(UTC).isoformat(),
        "ExpirationDate": (datetime.now(UTC) + timedelta(days=30)).isoformat(),
        "Subtotal": 100.00,
        "Tax": 10.00,
        "Discount": 5.00,
        "Total": 105.00,
        "Status": "pending",
        "Notes": "Test quotation",
    }

    response = client.post("/quotations/", json=payload, headers=auth_headers)
    assert response.status_code in {200, 201}

    data = response.json()
    assert data["customerid"] == test_customer_for_quotation.CustomerId
    assert data["subtotal"] == "100.00"
    assert data["total"] == "105.00"
    assert data["status"] == "pending"


def test_list_quotations(client, auth_headers, db_session: Session, test_customer_for_quotation):
    """Test listing all quotations."""
    # Create a quotation first
    quotation = Quotations(
        CustomerId=test_customer_for_quotation.CustomerId,
        QuoteDate=datetime.now(UTC),
        Subtotal=Decimal("200.00"),
        Tax=Decimal("20.00"),
        Total=Decimal("220.00"),
        Status="pending",
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
        CustomerId=test_customer_for_quotation.CustomerId,
        QuoteDate=datetime.now(UTC),
        Subtotal=Decimal("150.00"),
        Tax=Decimal("15.00"),
        Total=Decimal("165.00"),
        Status="approved",
    )
    db_session.add(quotation)
    db_session.commit()
    db_session.refresh(quotation)

    response = client.get(f"/quotations/{quotation.Id}", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == quotation.Id
    assert data["status"] == "approved"


def test_update_quotation(client, auth_headers, db_session: Session, test_customer_for_quotation):
    """Test updating a quotation."""
    # Create a quotation first
    quotation = Quotations(
        CustomerId=test_customer_for_quotation.CustomerId,
        QuoteDate=datetime.now(UTC),
        Subtotal=Decimal("100.00"),
        Tax=Decimal("10.00"),
        Total=Decimal("110.00"),
        Status="pending",
    )
    db_session.add(quotation)
    db_session.commit()
    db_session.refresh(quotation)

    # Update the quotation
    payload = {
        "Status": "approved",
        "Notes": "Updated notes",
    }

    response = client.patch(f"/quotations/{quotation.Id}", json=payload, headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "approved"
    assert data["notes"] == "Updated notes"


def test_delete_quotation(client, auth_headers, db_session: Session, test_customer_for_quotation):
    """Test deleting a quotation."""
    # Create a quotation first
    quotation = Quotations(
        CustomerId=test_customer_for_quotation.CustomerId,
        QuoteDate=datetime.now(UTC),
        Subtotal=Decimal("50.00"),
        Tax=Decimal("5.00"),
        Total=Decimal("55.00"),
        Status="pending",
    )
    db_session.add(quotation)
    db_session.commit()
    db_session.refresh(quotation)
    quotation_id = quotation.Id

    response = client.delete(f"/quotations/{quotation_id}", headers=auth_headers)
    assert response.status_code == 200

    # Verify it's deleted
    response = client.get(f"/quotations/{quotation_id}", headers=auth_headers)
    assert response.status_code == 404
