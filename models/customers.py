import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, Relationship, SQLModel

from core.datetime_utils import utcnow

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
    __tablename__ = "customers"
    __table_args__ = {"schema": "dbo"}

    customer_id: int | None = Field(default=None, primary_key=True, index=True)
    customer_type: CustomerTypeEnum = Field(
        sa_column=Column(
            SAEnum(CustomerTypeEnum, native_enum=False, values_callable=lambda x: [e.value for e in x]), nullable=False
        )
    )
    company_name: str | None = Field(default=None, max_length=200)
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    additional_name: str | None = Field(default=None, max_length=100)
    market: MarketEnum | None = Field(
        default=None,
        sa_column=Column(
            SAEnum(MarketEnum, native_enum=False, values_callable=lambda x: [e.value for e in x]), nullable=True
        ),
    )
    dtd_potential: DtdPotentialEnum | None = Field(
        default=None,
        sa_column=Column(
            SAEnum(DtdPotentialEnum, native_enum=False, values_callable=lambda x: [e.value for e in x]), nullable=True
        ),
    )
    primary_email: str | None = Field(default=None, max_length=255)
    primary_phone: str | None = Field(default=None, max_length=20)
    primary_address_id: int | None = Field(default=None, foreign_key="dbo.addresses.address_id")
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime | None = None
    created_by: int = Field(foreign_key="dbo.employees.employee_id")

    primary_address: Optional["Addresses"] = Relationship()
    creator: Optional["Employees"] = Relationship(sa_relationship_kwargs={"foreign_keys": "Customers.created_by"})
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
    __tablename__ = "customer_notes"
    __table_args__ = {"schema": "dbo"}

    customer_note_id: int | None = Field(default=None, primary_key=True, index=True)
    customer_id: int = Field(foreign_key="dbo.customers.customer_id")
    note_text: str
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime | None = None
    created_by: int = Field(foreign_key="dbo.employees.employee_id")

    customer: "Customers" = Relationship(back_populates="notes")
    creator: Optional["Employees"] = Relationship(sa_relationship_kwargs={"foreign_keys": "CustomerNotes.created_by"})


class CustomerAlternateContacts(SQLModel, table=True):
    __tablename__ = "customer_alternate_contacts"
    __table_args__ = {"schema": "dbo"}

    customer_alternate_contact_id: int | None = Field(default=None, primary_key=True, index=True)
    customer_id: int = Field(foreign_key="dbo.customers.customer_id")
    name: str = Field(max_length=200)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime | None = None

    customer: "Customers" = Relationship(back_populates="alternate_contacts")


class CustomerAttachments(SQLModel, table=True):
    __tablename__ = "customer_attachments"
    __table_args__ = {"schema": "dbo"}

    customer_attachment_id: int | None = Field(default=None, primary_key=True, index=True)
    customer_id: int = Field(foreign_key="dbo.customers.customer_id")
    file_name: str = Field(max_length=255)
    file_type: str | None = Field(default=None, max_length=100)
    file_path: str | None = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=utcnow)
    created_by: int = Field(foreign_key="dbo.employees.employee_id")

    customer: "Customers" = Relationship(back_populates="attachments")
    creator: Optional["Employees"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "CustomerAttachments.created_by"}
    )
