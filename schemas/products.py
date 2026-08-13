from datetime import datetime
from decimal import Decimal
from typing import Annotated

from sqlmodel import Field, SQLModel

Money = Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=2)]
TaxRate = Annotated[Decimal, Field(ge=0, le=100, max_digits=5, decimal_places=2)]


class ProductFamilyCreate(SQLModel):
    name: str
    description: str | None = None
    active: bool = True


class ProductFamilyUpdate(SQLModel):
    name: str | None = None
    description: str | None = None
    active: bool | None = None


class ProductFamilyRead(SQLModel):
    id: int
    name: str
    description: str | None = None
    active: bool
    created_at: datetime


class ProductCategoryCreate(SQLModel):
    family_id: int
    name: str
    description: str | None = None
    active: bool = True


class ProductCategoryUpdate(SQLModel):
    family_id: int | None = None
    name: str | None = None
    description: str | None = None
    active: bool | None = None


class ProductCategoryRead(SQLModel):
    id: int
    family_id: int
    name: str
    description: str | None = None
    active: bool


class ProductSpecificationCreate(SQLModel):
    product_id: int | None = None
    specification: str | None = None
    size: str | None = None
    material: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    notes: str | None = None


class ProductSpecificationUpdate(SQLModel):
    product_id: int | None = None
    specification: str | None = None
    size: str | None = None
    material: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    notes: str | None = None


class ProductSpecificationRead(ProductSpecificationCreate):
    id: int
    product_id: int | None = None


class ProductSpecificationOptionRead(SQLModel):
    id: int
    product_id: int | None = None
    specification: str
    size: str | None = None
    material: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    notes: str | None = None


class ProductCatalogCreate(SQLModel):
    code: str
    name: str
    family_id: int | None = None
    category_id: int | None = None
    unit: str | None = None
    min_stock: Decimal = Decimal(0)
    active: bool = True
    description: str | None = None
    specification: ProductSpecificationCreate | None = None


class ProductCatalogUpdate(SQLModel):
    code: str | None = None
    name: str | None = None
    family_id: int | None = None
    category_id: int | None = None
    unit: str | None = None
    min_stock: Decimal | None = None
    active: bool | None = None
    description: str | None = None
    specification: ProductSpecificationCreate | None = None


class ProductCatalogRead(SQLModel):
    id: int
    code: str
    name: str
    family_id: int | None = None
    category_id: int | None = None
    family_name: str | None = None
    category_name: str | None = None
    unit: str | None = None
    min_stock: Decimal
    active: bool
    description: str | None = None
    created_at: datetime
    specification: ProductSpecificationRead | None = None


class ProductCreate(SQLModel):
    name: str = Field(max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    type: str = Field(max_length=50)
    sku: str | None = Field(default=None, max_length=100)
    code: str | None = Field(default=None, max_length=50)
    family_id: int | None = None
    category_id: int | None = None
    size: str | None = Field(default=None, max_length=100)
    material_type: str | None = Field(default=None, max_length=100)
    specification: str | None = Field(default=None, max_length=100)
    manufacturer: str | None = Field(default=None, max_length=100)
    model: str | None = Field(default=None, max_length=100)
    unit_price: Money = Decimal("0.00")
    cost: Money = Decimal("0.00")
    tax_rate: TaxRate = Decimal("0.00")
    unit: str = Field(default="pieza", max_length=20)

    is_active: bool = True


class ProductUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    type: str | None = Field(default=None, max_length=50)
    sku: str | None = Field(default=None, max_length=100)
    code: str | None = Field(default=None, max_length=50)
    family_id: int | None = None
    category_id: int | None = None
    size: str | None = Field(default=None, max_length=100)
    material_type: str | None = Field(default=None, max_length=100)
    specification: str | None = Field(default=None, max_length=100)
    manufacturer: str | None = Field(default=None, max_length=100)
    model: str | None = Field(default=None, max_length=100)
    unit_price: Money | None = None
    cost: Money | None = None
    tax_rate: TaxRate | None = None
    unit: str | None = Field(default=None, max_length=20)

    is_active: bool | None = None


class ProductRead(SQLModel):
    id: int
    name: str
    description: str | None = None
    type: str
    sku: str | None = None
    code: str | None = None
    family_id: int | None = None
    category_id: int | None = None
    family_name: str | None = None
    category_name: str | None = None
    size: str | None = None
    material_type: str | None = None
    specification: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    unit_price: float
    cost: float
    tax_rate: float
    unit: str

    is_active: bool
    created_at: datetime


class Product(ProductRead):
    pass


class ProductEmployee(SQLModel):
    employee_id: int
    display_name: str | None = None
    email: str | None = None
    title: str | None = None


class ProductAttachment(SQLModel):
    product_attachment_id: int | None = None
    product_id: int
    file_name: str
    file_type: str | None = None
    file_path: str | None = None
    created_at: datetime
    created_by: int
    creator: ProductEmployee | None = None
