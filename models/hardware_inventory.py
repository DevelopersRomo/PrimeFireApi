from sqlmodel import SQLModel, Field, Relationship, CheckConstraint
from typing import Optional
from datetime import datetime, date

if __name__ == "models.hardware_inventory":
    from models.employees import Employees


class HardwareInventory(SQLModel, table=True):
    __tablename__ = "HardwareInventory"
    __table_args__ = (
        CheckConstraint("DeviceType IN ('Laptop', 'Desktop', 'Workstation', 'Server')"),
        CheckConstraint("StorageType IN ('HDD', 'SSD', 'NVMe', 'Hybrid')"),
        CheckConstraint("Status IN ('Active', 'In Repair', 'Retired', 'Spare')"),
        {'schema': 'dbo'},  # ✅ El diccionario siempre al final
    )

    HardwareID: Optional[int] = Field(default=None, primary_key=True, index=True)
    SerialNumber: str = Field(max_length=50, nullable=False, unique=True)
    Brand: str = Field(max_length=50, nullable=False)
    Model: Optional[str] = Field(default=None, max_length=100)
    DeviceType: Optional[str] = Field(default=None, max_length=20)
    Processor: Optional[str] = Field(default=None, max_length=100)
    RAM_GB: Optional[int] = Field(default=None)
    StorageType: Optional[str] = Field(default=None, max_length=20)
    StorageSize_GB: Optional[int] = Field(default=None)
    GPU: Optional[str] = Field(default=None, max_length=100)
    OperatingSystem: Optional[str] = Field(default=None, max_length=100)
    WarrantyStartDate: Optional[date] = Field(default=None)
    WarrantyEndDate: Optional[date] = Field(default=None)
    PurchaseDate: Optional[date] = Field(default=None)
    EmployeeId: Optional[int] = Field(default=None, foreign_key="dbo.Employees.EmployeeId")
    Location: Optional[str] = Field(default=None, max_length=100)
    Status: Optional[str] = Field(default="Active", max_length=20)
    Notes: Optional[str] = Field(default=None, max_length=255)
    CreatedAt: Optional[datetime] = Field(default_factory=datetime.utcnow)
    UpdatedAt: Optional[datetime] = Field(default=None)

    # Relationships
    employee: Optional["Employees"] = Relationship(back_populates="hardware_devices")
