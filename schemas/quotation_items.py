from decimal import Decimal

from sqlmodel import SQLModel


class QuotationItemCreate(SQLModel):
    product_id: int
    description: str | None = None
    quantity: Decimal = Decimal("0.00")
    unit_price: Decimal = Decimal("0.00")
    discount: Decimal = Decimal("0.00")
    tax: Decimal = Decimal("0.00")
    total: Decimal = Decimal("0.00")


class QuotationItemUpdate(SQLModel):
    product_id: int | None = None
    description: str | None = None
    quantity: Decimal | None = None
    unit_price: Decimal | None = None
    discount: Decimal | None = None
    tax: Decimal | None = None
    total: Decimal | None = None


class QuotationItemRead(SQLModel):
    id: int
    quotation_id: int
    product_id: int
    description: str | None = None
    quantity: Decimal
    unit_price: Decimal
    discount: Decimal
    tax: Decimal
    total: Decimal


class QuotationItem(QuotationItemRead):
    pass
