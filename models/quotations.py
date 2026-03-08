from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class Quotations(SQLModel, table=True):
    __tablename__ = "quotations"
    __table_args__ = {"schema": "dbo"}

    Id: Optional[int] = Field(default=None, primary_key=True)

    CustomerId: int = Field(foreign_key="dbo.Customers.Id", index=True)

    QuoteDate: datetime
    ExpirationDate: Optional[datetime] = None

    Subtotal: Decimal = Field(default=0, max_digits=18, decimal_places=2)
    Tax: Decimal = Field(default=0, max_digits=18, decimal_places=2)
    Discount: Decimal = Field(default=0, max_digits=18, decimal_places=2)
    Total: Decimal = Field(default=0, max_digits=18, decimal_places=2)

    Status: str = Field(index=True)
    Notes: Optional[str] = None

    CreatedAt: datetime = Field(default_factory=datetime.utcnow)