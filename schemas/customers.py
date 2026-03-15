from datetime import datetime

from pydantic import field_validator, model_validator
from sqlmodel import SQLModel

from models.customers import CustomerTypeEnum, DtdPotentialEnum, MarketEnum


class Address(SQLModel):
    AddressId: int | None = None
    Address1: str
    Address2: str | None = None
    City: str
    State: str
    ZipCode: str
    CountryId: int
    GooglePlaceId: str | None = None
    IsValidated: bool = False
    ValidatedAt: datetime | None = None
    CreatedAt: datetime


class AddressCreate(SQLModel):
    Address1: str
    Address2: str | None = None
    City: str
    State: str
    ZipCode: str
    CountryId: int
    GooglePlaceId: str | None = None


class AddressUpdate(SQLModel):
    Address1: str | None = None
    Address2: str | None = None
    City: str | None = None
    State: str | None = None
    ZipCode: str | None = None
    CountryId: int | None = None
    GooglePlaceId: str | None = None


class CustomerEmployee(SQLModel):
    EmployeeId: int
    DisplayName: str | None = None
    Email: str | None = None
    Title: str | None = None


class CustomerCreate(SQLModel):
    CustomerType: CustomerTypeEnum
    CompanyName: str | None = None
    FirstName: str | None = None
    LastName: str | None = None
    AdditionalName: str | None = None
    Market: MarketEnum | None = None
    DtdPotential: DtdPotentialEnum | None = None
    PrimaryEmail: str | None = None
    PrimaryPhone: str | None = None
    PrimaryAddress: AddressCreate | None = None
    PrimaryAddressId: int | None = None

    @model_validator(mode="after")
    def validate_residential(self):
        if self.CustomerType == CustomerTypeEnum.RESIDENTIAL:
            if not self.FirstName:
                raise ValueError("FirstName is required for residential customers")
            if not self.LastName:
                raise ValueError("LastName is required for residential customers")
            if self.CompanyName:
                raise ValueError("CompanyName should not be set for residential customers")
            if self.Market:
                raise ValueError("Market should not be set for residential customers")
            if self.DtdPotential:
                raise ValueError("DtdPotential should not be set for residential customers")
        return self

    @model_validator(mode="after")
    def validate_commercial(self):
        if self.CustomerType == CustomerTypeEnum.COMMERCIAL and not self.CompanyName:
            raise ValueError("CompanyName is required for commercial customers")
        return self

    @model_validator(mode="after")
    def validate_primary_contact(self):
        if not self.PrimaryEmail and not self.PrimaryPhone:
            raise ValueError("At least one of PrimaryEmail or PrimaryPhone is required")
        return self


class CustomerUpdate(SQLModel):
    CustomerType: CustomerTypeEnum | None = None
    CompanyName: str | None = None
    FirstName: str | None = None
    LastName: str | None = None
    AdditionalName: str | None = None
    Market: MarketEnum | None = None
    DtdPotential: DtdPotentialEnum | None = None
    PrimaryEmail: str | None = None
    PrimaryPhone: str | None = None
    PrimaryAddress: AddressUpdate | None = None
    PrimaryAddressId: int | None = None

    @classmethod
    @field_validator("Market", "DtdPotential", mode="before")
    def validate_enum_empty_string(cls, v):
        if v == "":  # noqa: PLC1901
            return None
        return v


class Customer(SQLModel):
    CustomerId: int | None = None
    CustomerType: CustomerTypeEnum
    CompanyName: str | None = None
    FirstName: str | None = None
    LastName: str | None = None
    AdditionalName: str | None = None
    Market: MarketEnum | None = None
    DtdPotential: DtdPotentialEnum | None = None
    PrimaryEmail: str | None = None
    PrimaryPhone: str | None = None
    PrimaryAddressId: int | None = None
    PrimaryAddress: Address | None = None
    CreatedAt: datetime
    UpdatedAt: datetime | None = None
    CreatedBy: int
    creator: CustomerEmployee | None = None


class CustomerNoteCreate(SQLModel):
    NoteText: str


class CustomerNoteUpdate(SQLModel):
    NoteText: str | None = None


class CustomerNote(SQLModel):
    CustomerNoteId: int | None = None
    CustomerId: int
    NoteText: str
    CreatedAt: datetime
    UpdatedAt: datetime | None = None
    CreatedBy: int
    creator: CustomerEmployee | None = None


class CustomerAlternateContactCreate(SQLModel):
    Name: str
    Email: str | None = None
    Phone: str | None = None

    @model_validator(mode="after")
    def validate_contact(self):
        if not self.Email and not self.Phone:
            raise ValueError("At least one of Email or Phone is required")
        return self


class CustomerAlternateContactUpdate(SQLModel):
    Name: str | None = None
    Email: str | None = None
    Phone: str | None = None

    @model_validator(mode="after")
    def validate_contact(self):
        if self.Email is None and self.Phone is None and self.Name is None:
            return self
        if self.Email is None and self.Phone is None:
            raise ValueError("At least one of Email or Phone must be provided when updating")
        return self


class CustomerAlternateContact(SQLModel):
    CustomerAlternateContactId: int | None = None
    CustomerId: int
    Name: str
    Email: str | None = None
    Phone: str | None = None
    CreatedAt: datetime
    UpdatedAt: datetime | None = None


class CustomerAttachment(SQLModel):
    CustomerAttachmentId: int | None = None
    CustomerId: int
    FileName: str
    FileType: str | None = None
    FilePath: str | None = None
    CreatedAt: datetime
    CreatedBy: int
    creator: CustomerEmployee | None = None


class CustomerMerged(SQLModel):
    Customer: Customer
    Notes: list[CustomerNote] = []
    Contacts: list[CustomerAlternateContact] = []
    Attachments: list[CustomerAttachment] = []


class CustomerFilters(SQLModel):
    customer_type: CustomerTypeEnum | None = None
    market: MarketEnum | None = None
    dtd_potential: DtdPotentialEnum | None = None
    search: str | None = None
