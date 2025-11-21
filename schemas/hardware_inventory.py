from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel


class HardwareInventoryBase(BaseModel):
    SerialNumber: str
    Brand: str
    Model: Optional[str] = None
    DeviceType: Optional[str] = None
    Processor: Optional[str] = None
    RAM_GB: Optional[int] = None
    StorageType: Optional[str] = None
    StorageSize_GB: Optional[int] = None
    GPU: Optional[str] = None
    OperatingSystem: Optional[str] = None
    WarrantyStartDate: Optional[date] = None
    WarrantyEndDate: Optional[date] = None
    PurchaseDate: Optional[date] = None
    EmployeeId: Optional[int] = None
    Location: Optional[str] = None
    Status: Optional[str] = "Active"
    Notes: Optional[str] = None


class HardwareInventoryCreate(HardwareInventoryBase):
    pass


class HardwareInventoryUpdate(HardwareInventoryBase):
    UpdatedAt: Optional[datetime] = datetime.utcnow()


class HardwareInventoryRead(HardwareInventoryBase):
    HardwareID: int
    CreatedAt: datetime
    UpdatedAt: Optional[datetime]

    class Config:
        from_attributes = True
