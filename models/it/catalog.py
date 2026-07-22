from datetime import datetime
from decimal import Decimal

from sqlmodel import Field, SQLModel

IT_ITEM_TYPES = (
    "SERVICE",
    "LICENSE",
    "HOSTING",
    "DOMAIN",
    "SSL",
    "SUBSCRIPTION",
    "SUPPORT",
    "OTHER",
)

IT_BILLING_CYCLES = ("ONE_TIME", "MONTHLY", "QUARTERLY", "ANNUAL")

IT_LICENSE_TYPES = ("PER_USER", "PER_DEVICE", "SITE", "SUBSCRIPTION")


class ITCategories(SQLModel, table=True):
    __tablename__ = "categories"
    __table_args__ = {"schema": "it"}

    category_id: int | None = Field(default=None, primary_key=True, index=True)
    tenant_id: int = Field(index=True)
    name: str = Field(max_length=100)
    description: str | None = Field(default=None, max_length=500)
    item_type: str | None = Field(default=None, max_length=30)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None


class ITCatalogItems(SQLModel, table=True):
    __tablename__ = "catalog_items"
    __table_args__ = {"schema": "it"}

    catalog_item_id: int | None = Field(default=None, primary_key=True, index=True)
    tenant_id: int = Field(index=True)
    category_id: int | None = Field(default=None, foreign_key="it.categories.category_id")
    item_type: str = Field(max_length=30)
    code: str | None = Field(default=None, max_length=100)
    sku: str | None = Field(default=None, max_length=100)
    name: str = Field(max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    unit: str = Field(default="EA", max_length=50)
    billing_cycle: str = Field(default="ONE_TIME", max_length=20)
    currency: str = Field(default="USD", max_length=3)
    unit_price: Decimal = Field(default=Decimal("0"), max_digits=18, decimal_places=2)
    cost: Decimal = Field(default=Decimal("0"), max_digits=18, decimal_places=2)
    tax_rate: Decimal = Field(default=Decimal("0"), max_digits=5, decimal_places=2)
    scope_template: str | None = None
    is_active: bool = Field(default=True)
    created_by: int | None = Field(default=None, foreign_key="dbo.employees.employee_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None


class ITServiceDetails(SQLModel, table=True):
    __tablename__ = "service_details"
    __table_args__ = {"schema": "it"}

    catalog_item_id: int = Field(primary_key=True, foreign_key="it.catalog_items.catalog_item_id")
    estimated_delivery_days: int | None = None
    included_hours: Decimal | None = Field(default=None, max_digits=10, decimal_places=2)
    deliverables: str | None = None
    exclusions: str | None = None
    technical_requirements: str | None = None


class ITLicenseDetails(SQLModel, table=True):
    __tablename__ = "license_details"
    __table_args__ = {"schema": "it"}

    catalog_item_id: int = Field(primary_key=True, foreign_key="it.catalog_items.catalog_item_id")
    vendor: str | None = Field(default=None, max_length=150)
    vendor_product_code: str | None = Field(default=None, max_length=100)
    license_type: str | None = Field(default=None, max_length=30)
    default_seats: int | None = None
    term_months: int | None = None
    auto_renew: bool = Field(default=False)
    procurement_notes: str | None = Field(default=None, max_length=1000)
