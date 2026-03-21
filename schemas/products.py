from datetime import datetime

from sqlmodel import SQLModel


class ProductCreate(SQLModel):
    name: str
    description: str | None = None
    type: str
    sku: str | None = None
    unit_price: float = 0
    cost: float = 0
    tax_rate: float = 0
    unit: str = "pieza"
    stock_quantity: int = 0
    is_active: bool = True


class ProductUpdate(SQLModel):
    name: str | None = None
    description: str | None = None
    type: str | None = None
    sku: str | None = None
    unit_price: float | None = None
    cost: float | None = None
    tax_rate: float | None = None
    unit: str | None = None
    stock_quantity: int | None = None
    is_active: bool | None = None


class ProductRead(SQLModel):
    id: int
    name: str
    description: str | None = None
    type: str
    sku: str | None = None
    unit_price: float
    cost: float
    tax_rate: float
    unit: str
    stock_quantity: int
    is_active: bool
    created_at: datetime


class Product(ProductRead):
    pass
