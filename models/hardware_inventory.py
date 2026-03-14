from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import CheckConstraint, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.employees import Employees

if __name__ == "models.hardware_inventory":
    pass


class HardwareInventory(SQLModel, table=True):
    __tablename__ = "HardwareInventory"
    __table_args__ = (
        CheckConstraint("DeviceType IN ('Laptop', 'Desktop', 'Workstation', 'Server')"),
        CheckConstraint("StorageType IN ('HDD', 'SSD', 'NVMe', 'Hybrid')"),
        CheckConstraint("Status IN ('Active', 'In Repair', 'Retired', 'Spare')"),
        {"schema": "dbo"},  # ✅ El diccionario siempre al final
    )

    HardwareID: int | None = Field(default=None, primary_key=True, index=True)
    SerialNumber: str = Field(max_length=50, nullable=False, unique=True)
    Brand: str = Field(max_length=50, nullable=False)
    Model: str | None = Field(default=None, max_length=100)
    DeviceType: str | None = Field(default=None, max_length=20)
    Processor: str | None = Field(default=None, max_length=100)
    RAM_GB: int | None = Field(default=None)
    StorageType: str | None = Field(default=None, max_length=20)
    StorageSize_GB: int | None = Field(default=None)
    GPU: str | None = Field(default=None, max_length=100)
    OperatingSystem: str | None = Field(default=None, max_length=100)
    WarrantyStartDate: date | None = Field(default=None)
    WarrantyEndDate: date | None = Field(default=None)
    PurchaseDate: date | None = Field(default=None)
    Location: str | None = Field(default=None, max_length=100)
    Status: str | None = Field(default="Active", max_length=20)
    Notes: str | None = Field(default=None, max_length=255)
    CreatedAt: datetime | None = Field(default_factory=datetime.utcnow)
    UpdatedAt: datetime | None = Field(default=None)

    # Relationships
    EmployeeId: int | None = Field(default=None, foreign_key="dbo.Employees.EmployeeId")

    Employee: Optional["Employees"] = Relationship(back_populates="hardware_inventories")
