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


# --- EMAIL TEMPLATES FOR AUTH ---


def build_password_recovery_email(*, to_email: str, token: str, app_url: str, tenant_title: str = "PrimeFire") -> tuple[str, str]:
    """Build password recovery email body and subject."""
    reset_url = f"{app_url}/reset-password?token={token}"
    subject = f"Reset your password - {tenant_title}"
    body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
    <!--[if mso]>
    <style type="text/css">
        body, table, td {{font-family: Arial, sans-serif !important;}}
    </style>
    <![endif]-->
</head>
<body style="margin: 0; padding: 0; background-color: #f4f4f4; font-family: Arial, sans-serif;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4;">
        <tr>
            <td align="center" style="padding: 40px 0;">
                <table width="600" cellpadding="0" cellspacing="0"
                       style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">

                    <!-- Header -->
                    <tr>
                        <td style="background-color: #007bff; padding: 20px; text-align: center;">
                            <div style="font-size: 32px; color: #ffffff; margin-bottom: 4px;">🔑</div>
                        </td>
                    </tr>

                    <!-- Title -->
                    <tr>
                        <td style="padding: 40px 40px 20px;">
                            <h1 style="margin: 0; color: #333; font-size: 24px; font-weight: bold;">
                                Reset your password
                            </h1>
                            <p style="margin: 10px 0 0; color: #666; font-size: 16px;">Hi there,</p>
                        </td>
                    </tr>

                    <!-- Message -->
                    <tr>
                        <td style="padding: 0 40px 20px;">
                            <p style="margin: 0; color: #333; font-size: 16px; line-height: 1.6;">
                                We received a request to reset the password for your {tenant_title} account.
                            </p>
                        </td>
                    </tr>

                    <!-- Action button -->
                    <tr>
                        <td style="padding: 30px 40px; text-align: center;">
                            <a href="{reset_url}"
                               target="_blank"
                               style="display: inline-block; padding: 12px 30px; background-color: #000000;
                                      color: #ffffff; text-decoration: none; border-radius: 4px; font-size: 14px; font-weight: bold;">
                                Reset password
                            </a>
                        </td>
                    </tr>

                    <!-- Expiry notice -->
                    <tr>
                        <td style="padding: 0 40px 20px;">
                            <p style="margin: 0; color: #666; font-size: 14px; line-height: 1.6;">
                                This link expires in <strong>15 minutes</strong> and can only be used once.
                                If you didn't request this change, you can safely ignore this email.
                            </p>
                        </td>
                    </tr>

                    <!-- Divider -->
                    <tr>
                        <td style="padding: 20px 40px;">
                            <hr style="border: none; border-top: 1px solid #e1e1e1; margin: 0;">
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="padding: 10px 40px 40px; text-align: center;">
                            <a href="{app_url}"
                               style="color: #5b5b5b; text-decoration: none; font-size: 14px;">
                                {tenant_title} Support · <a href="mailto:info@devromo.com" style="color: #5b5b5b;">info@devromo.com</a>
                            </a>
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>
</body>
</html>
    """
    return subject, body


def build_magic_link_email(*, to_email: str, token: str, app_url: str, tenant_title: str = "PrimeFire") -> tuple[str, str]:
    """Build magic link email body and subject."""
    login_url = f"{app_url}/magic-login?token={token}"
    subject = f"Your magic login link - {tenant_title}"
    body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
    <!--[if mso]>
    <style type="text/css">
        body, table, td {{font-family: Arial, sans-serif !important;}}
    </style>
    <![endif]-->
</head>
<body style="margin: 0; padding: 0; background-color: #f4f4f4; font-family: Arial, sans-serif;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4;">
        <tr>
            <td align="center" style="padding: 40px 0;">
                <table width="600" cellpadding="0" cellspacing="0"
                       style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">

                    <!-- Header -->
                    <tr>
                        <td style="background-color: #6f42c1; padding: 20px; text-align: center;">
                            <div style="font-size: 32px; color: #ffffff; margin-bottom: 4px;">✨</div>
                        </td>
                    </tr>

                    <!-- Title -->
                    <tr>
                        <td style="padding: 40px 40px 20px;">
                            <h1 style="margin: 0; color: #333; font-size: 24px; font-weight: bold;">
                                Magic Link Login
                            </h1>
                            <p style="margin: 10px 0 0; color: #666; font-size: 16px;">Hi there,</p>
                        </td>
                    </tr>

                    <!-- Message -->
                    <tr>
                        <td style="padding: 0 40px 20px;">
                            <p style="margin: 0; color: #333; font-size: 16px; line-height: 1.6;">
                                Click the button below to sign in to {tenant_title} automatically — no password needed.
                            </p>
                        </td>
                    </tr>

                    <!-- Action button -->
                    <tr>
                        <td style="padding: 30px 40px; text-align: center;">
                            <a href="{login_url}"
                               target="_blank"
                               style="display: inline-block; padding: 12px 30px; background-color: #000000;
                                      color: #ffffff; text-decoration: none; border-radius: 4px; font-size: 14px; font-weight: bold;">
                                Sign in to {tenant_title}
                            </a>
                        </td>
                    </tr>

                    <!-- Expiry notice -->
                    <tr>
                        <td style="padding: 0 40px 20px;">
                            <p style="margin: 0; color: #666; font-size: 14px; line-height: 1.6;">
                                This link expires in <strong>15 minutes</strong> and can only be used once.
                                If you didn't request this, you can safely ignore this email.
                            </p>
                        </td>
                    </tr>

                    <!-- Divider -->
                    <tr>
                        <td style="padding: 20px 40px;">
                            <hr style="border: none; border-top: 1px solid #e1e1e1; margin: 0;">
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="padding: 10px 40px 40px; text-align: center;">
                            <a href="{app_url}"
                               style="color: #5b5b5b; text-decoration: none; font-size: 14px;">
                                {tenant_title} Support · <a href="mailto:info@devromo.com" style="color: #5b5b5b;">info@devromo.com</a>
                            </a>
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>
</body>
</html>
    """
    return subject, body


async def send_password_recovery_email(*, to_email: str, token: str, app_url: str | None = None, tenant_title: str = "PrimeFire") -> tuple[bool, str | None]:
    """Send password recovery email. Returns (success, error_message)."""
    if app_url is None:
        app_url = getattr(settings, "APP_URL", "")
    subject, body = build_password_recovery_email(to_email=to_email, token=token, app_url=app_url, tenant_title=tenant_title)
    return await send_notification_email(to_emails=[to_email], subject=subject, body=body)


async def send_magic_link_email(*, to_email: str, token: str, app_url: str | None = None, tenant_title: str = "PrimeFire") -> tuple[bool, str | None]:
    """Send magic link email. Returns (success, error_message)."""
    if app_url is None:
        app_url = getattr(settings, "APP_URL", "")
    subject, body = build_magic_link_email(to_email=to_email, token=token, app_url=app_url, tenant_title=tenant_title)
    return await send_notification_email(to_emails=[to_email], subject=subject, body=body)
