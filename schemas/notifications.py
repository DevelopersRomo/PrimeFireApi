"""Schemas for notification API endpoints."""

from pydantic import BaseModel, EmailStr
from typing import Optional, Literal
from services.notifications.schemas import (
    NotificationField,
    TimeOffNotificationData,
    TicketNotificationData,
    TicketMessageNotificationData,
    UserApprovalNotificationData,
    FormNotificationRequest,
)


class CustomNotificationRequest(BaseModel):
    """Custom notification request schema."""

    title: str
    message_body: str
    to_email: str
    cc_email: Optional[str] = None
    action_type: str = "info"
    sub_title: Optional[str] = None
    performed_by_name: Optional[str] = None
    performed_by_email: Optional[str] = None
    fields: Optional[list[dict]] = None
    action_url: Optional[str] = None
    action_text: str = "View Details"


class NotificationRequestWrapper(BaseModel):
    """Wrapper for different notification types."""

    notification_type: Literal[
        "custom",
        "time_off_approved",
        "time_off_rejected",
        "ticket_created",
        "ticket_message",
        "user_approved",
        "form",
    ]
    
    # Custom notification
    custom: Optional[CustomNotificationRequest] = None
    
    # Time off notifications
    time_off_approved: Optional[TimeOffNotificationData] = None
    time_off_rejected: Optional[TimeOffNotificationData] = None
    
    # Ticket notifications
    ticket_created: Optional[TicketNotificationData] = None
    ticket_message: Optional[TicketMessageNotificationData] = None
    
    # User approval
    user_approved: Optional[UserApprovalNotificationData] = None
    
    # Form notification (backward compatibility)
    form: Optional[FormNotificationRequest] = None
    
    # Additional fields for ticket_message logic
    ticket_creator_id: Optional[int] = None
    ticket_creator_email: Optional[str] = None
    ticket_assigned_to_id: Optional[int] = None
    ticket_assigned_to_email: Optional[str] = None
    commenter_id: Optional[int] = None
    
    # For ticket_created
    notify_assignee: bool = True

