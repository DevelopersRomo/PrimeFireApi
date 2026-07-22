"""API tests for IT quotations: creation, totals, items, statuses, schedule."""

import pytest


@pytest.fixture
def quotation_payload(customer) -> dict:
    """Replica of the mockup quotation: $600 one-time + $280 annual = $880."""
    return {
        "customer_id": customer.customer_id,
        "quote_date": "2026-07-16",
        "expiration_date": "2026-08-15",
        "currency": "USD",
        "items": [
            {"name": "Website Development", "item_type": "SERVICE", "billing_cycle": "ONE_TIME", "unit_price": "450"},
            {"name": "SEO Setup", "item_type": "SERVICE", "billing_cycle": "ONE_TIME", "unit_price": "150"},
            {
                "name": "Managed Hosting (1 Year)",
                "item_type": "HOSTING",
                "billing_cycle": "ANNUAL",
                "unit_price": "150",
                "term_months": 12,
            },
            {
                "name": "Domain Registration (1 Year)",
                "item_type": "DOMAIN",
                "billing_cycle": "ANNUAL",
                "unit_price": "50",
                "term_months": 12,
            },
            {
                "name": "SSL Certificate (https)",
                "item_type": "SSL",
                "billing_cycle": "ANNUAL",
                "unit_price": "80",
                "term_months": 12,
            },
        ],
        "terms": {
            "delivery_time_text": "1 to 3 months",
            "validity_days": 30,
            "tax_note": "Prices do not include VAT",
        },
        "payment_schedule": [
            {"sequence_number": 1, "description": "Upon acceptance", "percentage": 50},
            {"sequence_number": 2, "description": "Upon design approval", "percentage": 25},
            {"sequence_number": 3, "description": "Upon final delivery", "percentage": 25},
        ],
    }


def _create(client, auth_headers, payload) -> dict:
    response = client.post("/it/quotations/", json=payload, headers=auth_headers)
    assert response.status_code == 201, response.text
    return response.json()


class TestQuotationCreate:
    def test_create_computes_mockup_totals(self, client, auth_headers, quotation_payload) -> None:
        quotation = _create(client, auth_headers, quotation_payload)
        assert quotation["status"] == "DRAFT"
        assert quotation["quotation_number"].startswith("Q-IT-")
        assert quotation["customer_name_snapshot"] == "Speedy Gonzalez Welding"
        assert float(quotation["one_time_subtotal"]) == 600.00
        assert float(quotation["annual_recurring_subtotal"]) == 280.00
        assert float(quotation["monthly_recurring_subtotal"]) == 0.00
        assert float(quotation["initial_total"]) == 880.00
        assert len(quotation["items"]) == 5
        assert len(quotation["payment_schedule"]) == 3
        assert quotation["terms"]["validity_days"] == 30

    def test_catalog_item_snapshot(self, client, auth_headers, customer, catalog_item_payload) -> None:
        catalog_item = client.post("/it/catalog/items/", json=catalog_item_payload, headers=auth_headers).json()
        quotation = _create(
            client,
            auth_headers,
            {
                "customer_id": customer.customer_id,
                "quote_date": "2026-07-16",
                "expiration_date": "2026-08-15",
                "items": [{"catalog_item_id": catalog_item["catalog_item_id"], "quantity": "1"}],
            },
        )
        item = quotation["items"][0]
        assert item["name_snapshot"] == "Website Development"
        assert float(item["unit_price"]) == 450.00

        # Changing the catalog later must not affect the quotation snapshot.
        client.patch(
            f"/it/catalog/items/{catalog_item['catalog_item_id']}",
            json={"unit_price": "999.00"},
            headers=auth_headers,
        )
        fetched = client.get(f"/it/quotations/{quotation['quotation_id']}", headers=auth_headers).json()
        assert float(fetched["items"][0]["unit_price"]) == 450.00

    def test_invalid_payment_percentages_rejected(self, client, auth_headers, quotation_payload) -> None:
        quotation_payload["payment_schedule"] = [
            {"sequence_number": 1, "description": "Upon acceptance", "percentage": 50},
        ]
        response = client.post("/it/quotations/", json=quotation_payload, headers=auth_headers)
        assert response.status_code == 422

    def test_unknown_customer_rejected(self, client, auth_headers, quotation_payload) -> None:
        quotation_payload["customer_id"] = 99999
        response = client.post("/it/quotations/", json=quotation_payload, headers=auth_headers)
        assert response.status_code == 404


class TestQuotationItems:
    def test_add_update_delete_item_recalculates(self, client, auth_headers, quotation_payload) -> None:
        quotation = _create(client, auth_headers, quotation_payload)
        qid = quotation["quotation_id"]

        added = client.post(
            f"/it/quotations/{qid}/items",
            json={"name": "Extra Work", "item_type": "SERVICE", "billing_cycle": "ONE_TIME", "unit_price": "100"},
            headers=auth_headers,
        )
        assert added.status_code == 201
        assert float(added.json()["initial_total"]) == 980.00

        item_id = next(i["quotation_item_id"] for i in added.json()["items"] if i["name_snapshot"] == "Extra Work")

        updated = client.patch(
            f"/it/quotations/{qid}/items/{item_id}",
            json={"quantity": "2"},
            headers=auth_headers,
        )
        assert updated.status_code == 200
        assert float(updated.json()["initial_total"]) == 1080.00

        removed = client.delete(f"/it/quotations/{qid}/items/{item_id}", headers=auth_headers)
        assert removed.status_code == 200
        assert float(removed.json()["initial_total"]) == 880.00


class TestQuotationStatuses:
    def test_valid_transition_draft_to_sent(self, client, auth_headers, quotation_payload) -> None:
        quotation = _create(client, auth_headers, quotation_payload)
        response = client.post(
            f"/it/quotations/{quotation['quotation_id']}/change-status",
            json={"status": "SENT", "notes": "Sent manually"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "SENT"
        assert response.json()["sent_at"] is not None

    def test_invalid_transition_rejected(self, client, auth_headers, quotation_payload) -> None:
        quotation = _create(client, auth_headers, quotation_payload)
        response = client.post(
            f"/it/quotations/{quotation['quotation_id']}/change-status",
            json={"status": "ACCEPTED"},
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_history_recorded(self, client, auth_headers, quotation_payload) -> None:
        quotation = _create(client, auth_headers, quotation_payload)
        qid = quotation["quotation_id"]
        client.post(f"/it/quotations/{qid}/change-status", json={"status": "SENT"}, headers=auth_headers)

        history = client.get(f"/it/quotations/{qid}/history", headers=auth_headers).json()
        statuses = [h["new_status"] for h in history]
        assert "DRAFT" in statuses
        assert "SENT" in statuses

    def test_delete_only_draft(self, client, auth_headers, quotation_payload) -> None:
        quotation = _create(client, auth_headers, quotation_payload)
        qid = quotation["quotation_id"]
        client.post(f"/it/quotations/{qid}/change-status", json={"status": "SENT"}, headers=auth_headers)

        response = client.delete(f"/it/quotations/{qid}", headers=auth_headers)
        assert response.status_code == 400

    def test_delete_draft(self, client, auth_headers, quotation_payload) -> None:
        quotation = _create(client, auth_headers, quotation_payload)
        response = client.delete(f"/it/quotations/{quotation['quotation_id']}", headers=auth_headers)
        assert response.status_code == 204
        assert client.get(f"/it/quotations/{quotation['quotation_id']}", headers=auth_headers).status_code == 404


class TestQuotationActions:
    def test_duplicate(self, client, auth_headers, quotation_payload) -> None:
        original = _create(client, auth_headers, quotation_payload)
        response = client.post(f"/it/quotations/{original['quotation_id']}/duplicate", headers=auth_headers)
        assert response.status_code == 200
        clone = response.json()
        assert clone["quotation_id"] != original["quotation_id"]
        assert clone["quotation_number"] != original["quotation_number"]
        assert clone["status"] == "DRAFT"
        assert float(clone["initial_total"]) == 880.00
        assert len(clone["items"]) == 5

    def test_filters(self, client, auth_headers, quotation_payload) -> None:
        _create(client, auth_headers, quotation_payload)
        drafts = client.get("/it/quotations/?status=DRAFT", headers=auth_headers).json()
        assert all(q["status"] == "DRAFT" for q in drafts)

        searched = client.get("/it/quotations/?search=Speedy", headers=auth_headers).json()
        assert len(searched) >= 1

    def test_terms_roundtrip(self, client, auth_headers, quotation_payload) -> None:
        quotation = _create(client, auth_headers, quotation_payload)
        qid = quotation["quotation_id"]

        put = client.put(
            f"/it/quotations/{qid}/terms",
            json={"delivery_time_text": "2 weeks", "validity_days": 15},
            headers=auth_headers,
        )
        assert put.status_code == 200

        got = client.get(f"/it/quotations/{qid}/terms", headers=auth_headers).json()
        assert got["delivery_time_text"] == "2 weeks"
        assert got["validity_days"] == 15

    def test_payment_schedule_roundtrip(self, client, auth_headers, quotation_payload) -> None:
        quotation = _create(client, auth_headers, quotation_payload)
        qid = quotation["quotation_id"]

        put = client.put(
            f"/it/quotations/{qid}/payment-schedule",
            json=[
                {"sequence_number": 1, "description": "Upfront", "percentage": 100},
            ],
            headers=auth_headers,
        )
        assert put.status_code == 200

        got = client.get(f"/it/quotations/{qid}/payment-schedule", headers=auth_headers).json()
        assert len(got) == 1
        assert got[0]["description"] == "Upfront"

    def test_payment_schedule_invalid_percentages(self, client, auth_headers, quotation_payload) -> None:
        quotation = _create(client, auth_headers, quotation_payload)
        response = client.put(
            f"/it/quotations/{quotation['quotation_id']}/payment-schedule",
            json=[{"sequence_number": 1, "description": "Partial", "percentage": 60}],
            headers=auth_headers,
        )
        assert response.status_code == 422
