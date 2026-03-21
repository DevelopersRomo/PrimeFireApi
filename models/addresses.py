from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, String
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.countries import Countries


class Addresses(SQLModel, table=True):
    __tablename__ = "addresses"
    __table_args__ = {"schema": "dbo"}

    address_id: int | None = Field(default=None, primary_key=True, index=True)
    address_1: str = Field(sa_column=Column("Address1", String(200)), max_length=200)
    address_2: str | None = Field(sa_column=Column("Address2", String(200), nullable=True, default=None), max_length=200)
    city: str = Field(max_length=100)
    state: str = Field(max_length=100)
    zip_code: str = Field(max_length=20)
    country_id: int = Field(foreign_key="dbo.countries.country_id")
    google_place_id: str | None = Field(default=None, max_length=255)
    is_validated: bool = Field(default=False)
    validated_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    country: Optional["Countries"] = Relationship()
