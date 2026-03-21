from datetime import date, datetime

from pydantic import BaseModel

from schemas.employees import EmployeeRead


class HardwareInventoryBase(BaseModel):
    serial_number: str
    brand: str
    model: str | None = None
    device_type: str | None = None
    processor: str | None = None
    ram_gb: int | None = None
    storage_type: str | None = None
    storage_size_gb: int | None = None
    gpu: str | None = None
    operating_system: str | None = None
    warranty_start_date: date | None = None
    warranty_end_date: date | None = None
    purchase_date: date | None = None
    employee_id: int | None = None
    location: str | None = None
    status: str | None = "Active"
    notes: str | None = None


class HardwareInventoryCreate(HardwareInventoryBase):
    pass


class HardwareInventoryUpdate(HardwareInventoryBase):
    updated_at: datetime | None = datetime.utcnow()


class HardwareInventoryRead(HardwareInventoryBase):
    hardware_id: int
    employee: EmployeeRead | None
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True
