"""Form notification functions.

IMPORTANT: All notifications are sent using BOT_EMAIL as the sender (orchestrator).
Even though actions are performed by specific users, the email always comes from BOT_EMAIL.
"""

from core.config import settings
from core.mail_profiles import DEFAULT_MAIL_PROFILE
from services.notifications.email_functions import (
    parse_email_list,
    send_outlook_email,
)
from services.notifications.schemas import (
    EmailAttachment,
    FormNotificationRequest,
    FormNotificationResponse,
)


def _form_notification_recipients(
    notification_data: FormNotificationRequest,
) -> tuple[list[str], list[str] | None, FormNotificationResponse | None]:
    to_emails = parse_email_list(notification_data.to)
    if not to_emails:
        return (
            [],
            None,
            FormNotificationResponse(
                success=False,
                error_message="No valid recipient emails",
            ),
        )

    cc_emails = parse_email_list(notification_data.cc) if notification_data.cc else None
    return to_emails, cc_emails, None


def _form_notification_attachments(notification_data: FormNotificationRequest) -> list[EmailAttachment] | None:
    if not notification_data.attach_pdf or not notification_data.pdf_file_name:
        return None
    return [
        EmailAttachment(
            name=notification_data.pdf_file_name,
            content_type="application/pdf",
            content_bytes="",
        )
    ]


async def _send_form_notification(
    notification_data: FormNotificationRequest,
    mail_profile: str = DEFAULT_MAIL_PROFILE,
) -> FormNotificationResponse:
    to_emails, cc_emails, error_response = _form_notification_recipients(notification_data)
    if error_response:
        return error_response

    sender_email = getattr(settings, "BOT_EMAIL", None)
    if not sender_email:
        return FormNotificationResponse(
            success=False,
            error_message="No sender email configured (BOT_EMAIL)",
        )

    success, message_id, error_message = await send_outlook_email(
        send_as_email=sender_email,
        to_emails=to_emails,
        subject=notification_data.subject,
        body=generate_form_notification_html(notification_data),
        cc_emails=cc_emails,
        attachments=_form_notification_attachments(notification_data),
        mail_profile=mail_profile,
    )
    if success:
        return FormNotificationResponse(
            success=True,
            message_id=message_id,
        )
    return FormNotificationResponse(
        success=False,
        error_message=error_message,
    )


def get_action_color(action_type: str) -> str:
    """Get color for action type."""
    colors = {
        "approved": "#28a745",
        "rejected": "#dc3545",
        "submitted": "#17a2b8",
        "pending": "#ffc107",
    }
    return colors.get(action_type.lower(), "#6c757d")


def get_action_icon(action_type: str) -> str:
    """Get icon URL or emoji for action type."""
    icons = {
        "approved": "✅",
        "rejected": "❌",
        "submitted": "📤",
        "pending": "⏳",
    }
    return icons.get(action_type.lower(), "📧")


def generate_form_notification_html(
    notification_data: FormNotificationRequest,
) -> str:
    """Generate HTML email template for form notification."""
    action_type = notification_data.action_type.lower()
    color = get_action_color(action_type)
    icon = get_action_icon(action_type)

    performed_by_name = notification_data.performed_by.name
    performed_by_email = notification_data.performed_by.email

    getattr(settings, "SUPPORT_EMAIL", "info@primefire.us")
    getattr(settings, "APP_URL", "https://primefireapp-cgh0c9ace5haapcc.mexicocentral-01.azurewebsites.net")

    notification_fields_html = ""
    if notification_data.notification_fields:
        fields_rows = ""
        for field in notification_data.notification_fields:
            label = field.get("label", "")
            value = field.get("value", "")
            fields_rows += f"""
                <tr>
                    <td style="background-color: #F2F2F2; font-weight: bold; color: #333; width: 30%; padding: 8px; border-bottom: 1px solid #e1e1e1;">
                        {label}
                    </td>
                    <td style="background-color: #ffffff; color: #666; padding: 8px; border-bottom: 1px solid #e1e1e1;">
                        {value}
                    </td>
                </tr>
            """

        notification_fields_html = f"""
            <tr>
                <td style="padding: 20px 40px;">
                    <table width="100%" cellpadding="0" cellspacing="0"
                           style="background-color: #f8f9fa; border: 1px solid #e1e1e1; border-radius: 6px;">
                        {fields_rows}
                    </table>
                </td>
            </tr>
        """

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{notification_data.subject}</title>
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

                    <!-- Header with colored banner -->
                    <tr>
                        <td style="background-color: {color}; padding: 20px; text-align: center;">
                            <div style="font-size: 48px; color: #ffffff; margin-bottom: 10px;">
                                {icon}
                            </div>
                        </td>
                    </tr>

                    <!-- Form title -->
                    <tr>
                        <td style="padding: 40px 40px 20px;">
                            <h1 style="margin: 0; color: #333; font-size: 24px; font-weight: bold;">
                                {notification_data.title}
                            </h1>
                            {f'<p style="margin: 10px 0 0; color: #666; font-size: 16px;">{notification_data.sub_title}</p>' if notification_data.sub_title else ""}
                        </td>
                    </tr>

                    <!-- Performed by information -->
                    <tr>
                        <td style="padding: 0 40px 20px;">
                            <p style="margin: 0; color: #666; font-size: 14px;">
                                <strong>Performed by:</strong> {performed_by_name} ({performed_by_email})
                            </p>
                            <p style="margin: 5px 0 0; color: #666; font-size: 14px;">
                                <strong>Action:</strong> <span style="text-transform: capitalize;">{action_type}</span>
                            </p>
                        </td>
                    </tr>

                    {notification_fields_html}

                    <!-- Message body -->
                    <tr>
                        <td style="padding: 20px 40px;">
                            <p style="margin: 0; color: #333; font-size: 16px; line-height: 1.6;">
                                {notification_data.message_body}
                            </p>
                        </td>
                    </tr>

                    <!-- Action button -->
                    <tr>
                        <td style="padding: 30px 40px; text-align: center;">
                            <a href="{notification_data.submission_url}"
                               target="_blank"
                               style="display: inline-block; padding: 12px 30px; background-color: #000000;
                                      color: #ffffff; text-decoration: none; border-radius: 4px; font-size: 14px; font-weight: bold;">
                                View in App
                            </a>
                        </td>
                    </tr>

                    <!-- Footer -->

                    <!-- Footer links -->

                </table>
            </td>
        </tr>
    </table>
</body>
</html>
    """

    return html.strip()


async def send_form_notification(
    notification_data: FormNotificationRequest,
    mail_profile: str = DEFAULT_MAIL_PROFILE,
) -> FormNotificationResponse:
    """
    Send form notification email.

    Returns:
        FormNotificationResponse with success status and message_id or error_message
    """
    try:
        return await _send_form_notification(notification_data, mail_profile)
    except Exception as e:
        return FormNotificationResponse(
            success=False,
            error_message=f"Error sending form notification: {e!s}",
        )
