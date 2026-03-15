import enum
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.addresses import Addresses
    from models.employees import Employees


class CustomerTypeEnum(enum.StrEnum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"


class MarketEnum(enum.StrEnum):
    COMMERCIAL = "commercial"
    INDIVIDUAL = "individual"
    ENVIRONMENTAL = "environmental"
    ENGINEERING = "engineering"


class DtdPotentialEnum(enum.StrEnum):
    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"
    ONE_OFF = "one_off"
    PROSPECT = "prospect"


class Customers(SQLModel, table=True):
    __tablename__ = "Customers"
    __table_args__ = {"schema": "dbo"}

    CustomerId: int | None = Field(default=None, primary_key=True, index=True)
    CustomerType: CustomerTypeEnum = Field(
        sa_column=Column(
            SAEnum(CustomerTypeEnum, native_enum=False, values_callable=lambda x: [e.value for e in x]), nullable=False
        )
    )
    CompanyName: str | None = Field(default=None, max_length=200)
    FirstName: str | None = Field(default=None, max_length=100)
    LastName: str | None = Field(default=None, max_length=100)
    AdditionalName: str | None = Field(default=None, max_length=100)
    Market: MarketEnum | None = Field(
        default=None,
        sa_column=Column(
            SAEnum(MarketEnum, native_enum=False, values_callable=lambda x: [e.value for e in x]), nullable=True
        ),
    )
    DtdPotential: DtdPotentialEnum | None = Field(
        default=None,
        sa_column=Column(
            SAEnum(DtdPotentialEnum, native_enum=False, values_callable=lambda x: [e.value for e in x]), nullable=True
        ),
    )
    PrimaryEmail: str | None = Field(default=None, max_length=255)
    PrimaryPhone: str | None = Field(default=None, max_length=20)
    PrimaryAddressId: int | None = Field(default=None, foreign_key="dbo.Addresses.AddressId")
    CreatedAt: datetime = Field(default_factory=lambda: datetime.now(UTC))
    UpdatedAt: datetime | None = None
    CreatedBy: int = Field(foreign_key="dbo.Employees.EmployeeId")

    primary_address: Optional["Addresses"] = Relationship()
    creator: Optional["Employees"] = Relationship(sa_relationship_kwargs={"foreign_keys": "Customers.CreatedBy"})
    notes: list["CustomerNotes"] = Relationship(
        back_populates="customer", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    alternate_contacts: list["CustomerAlternateContacts"] = Relationship(
        back_populates="customer", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    attachments: list["CustomerAttachments"] = Relationship(
        back_populates="customer", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class CustomerNotes(SQLModel, table=True):
    __tablename__ = "CustomerNotes"
    __table_args__ = {"schema": "dbo"}

    CustomerNoteId: int | None = Field(default=None, primary_key=True, index=True)
    CustomerId: int = Field(foreign_key="dbo.Customers.CustomerId")
    NoteText: str
    CreatedAt: datetime = Field(default_factory=lambda: datetime.now(UTC))
    UpdatedAt: datetime | None = None
    CreatedBy: int = Field(foreign_key="dbo.Employees.EmployeeId")

    customer: "Customers" = Relationship(back_populates="notes")
    creator: Optional["Employees"] = Relationship(sa_relationship_kwargs={"foreign_keys": "CustomerNotes.CreatedBy"})


class CustomerAlternateContacts(SQLModel, table=True):
    __tablename__ = "CustomerAlternateContacts"
    __table_args__ = {"schema": "dbo"}

    CustomerAlternateContactId: int | None = Field(default=None, primary_key=True, index=True)
    CustomerId: int = Field(foreign_key="dbo.Customers.CustomerId")
    Name: str = Field(max_length=200)
    Email: str | None = Field(default=None, max_length=255)
    Phone: str | None = Field(default=None, max_length=20)
    CreatedAt: datetime = Field(default_factory=lambda: datetime.now(UTC))
    UpdatedAt: datetime | None = None

    customer: "Customers" = Relationship(back_populates="alternate_contacts")


class CustomerAttachments(SQLModel, table=True):
    __tablename__ = "CustomerAttachments"
    __table_args__ = {"schema": "dbo"}

    CustomerAttachmentId: int | None = Field(default=None, primary_key=True, index=True)
    CustomerId: int = Field(foreign_key="dbo.Customers.CustomerId")
    FileName: str = Field(max_length=255)
    FileType: str | None = Field(default=None, max_length=100)
    FilePath: str | None = Field(default=None, max_length=500)
    CreatedAt: datetime = Field(default_factory=lambda: datetime.now(UTC))
    CreatedBy: int = Field(foreign_key="dbo.Employees.EmployeeId")

    customer: "Customers" = Relationship(back_populates="attachments")
    creator: Optional["Employees"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "CustomerAttachments.CreatedBy"}
    )
