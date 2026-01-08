"""Unified notification system with dynamic templates.

IMPORTANT: All notifications are sent using BOT_EMAIL as the sender (orchestrator).
Even though actions are performed by specific users, the email always comes from BOT_EMAIL.
This ensures consistent email delivery and proper authentication with Microsoft Graph API.
"""

from typing import Optional
from services.notifications.email_functions import send_outlook_email, parse_email_list
from services.notifications.teams_functions import send_teams_notification
from services.notifications.schemas import (
    NotificationResponse,
    NotificationField,
    TimeOffNotificationData,
    TicketNotificationData,
    TicketMessageNotificationData,
    UserApprovalNotificationData,
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
        "created": "#007bff",
        "commented": "#6f42c1",
        "user_approved": "#28a745",
    }
    return colors.get(action_type.lower(), "#6c757d")


def get_action_icon(action_type: str) -> str:
    """Get icon emoji for action type."""
    icons = {
        "approved": "✅",
        "rejected": "❌",
        "submitted": "📤",
        "pending": "⏳",
        "created": "🎫",
        "commented": "💬",
        "user_approved": "👤",
    }
    return icons.get(action_type.lower(), "📧")


def format_absence_type(absence_type: str) -> str:
    """Format absence type for display."""
    return absence_type.replace("_", " ").title()


def generate_notification_html(
    title: str,
    sub_title: Optional[str] = None,
    action_type: str = "info",
    message_body: str = "",
    performed_by_name: Optional[str] = None,
    performed_by_email: Optional[str] = None,
    fields: Optional[list[NotificationField]] = None,
    action_url: Optional[str] = None,
    action_text: str = "View Details",
) -> str:
    """Generate unified HTML email template for notifications."""
    color = get_action_color(action_type)
    icon = get_action_icon(action_type)
    
    support_email = getattr(settings, "SUPPORT_EMAIL", "info@primefire.us")
    app_url = getattr(settings, "APP_URL", "https://primefireapp-cgh0c9ace5haapcc.mexicocentral-01.azurewebsites.net")

    performed_by_html = ""
    if performed_by_name:
        performed_by_display = performed_by_name
        if performed_by_email:
            performed_by_display += f" ({performed_by_email})"
        performed_by_html = f"""
            <tr>
                <td style="padding: 0 40px 20px;">
                    <p style="margin: 0; color: #666; font-size: 14px;">
                        <strong>Performed by:</strong> {performed_by_display}
                    </p>
                </td>
            </tr>
        """

    fields_html = ""
    if fields:
        fields_rows = ""
        for field in fields:
            fields_rows += f"""
                <tr>
                    <td style="background-color: #F2F2F2; font-weight: bold; color: #333; width: 30%; padding: 8px; border-bottom: 1px solid #e1e1e1;">
                        {field.label}
                    </td>
                    <td style="background-color: #ffffff; color: #666; padding: 8px; border-bottom: 1px solid #e1e1e1;">
                        {field.value}
                    </td>
                </tr>
            """

        fields_html = f"""
            <tr>
                <td style="padding: 20px 40px;">
                    <table width="100%" cellpadding="0" cellspacing="0" 
                           style="background-color: #f8f9fa; border: 1px solid #e1e1e1; border-radius: 6px;">
                        {fields_rows}
                    </table>
                </td>
            </tr>
        """

    action_button_html = ""
    if action_url:
        action_button_html = f"""
            <tr>
                <td style="padding: 30px 40px; text-align: center;">
                    <a href="{action_url}" 
                       target="_blank"
                       style="display: inline-block; padding: 12px 30px; background-color: #000000; 
                              color: #ffffff; text-decoration: none; border-radius: 4px; font-size: 14px; font-weight: bold;">
                        {action_text}
                    </a>
                </td>
            </tr>
        """

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
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
                    
                    <!-- Title -->
                    <tr>
                        <td style="padding: 40px 40px 20px;">
                            <h1 style="margin: 0; color: #333; font-size: 24px; font-weight: bold;">
                                {title}
                            </h1>
                            {f'<p style="margin: 10px 0 0; color: #666; font-size: 16px;">{sub_title}</p>' if sub_title else ''}
                        </td>
                    </tr>
                    
                    {performed_by_html}
                    
                    {fields_html}
                    
                    <!-- Message body -->
                    {f'''
                    <tr>
                        <td style="padding: 20px 40px;">
                            <p style="margin: 0; color: #333; font-size: 16px; line-height: 1.6;">
                                {message_body}
                            </p>
                        </td>
                    </tr>
                    ''' if message_body else ''}
                    
                    {action_button_html}
                    
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


async def send_time_off_notification(
    notification_data: TimeOffNotificationData,
    action_type: str,
    to_email: str,
    cc_email: Optional[str] = None,
) -> NotificationResponse:
    """Send time off notification (approved/rejected)."""
    try:
        absence_type_display = format_absence_type(notification_data.absence_type)
        
        if action_type == "approved":
            title = f"Time Off Request Approved - {absence_type_display.title()}"
            message_body = f"Your {absence_type_display.lower()} request has been approved."
        elif action_type == "rejected":
            title = f"Time Off Request Rejected - {absence_type_display.title()}"
            message_body = f"Your {absence_type_display.lower()} request has been rejected."
        elif action_type == "submitted":
            title = f"New Time Off Request - {absence_type_display.title()}"
            message_body = f"A new {absence_type_display.lower()} request has been submitted for your review."
        else:
            title = f"Time Off Request - {absence_type_display.title()}"
            message_body = "Your time off request status has been updated."

        fields = [
            NotificationField(label="Request ID", value=f"#{notification_data.request_id}"),
            NotificationField(label="Type", value=absence_type_display),
            NotificationField(label="Start Date", value=notification_data.start_date),
            NotificationField(label="End Date", value=notification_data.end_date),
            NotificationField(label="Total Days", value=notification_data.total_days),
        ]

        if notification_data.total_hours:
            fields.append(NotificationField(label="Total Hours", value=notification_data.total_hours))

        if notification_data.reason:
            fields.append(NotificationField(label="Reason", value=notification_data.reason))

        if notification_data.review_notes:
            fields.append(NotificationField(label="Review Notes", value=notification_data.review_notes))

        html_body = generate_notification_html(
            title=title,
            sub_title=f"Request #{notification_data.request_id}",
            action_type=action_type,
            message_body=message_body,
            performed_by_name=notification_data.reviewed_by_name,
            performed_by_email=notification_data.reviewed_by_email,
            fields=fields,
            action_url=notification_data.action_url,
            action_text="View Request",
        )

        to_emails = parse_email_list(to_email)
        cc_emails = parse_email_list(cc_email) if cc_email else None

        sender_email = getattr(settings, "BOT_EMAIL", None)
        if not sender_email:
            return NotificationResponse(
                success=False,
                error_message="No sender email configured (BOT_EMAIL)",
            )

        subject = title
        success, message_id, error_message = await send_outlook_email(
            send_as_email=sender_email,
            to_emails=to_emails,
            subject=subject,
            body=html_body,
            cc_emails=cc_emails,
        )

        if success:
            return NotificationResponse(success=True, message_id=message_id)
        else:
            return NotificationResponse(success=False, error_message=error_message)

    except Exception as e:
        return NotificationResponse(
            success=False,
            error_message=f"Error sending time off notification: {str(e)}",
        )


async def send_ticket_assigned_notification(
    notification_data: TicketNotificationData,
    to_email: str,
    cc_email: Optional[str] = None,
) -> NotificationResponse:
    """Send notification when a ticket is assigned to someone."""
    try:
        title = "Ticket Assigned to You"
        message_body = f"A ticket has been assigned to you: {notification_data.title}"

        fields = [
            NotificationField(label="Ticket ID", value=f"#{notification_data.ticket_id}"),
            NotificationField(label="Title", value=notification_data.title),
            NotificationField(label="Status", value=notification_data.status.title()),
            NotificationField(label="Priority", value=notification_data.priority.title()),
            NotificationField(label="Created By", value=notification_data.created_by_name),
        ]

        if notification_data.description:
            fields.append(NotificationField(label="Description", value=notification_data.description[:200] + ("..." if len(notification_data.description) > 200 else "")))

        html_body = generate_notification_html(
            title=title,
            sub_title=f"Ticket #{notification_data.ticket_id}",
            action_type="created",
            message_body=message_body,
            performed_by_name=notification_data.created_by_name,
            performed_by_email=notification_data.created_by_email,
            fields=fields,
            action_url=notification_data.action_url,
            action_text="View Ticket",
        )

        to_emails = parse_email_list(to_email)
        cc_emails = parse_email_list(cc_email) if cc_email else None

        sender_email = getattr(settings, "BOT_EMAIL", None)
        if not sender_email:
            return NotificationResponse(
                success=False,
                error_message="No sender email configured (BOT_EMAIL)",
            )

        subject = f"Ticket Assigned: {notification_data.title}"
        success, message_id, error_message = await send_outlook_email(
            send_as_email=sender_email,
            to_emails=to_emails,
            subject=subject,
            body=html_body,
            cc_emails=cc_emails,
        )

        if success:
            return NotificationResponse(success=True, message_id=message_id)
        else:
            return NotificationResponse(success=False, error_message=error_message)

    except Exception as e:
        return NotificationResponse(
            success=False,
            error_message=f"Error sending ticket assigned notification: {str(e)}",
        )


async def send_ticket_created_notification(
    notification_data: TicketNotificationData,
    to_email: str,
    cc_email: Optional[str] = None,
) -> NotificationResponse:
    """Send notification when a ticket is created."""
    try:
        title = "New Ticket Created"
        message_body = f"A new ticket has been created: {notification_data.title}"

        fields = [
            NotificationField(label="Ticket ID", value=f"#{notification_data.ticket_id}"),
            NotificationField(label="Title", value=notification_data.title),
            NotificationField(label="Status", value=notification_data.status.title()),
            NotificationField(label="Priority", value=notification_data.priority.title()),
            NotificationField(label="Created By", value=notification_data.created_by_name),
        ]

        if notification_data.description:
            fields.append(NotificationField(label="Description", value=notification_data.description[:200] + ("..." if len(notification_data.description) > 200 else "")))

        if notification_data.assigned_to_name:
            fields.append(NotificationField(label="Assigned To", value=notification_data.assigned_to_name))

        html_body = generate_notification_html(
            title=title,
            sub_title=f"Ticket #{notification_data.ticket_id}",
            action_type="created",
            message_body=message_body,
            performed_by_name=notification_data.created_by_name,
            performed_by_email=notification_data.created_by_email,
            fields=fields,
            action_url=notification_data.action_url,
            action_text="View Ticket",
        )

        to_emails = parse_email_list(to_email)
        cc_emails = parse_email_list(cc_email) if cc_email else None

        sender_email = getattr(settings, "BOT_EMAIL", None)
        if not sender_email:
            return NotificationResponse(
                success=False,
                error_message="No sender email configured (BOT_EMAIL)",
            )

        subject = f"New Ticket: {notification_data.title}"
        success, message_id, error_message = await send_outlook_email(
            send_as_email=sender_email,
            to_emails=to_emails,
            subject=subject,
            body=html_body,
            cc_emails=cc_emails,
        )

        if success:
            return NotificationResponse(success=True, message_id=message_id)
        else:
            return NotificationResponse(success=False, error_message=error_message)

    except Exception as e:
        return NotificationResponse(
            success=False,
            error_message=f"Error sending ticket created notification: {str(e)}",
        )


async def send_ticket_message_notification(
    notification_data: TicketMessageNotificationData,
    to_email: str,
    cc_email: Optional[str] = None,
) -> NotificationResponse:
    """Send notification when a ticket message is posted."""
    try:
        title = "New Comment on Ticket"
        message_body = f"{notification_data.commenter_name} commented on ticket: {notification_data.ticket_title}"

        message_preview = notification_data.message_text[:200] + ("..." if len(notification_data.message_text) > 200 else "")

        fields = [
            NotificationField(label="Ticket ID", value=f"#{notification_data.ticket_id}"),
            NotificationField(label="Ticket Title", value=notification_data.ticket_title),
            NotificationField(label="Comment", value=message_preview),
        ]

        html_body = generate_notification_html(
            title=title,
            sub_title=f"Ticket #{notification_data.ticket_id}",
            action_type="commented",
            message_body=message_body,
            performed_by_name=notification_data.commenter_name,
            performed_by_email=notification_data.commenter_email,
            fields=fields,
            action_url=notification_data.action_url,
            action_text="View Ticket",
        )

        to_emails = parse_email_list(to_email)
        cc_emails = parse_email_list(cc_email) if cc_email else None

        sender_email = getattr(settings, "BOT_EMAIL", None)
        if not sender_email:
            return NotificationResponse(
                success=False,
                error_message="No sender email configured (BOT_EMAIL)",
            )

        subject = f"New Comment on Ticket #{notification_data.ticket_id}: {notification_data.ticket_title}"
        success, message_id, error_message = await send_outlook_email(
            send_as_email=sender_email,
            to_emails=to_emails,
            subject=subject,
            body=html_body,
            cc_emails=cc_emails,
        )

        if success:
            return NotificationResponse(success=True, message_id=message_id)
        else:
            return NotificationResponse(success=False, error_message=error_message)

    except Exception as e:
        return NotificationResponse(
            success=False,
            error_message=f"Error sending ticket message notification: {str(e)}",
        )


async def send_user_approval_notification(
    notification_data: UserApprovalNotificationData,
    to_email: str,
    cc_email: Optional[str] = None,
) -> NotificationResponse:
    """Send notification when a user is approved and ready to use."""
    try:
        title = "Account Approved and Ready"
        message_body = f"Your account has been approved and is now ready to use."

        fields = [
            NotificationField(label="User ID", value=f"#{notification_data.user_id}"),
            NotificationField(label="Name", value=notification_data.user_name),
            NotificationField(label="Email", value=notification_data.user_email),
        ]

        if notification_data.approved_by_name:
            fields.append(NotificationField(label="Approved By", value=notification_data.approved_by_name))

        html_body = generate_notification_html(
            title=title,
            sub_title=f"Welcome, {notification_data.user_name}!",
            action_type="user_approved",
            message_body=message_body,
            performed_by_name=notification_data.approved_by_name,
            performed_by_email=notification_data.approved_by_email,
            fields=fields,
            action_url=notification_data.action_url,
            action_text="Access Your Account",
        )

        to_emails = parse_email_list(to_email)
        cc_emails = parse_email_list(cc_email) if cc_email else None

        sender_email = getattr(settings, "BOT_EMAIL", None)
        if not sender_email:
            return NotificationResponse(
                success=False,
                error_message="No sender email configured (BOT_EMAIL)",
            )

        subject = "Account Approved - Ready to Use"
        success, message_id, error_message = await send_outlook_email(
            send_as_email=sender_email,
            to_emails=to_emails,
            subject=subject,
            body=html_body,
            cc_emails=cc_emails,
        )

        if success:
            return NotificationResponse(success=True, message_id=message_id)
        else:
            return NotificationResponse(success=False, error_message=error_message)

    except Exception as e:
        return NotificationResponse(
            success=False,
            error_message=f"Error sending user approval notification: {str(e)}",
        )


# Helper functions for easy integration with API endpoints

async def notify_time_off_approved(
    request_id: int,
    employee_id: int,
    employee_name: str,
    employee_email: str,
    absence_type: str,
    start_date: str,
    end_date: str,
    total_days: str,
    total_hours: Optional[str] = None,
    reason: Optional[str] = None,
    reviewed_by_name: Optional[str] = None,
    reviewed_by_email: Optional[str] = None,
    review_notes: Optional[str] = None,
    action_url: Optional[str] = None,
) -> NotificationResponse:
    """Helper function to send time off approved notification."""
    notification_data = TimeOffNotificationData(
        request_id=request_id,
        employee_id=employee_id,
        employee_name=employee_name,
        employee_email=employee_email,
        absence_type=absence_type,
        start_date=start_date,
        end_date=end_date,
        total_days=total_days,
        total_hours=total_hours,
        reason=reason,
        reviewed_by_name=reviewed_by_name,
        reviewed_by_email=reviewed_by_email,
        review_notes=review_notes,
        action_url=action_url,
    )
    return await send_time_off_notification(
        notification_data=notification_data,
        action_type="approved",
        to_email=employee_email,
    )


async def notify_time_off_rejected(
    request_id: int,
    employee_id: int,
    employee_name: str,
    employee_email: str,
    absence_type: str,
    start_date: str,
    end_date: str,
    total_days: str,
    total_hours: Optional[str] = None,
    reason: Optional[str] = None,
    reviewed_by_name: Optional[str] = None,
    reviewed_by_email: Optional[str] = None,
    review_notes: Optional[str] = None,
    action_url: Optional[str] = None,
) -> NotificationResponse:
    """Helper function to send time off rejected notification."""
    notification_data = TimeOffNotificationData(
        request_id=request_id,
        employee_id=employee_id,
        employee_name=employee_name,
        employee_email=employee_email,
        absence_type=absence_type,
        start_date=start_date,
        end_date=end_date,
        total_days=total_days,
        total_hours=total_hours,
        reason=reason,
        reviewed_by_name=reviewed_by_name,
        reviewed_by_email=reviewed_by_email,
        review_notes=review_notes,
        action_url=action_url,
    )
    return await send_time_off_notification(
        notification_data=notification_data,
        action_type="rejected",
        to_email=employee_email,
    )


async def notify_time_off_submitted(
    request_id: int,
    employee_id: int,
    employee_name: str,
    employee_email: str,
    absence_type: str,
    start_date: str,
    end_date: str,
    total_days: str,
    to_email: str,
    total_hours: Optional[str] = None,
    reason: Optional[str] = None,
    action_url: Optional[str] = None,
) -> NotificationResponse:
    """Helper function to send time off submitted notification (to manager)."""
    notification_data = TimeOffNotificationData(
        request_id=request_id,
        employee_id=employee_id,
        employee_name=employee_name,
        employee_email=employee_email,
        absence_type=absence_type,
        start_date=start_date,
        end_date=end_date,
        total_days=total_days,
        total_hours=total_hours,
        reason=reason,
        reviewed_by_name=employee_name,  # The requester "performed" the submission
        reviewed_by_email=employee_email,
        action_url=action_url,
    )
    return await send_time_off_notification(
        notification_data=notification_data,
        action_type="submitted",
        to_email=to_email,
    )


async def notify_ticket_created(
    ticket_id: int,
    title: str,
    description: Optional[str] = None,
    status: str = "todo",
    priority: str = "normal",
    created_by_name: str = "",
    created_by_email: str = "",
    assigned_to_name: Optional[str] = None,
    assigned_to_email: Optional[str] = None,
    action_url: Optional[str] = None,
    notify_assignee: bool = True,
) -> tuple[NotificationResponse, Optional[NotificationResponse]]:
    """Helper function to send ticket created notifications.
    
    Returns:
        (creator_notification, assignee_notification)
    """
    notification_data = TicketNotificationData(
        ticket_id=ticket_id,
        title=title,
        description=description,
        status=status,
        priority=priority,
        created_by_name=created_by_name,
        created_by_email=created_by_email,
        assigned_to_name=assigned_to_name,
        assigned_to_email=assigned_to_email,
        action_url=action_url,
    )
    
    creator_notification = await send_ticket_created_notification(
        notification_data=notification_data,
        to_email=created_by_email,
    )
    
    assignee_notification = None
    if notify_assignee and assigned_to_email and assigned_to_email != created_by_email:
        assignee_notification = await send_ticket_created_notification(
            notification_data=notification_data,
            to_email=assigned_to_email,
        )
    
    return creator_notification, assignee_notification


async def notify_ticket_message(
    ticket_id: int,
    ticket_title: str,
    message_id: int,
    message_text: str,
    commenter_id: int,
    commenter_name: str,
    commenter_email: str,
    ticket_creator_id: int,
    ticket_creator_email: str,
    ticket_assigned_to_id: Optional[int] = None,
    ticket_assigned_to_email: Optional[str] = None,
    action_url: Optional[str] = None,
) -> tuple[Optional[NotificationResponse], Optional[NotificationResponse]]:
    """Helper function to send ticket message notifications.
    
    Logic:
    - In LOCAL: Always notify both creator and assignee (skip validation)
    - In PROD: 
      - If commenter is creator, notify assignee
      - If commenter is assignee, notify creator
      - If commenter is neither, notify both creator and assignee
    
    Returns:
        (creator_notification, assignee_notification)
    """
    notification_data = TicketMessageNotificationData(
        ticket_id=ticket_id,
        ticket_title=ticket_title,
        message_id=message_id,
        message_text=message_text,
        commenter_name=commenter_name,
        commenter_email=commenter_email,
        action_url=action_url,
    )
    
    creator_notification = None
    assignee_notification = None
    
    environment = settings.ENVIRONMENT.value if hasattr(settings.ENVIRONMENT, "value") else str(settings.ENVIRONMENT)
    is_local = environment == "local"
    
    if is_local:
        if ticket_creator_email:
            creator_notification = await send_ticket_message_notification(
                notification_data=notification_data,
                to_email=ticket_creator_email,
            )
        if ticket_assigned_to_email:
            assignee_notification = await send_ticket_message_notification(
                notification_data=notification_data,
                to_email=ticket_assigned_to_email,
            )
    else:
        is_commenter_creator = commenter_id == ticket_creator_id
        is_commenter_assignee = ticket_assigned_to_id and commenter_id == ticket_assigned_to_id
        
        if is_commenter_creator:
            if ticket_assigned_to_email and ticket_assigned_to_email != commenter_email:
                assignee_notification = await send_ticket_message_notification(
                    notification_data=notification_data,
                    to_email=ticket_assigned_to_email,
                )
        elif is_commenter_assignee:
            if ticket_creator_email and ticket_creator_email != commenter_email:
                creator_notification = await send_ticket_message_notification(
                    notification_data=notification_data,
                    to_email=ticket_creator_email,
                )
        else:
            if ticket_creator_email and ticket_creator_email != commenter_email:
                creator_notification = await send_ticket_message_notification(
                    notification_data=notification_data,
                    to_email=ticket_creator_email,
                )
            if ticket_assigned_to_email and ticket_assigned_to_email != commenter_email:
                assignee_notification = await send_ticket_message_notification(
                    notification_data=notification_data,
                    to_email=ticket_assigned_to_email,
                )
    
    return creator_notification, assignee_notification


async def notify_user_approved(
    user_id: int,
    user_name: str,
    user_email: str,
    approved_by_name: Optional[str] = None,
    approved_by_email: Optional[str] = None,
    action_url: Optional[str] = None,
) -> NotificationResponse:
    """Helper function to send user approval notification."""
    notification_data = UserApprovalNotificationData(
        user_id=user_id,
        user_name=user_name,
        user_email=user_email,
        approved_by_name=approved_by_name,
        approved_by_email=approved_by_email,
        action_url=action_url,
    )
    return await send_user_approval_notification(
        notification_data=notification_data,
        to_email=user_email,
    )


async def send_custom_notification(
    title: str,
    message_body: str,
    to_email: str,
    cc_email: Optional[str] = None,
    action_type: str = "info",
    sub_title: Optional[str] = None,
    performed_by_name: Optional[str] = None,
    performed_by_email: Optional[str] = None,
    fields: Optional[list[NotificationField]] = None,
    action_url: Optional[str] = None,
    action_text: str = "View Details",
) -> NotificationResponse:
    """Send custom notification with basic parameters.
    
    Args:
        title: Email title/subject
        message_body: Main message content
        to_email: Recipient email address
        cc_email: Optional CC email address
        action_type: Type of action (approved, rejected, created, info, etc.)
        sub_title: Optional subtitle
        performed_by_name: Optional name of person who performed the action
        performed_by_email: Optional email of person who performed the action
        fields: Optional list of fields to display
        action_url: Optional URL for action button
        action_text: Text for action button
        
    Returns:
        NotificationResponse with success status
    """
    try:
        html_body = generate_notification_html(
            title=title,
            sub_title=sub_title,
            action_type=action_type,
            message_body=message_body,
            performed_by_name=performed_by_name,
            performed_by_email=performed_by_email,
            fields=fields,
            action_url=action_url,
            action_text=action_text,
        )

        to_emails = parse_email_list(to_email)
        cc_emails = parse_email_list(cc_email) if cc_email else None

        sender_email = getattr(settings, "BOT_EMAIL", None)
        if not sender_email:
            return NotificationResponse(
                success=False,
                error_message="No sender email configured (BOT_EMAIL)",
            )

        subject = title
        success, message_id, error_message = await send_outlook_email(
            send_as_email=sender_email,
            to_emails=to_emails,
            subject=subject,
            body=html_body,
            cc_emails=cc_emails,
        )

        if success:
            return NotificationResponse(success=True, message_id=message_id)
        else:
            return NotificationResponse(success=False, error_message=error_message)

    except Exception as e:
        return NotificationResponse(
            success=False,
            error_message=f"Error sending custom notification: {str(e)}",
        )


async def notify_teams(
    recipient_email: str,
    title: str,
    message_body: str,
    action_url: Optional[str] = None,
    action_text: str = "View Details",
) -> NotificationResponse:
    """
    Send a Teams notification to a user.
    
    Always uses BOT_EMAIL as sender (orchestrator).
    
    Args:
        recipient_email: Email address of the recipient
        title: Notification title
        message_body: Main message content
        action_url: Optional URL for action button
        action_text: Text for action button
        
    Returns:
        NotificationResponse with success status
    """
    return await send_teams_notification(
        recipient_email=recipient_email,
        title=title,
        message_body=message_body,
        action_url=action_url,
        action_text=action_text,
    )

