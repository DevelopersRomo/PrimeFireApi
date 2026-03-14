from datetime import datetime
from decimal import Decimal

from sqlmodel import Field, SQLModel


class Quotations(SQLModel, table=True):
    __tablename__ = "quotations"
    __table_args__ = {"schema": "dbo"}

    Id: int | None = Field(default=None, primary_key=True)

    CustomerId: int = Field(foreign_key="dbo.Customers.CustomerId", index=True)

    QuoteDate: datetime
    ExpirationDate: datetime | None = None

    Subtotal: Decimal = Field(default=0, max_digits=18, decimal_places=2)
    Tax: Decimal = Field(default=0, max_digits=18, decimal_places=2)
    Discount: Decimal = Field(default=0, max_digits=18, decimal_places=2)
    Total: Decimal = Field(default=0, max_digits=18, decimal_places=2)

    Status: str = Field(index=True)
    Notes: str | None = None

    CreatedAt: datetime = Field(default_factory=datetime.utcnow)
