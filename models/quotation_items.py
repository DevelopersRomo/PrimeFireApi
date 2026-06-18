from decimal import Decimal

from sqlmodel import Field, SQLModel


class QuotationItems(SQLModel, table=True):
    __tablename__ = "quotation_items"
    __table_args__ = {"schema": "dbo"}

    id: int | None = Field(default=None, primary_key=True)

    quotation_id: int = Field(foreign_key="dbo.quotations.id", index=True)
    product_id: int = Field(foreign_key="dbo.products.id", index=True)

    description: str | None = Field(default=None, max_length=1000)

    quantity: Decimal = Field(default=0, max_digits=18, decimal_places=2)
    unit_price: Decimal = Field(default=0, max_digits=18, decimal_places=2)
    discount: Decimal = Field(default=0, max_digits=18, decimal_places=2)
    tax: Decimal = Field(default=0, max_digits=18, decimal_places=2)
    total: Decimal = Field(default=0, max_digits=18, decimal_places=2)
