from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from api.dependencies import require_authentication
from bd.dependencies import get_db
from models.products import Products
from schemas.products import (
    Product,
    ProductCreate,
    ProductRead,
    ProductUpdate,
)

router = APIRouter()


# ----------------------------
# CREATE
# ----------------------------
@router.post("", response_model=Product)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    db_product = Products(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


# ----------------------------
# READ ALL
# ----------------------------
@router.get("", response_model=list[ProductRead])
def get_products(
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    statement = select(Products)
    return db.exec(statement).all()


# ----------------------------
# READ ONE
# ----------------------------
@router.get("/{product_id}", response_model=Product)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    product = db.get(Products, product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


# ----------------------------
# UPDATE (PUT)
# ----------------------------
@router.put("/{product_id}", response_model=Product)
def update_product(
    product_id: int,
    product: ProductCreate,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    db_product = db.get(Products, product_id)

    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    for key, value in product.model_dump().items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)
    return db_product


# ----------------------------
# PATCH
# ----------------------------
@router.patch("/{product_id}", response_model=Product)
def patch_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    db_product = db.get(Products, product_id)

    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = product.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)
    return db_product


# ----------------------------
# DELETE
# ----------------------------
@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    product = db.get(Products, product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()

    return {"message": "Product deleted successfully"}
