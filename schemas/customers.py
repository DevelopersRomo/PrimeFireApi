from sqlmodel import SQLModel
from typing import Optional, List
from datetime import datetime
from pydantic import field_validator, model_validator
from models.customers import CustomerTypeEnum, MarketEnum, DtdPotentialEnum

class Address(SQLModel):
    AddressId: Optional[int] = None
    Address1: str
    Address2: Optional[str] = None
    City: str
    State: str
    ZipCode: str
    CountryId: int
    GooglePlaceId: Optional[str] = None
    IsValidated: bool = False
    ValidatedAt: Optional[datetime] = None
    CreatedAt: datetime

class AddressCreate(SQLModel):
    Address1: str
    Address2: Optional[str] = None
    City: str
    State: str
    ZipCode: str
    CountryId: int
    GooglePlaceId: Optional[str] = None

class AddressUpdate(SQLModel):
    Address1: Optional[str] = None
    Address2: Optional[str] = None
    City: Optional[str] = None
    State: Optional[str] = None
    ZipCode: Optional[str] = None
    CountryId: Optional[int] = None
    GooglePlaceId: Optional[str] = None

class CustomerEmployee(SQLModel):
    EmployeeId: int
    DisplayName: Optional[str] = None
    Email: Optional[str] = None
    Title: Optional[str] = None

class CustomerCreate(SQLModel):
    CustomerType: CustomerTypeEnum
    CompanyName: Optional[str] = None
    FirstName: Optional[str] = None
    LastName: Optional[str] = None
    AdditionalName: Optional[str] = None
    Market: Optional[MarketEnum] = None
    DtdPotential: Optional[DtdPotentialEnum] = None
    PrimaryEmail: Optional[str] = None
    PrimaryPhone: Optional[str] = None
    PrimaryAddress: Optional[AddressCreate] = None
    PrimaryAddressId: Optional[int] = None

    @model_validator(mode='after')
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

    @model_validator(mode='after')
    def validate_commercial(self):
        if self.CustomerType == CustomerTypeEnum.COMMERCIAL:
            if not self.CompanyName:
                raise ValueError("CompanyName is required for commercial customers")
        return self

    @model_validator(mode='after')
    def validate_primary_contact(self):
        if not self.PrimaryEmail and not self.PrimaryPhone:
            raise ValueError("At least one of PrimaryEmail or PrimaryPhone is required")
        return self

class CustomerUpdate(SQLModel):
    CustomerType: Optional[CustomerTypeEnum] = None
    CompanyName: Optional[str] = None
    FirstName: Optional[str] = None
    LastName: Optional[str] = None
    AdditionalName: Optional[str] = None
    Market: Optional[MarketEnum] = None
    DtdPotential: Optional[DtdPotentialEnum] = None
    PrimaryEmail: Optional[str] = None
    PrimaryPhone: Optional[str] = None
    PrimaryAddress: Optional[AddressUpdate] = None
    PrimaryAddressId: Optional[int] = None

    @field_validator('Market', 'DtdPotential', mode='before')
    def validate_enum_empty_string(cls, v):
        if v == "":
            return None
        return v

class Customer(SQLModel):
    CustomerId: Optional[int] = None
    CustomerType: CustomerTypeEnum
    CompanyName: Optional[str] = None
    FirstName: Optional[str] = None
    LastName: Optional[str] = None
    AdditionalName: Optional[str] = None
    Market: Optional[MarketEnum] = None
    DtdPotential: Optional[DtdPotentialEnum] = None
    PrimaryEmail: Optional[str] = None
    PrimaryPhone: Optional[str] = None
    PrimaryAddressId: Optional[int] = None
    PrimaryAddress: Optional[Address] = None
    CreatedAt: datetime
    UpdatedAt: Optional[datetime] = None
    CreatedBy: int
    creator: Optional[CustomerEmployee] = None

class CustomerNoteCreate(SQLModel):
    NoteText: str

class CustomerNoteUpdate(SQLModel):
    NoteText: Optional[str] = None

class CustomerNote(SQLModel):
    CustomerNoteId: Optional[int] = None
    CustomerId: int
    NoteText: str
    CreatedAt: datetime
    UpdatedAt: Optional[datetime] = None
    CreatedBy: int
    creator: Optional[CustomerEmployee] = None

class CustomerAlternateContactCreate(SQLModel):
    Name: str
    Email: Optional[str] = None
    Phone: Optional[str] = None

    @model_validator(mode='after')
    def validate_contact(self):
        if not self.Email and not self.Phone:
            raise ValueError("At least one of Email or Phone is required")
        return self

class CustomerAlternateContactUpdate(SQLModel):
    Name: Optional[str] = None
    Email: Optional[str] = None
    Phone: Optional[str] = None

    @model_validator(mode='after')
    def validate_contact(self):
        if self.Email is None and self.Phone is None:
            if self.Name is None:
                return self
        if self.Email is None and self.Phone is None:
            raise ValueError("At least one of Email or Phone must be provided when updating")
        return self

class CustomerAlternateContact(SQLModel):
    CustomerAlternateContactId: Optional[int] = None
    CustomerId: int
    Name: str
    Email: Optional[str] = None
    Phone: Optional[str] = None
    CreatedAt: datetime
    UpdatedAt: Optional[datetime] = None

class CustomerAttachment(SQLModel):
    CustomerAttachmentId: Optional[int] = None
    CustomerId: int
    FileName: str
    FileType: Optional[str] = None
    FilePath: Optional[str] = None
    CreatedAt: datetime
    CreatedBy: int
    creator: Optional[CustomerEmployee] = None

class CustomerMerged(SQLModel):
    Customer: Customer
    Notes: List[CustomerNote] = []
    Contacts: List[CustomerAlternateContact] = []
    Attachments: List[CustomerAttachment] = []

class CustomerFilters(SQLModel):
    customer_type: Optional[CustomerTypeEnum] = None
    market: Optional[MarketEnum] = None
    dtd_potential: Optional[DtdPotentialEnum] = None
    search: Optional[str] = None
