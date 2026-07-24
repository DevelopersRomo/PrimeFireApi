from datetime import datetime

from pydantic import BaseModel, Field


class EmailTemplateBase(BaseModel):
    subject: str = Field(max_length=300)
    title: str = Field(max_length=300)
    message_body: str
    footer: str | None = None
    header_color: str | None = None
    is_active: bool = True


class EmailTemplateUpdate(BaseModel):
    subject: str | None = None
    title: str | None = None
    message_body: str | None = None
    footer: str | None = None
    header_color: str | None = None
    is_active: bool | None = None


class EmailDefaultRead(EmailTemplateBase):
    default_id: int
    tenant_id: int
    created_at: datetime
    updated_at: datetime
    logo_path: str | None = None


class EmailCustomerTemplateCreate(EmailTemplateBase):
    customer_id: int


class EmailCustomerTemplateRead(EmailTemplateBase):
    template_id: int
    tenant_id: int
    customer_id: int
    created_at: datetime
    updated_at: datetime
    logo_path: str | None = None
