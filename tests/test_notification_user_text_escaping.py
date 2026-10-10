from unittest.mock import AsyncMock, patch

import pytest

from services.it import email_service
from services.notifications.expenses import notify_expense_message
from services.notifications.notifications import (
    send_custom_notification,
    send_inventory_movement_notification,
    send_ticket_assigned_notification,
    send_ticket_message_notification,
    send_time_off_notification,
)
from services.notifications.schemas import (
    InventoryMovementNotificationData,
    TicketMessageNotificationData,
    TicketNotificationData,
    TimeOffNotificationData,
)


@pytest.mark.asyncio
async def test_expense_message_notification_escapes_user_text():
    message = '<a href="https://evil.example">x</a> <img src=x>'
    with patch("services.notifications.expenses.send_custom_notification", new_callable=AsyncMock) as send:
        await notify_expense_message(1, "EXP-1", "recipient@example.com", "Author", None, message)

    assert send.call_args.kwargs["message_body"] == (
        "&lt;a href=&quot;https://evil.example&quot;&gt;x&lt;/a&gt; &lt;img src=x&gt;"
    )


@pytest.mark.asyncio
async def test_ticket_notification_escapes_user_title_and_description():
    data = TicketNotificationData(
        ticket_id=1,
        title='<a href="https://evil.example">x</a>',
        description="<img src=x>",
        status="todo",
        priority="normal",
        created_by_name="Creator",
        created_by_email="creator@example.com",
    )
    with (
        patch("services.notifications.notifications.settings.BOT_EMAIL", "bot@example.com"),
        patch("services.notifications.notifications.send_outlook_email", new_callable=AsyncMock) as send,
    ):
        send.return_value = (True, "message-id", None)
        await send_ticket_assigned_notification(data, "recipient@example.com")

    body = send.call_args.kwargs["body"]
    assert "&lt;a href=&quot;https://evil.example&quot;&gt;x&lt;/a&gt;" in body
    assert "&lt;img src=x&gt;" in body
    assert '<a href="https://evil.example">x</a>' not in body
    assert "<img src=x>" not in body


@pytest.mark.asyncio
async def test_ticket_comment_notification_escapes_comment_and_title():
    data = TicketMessageNotificationData(
        ticket_id=1,
        ticket_title="<img src=x>",
        message_id=2,
        message_text='<a href="https://evil.example">x</a>',
        commenter_name="Commenter",
        commenter_email="commenter@example.com",
    )
    with (
        patch("services.notifications.notifications.settings.BOT_EMAIL", "bot@example.com"),
        patch("services.notifications.notifications.send_outlook_email", new_callable=AsyncMock) as send,
    ):
        send.return_value = (True, "message-id", None)
        await send_ticket_message_notification(data, "recipient@example.com")

    body = send.call_args.kwargs["body"]
    assert "&lt;img src=x&gt;" in body
    assert "&lt;a href=&quot;" in body
    assert "<img src=x>" not in body
    assert '<a href="https://evil.example">x</a>' not in body


@pytest.mark.asyncio
async def test_time_off_notification_escapes_reason_and_review_notes():
    data = TimeOffNotificationData(
        request_id=1,
        employee_id=2,
        employee_name="Employee",
        employee_email="employee@example.com",
        absence_type="vacation",
        start_date="2026-10-09",
        end_date="2026-10-10",
        total_days="1",
        reason="<img src=x>",
        review_notes="<b>Review</b>",
    )
    with (
        patch(
            "services.notifications.notifications._resolve_email_branding",
            return_value={
                "support_email": "support@example.com",
                "app_url": "https://example.com",
                "app_name": "PrimeFire",
                "include_support_section": True,
            },
        ),
        patch("services.notifications.notifications.settings.BOT_EMAIL", "bot@example.com"),
        patch("services.notifications.notifications.send_outlook_email", new_callable=AsyncMock) as send,
    ):
        send.return_value = (True, "message-id", None)
        await send_time_off_notification(data, "approved", "recipient@example.com")

    body = send.call_args.kwargs["body"]
    assert "&lt;img src=x&gt;" in body
    assert "&lt;b&gt;Review&lt;/b&gt;" in body
    assert "<img src=x>" not in body
    assert "<b>Review</b>" not in body


@pytest.mark.asyncio
async def test_inventory_notification_escapes_movement_note():
    data = InventoryMovementNotificationData(
        movement_id=1,
        movement_type="IN",
        product_name="Product",
        quantity="1",
        notes='<a href="https://evil.example">x</a>',
        project="<img src=x>",
        po_number="<b>PO</b>",
    )
    with (
        patch("services.notifications.notifications.settings.BOT_EMAIL", "bot@example.com"),
        patch("services.notifications.notifications.send_outlook_email", new_callable=AsyncMock) as send,
    ):
        send.return_value = (True, "message-id", None)
        await send_inventory_movement_notification(data, "recipient@example.com")

    body = send.call_args.kwargs["body"]
    assert "&lt;a href=&quot;https://evil.example&quot;&gt;x&lt;/a&gt;" in body
    assert '<a href="https://evil.example">x</a>' not in body
    assert "&lt;img src=x&gt;" in body
    assert "<img src=x>" not in body
    assert "&lt;b&gt;PO&lt;/b&gt;" in body


@pytest.mark.asyncio
async def test_send_custom_notification_keeps_supplied_html_unchanged():
    with (
        patch("services.notifications.notifications.settings.BOT_EMAIL", "bot@example.com"),
        patch("services.notifications.notifications.send_outlook_email", new_callable=AsyncMock) as send,
    ):
        send.return_value = (True, "message-id", None)
        await send_custom_notification(
            title='<a href="https://example.com">title</a>',
            message_body="Message",
            to_email="recipient@example.com",
        )

    assert '<a href="https://example.com">title</a>' in send.call_args.kwargs["body"]


def test_quotation_email_keeps_generated_html_markup():
    body = email_service._build_email_body(  # noqa: SLF001
        title="Quotation",
        message_body="Hello {customer_name}",
        footer="Footer",
        placeholders={
            "customer_name": "Customer",
            "quotation_number": "Q-1",
            "expiration_date": "",
            "total": "",
            "currency": "USD",
        },
        quotation=None,
    )

    assert "Hello Customer<br><br><span" in body
    assert "</span>" in body
    assert "&lt;br&gt;" not in body
