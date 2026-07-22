from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ItCategoryBase(BaseModel):
    name: str = Field(max_length=100)
    description: str | None = Field(default=None, max_length=500)
    item_type: str | None = None
    is_active: bool = True


class ItCategoryCreate(ItCategoryBase):
    pass


class ItCategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    item_type: str | None = None
    is_active: bool | None = None


class ItCategoryRead(ItCategoryBase):
    category_id: int
    tenant_id: int
    created_at: datetime
    updated_at: datetime | None = None


class ItServiceDetailsPayload(BaseModel):
    estimated_delivery_days: int | None = None
    included_hours: Decimal | None = None
    deliverables: str | None = None
    exclusions: str | None = None
    technical_requirements: str | None = None


class ItLicenseDetailsPayload(BaseModel):
    vendor: str | None = None
    vendor_product_code: str | None = None
    license_type: str | None = None
    default_seats: int | None = None
    term_months: int | None = None
    auto_renew: bool = False
    procurement_notes: str | None = None


class ItCatalogItemBase(BaseModel):
    category_id: int | None = None
    item_type: str
    code: str | None = None
    sku: str | None = None
    name: str = Field(max_length=200)
    description: str | None = None
    unit: str = "EA"
    billing_cycle: str = "ONE_TIME"
    currency: str = "USD"
    unit_price: Decimal = Decimal("0")
    cost: Decimal = Decimal("0")
    tax_rate: Decimal = Decimal("0")
    scope_template: str | None = None
    is_active: bool = True


class ItCatalogItemCreate(ItCatalogItemBase):
    service_details: ItServiceDetailsPayload | None = None
    license_details: ItLicenseDetailsPayload | None = None


class ItCatalogItemUpdate(BaseModel):
    category_id: int | None = None
    item_type: str | None = None
    code: str | None = None
    sku: str | None = None
    name: str | None = None
    description: str | None = None
    unit: str | None = None
    billing_cycle: str | None = None
    currency: str | None = None
    unit_price: Decimal | None = None
    cost: Decimal | None = None
    tax_rate: Decimal | None = None
    scope_template: str | None = None
    is_active: bool | None = None
    service_details: ItServiceDetailsPayload | None = None
    license_details: ItLicenseDetailsPayload | None = None


class ItCatalogItemRead(ItCatalogItemBase):
    catalog_item_id: int
    tenant_id: int
    created_by: int | None = None
    created_at: datetime
    updated_at: datetime | None = None
    service_details: ItServiceDetailsPayload | None = None
    license_details: ItLicenseDetailsPayload | None = None
