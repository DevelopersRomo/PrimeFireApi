from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from api.dependencies import require_authentication
from bd.dependencies import get_db
from models.inventory import InventoryMovements, Warehouses
from models.products import Products
from schemas.inventory import (
    InventoryMovement,
    InventoryMovementCreate,
    InventoryStock,
    Warehouse,
    WarehouseCreate,
    WarehouseUpdate,
)

router = APIRouter()


VALID_MOVEMENT_TYPES = {"IN", "OUT", "ADJUSTMENT"}


def get_current_stock(db: Session, product_id: int, warehouse_id: int | None = None) -> Decimal:
    query = select(InventoryMovements).where(InventoryMovements.product_id == product_id)

    if warehouse_id is not None:
        query = query.where(InventoryMovements.warehouse_id == warehouse_id)

    movements = db.exec(query).all()

    stock = Decimal("0")

    for movement in movements:
        if movement.movement_type == "IN":
            stock += movement.quantity
        elif movement.movement_type == "OUT":
            stock -= movement.quantity
        elif movement.movement_type == "ADJUSTMENT":
            stock += movement.quantity

    return stock


def movement_to_schema(db: Session, movement: InventoryMovements) -> InventoryMovement:
    product = db.exec(select(Products).where(Products.id == movement.product_id)).first()

    warehouse = None
    if movement.warehouse_id:
        warehouse = db.exec(select(Warehouses).where(Warehouses.warehouse_id == movement.warehouse_id)).first()

    return InventoryMovement(
        movement_id=movement.movement_id,
        product_id=movement.product_id,
        warehouse_id=movement.warehouse_id,
        movement_type=movement.movement_type,
        quantity=movement.quantity,
        movement_date=movement.movement_date,
        project=movement.project,
        po_number=movement.po_number,
        reference_type=movement.reference_type,
        reference_id=movement.reference_id,
        notes=movement.notes,
        created_by=movement.created_by,
        created_at=movement.created_at,
        product_name=product.name if product else None,
        product_code=getattr(product, "code", None) if product else None,
        warehouse_name=warehouse.name if warehouse else None,
    )


# ----------------------------
# WAREHOUSES
# ----------------------------

@router.get("/warehouses", response_model=list[Warehouse])
def get_warehouses(db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    warehouses = db.exec(select(Warehouses)).all()
    return warehouses


@router.get("/warehouses/{warehouse_id}", response_model=Warehouse)
def get_warehouse(
    warehouse_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    warehouse = db.exec(select(Warehouses).where(Warehouses.warehouse_id == warehouse_id)).first()

    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")

    return warehouse


@router.post("/warehouses", response_model=Warehouse)
def create_warehouse(
    warehouse: WarehouseCreate,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    db_warehouse = Warehouses(**warehouse.model_dump())

    db.add(db_warehouse)
    db.commit()
    db.refresh(db_warehouse)

    return db_warehouse


@router.patch("/warehouses/{warehouse_id}", response_model=Warehouse)
def update_warehouse(
    warehouse_id: int,
    warehouse: WarehouseUpdate,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    db_warehouse = db.exec(select(Warehouses).where(Warehouses.warehouse_id == warehouse_id)).first()

    if not db_warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")

    update_data = warehouse.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_warehouse, key, value)

    db.commit()
    db.refresh(db_warehouse)

    return db_warehouse


@router.delete("/warehouses/{warehouse_id}")
def delete_warehouse(
    warehouse_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    db_warehouse = db.exec(select(Warehouses).where(Warehouses.warehouse_id == warehouse_id)).first()

    if not db_warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")

    has_movements = db.exec(
        select(InventoryMovements).where(InventoryMovements.warehouse_id == warehouse_id)
    ).first()

    if has_movements:
        raise HTTPException(
            status_code=400,
            detail="Warehouse cannot be deleted because it has inventory movements",
        )

    db.delete(db_warehouse)
    db.commit()

    return {"message": "Warehouse deleted successfully"}


# ----------------------------
# MOVEMENTS
# ----------------------------

@router.get("/movements", response_model=list[InventoryMovement])
def get_inventory_movements(
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    movements = db.exec(
        select(InventoryMovements).order_by(InventoryMovements.created_at.desc())
    ).all()

    return [movement_to_schema(db, movement) for movement in movements]


@router.get("/movements/{movement_id}", response_model=InventoryMovement)
def get_inventory_movement(
    movement_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    movement = db.exec(
        select(InventoryMovements).where(InventoryMovements.movement_id == movement_id)
    ).first()

    if not movement:
        raise HTTPException(status_code=404, detail="Inventory movement not found")

    return movement_to_schema(db, movement)


@router.post("/movements", response_model=InventoryMovement)
def create_inventory_movement(
    movement: InventoryMovementCreate,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    movement_type = movement.movement_type.upper().strip()

    if movement_type not in VALID_MOVEMENT_TYPES:
        raise HTTPException(status_code=400, detail="movement_type must be IN, OUT, or ADJUSTMENT")

    if movement.quantity <= 0 and movement_type in {"IN", "OUT"}:
        raise HTTPException(status_code=400, detail="quantity must be greater than zero")

    product = db.exec(select(Products).where(Products.id == movement.product_id)).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if movement.warehouse_id:
        warehouse = db.exec(select(Warehouses).where(Warehouses.warehouse_id == movement.warehouse_id)).first()
        if not warehouse:
            raise HTTPException(status_code=404, detail="Warehouse not found")

    if movement_type == "OUT":
        current_stock = get_current_stock(db, movement.product_id, movement.warehouse_id)

        if current_stock < movement.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock. Available: {current_stock}",
            )

    data = movement.model_dump()
    data["movement_type"] = movement_type

    db_movement = InventoryMovements(**data)

    db.add(db_movement)
    db.commit()
    db.refresh(db_movement)

    return movement_to_schema(db, db_movement)


@router.post("/entries", response_model=InventoryMovement)
def create_inventory_entry(
    movement: InventoryMovementCreate,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    movement.movement_type = "IN"
    return create_inventory_movement(movement, db, _auth)


@router.post("/outputs", response_model=InventoryMovement)
def create_inventory_output(
    movement: InventoryMovementCreate,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    movement.movement_type = "OUT"
    return create_inventory_movement(movement, db, _auth)


@router.post("/adjustments", response_model=InventoryMovement)
def create_inventory_adjustment(
    movement: InventoryMovementCreate,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    movement.movement_type = "ADJUSTMENT"

    if movement.quantity == 0:
        raise HTTPException(status_code=400, detail="Adjustment quantity cannot be zero")

    return create_inventory_movement(movement, db, _auth)


# ----------------------------
# STOCK
# ----------------------------

@router.get("/stock", response_model=list[InventoryStock])
def get_inventory_stock(
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    products = db.exec(select(Products)).all()

    result: list[InventoryStock] = []

    for product in products:
        movements = db.exec(
            select(InventoryMovements).where(InventoryMovements.product_id == product.id)
        ).all()

        total_in = Decimal("0")
        total_out = Decimal("0")
        total_adjustment = Decimal("0")

        for movement in movements:
            if movement.movement_type == "IN":
                total_in += movement.quantity
            elif movement.movement_type == "OUT":
                total_out += movement.quantity
            elif movement.movement_type == "ADJUSTMENT":
                total_adjustment += movement.quantity

        stock_on_hand = total_in - total_out + total_adjustment

        min_stock = getattr(product, "min_stock", None)
        if stock_on_hand <= 0:
            status = "Out of Stock"
        elif min_stock is not None and stock_on_hand < min_stock:
            status = "Low Stock"
        else:
            status = "Active"

        result.append(
            InventoryStock(
                product_id=product.id,
                code=getattr(product, "code", None),
                name=product.name,
                family=getattr(product, "family", None),
                category=getattr(product, "category", None),
                size=getattr(product, "size", None),
                material_type=getattr(product, "material_type", None),
                unit=getattr(product, "unit", None),
                min_stock=min_stock,
                needed_quantity=getattr(product, "needed_quantity", None),
                total_in=total_in,
                total_out=total_out,
                total_adjustment=total_adjustment,
                stock_on_hand=stock_on_hand,
                status=status,
            )
        )

    return result


@router.get("/stock/{product_id}", response_model=InventoryStock)
def get_product_stock(
    product_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    stock_items = get_inventory_stock(db, _auth)

    for item in stock_items:
        if item.product_id == product_id:
            return item

    raise HTTPException(status_code=404, detail="Product not found")
