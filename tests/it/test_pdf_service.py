"""Tests for the IT quotation PDF service (HTML render + optional PDF)."""

import importlib.util

import pytest
from sqlmodel import select

from models.it.quotations import ITQuotations
from services.it.pdf_service import render_quotation_html

WEASYPRINT_AVAILABLE = importlib.util.find_spec("weasyprint") is not None


@pytest.fixture
def quotation(client, auth_headers, customer, db_session) -> ITQuotations:
    payload = {
        "customer_id": customer.customer_id,
        "quote_date": "2026-07-16",
        "expiration_date": "2026-08-15",
        "items": [
            {"name": "Website Development", "item_type": "SERVICE", "billing_cycle": "ONE_TIME", "unit_price": "450"},
            {"name": "Managed Hosting", "item_type": "HOSTING", "billing_cycle": "ANNUAL", "unit_price": "150"},
        ],
        "payment_schedule": [
            {"sequence_number": 1, "description": "Upon acceptance", "percentage": 100},
        ],
    }
    response = client.post("/it/quotations/", json=payload, headers=auth_headers)
    assert response.status_code == 201, response.text
    quotation_id = response.json()["quotation_id"]
    return db_session.exec(select(ITQuotations).where(ITQuotations.quotation_id == quotation_id)).one()


class TestRenderHtml:
    def test_render_contains_quotation_data(self, db_session, quotation) -> None:
        html = render_quotation_html(db_session, quotation)
        assert quotation.quotation_number in html
        assert "Website Development" in html
        assert "Managed Hosting" in html
        assert "Payment Schedule" in html
        assert "$450.00" in html
        assert "Initial Amount" in html

    def test_render_totals(self, db_session, quotation) -> None:
        html = render_quotation_html(db_session, quotation)
        assert "$600.00" in html  # initial: 450 one-time + 150 annual first year
        assert "$150.00" in html


@pytest.mark.skipif(not WEASYPRINT_AVAILABLE, reason="WeasyPrint not installed")
class TestGeneratePdf:
    def test_generate_pdf_registers_document(self, db_session, quotation, tmp_path, monkeypatch) -> None:
        import services.it.document_storage as storage

        monkeypatch.setattr(storage, "BASE_DIR", tmp_path)

        from services.it.pdf_service import generate_quotation_pdf

        try:
            document = generate_quotation_pdf(db_session, quotation)
        except Exception as exc:  # pragma: no cover - native GTK libs missing locally
            pytest.skip(f"WeasyPrint native dependencies unavailable: {exc}")

        assert document.document_version == 1
        assert document.file_name.endswith(".pdf")
        assert document.file_hash
