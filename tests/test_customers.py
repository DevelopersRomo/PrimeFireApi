from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlmodel import Session

from models.customers import (
    CustomerAlternateContacts,
    CustomerNotes,
    CustomerTypeEnum,
    Customers,
)
from tests.conftest import create_test_record


def test_customers_crud(client: TestClient, auth_headers: dict, permission_override):
    permission_override("customers", {"can_view"})
    response = client.get("/customers/")
    assert response.status_code in {401, 200}

    response = client.get("/customers/", headers=auth_headers)
    assert response.status_code == 200


def test_customer_routes_require_module_permissions(
    client: TestClient, auth_headers: dict, db_session: Session, other_employee
) -> None:
    customer = create_test_record(
        db_session,
        Customers,
        CustomerType="commercial",
        CompanyName="Permission test customer",
        CreatedBy=other_employee.employee_id,
    )
    note = create_test_record(
        db_session,
        CustomerNotes,
        customer_id=customer.customer_id,
        note_text="Original note",
        created_by=other_employee.employee_id,
    )
    contact = create_test_record(
        db_session,
        CustomerAlternateContacts,
        customer_id=customer.customer_id,
        name="Other employee",
        email="other@example.test",
    )
    db_session.commit()

    responses = [
        client.get("/customers", headers=auth_headers),
        client.patch(f"/customers/{customer.customer_id}", json={"company_name": "Changed"}, headers=auth_headers),
        client.patch(
            f"/customers/{customer.customer_id}/notes/{note.customer_note_id}",
            json={"note_text": "Changed"},
            headers=auth_headers,
        ),
        client.patch(
            f"/customers/{customer.customer_id}/contacts/{contact.customer_alternate_contact_id}",
            json={"email": "changed@example.test"},
            headers=auth_headers,
        ),
        client.delete(f"/customers/{customer.customer_id}", headers=auth_headers),
    ]

    assert [response.status_code for response in responses] == [403] * len(responses)


def test_quotation_permission_can_read_customers_without_write_access(
    client: TestClient, auth_headers: dict, db_session: Session, permission_override
) -> None:
    permission_override("quotations", {"can_view"})
    customer = create_test_record(
        db_session,
        Customers,
        CustomerType="commercial",
        CompanyName="Quotation customer",
        CreatedBy=1,
    )
    db_session.commit()

    listed = client.get("/customers", headers=auth_headers)
    updated = client.patch(f"/customers/{customer.customer_id}", json={"company_name": "Changed"}, headers=auth_headers)

    assert listed.status_code == 200
    assert updated.status_code == 403


def test_customer_pagination_uses_customer_id_tiebreaker(
    client: TestClient, auth_headers: dict, db_session: Session, permission_override
) -> None:
    permission_override("customers", {"can_view"})
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
