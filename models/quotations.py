from datetime import datetime
from decimal import Decimal

from sqlmodel import Field, SQLModel


class Quotations(SQLModel, table=True):
    __tablename__ = "quotations"
    __table_args__ = {"schema": "dbo"}

    id: int | None = Field(default=None, primary_key=True)

    customer_id: int = Field(foreign_key="dbo.customers.customer_id", index=True)

    quote_date: datetime
    expiration_date: datetime | None = None

    subtotal: Decimal = Field(default=0, max_digits=18, decimal_places=2)
    tax: Decimal = Field(default=0, max_digits=18, decimal_places=2)
    discount: Decimal = Field(default=0, max_digits=18, decimal_places=2)
    total: Decimal = Field(default=0, max_digits=18, decimal_places=2)

    status: str = Field(index=True)
    notes: str | None = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
