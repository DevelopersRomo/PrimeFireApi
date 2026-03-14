from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from api.dependencies import require_authentication
from bd.dependencies import get_db
from models.licenses import Licenses
from schemas.licenses import License, LicenseCreate, LicenseRead, LicenseUpdate

router = APIRouter()


# ----------------------------
# 📌 CREATE
# ----------------------------
@router.post("", response_model=License)
def create_license(license: LicenseCreate, db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    db_license = Licenses(**license.model_dump())
    db.add(db_license)
    db.commit()
    db.refresh(db_license)
    return db_license


# ----------------------------
# 📌 READ ALL
# ----------------------------
@router.get("", response_model=list[LicenseRead])
def get_licenses(db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    statement = select(Licenses)
    return db.exec(statement).all()


# ----------------------------
# 📌 READ ONE
# ----------------------------
@router.get("/{license_id}", response_model=License)
def get_license(license_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    db_license = db.exec(select(Licenses).filter(Licenses.LicenseId == license_id)).first()
    if not db_license:
        raise HTTPException(status_code=404, detail="License not found")
    return db_license


# ----------------------------
# 📌 UPDATE (PUT - full update)
# ----------------------------
@router.put("/{license_id}", response_model=License)
def update_license(
    license_id: int, license: LicenseCreate, db: Session = Depends(get_db), _auth=Depends(require_authentication)
):
    db_license = db.exec(select(Licenses).filter(Licenses.LicenseId == license_id)).first()
    if not db_license:
        raise HTTPException(status_code=404, detail="License not found")

    for key, value in license.model_dump().items():
        setattr(db_license, key, value)

    db.commit()
    db.refresh(db_license)
    return db_license


# ----------------------------
# 📌 UPDATE (PATCH - partial update)
# ----------------------------
@router.patch("/{license_id}", response_model=License)
def patch_license(
    license_id: int, license: LicenseUpdate, db: Session = Depends(get_db), _auth=Depends(require_authentication)
):
    db_license = db.exec(select(Licenses).filter(Licenses.LicenseId == license_id)).first()
    if not db_license:
        raise HTTPException(status_code=404, detail="License not found")

    update_data = license.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_license, key, value)

    db.commit()
    db.refresh(db_license)
    return db_license


# ----------------------------
# 📌 DELETE
# ----------------------------
@router.delete("/{license_id}")
def delete_license(license_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    db_license = db.exec(select(Licenses).filter(Licenses.LicenseId == license_id)).first()
    if not db_license:
        raise HTTPException(status_code=404, detail="License not found")

    db.delete(db_license)
    db.commit()
    return {"message": "License deleted successfully"}
