from datetime import datetime

from sqlmodel import Field, SQLModel


class ITEmailDefault(SQLModel, table=True):
    """Tenant-wide default email template for IT quotations."""

    __tablename__ = "email_defaults"
    __table_args__ = {"schema": "it"}

    default_id: int | None = Field(default=None, primary_key=True, index=True)
    tenant_id: int = Field(index=True)
    subject: str = Field(max_length=300)
    title: str = Field(max_length=300)
    message_body: str
    footer: str | None = Field(default=None, max_length=1000)
    header_color: str | None = Field(default=None, max_length=20)
    logo_path: str | None = Field(default=None, max_length=1000)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ITEmailCustomerTemplate(SQLModel, table=True):
    """Per-customer email template override for IT quotations."""

    __tablename__ = "email_customer_templates"
    __table_args__ = {"schema": "it"}

    template_id: int | None = Field(default=None, primary_key=True, index=True)
    tenant_id: int = Field(index=True)
    customer_id: int = Field(index=True)
    subject: str = Field(max_length=300)
    title: str = Field(max_length=300)
    message_body: str
    footer: str | None = Field(default=None, max_length=1000)
    header_color: str | None = Field(default=None, max_length=20)
    logo_path: str | None = Field(default=None, max_length=1000)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
