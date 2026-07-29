from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator, model_validator

from models.agreements import AgreementAttachmentType, AgreementType


class AgreementCreate(BaseModel):
    title: str = Field(min_length=1, max_length=250)
    agreement_type: AgreementType
    customer_id: int | None = None
    counterparty_name: str = Field(min_length=1, max_length=250)
    owner_employee_id: int
    effective_date: date
    expiration_date: date | None = None
    notes: str | None = None

    @field_validator("title", "counterparty_name")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Value cannot be blank")
        return value

    @field_validator("notes")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return value.strip() or None if value is not None else None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.expiration_date and self.expiration_date < self.effective_date:
            raise ValueError("Expiration date cannot precede effective date")
        return self


class AgreementUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=250)
    agreement_type: AgreementType | None = None
    customer_id: int | None = None
    counterparty_name: str | None = Field(default=None, min_length=1, max_length=250)
    effective_date: date | None = None
    expiration_date: date | None = None
    notes: str | None = None

    @field_validator("title", "counterparty_name")
    @classmethod
    def strip_optional_required_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("Value cannot be blank")
        return value

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return value.strip() or None if value is not None else None


class AgreementTerminationUpdate(BaseModel):
    terminated_on: date | None = None
    termination_reason: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def validate_termination(self):
        reason = self.termination_reason.strip() if self.termination_reason else None
        if bool(self.terminated_on) != bool(reason):
            raise ValueError("Termination date and reason must be provided together")
        self.termination_reason = reason
        return self


class AgreementOwnerUpdate(BaseModel):
    owner_employee_id: int


class AgreementAttachmentRead(BaseModel):
    agreement_attachment_id: int
    agreement_id: int
    attachment_type: AgreementAttachmentType
    version_number: int | None
    is_current: bool
    replacement_reason: str | None
    original_filename: str
    file_extension: str
    mime_type: str
    file_size: int
    sha256: str
    created_at: datetime
    created_by: int
    archived_at: datetime | None
    archived_by: int | None


class AgreementRead(BaseModel):
    agreement_id: int
    title: str
    agreement_type: AgreementType
    customer_id: int | None
    customer_name: str | None
    counterparty_name: str
    owner_employee_id: int
    owner_name: str
    effective_date: date
    expiration_date: date | None
    terminated_on: date | None
    termination_reason: str | None
    terminated_by: int | None
    notes: str | None
    lifecycle_status: str
    created_at: datetime
    created_by: int
    created_by_name: str
    updated_at: datetime | None
    updated_by: int | None
    updated_by_name: str | None
    archived_at: datetime | None
    archived_by: int | None
    archived_by_name: str | None


class AgreementDetail(AgreementRead):
    current_primary: AgreementAttachmentRead | None
    primary_versions: list[AgreementAttachmentRead]
    supporting_attachments: list[AgreementAttachmentRead]


class AgreementListResponse(BaseModel):
    items: list[AgreementRead]
    total: int
    skip: int
    limit: int
    has_more: bool
