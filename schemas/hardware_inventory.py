from datetime import date, datetime

from pydantic import BaseModel

from schemas.employees import EmployeeRead


class HardwareInventoryBase(BaseModel):
    SerialNumber: str
    Brand: str
    Model: str | None = None
    DeviceType: str | None = None
    Processor: str | None = None
    RAM_GB: int | None = None
    StorageType: str | None = None
    StorageSize_GB: int | None = None
    GPU: str | None = None
    OperatingSystem: str | None = None
    WarrantyStartDate: date | None = None
    WarrantyEndDate: date | None = None
    PurchaseDate: date | None = None
    EmployeeId: int | None = None
    Location: str | None = None
    Status: str | None = "Active"
    Notes: str | None = None


class HardwareInventoryCreate(HardwareInventoryBase):
    pass


class HardwareInventoryUpdate(HardwareInventoryBase):
    UpdatedAt: datetime | None = datetime.utcnow()  # noqa: DTZ003


class HardwareInventoryRead(HardwareInventoryBase):
    HardwareID: int
    Employee: EmployeeRead | None
    CreatedAt: datetime
    UpdatedAt: datetime | None

    class Config:
        from_attributes = True
