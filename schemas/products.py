from datetime import datetime

from sqlmodel import SQLModel


class ProductCreate(SQLModel):
    Name: str
    Description: str | None = None
    Type: str
    SKU: str | None = None
    UnitPrice: float = 0
    Cost: float = 0
    TaxRate: float = 0
    Unit: str = "pieza"
    StockQuantity: int = 0
    IsActive: bool = True


class ProductUpdate(SQLModel):
    Name: str | None = None
    Description: str | None = None
    Type: str | None = None
    SKU: str | None = None
    UnitPrice: float | None = None
    Cost: float | None = None
    TaxRate: float | None = None
    Unit: str | None = None
    StockQuantity: int | None = None
    IsActive: bool | None = None


class ProductRead(SQLModel):
    Id: int
    Name: str
    Description: str | None
    Type: str
    SKU: str | None
    UnitPrice: float
    Cost: float
    TaxRate: float
    Unit: str
    StockQuantity: int
    IsActive: bool
    CreatedAt: datetime


class Product(ProductRead):
    pass
