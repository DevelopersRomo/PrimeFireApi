from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.countries import Countries


class Addresses(SQLModel, table=True):
    __tablename__ = "Addresses"
    __table_args__ = {"schema": "dbo"}

    AddressId: int | None = Field(default=None, primary_key=True, index=True)
    Address1: str = Field(max_length=200)
    Address2: str | None = Field(default=None, max_length=200)
    City: str = Field(max_length=100)
    State: str = Field(max_length=100)
    ZipCode: str = Field(max_length=20)
    CountryId: int = Field(foreign_key="dbo.Countries.CountryId")
    GooglePlaceId: str | None = Field(default=None, max_length=255)
    IsValidated: bool = Field(default=False)
    ValidatedAt: datetime | None = None
    CreatedAt: datetime = Field(default_factory=lambda: datetime.now(UTC))

    country: Optional["Countries"] = Relationship()
