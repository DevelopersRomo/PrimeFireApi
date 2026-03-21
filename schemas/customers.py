from datetime import datetime

from pydantic import field_validator, model_validator
from sqlmodel import SQLModel

from models.customers import CustomerTypeEnum, DtdPotentialEnum, MarketEnum


class Address(SQLModel):
    address_id: int | None = None
    address_1: str
    address_2: str | None = None
    city: str
    state: str
    zip_code: str
    country_id: int
    google_place_id: str | None = None
    is_validated: bool = False
    validated_at: datetime | None = None
    created_at: datetime


class AddressCreate(SQLModel):
    address_1: str
    address_2: str | None = None
    city: str
    state: str
    zip_code: str
    country_id: int
    google_place_id: str | None = None


class AddressUpdate(SQLModel):
    address_1: str | None = None
    address_2: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    country_id: int | None = None
    google_place_id: str | None = None


class CustomerEmployee(SQLModel):
    employee_id: int
    display_name: str | None = None
    email: str | None = None
    title: str | None = None


class CustomerCreate(SQLModel):
    customer_type: CustomerTypeEnum
    company_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    additional_name: str | None = None
    market: MarketEnum | None = None
    dtd_potential: DtdPotentialEnum | None = None
    primary_email: str | None = None
    primary_phone: str | None = None
    primary_address: AddressCreate | None = None
    primary_address_id: int | None = None

    @model_validator(mode="after")
    def validate_residential(self):
        if self.customer_type == CustomerTypeEnum.RESIDENTIAL:
            if not self.first_name:
                raise ValueError("first_name is required for residential customers")
            if not self.last_name:
                raise ValueError("last_name is required for residential customers")
            if self.company_name:
                raise ValueError("company_name should not be set for residential customers")
            if self.market:
                raise ValueError("market should not be set for residential customers")
            if self.dtd_potential:
                raise ValueError("dtd_potential should not be set for residential customers")
        return self

    @model_validator(mode="after")
    def validate_commercial(self):
        if self.customer_type == CustomerTypeEnum.COMMERCIAL and not self.company_name:
            raise ValueError("company_name is required for commercial customers")
        return self

    @model_validator(mode="after")
    def validate_primary_contact(self):
        if not self.primary_email and not self.primary_phone:
            raise ValueError("At least one of primary_email or primary_phone is required")
        return self


class CustomerUpdate(SQLModel):
    customer_type: CustomerTypeEnum | None = None
    company_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    additional_name: str | None = None
    market: MarketEnum | None = None
    dtd_potential: DtdPotentialEnum | None = None
    primary_email: str | None = None
    primary_phone: str | None = None
    primary_address: AddressUpdate | None = None
    primary_address_id: int | None = None

    @classmethod
    @field_validator("market", "dtd_potential", mode="before")
    def validate_enum_empty_string(cls, v):
        if v == "":
            return None
        return v


class Customer(SQLModel):
    customer_id: int | None = None
    customer_type: CustomerTypeEnum
    company_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    additional_name: str | None = None
    market: MarketEnum | None = None
    dtd_potential: DtdPotentialEnum | None = None
    primary_email: str | None = None
    primary_phone: str | None = None
    primary_address_id: int | None = None
    primary_address: Address | None = None
    created_at: datetime
    updated_at: datetime | None = None
    created_by: int
    creator: CustomerEmployee | None = None


class CustomerNoteCreate(SQLModel):
    note_text: str


class CustomerNoteUpdate(SQLModel):
    note_text: str | None = None


class CustomerNote(SQLModel):
    customer_note_id: int | None = None
    customer_id: int
    note_text: str
    created_at: datetime
    updated_at: datetime | None = None
    created_by: int
    creator: CustomerEmployee | None = None


class CustomerAlternateContactCreate(SQLModel):
    name: str
    email: str | None = None
    phone: str | None = None

    @model_validator(mode="after")
    def validate_contact(self):
        if not self.email and not self.phone:
            raise ValueError("At least one of email or phone is required")
        return self


class CustomerAlternateContactUpdate(SQLModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None

    @model_validator(mode="after")
    def validate_contact(self):
        if self.email is None and self.phone is None and self.name is None:
            return self
        if self.email is None and self.phone is None:
            raise ValueError("At least one of email or phone must be provided when updating")
        return self


class CustomerAlternateContact(SQLModel):
    customer_alternate_contact_id: int | None = None
    customer_id: int
    name: str
    email: str | None = None
    phone: str | None = None
    created_at: datetime
    updated_at: datetime | None = None


class CustomerAttachment(SQLModel):
    customer_attachment_id: int | None = None
    customer_id: int
    file_name: str
    file_type: str | None = None
    file_path: str | None = None
    created_at: datetime
    created_by: int
    creator: CustomerEmployee | None = None


class CustomerMerged(SQLModel):
    customer: Customer
    notes: list[CustomerNote] = []
    contacts: list[CustomerAlternateContact] = []
    attachments: list[CustomerAttachment] = []


class CustomerFilters(SQLModel):
    customer_type: CustomerTypeEnum | None = None
    market: MarketEnum | None = None
    dtd_potential: DtdPotentialEnum | None = None
    search: str | None = None
