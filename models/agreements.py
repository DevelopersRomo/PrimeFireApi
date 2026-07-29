import enum
from datetime import date, datetime

from sqlalchemy import Column
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, SQLModel

from core.datetime_utils import utcnow


class AgreementType(enum.StrEnum):
    SERVICE_AGREEMENT = "SERVICE_AGREEMENT"
    MASTER_SERVICE_AGREEMENT = "MASTER_SERVICE_AGREEMENT"
    NDA = "NDA"
    MAINTENANCE_AGREEMENT = "MAINTENANCE_AGREEMENT"
    OTHER = "OTHER"


class AgreementAttachmentType(enum.StrEnum):
    PRIMARY = "PRIMARY"
    SUPPORTING = "SUPPORTING"


class Agreements(SQLModel, table=True):
    __tablename__ = "agreements"
    __table_args__ = {"schema": "dbo"}

    agreement_id: int | None = Field(default=None, primary_key=True, index=True)
    title: str = Field(max_length=250)
    agreement_type: AgreementType = Field(
        sa_column=Column(
            SAEnum(AgreementType, native_enum=False, values_callable=lambda values: [item.value for item in values]),
            nullable=False,
        )
    )
    customer_id: int | None = Field(default=None, foreign_key="dbo.customers.customer_id", index=True)
    counterparty_name: str = Field(max_length=250, index=True)
    owner_employee_id: int = Field(foreign_key="dbo.employees.employee_id", index=True)
    effective_date: date = Field(index=True)
    expiration_date: date | None = Field(default=None, index=True)
    terminated_on: date | None = Field(default=None, index=True)
    termination_reason: str | None = Field(default=None, max_length=1000)
    terminated_by: int | None = Field(default=None, foreign_key="dbo.employees.employee_id")
    notes: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=utcnow)
    created_by: int = Field(foreign_key="dbo.employees.employee_id")
    updated_at: datetime | None = None
    updated_by: int | None = Field(default=None, foreign_key="dbo.employees.employee_id")
    archived_at: datetime | None = Field(default=None, index=True)
    archived_by: int | None = Field(default=None, foreign_key="dbo.employees.employee_id")


class AgreementAttachments(SQLModel, table=True):
    __tablename__ = "agreement_attachments"
    __table_args__ = {"schema": "dbo"}

    agreement_attachment_id: int | None = Field(default=None, primary_key=True, index=True)
    agreement_id: int = Field(foreign_key="dbo.agreements.agreement_id", index=True)
    attachment_type: AgreementAttachmentType = Field(
        sa_column=Column(
            SAEnum(
                AgreementAttachmentType,
                native_enum=False,
                values_callable=lambda values: [item.value for item in values],
            ),
            nullable=False,
        )
    )
    version_number: int | None = None
    is_current: bool = Field(default=False, index=True)
    replacement_reason: str | None = Field(default=None, max_length=1000)
    original_filename: str = Field(max_length=255)
    stored_filename: str = Field(max_length=100)
    storage_path: str = Field(max_length=500)
    file_extension: str = Field(max_length=10)
    mime_type: str = Field(max_length=150)
    file_size: int
    sha256: str = Field(max_length=64)
    created_at: datetime = Field(default_factory=utcnow)
    created_by: int = Field(foreign_key="dbo.employees.employee_id")
    archived_at: datetime | None = Field(default=None, index=True)
    archived_by: int | None = Field(default=None, foreign_key="dbo.employees.employee_id")
