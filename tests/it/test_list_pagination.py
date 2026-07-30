"""Pagination, reporting, compatibility, and permission tests for IT route lists."""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from models.it.catalog import ITCatalogItems
from models.it.email_templates import ITEmailCustomerTemplate, ITEmailDefault
from models.it.quotations import ITQuotations
from models.it.templates import ITPdfTemplates


def _catalog_item(tenant_id: int, name: str, item_type: str = "SERVICE") -> ITCatalogItems:
    return ITCatalogItems(
        tenant_id=tenant_id,
        name=name,
        item_type=item_type,
        billing_cycle="ONE_TIME",
        unit_price=Decimal(10),
    )


def _quotation(
    tenant_id: int,
    customer_id: int,
    number: str,
    status: str,
    quote_date: date,
    total: int,
) -> ITQuotations:
    return ITQuotations(
        tenant_id=tenant_id,
        customer_id=customer_id,
        quotation_number=number,
        status=status,
        quote_date=quote_date,
        expiration_date=quote_date + timedelta(days=30),
        customer_name_snapshot=f"Customer {number}",
        initial_total=Decimal(total),
        monthly_recurring_subtotal=Decimal(total / 10),
        annual_recurring_subtotal=Decimal(total / 5),
    )


def test_catalog_metadata_filters_count_order_tenant_and_legacy(client, auth_headers, db_session) -> None:
    db_session.add_all(
        [
            _catalog_item(1, "Zulu Service"),
            _catalog_item(1, "Alpha Service"),
            _catalog_item(1, "Hidden License", "LICENSE"),
            _catalog_item(2, "Other Tenant Service"),
        ]
    )
    db_session.commit()

    response = client.get(
        "/it/catalog/items/?with_meta=true&item_type=SERVICE&search=service&limit=1",
        headers=auth_headers,
    )
    assert response.status_code == 200, response.text
    page = response.json()
    assert page["total"] == 2
    assert page["has_more"] is True
    assert [item["name"] for item in page["items"]] == ["Alpha Service"]

    legacy = client.get("/it/catalog/items/?item_type=SERVICE", headers=auth_headers).json()
    assert isinstance(legacy, list)
    assert [item["name"] for item in legacy] == ["Alpha Service", "Zulu Service"]


def test_quotation_metadata_filters_count_order_tenant_and_legacy(
    client, auth_headers, db_session, customer
) -> None:
    customer_id = customer.customer_id
    rows = [
        _quotation(1, customer_id, "Q-IT-002", "DRAFT", date(2026, 7, 2), 200),
        _quotation(1, customer_id, "Q-IT-001", "DRAFT", date(2026, 7, 1), 100),
        _quotation(1, customer_id, "Q-IT-003", "SENT", date(2026, 7, 3), 300),
        _quotation(2, customer_id, "Q-IT-999", "DRAFT", date(2026, 7, 4), 999),
    ]
    for index, row in enumerate(rows):
        row.created_at = row.created_at.replace(microsecond=index)
        db_session.add(row)
    db_session.commit()

    response = client.get(
        "/it/quotations/?with_meta=true&status=DRAFT&date_from=2026-07-01&date_to=2026-07-02&limit=1",
        headers=auth_headers,
    )
    assert response.status_code == 200, response.text
    page = response.json()
    assert page["total"] == 2
    assert page["has_more"] is True
    assert page["items"][0]["quotation_number"] == "Q-IT-001"
    assert page["items"][0]["customer_name_snapshot"] == "Customer Q-IT-001"

    legacy = client.get("/it/quotations/?status=SENT", headers=auth_headers).json()
    assert isinstance(legacy, list)
    assert [row["quotation_number"] for row in legacy] == ["Q-IT-003"]


def test_sent_report_paginates_rows_and_calculates_full_filtered_metrics(
    client, auth_headers, db_session, customer
) -> None:
    customer_id = customer.customer_id
    db_session.add_all(
        [
            _quotation(1, customer_id, "Q-IT-S", "SENT", date(2026, 7, 1), 100),
            _quotation(1, customer_id, "Q-IT-V", "VIEWED", date(2026, 7, 2), 200),
            _quotation(1, customer_id, "Q-IT-A", "ACCEPTED", date(2026, 7, 3), 300),
            _quotation(1, customer_id, "Q-IT-X", "CANCELLED", date(2026, 7, 4), 400),
            _quotation(1, customer_id, "Q-IT-OLD", "SENT", date(2026, 6, 1), 500),
            _quotation(2, customer_id, "Q-IT-OTHER", "SENT", date(2026, 7, 5), 900),
        ]
    )
    db_session.commit()

    response = client.get(
        "/it/quotations/report?date_from=2026-07-01&date_to=2026-07-31&limit=2",
        headers=auth_headers,
    )
    assert response.status_code == 200, response.text
    report = response.json()
    assert report["total"] == 3
    assert report["has_more"] is True
    assert [row["quotation_number"] for row in report["items"]] == ["Q-IT-A", "Q-IT-V"]
    assert report["metrics"] == {
        "sent_count": 3,
        "total_amount": "600.00",
        "monthly_recurring": "60.00",
        "annual_recurring": "120.00",
        "conversion_rate": "33.33333333333333333333333333",
        "sent_status_count": 1,
        "viewed_status_count": 1,
        "accepted_status_count": 1,
        "rejected_status_count": 0,
    }


def test_template_metadata_order_tenant_and_legacy(client, auth_headers, db_session) -> None:
    db_session.add_all(
        [
            ITPdfTemplates(tenant_id=1, name="Zulu", template_key="z", company_name="PrimeFire"),
            ITPdfTemplates(tenant_id=1, name="Alpha", template_key="a", company_name="PrimeFire"),
            ITPdfTemplates(tenant_id=2, name="Other", template_key="o", company_name="Other"),
        ]
    )
    db_session.commit()

    page = client.get("/it/templates/?with_meta=true&limit=1", headers=auth_headers).json()
    assert page["total"] == 2
    assert page["has_more"] is True
    assert page["items"][0]["name"] == "Alpha"

    legacy = client.get("/it/templates/", headers=auth_headers).json()
    assert isinstance(legacy, list)
    assert [template["name"] for template in legacy] == ["Alpha", "Zulu"]


def test_email_template_rows_paginate_default_and_overrides_without_cross_tenant_data(
    client, auth_headers, db_session, customer
) -> None:
    default = ITEmailDefault(
        tenant_id=1,
        subject="Default",
        title="Default",
        message_body="Default body",
    )
    first = ITEmailCustomerTemplate(
        tenant_id=1,
        customer_id=customer.customer_id,
        subject="Customer",
        title="Customer",
        message_body="Customer body",
    )
    other = ITEmailCustomerTemplate(
        tenant_id=2,
        customer_id=999,
        subject="Other",
        title="Other",
        message_body="Other body",
    )
    db_session.add_all([default, first, other])
    db_session.commit()

    first_page = client.get("/it/email-templates/rows?limit=1", headers=auth_headers).json()
    assert first_page["total"] == 2
    assert first_page["items"][0]["kind"] == "default"
    assert first_page["items"][0]["configured"] is True
    assert first_page["has_more"] is True

    second_page = client.get("/it/email-templates/rows?skip=1&limit=1", headers=auth_headers).json()
    assert second_page["items"][0]["kind"] == "customer"
    assert second_page["items"][0]["customer_id"] == customer.customer_id
    assert second_page["has_more"] is False

    configured_ids = client.get("/it/email-templates/customer-ids", headers=auth_headers).json()
    assert configured_ids == [customer.customer_id]

    legacy = client.get("/it/email-templates/customer", headers=auth_headers).json()
    assert isinstance(legacy, list)
    assert [template["customer_id"] for template in legacy] == [customer.customer_id]


@pytest.mark.parametrize(
    ("module_key", "action", "method", "path", "payload"),
    [
        ("it_catalog", "can_create", "POST", "/it/catalog/items/", {"item_type": "SERVICE", "name": "Denied"}),
        ("it_catalog", "can_edit", "PATCH", "/it/catalog/items/999999", {"name": "Denied"}),
        ("it_catalog", "can_delete", "DELETE", "/it/catalog/items/999999", None),
        ("it_quotations", "can_edit", "POST", "/it/quotations/999999/change-status", {"status": "SENT"}),
        ("it_quotations", "can_delete", "DELETE", "/it/quotations/999999", None),
        ("it_templates", "can_create", "POST", "/it/templates/", {"name": "Denied", "template_key": "d", "company_name": "Denied"}),
        ("it_templates", "can_edit", "PATCH", "/it/templates/999999", {"name": "Denied"}),
        ("it_email_templates", "can_edit", "PUT", "/it/email-templates/default", {"subject": "Denied", "title": "Denied", "message_body": "Denied"}),
        ("it_email_templates", "can_delete", "DELETE", "/it/email-templates/customer/999999", None),
    ],
)
def test_it_mutations_require_exact_permissions(
    client,
    auth_headers,
    permission_override,
    module_key,
    action,
    method,
    path,
    payload,
) -> None:
    permission_override(module_key, set())
    denied = client.request(method, path, headers=auth_headers, json=payload)
    assert denied.status_code == 403
    assert denied.json()["detail"] == f"Missing '{action}' permission for module '{module_key}'."

    permission_override(module_key, {action})
    allowed = client.request(method, path, headers=auth_headers, json=payload)
    assert allowed.status_code != 403


def test_email_override_rejects_unknown_customer(client, auth_headers) -> None:
    response = client.put(
        "/it/email-templates/customer/999999",
        headers=auth_headers,
        json={"subject": "Unknown", "title": "Unknown", "message_body": "Unknown"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found"


def test_sent_report_requires_dashboard_view_permission(client, auth_headers, permission_override) -> None:
    permission_override("it_dashboard", set())
    denied = client.get("/it/quotations/report", headers=auth_headers)
    assert denied.status_code == 403

    permission_override("it_dashboard", {"can_view"})
    allowed = client.get("/it/quotations/report", headers=auth_headers)
    assert allowed.status_code == 200
