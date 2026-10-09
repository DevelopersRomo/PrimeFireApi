from datetime import UTC, datetime
from decimal import Decimal

from models.customers import CustomerTypeEnum, Customers
from models.products import Products
from models.quotation_items import QuotationItems
from models.quotations import Quotations


def test_quotation_item_update_requires_quotations_can_edit(client, auth_headers, db_session):
    customer = Customers(
        company_name="Item Permission Customer",
        first_name="Test",
        last_name="Customer",
        customer_type=CustomerTypeEnum.COMMERCIAL,
        created_by=1,
    )
    product = Products(name="Permission Product", type="Product")
    db_session.add_all([customer, product])
    db_session.commit()
    db_session.refresh(customer)
    db_session.refresh(product)
    quotation = Quotations(
        customer_id=customer.customer_id,
        quote_date=datetime.now(UTC),
        status="pending",
    )
    db_session.add(quotation)
    db_session.commit()
    db_session.refresh(quotation)
    item = QuotationItems(
        quotation_id=quotation.id,
        product_id=product.id,
        quantity=Decimal("1.00"),
        unit_price=Decimal("100.00"),
        discount=Decimal("0.00"),
        tax=Decimal("0.00"),
        total=Decimal("100.00"),
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)

    response = client.put(
        f"/quotations/{quotation.id}/items/{item.id}",
        json={"product_id": product.id, "quantity": "1", "unit_price": "0.01", "discount": "0", "tax": "0", "total": "0.01"},
        headers=auth_headers,
    )

    assert response.status_code == 403
