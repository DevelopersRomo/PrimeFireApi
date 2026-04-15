"""Schemas for notification API endpoints."""

import re
from typing import Literal

from pydantic import AnyHttpUrl, BaseModel, EmailStr, Field, field_validator

from services.notifications.schemas import (
    FormNotificationRequest,
    TicketMessageNotificationData,
    TicketNotificationData,
    TimeOffNotificationData,
    UserApprovalNotificationData,
)

PHONE_REGEX = re.compile(r"^\+?[0-9()\-\.\s]{7,25}$")
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


class ContactPrimeFireField(BaseModel):
    """Dynamic field for contact-primefire template."""

    key: str = Field(min_length=1, max_length=100)
    label: str = Field(min_length=1, max_length=150)
    type: Literal["text", "email", "phone", "url", "number", "textarea"] = "text"
    value: str = Field(default="", max_length=4000)

    @classmethod
    @field_validator("key", "label", "value", mode="before")
    @classmethod
    def strip_string_values(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value

    @classmethod
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
        elif field_type == "url" and not (value.startswith(("http://", "https://"))):
            raise ValueError("URL must start with http:// or https://")

        return value


class ContactPrimeFireRequest(BaseModel):
    """Request body for /notifications/send/contact-primefire."""

    # Required fields
    name: str = Field(min_length=1, max_length=150)
    email: EmailStr
    phone: str = Field(min_length=7, max_length=30)
    cf_turnstile_response: str = Field(
        min_length=1,
        max_length=2048,
    )

    # Optional fields
    to_email: EmailStr | None = None
    cc_email: str | None = Field(default=None, max_length=500)
    logo_url: AnyHttpUrl | None = None
    title: str | None = Field(default=None, max_length=180)
    subject: str | None = Field(default=None, max_length=180)
    subtitle: str | None = Field(default=None, max_length=300)
    company: str | None = Field(default=None, max_length=150)
    industry: str | None = Field(default=None, max_length=120)
    service: str | None = Field(default=None, max_length=120)
    website: str | None = Field(default=None, max_length=255)
    fields: list[ContactPrimeFireField] = Field(default_factory=list)
    note: str | None = Field(default=None, max_length=4000)

    @classmethod
    @field_validator(
        "title",
        "subject",
        "subtitle",
        "name",
        "company",
        "industry",
        "service",
        "website",
        "note",
        "phone",
        "cf_turnstile_response",
        mode="before",
    )
    @classmethod
    def strip_optional_strings(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value

    @classmethod
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
    message_id: str | None = None


class CustomNotificationRequest(BaseModel):
    """Custom notification request schema."""

    title: str
    message_body: str
    to_email: str
    cc_email: str | None = None
    action_type: str = "info"
    sub_title: str | None = None
    performed_by_name: str | None = None
    performed_by_email: str | None = None
    fields: list[dict] | None = None
    action_url: str | None = None
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
    custom: CustomNotificationRequest | None = None

    # Time off notifications
    time_off_approved: TimeOffNotificationData | None = None
    time_off_rejected: TimeOffNotificationData | None = None

    # Ticket notifications
    ticket_created: TicketNotificationData | None = None
    ticket_message: TicketMessageNotificationData | None = None

    # User approval
    user_approved: UserApprovalNotificationData | None = None

    # Form notification (backward compatibility)
    form: FormNotificationRequest | None = None

    # Additional fields for ticket_message logic
    ticket_creator_id: int | None = None
    ticket_creator_email: str | None = None
    ticket_assigned_to_id: int | None = None
    ticket_assigned_to_email: str | None = None
    commenter_id: int | None = None

    # For ticket_created
    notify_assignee: bool = True
