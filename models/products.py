from datetime import datetime

from sqlmodel import Field, SQLModel


class Products(SQLModel, table=True):
    __tablename__ = "Products"
    __table_args__ = {"schema": "dbo"}

    Id: int | None = Field(default=None, primary_key=True)

    Name: str = Field(max_length=200, index=True)
    Description: str | None = Field(default=None, max_length=2000)
    # Product | Service
    Type: str = Field(index=True)
    SKU: str | None = Field(default=None, index=True)
    UnitPrice: float = 0
    Cost: float = 0
    TaxRate: float = 0
    # pieza, hora, mes, licencia...
    Unit: str = "pieza"
    StockQuantity: int = 0
    IsActive: bool = True
    CreatedAt: datetime = Field(default_factory=datetime.utcnow)
