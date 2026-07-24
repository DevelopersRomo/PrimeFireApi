from datetime import datetime

from sqlmodel import Field, SQLModel


class ITPdfTemplates(SQLModel, table=True):
    __tablename__ = "pdf_templates"
    __table_args__ = {"schema": "it"}

    template_id: int | None = Field(default=None, primary_key=True, index=True)
    tenant_id: int = Field(index=True)
    name: str = Field(max_length=150)
    template_key: str = Field(max_length=100)
    company_name: str = Field(max_length=200)
    document_title: str | None = Field(default=None, max_length=200)
    logo_url: str | None = Field(default=None, max_length=500)
    primary_color: str | None = Field(default=None, max_length=20)
    secondary_color: str | None = Field(default=None, max_length=20)
    address_text: str | None = Field(default=None, max_length=500)
    phone: str | None = Field(default=None, max_length=50)
    email: str | None = Field(default=None, max_length=150)
    website: str | None = Field(default=None, max_length=200)
    default_footer: str | None = Field(default=None, max_length=1000)
    signature_name: str | None = Field(default=None, max_length=150)
    signature_title: str | None = Field(default=None, max_length=150)
    signature_image_url: str | None = Field(default=None, max_length=500)
    is_default: bool = Field(default=False)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
