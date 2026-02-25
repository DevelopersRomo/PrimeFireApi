from sqlmodel import SQLModel
from typing import Optional
from datetime import datetime


class ProductCreate(SQLModel):
    Name: str
    Description: Optional[str] = None
    Type: str
    SKU: Optional[str] = None
    UnitPrice: float = 0
    Cost: float = 0
    TaxRate: float = 0
    Unit: str = "pieza"
    StockQuantity: int = 0
    IsActive: bool = True


class ProductUpdate(SQLModel):
    Name: Optional[str] = None
    Description: Optional[str] = None
    Type: Optional[str] = None
    SKU: Optional[str] = None
    UnitPrice: Optional[float] = None
    Cost: Optional[float] = None
    TaxRate: Optional[float] = None
    Unit: Optional[str] = None
    StockQuantity: Optional[int] = None
    IsActive: Optional[bool] = None


class ProductRead(SQLModel):
    Id: int
    Name: str
    Description: Optional[str]
    Type: str
    SKU: Optional[str]
    UnitPrice: float
    Cost: float
    TaxRate: float
    Unit: str
    StockQuantity: int
    IsActive: bool
    CreatedAt: datetime


class Product(ProductRead):
    pass
