from helpers.string_helpers import parse_email_list

"""Email notification functions using Microsoft Graph API."""

import asyncio
import logging

import httpx

from core.config import settings
from services.notifications.auth import get_graph_api_auth_headers
from services.notifications.schemas import EmailAttachment

logger = logging.getLogger(__name__)


def get_retry_client() -> httpx.AsyncClient:
    """Get HTTP client with retry logic."""
    return httpx.AsyncClient(
        timeout=httpx.Timeout(30.0, connect=10.0),
        limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
    )


async def send_outlook_email(
    *,
    send_as_email: str,
    to_emails: list[str],
    subject: str,
    body: str,
    cc_emails: list[str] | None = None,
    bcc_emails: list[str] | None = None,
    attachments: list[EmailAttachment] | None = None,
    save_to_sent_items: bool = True,
) -> tuple[bool, str | None, str | None]:
    """
    Send email using Microsoft Graph API.

    NOTE: send_as_email should always be BOT_EMAIL (the orchestrator).
    All notifications are sent from BOT_EMAIL, even though actions may be performed by different users.

    Returns:
        (success: bool, message_id: str | None, error_message: str | None)
    """
    headers = await get_graph_api_auth_headers()
    if not headers:
        return False, None, "Failed to get authentication headers"

    validated_to = []
    for email in to_emails:
        parsed = parse_email_list(email)
        validated_to.extend(parsed)

    if not validated_to:
        return False, None, "No valid recipient emails"

    validated_cc = []
    if cc_emails:
        for email in cc_emails:
            parsed = parse_email_list(email)
            validated_cc.extend(parsed)

    validated_bcc = []
    if bcc_emails:
        for email in bcc_emails:
            parsed = parse_email_list(email)
            validated_bcc.extend(parsed)

    message = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "html",
                "content": body,
            },
            "toRecipients": [{"emailAddress": {"address": email}} for email in validated_to],
        },
        "saveToSentItems": save_to_sent_items,
    }

    if validated_cc:
        message["message"]["ccRecipients"] = [{"emailAddress": {"address": email}} for email in validated_cc]

    if validated_bcc:
        message["message"]["bccRecipients"] = [{"emailAddress": {"address": email}} for email in validated_bcc]

    if attachments:
        message["message"]["attachments"] = [
            {
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": att.name,
                "contentType": att.content_type,
                "contentBytes": att.content_bytes,
            }
            for att in attachments
        ]

    url = f"https://graph.microsoft.com/v1.0/users/{send_as_email}/sendMail"

    max_retries = 3
    last_error = None

    async with get_retry_client() as client:
        for attempt in range(max_retries):
            try:
                response = await client.post(url, headers=headers, json=message)
                response.raise_for_status()

                message_id = response.headers.get("x-request-id") or response.headers.get("request-id")

                logger.info(f"Email sent successfully to {validated_to}. Message ID: {message_id}")
                return True, message_id, None

            except httpx.HTTPStatusError as e:
                last_error = f"HTTP {e.response.status_code}: {e.response.text}"
                if e.response.status_code < 500:
                    break
                logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {last_error}")
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {last_error}")

            if attempt < max_retries - 1:
                await asyncio.sleep(2**attempt)

    error_msg = f"Failed to send email after {max_retries} attempts: {last_error}"
    logger.error(error_msg)
    return False, None, error_msg


async def send_notification_email(
    *,
    to_emails: list[str],
    subject: str,
    body: str,
    cc_emails: list[str] | None = None,
    bcc_emails: list[str] | None = None,
    sender_email: str | None = None,
    attachments: list[EmailAttachment] | None = None,
) -> tuple[bool, str | None]:
    """
    Send a notification email.

    Always uses BOT_EMAIL as sender (orchestrator).
    The sender_email parameter is ignored - BOT_EMAIL is always used.

    Returns:
        (success: bool, error_message: str | None)
    """
    sender_email = getattr(settings, "BOT_EMAIL", None)
    if not sender_email:
        return False, "No sender email configured (BOT_EMAIL)"

    success, _message_id, error_message = await send_outlook_email(
        send_as_email=sender_email,
        to_emails=to_emails,
        subject=subject,
        body=body,
        cc_emails=cc_emails,
        bcc_emails=bcc_emails,
        attachments=attachments,
    )

    return success, error_message
