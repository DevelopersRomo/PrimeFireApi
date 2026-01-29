from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, timezone
from sqlalchemy import Enum as SAEnum
import enum

if TYPE_CHECKING:
    from models.employees import Employees
    from models.addresses import Addresses

class CustomerTypeEnum(str, enum.Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"

class MarketEnum(str, enum.Enum):
    COMMERCIAL = "commercial"
    INDIVIDUAL = "individual"
    ENVIRONMENTAL = "environmental"
    ENGINEERING = "engineering"

class DtdPotentialEnum(str, enum.Enum):
    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"
    ONE_OFF = "one_off"
    PROSPECT = "prospect"

class Customers(SQLModel, table=True):
    __tablename__ = "Customers"
    __table_args__ = {'schema': 'dbo'}

    CustomerId: Optional[int] = Field(default=None, primary_key=True, index=True)
    CustomerType: CustomerTypeEnum = Field(
        sa_type=SAEnum(CustomerTypeEnum, values_callable=lambda x: [e.value for e in x])
    )
    CompanyName: Optional[str] = Field(default=None, max_length=200)
    FirstName: Optional[str] = Field(default=None, max_length=100)
    LastName: Optional[str] = Field(default=None, max_length=100)
    AdditionalName: Optional[str] = Field(default=None, max_length=100)
    Market: Optional[MarketEnum] = Field(
        default=None,
        sa_type=SAEnum(MarketEnum, values_callable=lambda x: [e.value for e in x])
    )
    DtdPotential: Optional[DtdPotentialEnum] = Field(
        default=None,
        sa_type=SAEnum(DtdPotentialEnum, values_callable=lambda x: [e.value for e in x])
    )
    PrimaryEmail: Optional[str] = Field(default=None, max_length=255)
    PrimaryPhone: Optional[str] = Field(default=None, max_length=20)
    PrimaryAddressId: Optional[int] = Field(default=None, foreign_key="dbo.Addresses.AddressId")
    CreatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    UpdatedAt: Optional[datetime] = None
    CreatedBy: int = Field(foreign_key="dbo.Employees.EmployeeId")

    primary_address: Optional["Addresses"] = Relationship()
    creator: Optional["Employees"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "Customers.CreatedBy"}
    )
    notes: List["CustomerNotes"] = Relationship(back_populates="customer", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    alternate_contacts: List["CustomerAlternateContacts"] = Relationship(back_populates="customer", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    attachments: List["CustomerAttachments"] = Relationship(back_populates="customer", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

class CustomerNotes(SQLModel, table=True):
    __tablename__ = "CustomerNotes"
    __table_args__ = {'schema': 'dbo'}

    CustomerNoteId: Optional[int] = Field(default=None, primary_key=True, index=True)
    CustomerId: int = Field(foreign_key="dbo.Customers.CustomerId")
    NoteText: str
    CreatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    UpdatedAt: Optional[datetime] = None
    CreatedBy: int = Field(foreign_key="dbo.Employees.EmployeeId")

    customer: "Customers" = Relationship(back_populates="notes")
    creator: Optional["Employees"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "CustomerNotes.CreatedBy"}
    )

class CustomerAlternateContacts(SQLModel, table=True):
    __tablename__ = "CustomerAlternateContacts"
    __table_args__ = {'schema': 'dbo'}

    CustomerAlternateContactId: Optional[int] = Field(default=None, primary_key=True, index=True)
    CustomerId: int = Field(foreign_key="dbo.Customers.CustomerId")
    Name: str = Field(max_length=200)
    Email: Optional[str] = Field(default=None, max_length=255)
    Phone: Optional[str] = Field(default=None, max_length=20)
    CreatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    UpdatedAt: Optional[datetime] = None

    customer: "Customers" = Relationship(back_populates="alternate_contacts")

class CustomerAttachments(SQLModel, table=True):
    __tablename__ = "CustomerAttachments"
    __table_args__ = {'schema': 'dbo'}

    CustomerAttachmentId: Optional[int] = Field(default=None, primary_key=True, index=True)
    CustomerId: int = Field(foreign_key="dbo.Customers.CustomerId")
    FileName: str = Field(max_length=255)
    FileType: Optional[str] = Field(default=None, max_length=100)
    FilePath: Optional[str] = Field(default=None, max_length=500)
    CreatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    CreatedBy: int = Field(foreign_key="dbo.Employees.EmployeeId")

    customer: "Customers" = Relationship(back_populates="attachments")
    creator: Optional["Employees"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "CustomerAttachments.CreatedBy"}
    )
