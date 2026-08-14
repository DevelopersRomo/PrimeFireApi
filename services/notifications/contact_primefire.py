"""Contact PrimeFire notification service."""

from html import escape
from urllib.parse import urlparse

from core.config import settings
from core.mail_profiles import DEFAULT_MAIL_PROFILE
from schemas.notifications import ContactPrimeFireRequest
from services.notifications.email_functions import parse_email_list, send_outlook_email
from services.notifications.schemas import NotificationResponse

DEFAULT_LOGO_URL = "https://primefire.do/assets/images/logoRDF.png"


def sanitize_logo_url(raw_url: str | None) -> str:
    """Normalize logo URL and fallback to default if invalid."""
    if not raw_url:
        return DEFAULT_LOGO_URL

    candidate = raw_url.strip()
    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return DEFAULT_LOGO_URL

    return candidate


def _safe_text(value: str | None) -> str:
    if not value:
        return ""
    return escape(str(value).strip())


def _build_field_rows(notification_data: ContactPrimeFireRequest) -> str:
    """Build HTML rows from fixed and dynamic fields."""
    fields = [
        ("Name", notification_data.name),
        ("Company", notification_data.company),
        ("Email", notification_data.email),
        ("Phone", notification_data.phone),
        ("Industry", notification_data.industry),
        ("Service", notification_data.service),
    ]

    if notification_data.note:
        if notification_data.subject:
            fields.append(("Subject", notification_data.subject))
        fields.append(("Note", notification_data.note))

    for field in notification_data.fields:
        label = field.label or field.key
        fields.append((label, field.value))

    rows = []
    for label, value in fields:
        if value is None or str(value).strip() == "":  # noqa: PLC1901
            continue
        rows.append(
            f"""
            <p style=\"margin-bottom:10px\">\
                <strong>{_safe_text(label)}:</strong> {_safe_text(str(value))}\
            </p>
            """
        )

    return "".join(rows)


def generate_contact_primefire_html(notification_data: ContactPrimeFireRequest) -> str:
    """Generate contact-primefire HTML with base template aesthetics."""
    logo_url = sanitize_logo_url(str(notification_data.logo_url) if notification_data.logo_url else None)
    title = _safe_text(notification_data.title)
    subtitle = _safe_text(notification_data.subtitle) or "A new contact request was received."
    field_rows = _build_field_rows(notification_data)

    return f"""
<table style="margin-left:auto; margin-right:auto" cellspacing="0" cellpadding="0" role="presentation">
  <tbody>
    <tr>
      <td style="width:630px" width="630">
        <table style="width:100%" width="100%" cellspacing="0" cellpadding="0" role="presentation">
          <tbody>
            <tr>
              <td style="background-color:#ffffff; padding:40px 60px;">
                <table style="width:100%" width="100%" cellspacing="0" cellpadding="0" role="presentation">
                  <tbody>
                    <tr>
                      <td align="center">
                        <img
                          style="display:inline-block; border:0; height:auto; width:auto; margin:0 auto; max-width:400px;"
                          alt="PrimeFire Logo"
                          width="400"
                          src="{logo_url}"
                        >
                      </td>
                    </tr>
                    <tr>
                      <td>
                        <div style="line-height:40px; font-size:1px; display:block;">&nbsp;</div>
                      </td>
                    </tr>
                    <tr>
                      <td>
                        <h1 style="margin:0; font-family:Poppins, 'Segoe UI', Arial, sans-serif; line-height:34px; font-weight:700; font-size:29px; color:#333333; text-align:left;">
                          {title}
                        </h1>
                      </td>
                    </tr>
                    <tr>
                      <td>
                        <div style="line-height:11px; font-size:1px; display:block;">&nbsp;</div>
                      </td>
                    </tr>
                    <tr>
                      <td>
                        <p style="margin:0; font-family:Poppins, 'Segoe UI', Arial, sans-serif; line-height:22px; font-weight:500; font-size:16px; color:#333333; text-align:left;">
                          {subtitle}
                        </p>
                      </td>
                    </tr>
                    <tr>
                      <td>
                        <div style="line-height:20px; font-size:1px; display:block;">&nbsp;</div>
                      </td>
                    </tr>
                    <tr>
                      <td align="left">
                        <div style="font-family:Poppins, 'Segoe UI', Arial, sans-serif; line-height:22px; font-weight:500; font-size:16px; color:#333333;">
                          {field_rows}
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </td>
            </tr>
          </tbody>
        </table>
      </td>
    </tr>
  </tbody>
</table>
    """.strip()


def generate_confirmation_html(
    logo_url: str | None = None,
) -> str:
    """Generate confirmation HTML for the user who submitted the contact form."""
    url = sanitize_logo_url(logo_url)

    return f"""
<table style="margin-left:auto; margin-right:auto" cellspacing="0" cellpadding="0" role="presentation">
  <tbody>
    <tr>
      <td style="width:630px" width="630">
        <table style="width:100%" width="100%" cellspacing="0" cellpadding="0" role="presentation">
          <tbody>
            <tr>
              <td style="background-color:#ffffff; padding:40px 60px;">
                <table style="width:100%" width="100%" cellspacing="0" cellpadding="0" role="presentation">
                  <tbody>
                    <tr>
                      <td align="center">
                        <img
                          style="display:inline-block; border:0; height:auto; width:auto; margin:0 auto; max-width:400px;"
                          alt="PrimeFire Logo"
                          width="400"
                          src="{url}"
                        >
                      </td>
                    </tr>
                    <tr>
                      <td>
                        <div style="line-height:40px; font-size:1px; display:block;">&nbsp;</div>
                      </td>
                    </tr>
                    <tr>
                      <td>
                        <h1 style="margin:0; font-family:Poppins, 'Segoe UI', Arial, sans-serif; line-height:34px; font-weight:700; font-size:29px; color:#333333; text-align:left;">
                          Thank You for Contacting Us
                        </h1>
                      </td>
                    </tr>
                    <tr>
                      <td>
                        <div style="line-height:11px; font-size:1px; display:block;">&nbsp;</div>
                      </td>
                    </tr>
                    <tr>
                      <td>
                        <p style="margin:0; font-family:Poppins, 'Segoe UI', Arial, sans-serif; line-height:22px; font-weight:500; font-size:16px; color:#333333; text-align:left;">
                          We have received your message and would like to thank you for reaching out to us.
                        </p>
                      </td>
                    </tr>
                    <tr>
                      <td>
                        <div style="line-height:16px; font-size:1px; display:block;">&nbsp;</div>
                      </td>
                    </tr>
                    <tr>
                      <td>
                        <p style="margin:0; font-family:Poppins, 'Segoe UI', Arial, sans-serif; line-height:22px; font-weight:500; font-size:16px; color:#333333; text-align:left;">
                          Our team is reviewing your inquiry and will get back to you as soon as possible. We typically respond within 24-48 business hours.
                        </p>
                      </td>
                    </tr>
                    <tr>
                      <td>
                        <div style="line-height:24px; font-size:1px; display:block;">&nbsp;</div>
                      </td>
                    </tr>
                    <tr>
                      <td>
                        <p style="margin:0; font-family:Poppins, 'Segoe UI', Arial, sans-serif; line-height:22px; font-weight:500; font-size:16px; color:#333333; text-align:left;">
                          Best regards,<br>
                          <strong>The PrimeFire Team</strong>
                        </p>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </td>
            </tr>
          </tbody>
        </table>
      </td>
    </tr>
  </tbody>
</table>
    """.strip()


async def send_contact_primefire_notification(
    notification_data: ContactPrimeFireRequest,
    mail_profile: str = DEFAULT_MAIL_PROFILE,
) -> NotificationResponse:
    """Send contact-primefire notification email."""
    to_emails = parse_email_list(str(notification_data.to_email))
    if not to_emails:
        return NotificationResponse(
            success=False,
            error_message="No valid recipient emails",
        )

    cc_emails = None
    if notification_data.cc_email:
        parsed_cc = parse_email_list(str(notification_data.cc_email))
        cc_emails = parsed_cc or None

    sender_email = getattr(settings, "BOT_EMAIL", "")
    if not sender_email:
        return NotificationResponse(
            success=False,
            error_message="No sender email configured (BOT_EMAIL)",
        )

    html_body = generate_contact_primefire_html(notification_data)

    success, message_id, error_message = await send_outlook_email(
        send_as_email=sender_email,
        to_emails=to_emails,
        subject=notification_data.title,
        body=html_body,
        cc_emails=cc_emails,
        mail_profile=mail_profile,
    )

    if not success:
        return NotificationResponse(
            success=False,
            error_message=error_message or "Unknown error while sending contact-primefire notification",
        )

    # Send confirmation email to the user who submitted the form
    if notification_data.email:
        user_email = str(notification_data.email).strip()
        user_emails = parse_email_list(user_email)
        if user_emails:
            confirmation_html = generate_confirmation_html(
                str(notification_data.logo_url) if notification_data.logo_url else None,
            )
            await send_outlook_email(
                send_as_email=sender_email,
                to_emails=user_emails,
                subject="We Received Your Message - PrimeFire",
                body=confirmation_html,
                mail_profile=mail_profile,
            )

    return NotificationResponse(success=True, message_id=message_id)
