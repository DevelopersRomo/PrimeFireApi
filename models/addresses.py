from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING:
    from models.countries import Countries

class Addresses(SQLModel, table=True):
    __tablename__ = "Addresses"
    __table_args__ = {'schema': 'dbo'}

    AddressId: Optional[int] = Field(default=None, primary_key=True, index=True)
    Address1: str = Field(max_length=200)
    Address2: Optional[str] = Field(default=None, max_length=200)
    City: str = Field(max_length=100)
    State: str = Field(max_length=100)
    ZipCode: str = Field(max_length=20)
    CountryId: int = Field(foreign_key="dbo.Countries.CountryId")
    GooglePlaceId: Optional[str] = Field(default=None, max_length=255)
    IsValidated: bool = Field(default=False)
    ValidatedAt: Optional[datetime] = None
    CreatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    country: Optional["Countries"] = Relationship()
