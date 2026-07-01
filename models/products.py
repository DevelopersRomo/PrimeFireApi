from datetime import datetime
from decimal import Decimal

from sqlmodel import Field, Relationship, SQLModel


class ProductFamilies(SQLModel, table=True):
    __tablename__ = "product_families"
    __table_args__ = {"schema": "dbo"}

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, index=True)
    description: str | None = Field(default=None)
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    categories: list["ProductCategories"] = Relationship(back_populates="family")
    products: list["Products"] = Relationship(back_populates="family")


class ProductCategories(SQLModel, table=True):
    __tablename__ = "product_categories"
    __table_args__ = {"schema": "dbo"}

    id: int | None = Field(default=None, primary_key=True)
    family_id: int = Field(foreign_key="dbo.product_families.id", index=True)
    name: str = Field(max_length=100, index=True)
    description: str | None = Field(default=None)
    active: bool = True

    family: ProductFamilies | None = Relationship(back_populates="categories")
    products: list["Products"] = Relationship(back_populates="category")


class ProductCatalog(SQLModel, table=True):
    __tablename__ = "product_catalog"
    __table_args__ = {"schema": "dbo"}

    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(max_length=50, index=True)
    name: str = Field(max_length=255, index=True)
    family_id: int | None = Field(default=None, foreign_key="dbo.product_families.id", index=True)
    category_id: int | None = Field(default=None, foreign_key="dbo.product_categories.id", index=True)
    unit: str | None = Field(default=None, max_length=20)
    min_stock: Decimal = Field(default=Decimal(0), max_digits=12, decimal_places=2)
    active: bool = True
    description: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ProductSpecifications(SQLModel, table=True):
    __tablename__ = "product_specifications"
    __table_args__ = {"schema": "dbo"}

    id: int | None = Field(default=None, primary_key=True)
    product_id: int | None = Field(default=None, foreign_key="dbo.product_catalog.id", index=True)
    specification: str | None = Field(default=None, max_length=100)
    size: str | None = Field(default=None, max_length=100)
    material: str | None = Field(default=None, max_length=100)
    manufacturer: str | None = Field(default=None, max_length=100)
    model: str | None = Field(default=None, max_length=100)
    notes: str | None = Field(default=None)


class Products(SQLModel, table=True):
    __tablename__ = "products"
    __table_args__ = {"schema": "dbo"}

    id: int | None = Field(default=None, primary_key=True)

    name: str = Field(max_length=200, index=True)
    description: str | None = Field(default=None, max_length=2000)
    # Product | Service
    type: str = Field(index=True)
    sku: str | None = Field(default=None, index=True)
    code: str | None = Field(default=None, max_length=50, index=True)
    family_id: int | None = Field(default=None, foreign_key="dbo.product_families.id", index=True)
    category_id: int | None = Field(default=None, foreign_key="dbo.product_categories.id", index=True)
    size: str | None = Field(default=None, max_length=100)
    material_type: str | None = Field(default=None, max_length=100)
    specification: str | None = Field(default=None, max_length=100)
    manufacturer: str | None = Field(default=None, max_length=100)
    model: str | None = Field(default=None, max_length=100)
    unit_price: float = 0
    cost: float = 0
    tax_rate: float = 0
    # pieza, hora, mes, licencia...
    unit: str = "pieza"
    min_stock: Decimal = Field(default=Decimal(0), max_digits=12, decimal_places=2)
    stock_quantity: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    family: ProductFamilies | None = Relationship(back_populates="products")
    category: ProductCategories | None = Relationship(back_populates="products")
