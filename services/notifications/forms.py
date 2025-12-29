"""Form notification functions.

IMPORTANT: All notifications are sent using BOT_EMAIL as the sender (orchestrator).
Even though actions are performed by specific users, the email always comes from BOT_EMAIL.
"""

import base64
from typing import Optional
from services.notifications.email_functions import (
    send_outlook_email,
    parse_email_list,
)
from services.notifications.schemas import (
    FormNotificationRequest,
    FormNotificationResponse,
    EmailAttachment,
)
from core.config import settings


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
    
    support_email = getattr(settings, "SUPPORT_EMAIL", "info@primefire.us")
    app_url = getattr(settings, "APP_URL", "https://primefireapp-cgh0c9ace5haapcc.mexicocentral-01.azurewebsites.net")

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
                            {f'<p style="margin: 10px 0 0; color: #666; font-size: 16px;">{notification_data.sub_title}</p>' if notification_data.sub_title else ''}
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
                    <tr>
                        <td style="padding: 40px 40px 20px; text-align: center; border-top: 1px solid #bbbbbb;">
                            <p style="margin: 0; color: #5b5b5b; font-size: 14px;">
                                If you have any questions, please email us at
                                <a href="mailto:{support_email}" style="color: #5b5b5b; text-decoration: none;">
                                    {support_email}
                                </a>
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer links -->
                    <tr>
                        <td style="padding: 10px 40px 40px; text-align: center;">
                            <a href="{app_url}" 
                               style="padding: 5px 15px; color: #5b5b5b; text-decoration: none; font-size: 14px;">
                                PrimeFire App
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

    return html.strip()


async def send_form_notification(
    notification_data: FormNotificationRequest,
) -> FormNotificationResponse:
    """
    Send form notification email.

    Returns:
        FormNotificationResponse with success status and message_id or error_message
    """
    try:
        to_emails = parse_email_list(notification_data.to)
        if not to_emails:
            return FormNotificationResponse(
                success=False,
                error_message="No valid recipient emails",
            )

        cc_emails = None
        if notification_data.cc:
            cc_emails = parse_email_list(notification_data.cc)

        html_body = generate_form_notification_html(notification_data)

        attachments = None
        if notification_data.attach_pdf and notification_data.pdf_file_name:
            attachments = [
                EmailAttachment(
                    name=notification_data.pdf_file_name,
                    content_type="application/pdf",
                    content_bytes="",
                )
            ]

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
            body=html_body,
            cc_emails=cc_emails,
            attachments=attachments,
        )

        if success:
            return FormNotificationResponse(
                success=True,
                message_id=message_id,
            )
        else:
            return FormNotificationResponse(
                success=False,
                error_message=error_message,
            )

    except Exception as e:
        return FormNotificationResponse(
            success=False,
            error_message=f"Error sending form notification: {str(e)}",
        )


