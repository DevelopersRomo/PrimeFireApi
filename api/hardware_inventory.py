from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from api.dependencies import require_authentication
from bd.dependencies import get_db
from models.hardware_inventory import HardwareInventory
from schemas.hardware_inventory import HardwareInventoryRead, HardwareInventoryCreate, HardwareInventoryUpdate

router = APIRouter()

# ----------------------------
# 📌 CREATE
# ----------------------------
@router.post("/", response_model=HardwareInventoryRead)
def create_hardware(
    hardware: HardwareInventoryCreate,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication)
):
    db_hardware = HardwareInventory(**hardware.model_dump())
    db.add(db_hardware)
    db.commit()
    db.refresh(db_hardware)
    return db_hardware


# ----------------------------
# 📌 READ ALL
# ----------------------------
@router.get("/", response_model=List[HardwareInventoryRead])
def get_hardware_list(
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication)
):
    return db.exec(select(HardwareInventory)).all()


# ----------------------------
# 📌 READ ONE
# ----------------------------
@router.get("/{hardware_id}", response_model=HardwareInventoryRead)
def get_hardware(
    hardware_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication)
):
    db_hardware = db.exec(
        select(HardwareInventory).filter(HardwareInventory.HardwareID == hardware_id)
    ).first()
    if not db_hardware:
        raise HTTPException(status_code=404, detail="Hardware not found")
    return db_hardware


# ----------------------------
# 📌 UPDATE
# ----------------------------
@router.put("/{hardware_id}", response_model=HardwareInventoryRead)
def update_hardware(
    hardware_id: int,
    hardware: HardwareInventoryUpdate,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication)
):
    db_hardware = db.exec(
        select(HardwareInventory).filter(HardwareInventory.HardwareID == hardware_id)
    ).first()
    if not db_hardware:
        raise HTTPException(status_code=404, detail="Hardware not found")

    for key, value in hardware.model_dump(exclude_unset=True).items():
        setattr(db_hardware, key, value)

    db_hardware.UpdatedAt = hardware.UpdatedAt or None
    db.commit()
    db.refresh(db_hardware)
    return db_hardware


# ----------------------------
# 📌 DELETE
# ----------------------------
@router.delete("/{hardware_id}")
def delete_hardware(
    hardware_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication)
):
    db_hardware = db.exec(
        select(HardwareInventory).filter(HardwareInventory.HardwareID == hardware_id)
    ).first()
    if not db_hardware:
        raise HTTPException(status_code=404, detail="Hardware not found")

    db.delete(db_hardware)
    db.commit()
    return {"message": "Hardware deleted successfully"}
