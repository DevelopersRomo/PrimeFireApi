from datetime import datetime

from pydantic import BaseModel, Field


class ItPdfTemplateBase(BaseModel):
    name: str = Field(max_length=150)
    template_key: str = Field(max_length=100)
    company_name: str = Field(max_length=200)
    document_title: str | None = None
    logo_url: str | None = None
    primary_color: str | None = None
    secondary_color: str | None = None
    address_text: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    default_footer: str | None = None
    signature_name: str | None = None
    signature_title: str | None = None
    signature_image_url: str | None = None
    is_default: bool = False
    is_active: bool = True


class ItPdfTemplateCreate(ItPdfTemplateBase):
    pass


class ItPdfTemplateUpdate(BaseModel):
    name: str | None = None
    template_key: str | None = None
    company_name: str | None = None
    document_title: str | None = None
    logo_url: str | None = None
    primary_color: str | None = None
    secondary_color: str | None = None
    address_text: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    default_footer: str | None = None
    signature_name: str | None = None
    signature_title: str | None = None
    signature_image_url: str | None = None
    is_default: bool | None = None
    is_active: bool | None = None


class ItPdfTemplateRead(ItPdfTemplateBase):
    template_id: int
    tenant_id: int
    created_at: datetime
