"""Schemas for notification system."""

from pydantic import BaseModel


class EmailAttachment(BaseModel):
    """Email attachment schema."""

    name: str
    content_type: str
    content_bytes: str
    content_id: str | None = None
    is_inline: bool = False


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
    cc_recipients: list[str] | None = None
    bcc_recipients: list[str] | None = None
    sender_email: str | None = None
    team_id: str | None = None
    channel_id: str | None = None
    mentions: list[TeamsMention] | None = None
    attachments: list[EmailAttachment] | None = None
    url: str | None = None


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
    cc: str | None = None
    action_type: str
    company_id: str | None = None
    subject: str
    title: str
    sub_title: str | None = None
    message_body: str
    submission_url: str | None = None
    url: str | None = None
    attach_pdf: bool = False
    upload_pdf_to_ifs: bool = False
    pdf_file_name: str | None = None
    form_data: FormData | None = None
    notification_fields: list[dict] | None = None
    # Site URL, matched against tenant_logos.url to pick the sending tenant
    tenant_url: str | None = None
    # Explicit profile key override, wins over whatever tenant_url resolves to
    mail_profile: str | None = None


class DocumentUpload(BaseModel):
    """Document upload schema."""

    document_type: str
    document_number: str
    document_revision: str


class FormNotificationResponse(BaseModel):
    """Form notification response schema."""

    success: bool
    message_id: str | None = None
    error_message: str | None = None


class NotificationResponse(BaseModel):
    """Generic notification response schema."""

    success: bool
    message_id: str | None = None
    error_message: str | None = None


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
    total_hours: str | None = None
    reason: str | None = None
    reviewed_by_name: str | None = None
    reviewed_by_email: str | None = None
    review_notes: str | None = None
    action_url: str | None = None


class TicketNotificationData(BaseModel):
    """Ticket notification data."""

    ticket_id: int
    title: str
    description: str | None = None
    status: str
    priority: str
    created_by_name: str
    created_by_email: str
    assigned_to_name: str | None = None
    assigned_to_email: str | None = None
    action_url: str | None = None


class TicketMessageNotificationData(BaseModel):
    """Ticket message notification data."""

    ticket_id: int
    ticket_title: str
    message_id: int
    message_text: str
    commenter_name: str
    commenter_email: str
    action_url: str | None = None


class UserApprovalNotificationData(BaseModel):
    """User approval notification data."""

    user_id: int
    user_name: str
    user_email: str
    approved_by_name: str | None = None
    approved_by_email: str | None = None
    action_url: str | None = None


class InventoryMovementNotificationData(BaseModel):
    """Inventory movement notification data."""

    movement_id: int
    movement_type: str  # "IN", "OUT", "ADJUSTMENT"
    product_name: str
    product_code: str | None = None
    warehouse_name: str | None = None
    quantity: str
    movement_date: str | None = None
    project: str | None = None
    po_number: str | None = None
    reference_type: str | None = None
    notes: str | None = None
    created_by_name: str | None = None
    action_url: str | None = None


class InventoryApprovalNotificationData(BaseModel):
    """Inventory movement approval notification data."""

    approval_id: int
    movement_type: str  # "OUT", "ADJUSTMENT"
    product_name: str
    product_code: str | None = None
    warehouse_name: str | None = None
    quantity: str
    movement_date: str | None = None
    project: str | None = None
    po_number: str | None = None
    notes: str | None = None
    requested_by_name: str | None = None
    reviewed_by_name: str | None = None
    review_note: str | None = None
    action_url: str | None = None


class TimeSheetNotificationData(BaseModel):
    """TimeSheet notification data."""

    employee_id: int
    employee_name: str
    employee_email: str
    notification_type: str  # "regular_hours" o "overtime"
    hours_worked: float
    customer_name: str | None = None
    clock_in_time: str | None = None
    action_url: str | None = None
