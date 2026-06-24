from datetime import date, datetime
from decimal import Decimal

from sqlmodel import SQLModel


class WarehouseCreate(SQLModel):
    name: str
    location_id: int | None = None
    location: str | None = None
    is_active: bool = True


class WarehouseUpdate(SQLModel):
    name: str | None = None
    location_id: int | None = None
    location: str | None = None
    is_active: bool | None = None


class Warehouse(SQLModel):
    warehouse_id: int | None = None
    name: str
    location_id: int | None = None
    location: str | None = None
    is_active: bool = True


class WarehouseLocationCreate(SQLModel):
    name: str


class WarehouseLocationUpdate(SQLModel):
    name: str | None = None
    is_active: bool | None = None


class WarehouseLocation(SQLModel):
    warehouse_location_id: int | None = None
    name: str
    is_active: bool = True


class InventoryMovementCreate(SQLModel):
    product_id: int
    warehouse_id: int | None = None
    movement_type: str  # IN, OUT, ADJUSTMENT
    quantity: Decimal
    movement_date: date | None = None
    project: str | None = None
    po_number: str | None = None
    reference_type: str | None = None
    reference_id: int | None = None
    notes: str | None = None
    min_stock: Decimal | None = None


class InventoryMovement(SQLModel):
    movement_id: int | None = None
    product_id: int
    warehouse_id: int | None = None
    movement_type: str
    quantity: Decimal
    movement_date: date | None = None
    project: str | None = None
    po_number: str | None = None
    reference_type: str | None = None
    reference_id: int | None = None
    notes: str | None = None
    created_by: str | None = None
    created_at: datetime | None = None

    product_name: str | None = None
    product_code: str | None = None
    warehouse_name: str | None = None
    min_stock: Decimal | None = None


class InventoryStock(SQLModel):
    product_id: int
    code: str | None = None
    name: str | None = None
    family: str | None = None
    category: str | None = None
    size: str | None = None
    material_type: str | None = None
    unit: str | None = None
    min_stock: Decimal | None = None
    needed_quantity: Decimal | None = None
    total_in: Decimal = Decimal(0)
    total_out: Decimal = Decimal(0)
    total_adjustment: Decimal = Decimal(0)
    stock_on_hand: Decimal = Decimal(0)
    status: str | None = None
