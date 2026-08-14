from helpers.string_helpers import parse_email_list

"""Email notification functions using Microsoft Graph API."""

import asyncio
import logging

import httpx

from core.config import settings
from core.mail_profiles import DEFAULT_MAIL_PROFILE, get_mail_credentials, normalize_profile_key
from services.notifications.auth import get_graph_api_auth_headers
from services.notifications.schemas import EmailAttachment

logger = logging.getLogger(__name__)


def _normalize_app_url(raw_url: str | None) -> str:
    """Return a normalized absolute URL, forcing https when scheme is missing."""
    candidate = (raw_url or "").strip()
    if not candidate:
        candidate = (getattr(settings, "APP_URL", "") or "").strip()
    if not candidate:
        return ""

    cleaned = candidate.rstrip("/")
    if cleaned.startswith("https://"):
        return cleaned
    if cleaned.startswith("http://"):
        return f"https://{cleaned[len('http://') :]}"
    return f"https://{cleaned}"


def _build_auth_url(*, app_url: str | None, path: str, token: str) -> str:
    base_url = _normalize_app_url(app_url)
    clean_token = (token or "").strip()
    return f"{base_url}{path}?token={clean_token}"


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
    mail_profile: str = DEFAULT_MAIL_PROFILE,
) -> tuple[bool, str | None, str | None]:
    """
    Send email using Microsoft Graph API.

    NOTE: send_as_email should always be BOT_EMAIL (the orchestrator).
    All notifications are sent from BOT_EMAIL, even though actions may be performed by different users.

    mail_profile names the Microsoft tenant that issues the token and owns the sender
    mailbox (see core/mail_profiles). A named profile replaces send_as_email with its
    own BOT_EMAIL; an unconfigured one falls back to the default tenant.

    Returns:
        (success: bool, message_id: str | None, error_message: str | None)
    """
    credentials = get_mail_credentials(mail_profile)
    if credentials:
        send_as_email = credentials.bot_email

    logger.info(
        f"[SEND_OUTLOOK_EMAIL] Starting email send - send_as={send_as_email}, mail_profile={normalize_profile_key(mail_profile)}, resolved={bool(credentials)}, subject='{subject}', to_count={len(to_emails)}"
    )

    headers = await get_graph_api_auth_headers(mail_profile=mail_profile)
    if not headers:
        logger.error("[SEND_OUTLOOK_EMAIL] Failed to get authentication headers")
        return False, None, "Failed to get authentication headers"
    logger.info("[SEND_OUTLOOK_EMAIL] Authentication headers obtained successfully")

    validated_to = []
    for email in to_emails:
        parsed = parse_email_list(email)
        validated_to.extend(parsed)
    logger.info(f"[SEND_OUTLOOK_EMAIL] Validated recipient emails: {validated_to}")

    if not validated_to:
        logger.error("[SEND_OUTLOOK_EMAIL] No valid recipient emails found")
        return False, None, "No valid recipient emails"

    validated_cc = []
    if cc_emails:
        for email in cc_emails:
            parsed = parse_email_list(email)
            validated_cc.extend(parsed)
    logger.info(f"[SEND_OUTLOOK_EMAIL] CC emails: {validated_cc or 'none'}")

    validated_bcc = []
    if bcc_emails:
        for email in bcc_emails:
            parsed = parse_email_list(email)
            validated_bcc.extend(parsed)
    logger.info(f"[SEND_OUTLOOK_EMAIL] BCC emails: {validated_bcc or 'none'}")

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
        logger.info(f"[SEND_OUTLOOK_EMAIL] Adding {len(attachments)} attachment(s)")
        message["message"]["attachments"] = [
            {
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": att.name,
                "contentType": att.content_type,
                "contentBytes": att.content_bytes,
                **(
                    {"contentId": att.content_id, "isInline": True}
                    if att.is_inline and att.content_id
                    else {}
                ),
            }
            for att in attachments
        ]

    url = f"https://graph.microsoft.com/v1.0/users/{send_as_email}/sendMail"
    logger.info(f"[SEND_OUTLOOK_EMAIL] Graph API URL: {url}")

    max_retries = 3
    last_error = None

    async with get_retry_client() as client:
        for attempt in range(max_retries):
            try:
                logger.info(f"[SEND_OUTLOOK_EMAIL] Attempt {attempt + 1}/{max_retries} - posting to Graph API")
                response = await client.post(url, headers=headers, json=message)
                response.raise_for_status()

                message_id = response.headers.get("x-request-id") or response.headers.get("request-id")
                logger.info(
                    f"[SEND_OUTLOOK_EMAIL] ✅ Email sent successfully to {validated_to}. Message ID: {message_id}, Status: {response.status_code}"
                )
                return True, message_id, None

            except httpx.HTTPStatusError as e:
                last_error = f"HTTP {e.response.status_code}: {e.response.text[:500]}"
                logger.warning(f"[SEND_OUTLOOK_EMAIL] Attempt {attempt + 1}/{max_retries} failed - {last_error}")
                if e.response.status_code < 500:
                    logger.exception(
                        f"[SEND_OUTLOOK_EMAIL] Client error (4xx) - not retrying. Status: {e.response.status_code}"
                    )
                    break
            except Exception as e:
                last_error = str(e)
                logger.warning(f"[SEND_OUTLOOK_EMAIL] Attempt {attempt + 1}/{max_retries} failed - {last_error}")

            if attempt < max_retries - 1:
                wait_time = 2**attempt
                logger.info(f"[SEND_OUTLOOK_EMAIL] Waiting {wait_time} seconds before retry...")
                await asyncio.sleep(wait_time)

    error_msg = f"Failed to send email after {max_retries} attempts: {last_error}"
    logger.error(f"[SEND_OUTLOOK_EMAIL] ❌ {error_msg}")
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
    mail_profile: str = DEFAULT_MAIL_PROFILE,
) -> tuple[bool, str | None]:
    """
    Send a notification email.

    Always uses the bot mailbox of the given mail profile, or BOT_EMAIL when that
    profile is the default or unconfigured. The sender_email parameter is ignored.

    Returns:
        (success: bool, error_message: str | None)
    """
    credentials = get_mail_credentials(mail_profile)
    sender_email = credentials.bot_email if credentials else getattr(settings, "BOT_EMAIL", None)
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
        mail_profile=mail_profile,
    )

    return success, error_message


# --- EMAIL TEMPLATES FOR AUTH ---


def build_password_recovery_email(
    *, to_email: str, token: str, app_url: str, tenant_title: str = "PrimeFire"
) -> tuple[str, str]:
    """Build password recovery email body and subject."""
    app_url = _normalize_app_url(app_url)
    reset_url = _build_auth_url(app_url=app_url, path="/reset-password", token=token)
    support_email = getattr(settings, "SUPPORT_EMAIL", "info@devromo.com")
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
                                {tenant_title} Support
                            </a>
                            <span style="color: #5b5b5b; font-size: 14px;"> · </span>
                            <a href="mailto:{support_email}"
                               style="color: #5b5b5b; text-decoration: none; font-size: 14px;">
                                {support_email}
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


def build_magic_link_email(
    *, to_email: str, token: str, app_url: str, tenant_title: str = "PrimeFire"
) -> tuple[str, str]:
    """Build magic link email body and subject."""
    app_url = _normalize_app_url(app_url)
    login_url = _build_auth_url(app_url=app_url, path="/magic-login", token=token)
    support_email = getattr(settings, "SUPPORT_EMAIL", "info@devromo.com")
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
                                {tenant_title} Support
                            </a>
                            <span style="color: #5b5b5b; font-size: 14px;"> · </span>
                            <a href="mailto:{support_email}"
                               style="color: #5b5b5b; text-decoration: none; font-size: 14px;">
                                {support_email}
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


async def send_password_recovery_email(
    *, to_email: str, token: str, app_url: str | None = None, tenant_title: str = "PrimeFire"
) -> tuple[bool, str | None]:
    """Send password recovery email. Returns (success, error_message)."""
    if app_url is None:
        app_url = getattr(settings, "APP_URL", "")
    subject, body = build_password_recovery_email(
        to_email=to_email, token=token, app_url=app_url, tenant_title=tenant_title
    )
    return await send_notification_email(to_emails=[to_email], subject=subject, body=body)


async def send_magic_link_email(
    *, to_email: str, token: str, app_url: str | None = None, tenant_title: str = "PrimeFire"
) -> tuple[bool, str | None]:
    """Send magic link email. Returns (success, error_message)."""
    if app_url is None:
        app_url = getattr(settings, "APP_URL", "")
    subject, body = build_magic_link_email(to_email=to_email, token=token, app_url=app_url, tenant_title=tenant_title)
    return await send_notification_email(to_emails=[to_email], subject=subject, body=body)
