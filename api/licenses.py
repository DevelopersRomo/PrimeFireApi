from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from api.dependencies import require_authentication
from bd.dependencies import get_db
from models.licenses import Licenses
from schemas.licenses import License, LicenseCreate, LicenseRead, LicenseUpdate
from schemas.pagination import PaginatedResponse

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
@router.get("", response_model=list[LicenseRead] | PaginatedResponse[LicenseRead])
def get_licenses(
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=1000),
    with_meta: bool = Query(False),
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    statement = (
        select(Licenses)
        .options(selectinload(Licenses.employee))
        .order_by(Licenses.created_at.desc(), Licenses.license_id.desc())
        .offset(skip)
        .limit(limit)
    )
    items = db.exec(statement).all()

    if not with_meta:
        return items

    total = db.exec(select(func.count()).select_from(Licenses)).one()
    return PaginatedResponse[LicenseRead](
        items=items,
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + len(items) < total,
    )


# ----------------------------
# 📌 READ ONE
# ----------------------------
@router.get("/{license_id}", response_model=License)
def get_license(license_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    db_license = db.exec(select(Licenses).filter(Licenses.license_id == license_id)).first()
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
    db_license = db.exec(select(Licenses).filter(Licenses.license_id == license_id)).first()
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
    db_license = db.exec(select(Licenses).filter(Licenses.license_id == license_id)).first()
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
    db_license = db.exec(select(Licenses).filter(Licenses.license_id == license_id)).first()
    if not db_license:
        raise HTTPException(status_code=404, detail="License not found")

    db.delete(db_license)
    db.commit()
    return {"message": "License deleted successfully"}
