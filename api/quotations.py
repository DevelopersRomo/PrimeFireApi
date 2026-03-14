from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from api.dependencies import require_authentication
from bd.dependencies import get_db
from models.quotations import Quotations
from schemas.quotations import (
    QuotationCreate,
    QuotationRead,
    QuotationUpdate,
)

router = APIRouter(
    prefix="/quotations",
    tags=["quotations"],
)


# ----------------------------
# CREATE
# POST /quotations/
# ----------------------------
@router.post(
    "/",
    response_model=QuotationRead,
    status_code=status.HTTP_201_CREATED,
)
def create_quotation(
    quotation: QuotationCreate,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    db_quotation = Quotations(**quotation.model_dump(by_alias=False))

    db.add(db_quotation)
    db.commit()
    db.refresh(db_quotation)

    return db_quotation


# ----------------------------
# READ ALL
# GET /quotations/
# ----------------------------
@router.get("/", response_model=list[QuotationRead])
def get_quotations(
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    statement = select(Quotations)
    return db.exec(statement).all()


# ----------------------------
# READ ONE
# GET /quotations/{quotation_id}
# ----------------------------
@router.get("/{quotation_id}", response_model=QuotationRead)
def get_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    quotation = db.get(Quotations, quotation_id)

    if not quotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quotation not found",
        )

    return quotation


# ----------------------------
# UPDATE (PUT)
# PUT /quotations/{quotation_id}
# ----------------------------
@router.put("/{quotation_id}", response_model=QuotationRead)
def update_quotation(
    quotation_id: int,
    quotation: QuotationCreate,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    db_quotation = db.get(Quotations, quotation_id)

    if not db_quotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quotation not found",
        )

    data = quotation.model_dump(by_alias=False)

    for key, value in data.items():
        setattr(db_quotation, key, value)

    db.add(db_quotation)
    db.commit()
    db.refresh(db_quotation)

    return db_quotation


# ----------------------------
# PATCH
# PATCH /quotations/{quotation_id}
# ----------------------------
@router.patch("/{quotation_id}", response_model=QuotationRead)
def patch_quotation(
    quotation_id: int,
    quotation: QuotationUpdate,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    db_quotation = db.get(Quotations, quotation_id)

    if not db_quotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quotation not found",
        )

    update_data = quotation.model_dump(exclude_unset=True, by_alias=False)

    for key, value in update_data.items():
        setattr(db_quotation, key, value)

    db.add(db_quotation)
    db.commit()
    db.refresh(db_quotation)

    return db_quotation


# ----------------------------
# DELETE
# DELETE /quotations/{quotation_id}
# ----------------------------
@router.delete("/{quotation_id}", status_code=status.HTTP_200_OK)
def delete_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    quotation = db.get(Quotations, quotation_id)

    if not quotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quotation not found",
        )

    db.delete(quotation)
    db.commit()

    return {"message": "Quotation deleted successfully"}
