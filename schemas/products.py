from datetime import datetime
from decimal import Decimal

from sqlmodel import SQLModel


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
    name: str
    description: str | None = None
    type: str
    sku: str | None = None
    code: str | None = None
    family_id: int | None = None
    category_id: int | None = None
    size: str | None = None
    material_type: str | None = None
    specification: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    unit_price: float = 0
    cost: float = 0
    tax_rate: float = 0
    unit: str = "pieza"

    is_active: bool = True


class ProductUpdate(SQLModel):
    name: str | None = None
    description: str | None = None
    type: str | None = None
    sku: str | None = None
    code: str | None = None
    family_id: int | None = None
    category_id: int | None = None
    size: str | None = None
    material_type: str | None = None
    specification: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    unit_price: float | None = None
    cost: float | None = None
    tax_rate: float | None = None
    unit: str | None = None

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
