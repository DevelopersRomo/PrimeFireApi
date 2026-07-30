from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlmodel import Session

from models.customers import CustomerTypeEnum, Customers


def test_customers_crud(client: TestClient, auth_headers: dict):
    response = client.get("/customers/")
    assert response.status_code in {401, 200}

    response = client.get("/customers/", headers=auth_headers)
    assert response.status_code == 200


def test_customer_pagination_uses_customer_id_tiebreaker(
    client: TestClient, auth_headers: dict, db_session: Session
) -> None:
    created_at = datetime(2026, 7, 29, 12, tzinfo=UTC)
    customers = [
        Customers(
            customer_type=CustomerTypeEnum.COMMERCIAL,
            company_name=f"Stable customer {index}",
            created_at=created_at,
            created_by=1,
        )
        for index in range(2)
    ]
    db_session.add_all(customers)
    db_session.commit()
    for customer in customers:
        db_session.refresh(customer)

    first_id = customers[0].customer_id
    second_id = customers[1].customer_id
    assert first_id is not None
    assert second_id is not None

    params = {"with_meta": "true", "search": "Stable customer", "limit": 1}
    first_page = client.get("/customers", params=params, headers=auth_headers)
    second_page = client.get("/customers", params={**params, "skip": 1}, headers=auth_headers)

    assert first_page.status_code == 200
    assert second_page.status_code == 200
    assert first_page.json()["items"][0]["customer_id"] == max(first_id, second_id)
    assert second_page.json()["items"][0]["customer_id"] == min(first_id, second_id)
