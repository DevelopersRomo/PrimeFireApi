"""Schemas for notification API endpoints."""

import re
from pydantic import AnyHttpUrl, BaseModel, EmailStr, Field, field_validator
from typing import Optional, Literal
from services.notifications.schemas import (
    NotificationField,
    TimeOffNotificationData,
    TicketNotificationData,
    TicketMessageNotificationData,
    UserApprovalNotificationData,
    FormNotificationRequest,
)


PHONE_REGEX = re.compile(r"^\+?[0-9()\-\.\s]{7,25}$")
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


class ContactPrimeFireField(BaseModel):
    """Dynamic field for contact-primefire template."""

    key: str = Field(min_length=1, max_length=100)
    label: str = Field(min_length=1, max_length=150)
    type: Literal["text", "email", "phone", "url", "number", "textarea"] = "text"
    value: str = Field(default="", max_length=4000)

    @field_validator("key", "label", "value", mode="before")
    @classmethod
    def strip_string_values(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("value")
    @classmethod
    def validate_value_by_type(cls, value: str, info):
        field_type = info.data.get("type", "text")
        if not value:
            return value

        if field_type == "email":
            if not EMAIL_REGEX.match(value):
                raise ValueError("Invalid email format")
        elif field_type == "phone":
            digits_count = len(re.sub(r"\D", "", value))
            if not PHONE_REGEX.match(value) or digits_count < 7:
                raise ValueError("Invalid phone format")
        elif field_type == "url":
            if not (value.startswith("http://") or value.startswith("https://")):
                raise ValueError("URL must start with http:// or https://")

        return value


class ContactPrimeFireRequest(BaseModel):
    """Request body for /notifications/send/contact-primefire."""

    # Required fields
    name: str = Field(min_length=1, max_length=150)
    email: EmailStr
    phone: str = Field(min_length=7, max_length=30)

    # Optional fields
    to_email: Optional[EmailStr] = None
    cc_email: Optional[EmailStr] = None
    logo_url: Optional[AnyHttpUrl] = None
    title: Optional[str] = Field(default=None, max_length=180)
    subtitle: Optional[str] = Field(default=None, max_length=300)
    company: Optional[str] = Field(default=None, max_length=150)
    industry: Optional[str] = Field(default=None, max_length=120)
    service: Optional[str] = Field(default=None, max_length=120)
    fields: list[ContactPrimeFireField] = Field(default_factory=list)
    note: Optional[str] = Field(default=None, max_length=4000)

    @field_validator("title", "subtitle", "name", "company", "industry", "service", "note", "phone", mode="before")
    @classmethod
    def strip_optional_strings(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str):
        digits_count = len(re.sub(r"\D", "", value))
        if not PHONE_REGEX.match(value) or digits_count < 7:
            raise ValueError("Invalid phone format")
        return value


class ContactPrimeFireResponse(BaseModel):
    """Response for /notifications/send/contact-primefire."""

    success: bool
    status: str
    message: str
    message_id: Optional[str] = None


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

