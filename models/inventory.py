from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class Warehouses(SQLModel, table=True):
    __tablename__ = "warehouses"
    __table_args__ = {"schema": "dbo"}

    warehouse_id: int | None = Field(default=None, primary_key=True, index=True)
    name: str = Field(max_length=100)
    location_id: int | None = Field(default=None, foreign_key="dbo.warehouse_locations.warehouse_location_id")
    location: str | None = Field(default=None, max_length=200)
    is_active: bool = Field(default=True)

    location_ref: Optional["WarehouseLocations"] = Relationship(back_populates="warehouses")
    movements: list["InventoryMovements"] = Relationship(back_populates="warehouse")


class WarehouseLocations(SQLModel, table=True):
    __tablename__ = "warehouse_locations"
    __table_args__ = {"schema": "dbo"}

    warehouse_location_id: int | None = Field(default=None, primary_key=True, index=True)
    name: str = Field(max_length=200, unique=True, index=True)
    is_active: bool = Field(default=True)

    warehouses: list[Warehouses] = Relationship(back_populates="location_ref")


class InventoryMovementApprovals(SQLModel, table=True):
    __tablename__ = "inventory_movement_approvals"
    __table_args__ = {"schema": "dbo"}

    approval_id: int | None = Field(default=None, primary_key=True, index=True)

    product_id: int = Field(foreign_key="dbo.products.id")
    warehouse_id: int | None = Field(default=None, foreign_key="dbo.warehouses.warehouse_id")

    movement_type: str = Field(max_length=20)  # OUT, ADJUSTMENT
    quantity: Decimal = Field(max_digits=18, decimal_places=2)

    movement_date: date = Field(default_factory=date.today)

    project: str | None = Field(default=None, max_length=150)
    po_number: str | None = Field(default=None, max_length=100)

    reference_type: str | None = Field(default=None, max_length=50)
    reference_id: int | None = Field(default=None)

    notes: str | None = Field(default=None, max_length=500)

    status: str = Field(default="PENDING", max_length=20)  # PENDING, APPROVED, REJECTED
    requested_by: str | None = Field(default=None, max_length=100)
    requested_by_email: str | None = Field(default=None, max_length=255)
    review_note: str | None = Field(default=None, max_length=500)
    reviewed_by: str | None = Field(default=None, max_length=100)
    reviewed_at: datetime | None = Field(default=None)
    movement_id: int | None = Field(default=None, foreign_key="dbo.inventory_movements.movement_id")
    created_at: datetime = Field(default_factory=datetime.now)


class InventoryMovements(SQLModel, table=True):
    __tablename__ = "inventory_movements"
    __table_args__ = {"schema": "dbo"}

    movement_id: int | None = Field(default=None, primary_key=True, index=True)

    product_id: int = Field(foreign_key="dbo.products.id")
    warehouse_id: int | None = Field(default=None, foreign_key="dbo.warehouses.warehouse_id")

    movement_type: str = Field(max_length=20)  # IN, OUT, ADJUSTMENT
    quantity: Decimal = Field(max_digits=18, decimal_places=2)

    movement_date: date = Field(default_factory=date.today)

    project: str | None = Field(default=None, max_length=150)
    po_number: str | None = Field(default=None, max_length=100)

    reference_type: str | None = Field(default=None, max_length=50)
    reference_id: int | None = Field(default=None)

    notes: str | None = Field(default=None, max_length=500)
    created_by: str | None = Field(default=None, max_length=100)
    created_at: datetime = Field(default_factory=datetime.now)

    warehouse: Optional["Warehouses"] = Relationship(back_populates="movements")
