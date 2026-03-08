"""Schemas for notification system."""

from pydantic import BaseModel, EmailStr
from typing import Optional


class EmailAttachment(BaseModel):
    """Email attachment schema."""

    name: str
    content_type: str
    content_bytes: str


class TeamsMention(BaseModel):
    """Teams mention schema."""

    id: int
    mention_text: str
    mentioned: "MentionedEntity"


class MentionedEntity(BaseModel):
    """Mentioned entity schema."""

    user: "UserMentioned"


class UserMentioned(BaseModel):
    """User mentioned schema."""

    id: str


class NotificationRequest(BaseModel):
    """Base notification request schema."""

    notification_type: str
    recipients: list[str]
    subject: str
    body: str
    cc_recipients: Optional[list[str]] = None
    bcc_recipients: Optional[list[str]] = None
    sender_email: Optional[str] = None
    team_id: Optional[str] = None
    channel_id: Optional[str] = None
    mentions: Optional[list[TeamsMention]] = None
    attachments: Optional[list[EmailAttachment]] = None
    url: Optional[str] = None


class UserProfile(BaseModel):
    """User profile schema."""

    email: str
    name: str
    user_principal_name: str


class FormData(BaseModel):
    """Form data schema."""

    form_id: str
    submission_id: str
    project_id: str
    project_name: str


class FormNotificationRequest(BaseModel):
    """Form notification request schema (for backward compatibility)."""

    performed_by: UserProfile
    to: str
    cc: Optional[str] = None
    action_type: str
    company_id: Optional[str] = None
    subject: str
    title: str
    sub_title: Optional[str] = None
    message_body: str
    submission_url: Optional[str] = None
    url: Optional[str] = None
    attach_pdf: bool = False
    upload_pdf_to_ifs: bool = False
    pdf_file_name: Optional[str] = None
    form_data: Optional[FormData] = None
    notification_fields: Optional[list[dict]] = None


class DocumentUpload(BaseModel):
    """Document upload schema."""

    document_type: str
    document_number: str
    document_revision: str


class FormNotificationResponse(BaseModel):
    """Form notification response schema."""

    success: bool
    message_id: Optional[str] = None
    error_message: Optional[str] = None


class NotificationResponse(BaseModel):
    """Generic notification response schema."""

    success: bool
    message_id: Optional[str] = None
    error_message: Optional[str] = None


class NotificationField(BaseModel):
    """Field for notification data display."""

    label: str
    value: str


class TimeOffNotificationData(BaseModel):
    """Time off notification data."""

    request_id: int
    employee_id: int
    employee_name: str
    employee_email: str
    absence_type: str
    start_date: str
    end_date: str
    total_days: str
    total_hours: Optional[str] = None
    reason: Optional[str] = None
    reviewed_by_name: Optional[str] = None
    reviewed_by_email: Optional[str] = None
    review_notes: Optional[str] = None
    action_url: Optional[str] = None


class TicketNotificationData(BaseModel):
    """Ticket notification data."""

    ticket_id: int
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    created_by_name: str
    created_by_email: str
    assigned_to_name: Optional[str] = None
    assigned_to_email: Optional[str] = None
    action_url: Optional[str] = None


class TicketMessageNotificationData(BaseModel):
    """Ticket message notification data."""

    ticket_id: int
    ticket_title: str
    message_id: int
    message_text: str
    commenter_name: str
    commenter_email: str
    action_url: Optional[str] = None


class UserApprovalNotificationData(BaseModel):
    """User approval notification data."""

    user_id: int
    user_name: str
    user_email: str
    approved_by_name: Optional[str] = None
    approved_by_email: Optional[str] = None
    action_url: Optional[str] = None


class TimeSheetNotificationData(BaseModel):
    """TimeSheet notification data."""

    employee_id: int
    employee_name: str
    employee_email: str
    notification_type: str  # "regular_hours" o "overtime"
    hours_worked: float
    customer_name: Optional[str] = None
    clock_in_time: Optional[str] = None
    action_url: Optional[str] = None
