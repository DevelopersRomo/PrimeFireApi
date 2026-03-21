from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import CheckConstraint, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.employees import Employees


class HardwareInventory(SQLModel, table=True):
    __tablename__ = "hardware_inventory"
    __table_args__ = (
        CheckConstraint("device_type IN ('Laptop', 'Desktop', 'Workstation', 'Server')"),
        CheckConstraint("storage_type IN ('HDD', 'SSD', 'NVMe', 'Hybrid')"),
        CheckConstraint("status IN ('Active', 'In Repair', 'Retired', 'Spare')"),
        {"schema": "dbo"},
    )

    hardware_id: int | None = Field(default=None, primary_key=True, index=True)
    serial_number: str = Field(max_length=50, nullable=False, unique=True)
    brand: str = Field(max_length=50, nullable=False)
    model: str | None = Field(default=None, max_length=100)
    device_type: str | None = Field(default=None, max_length=20)
    processor: str | None = Field(default=None, max_length=100)
    ram_gb: int | None = Field(default=None)
    storage_type: str | None = Field(default=None, max_length=20)
    storage_size_gb: int | None = Field(default=None)
    gpu: str | None = Field(default=None, max_length=100)
    operating_system: str | None = Field(default=None, max_length=100)
    warranty_start_date: date | None = Field(default=None)
    warranty_end_date: date | None = Field(default=None)
    purchase_date: date | None = Field(default=None)
    location: str | None = Field(default=None, max_length=100)
    status: str | None = Field(default="Active", max_length=20)
    notes: str | None = Field(default=None, max_length=255)
    created_at: datetime | None = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = Field(default=None)

    # Relationships
    employee_id: int | None = Field(default=None, foreign_key="dbo.employees.employee_id")

    employee: Optional["Employees"] = Relationship(back_populates="hardware_inventories")
