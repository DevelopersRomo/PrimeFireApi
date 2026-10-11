"""Rendering a quotation PDF is CPU-bound, so sending a quotation must not run it on the event loop."""

import asyncio
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from services.it import email_service


class _Stop(Exception):
    pass


def test_send_quotation_renders_the_pdf_off_the_event_loop(monkeypatch) -> None:
    on_loop: list[bool] = []

    def spy(db, quotation, generated_by=None):
        try:
            asyncio.get_running_loop()
            on_loop.append(True)
        except RuntimeError:
            on_loop.append(False)
        raise _Stop

    monkeypatch.setattr(email_service, "generate_quotation_pdf", spy)
    monkeypatch.setattr(email_service, "next_customer_quotation_number", lambda *args, **kwargs: "Q-1")
    quotation = SimpleNamespace(
        customer_email_snapshot="customer@example.com",
        sent_at=None,
        tenant_id=1,
        customer_id=1,
        customer_name_snapshot="Customer",
        quotation_number=None,
    )

    with pytest.raises(_Stop):
        asyncio.run(email_service.send_quotation_email(MagicMock(), quotation, sent_by=1))

    assert on_loop == [False]
