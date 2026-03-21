from datetime import datetime

from sqlmodel import Field, SQLModel


class Products(SQLModel, table=True):
    __tablename__ = "products"
    __table_args__ = {"schema": "dbo"}

    id: int | None = Field(default=None, primary_key=True)

    name: str = Field(max_length=200, index=True)
    description: str | None = Field(default=None, max_length=2000)
    # Product | Service
    type: str = Field(index=True)
    sku: str | None = Field(default=None, index=True)
    unit_price: float = 0
    cost: float = 0
    tax_rate: float = 0
    # pieza, hora, mes, licencia...
    unit: str = "pieza"
    stock_quantity: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
