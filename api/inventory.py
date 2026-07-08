from decimal import Decimal

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from api.dependencies import get_current_employee, require_authentication
from bd.dependencies import get_db
from models.employees import Employees
from models.inventory import InventoryMovements, WarehouseLocations, Warehouses
from models.products import ProductCategories, ProductFamilies, Products
from schemas.inventory import (
    InventoryMovement,
    InventoryMovementCreate,
    InventoryStock,
    Warehouse,
    WarehouseCreate,
    WarehouseLocation,
    WarehouseLocationCreate,
    WarehouseLocationUpdate,
    WarehouseUpdate,
)
from services.notifications.notifications import notify_inventory_movement

router = APIRouter()


VALID_MOVEMENT_TYPES = {"IN", "OUT", "ADJUSTMENT"}

# Roles that must BOTH be present for an employee to receive inventory movement notifications
INVENTORY_NOTIFICATION_ROLES = {"project manager", "business proposals"}

# Admins receive inventory movement notifications regardless of warehouse match
ADMIN_ROLE = "admin"

# ISO 3166-1 alpha-2 codes to full country/territory names (mirrors frontend warehouse-scope.util.ts)
COUNTRY_CODE_MAP = {
    "af": "afghanistan", "al": "albania", "dz": "algeria", "ar": "argentina", "au": "australia",
    "at": "austria", "be": "belgium", "bo": "bolivia", "br": "brazil", "ca": "canada",
    "cl": "chile", "cn": "china", "co": "colombia", "cr": "costa rica", "cu": "cuba",
    "do": "dominican republic", "ec": "ecuador", "eg": "egypt", "sv": "el salvador",
    "fr": "france", "de": "germany", "gt": "guatemala", "hn": "honduras", "in": "india",
    "ie": "ireland", "il": "israel", "it": "italy", "jm": "jamaica", "jp": "japan",
    "mx": "mexico", "nl": "netherlands", "nz": "new zealand", "ni": "nicaragua",
    "ng": "nigeria", "no": "norway", "pa": "panama", "py": "paraguay", "pe": "peru",
    "ph": "philippines", "pl": "poland", "pt": "portugal", "pr": "puerto rico",
    "ru": "russia", "es": "spain", "se": "sweden", "ch": "switzerland", "tr": "turkey",
    "gb": "united kingdom", "us": "united states", "uy": "uruguay", "ve": "venezuela",
    "vi": "us virgin islands",
}


def normalize_country(value: str | None) -> str:
    lower = (value or "").strip().lower()
    return COUNTRY_CODE_MAP.get(lower, lower)


def get_movement_notification_emails(db: Session, warehouse: Warehouses) -> list[str]:
    """Admins always receive; Project Manager + Business Proposals only when city/country match the warehouse."""
    warehouse_city = (warehouse.name or "").strip().lower()
    warehouse_country = normalize_country(warehouse.location)

    employees = db.exec(
        select(Employees).options(selectinload(Employees.roles), selectinload(Employees.country))
    ).all()

    emails = []
    for employee in employees:
        if not employee.email:
            continue
        role_names = {(role.role_name or "").strip().lower() for role in employee.roles}

        if ADMIN_ROLE in role_names:
            emails.append(employee.email)
            continue

        if not INVENTORY_NOTIFICATION_ROLES.issubset(role_names):
            continue
        if not warehouse_city or not warehouse_country:
            continue
        employee_city = (employee.city or "").strip().lower()
        employee_country = normalize_country(employee.country.name if employee.country else None)
        if employee_city == warehouse_city and employee_country == warehouse_country:
            emails.append(employee.email)

    return emails


def get_current_stock(db: Session, product_id: int, warehouse_id: int | None = None) -> Decimal:
    query = select(InventoryMovements).where(InventoryMovements.product_id == product_id)

    if warehouse_id is not None:
        query = query.where(InventoryMovements.warehouse_id == warehouse_id)

    movements = db.exec(query).all()

    stock = Decimal(0)

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
        min_stock=product.min_stock if product else None,
    )


def get_product_family_name(db: Session, product: Products) -> str | None:
    if not product.family_id:
        return None
    family = db.get(ProductFamilies, product.family_id)
    return family.name if family else None


def get_product_category_name(db: Session, product: Products) -> str | None:
    if not product.category_id:
        return None
    category = db.get(ProductCategories, product.category_id)
    return category.name if category else None


def normalize_location_name(name: str) -> str:
    normalized = name.strip()
    if not normalized:
        raise HTTPException(status_code=400, detail="Location name is required")
    if len(normalized) > 200:
        raise HTTPException(status_code=400, detail="Location name cannot exceed 200 characters")
    return normalized


def get_location_by_id(db: Session, location_id: int | None) -> WarehouseLocations | None:
    if location_id is None:
        return None
    location = db.exec(
        select(WarehouseLocations).where(WarehouseLocations.warehouse_location_id == location_id)
    ).first()
    if not location:
        raise HTTPException(status_code=404, detail="Warehouse location not found")
    return location


def get_existing_location_by_name(db: Session, name: str) -> WarehouseLocations | None:
    normalized = normalize_location_name(name)
    return db.exec(select(WarehouseLocations).where(func.lower(WarehouseLocations.name) == normalized.lower())).first()


# ----------------------------
# WAREHOUSE LOCATIONS
# ----------------------------


@router.get("/warehouse-locations", response_model=list[WarehouseLocation])
def get_warehouse_locations(
    search: str | None = Query(default=None),
    active_only: bool = True,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    query = select(WarehouseLocations)

    if active_only:
        query = query.where(WarehouseLocations.is_active == True)  # noqa: E712

    if search:
        query = query.where(func.lower(WarehouseLocations.name).contains(search.strip().lower()))

    return db.exec(query.order_by(WarehouseLocations.name)).all()


@router.post("/warehouse-locations", response_model=WarehouseLocation)
def create_warehouse_location(
    location: WarehouseLocationCreate,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    name = normalize_location_name(location.name)
    existing = get_existing_location_by_name(db, name)

    if existing:
        raise HTTPException(status_code=400, detail="Warehouse location already exists")

    db_location = WarehouseLocations(name=name, is_active=True)
    db.add(db_location)
    db.commit()
    db.refresh(db_location)

    return db_location


@router.patch("/warehouse-locations/{location_id}", response_model=WarehouseLocation)
def update_warehouse_location(
    location_id: int,
    location: WarehouseLocationUpdate,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    db_location = get_location_by_id(db, location_id)
    if not db_location:
        raise HTTPException(status_code=404, detail="Warehouse location not found")

    if location.name is not None:
        name = normalize_location_name(location.name)
        existing = get_existing_location_by_name(db, name)
        if existing and existing.warehouse_location_id != location_id:
            raise HTTPException(status_code=400, detail="Warehouse location already exists")
        db_location.name = name

    if location.is_active is not None:
        db_location.is_active = location.is_active

    db.commit()
    db.refresh(db_location)

    return db_location


# ----------------------------
# WAREHOUSES
# ----------------------------


@router.get("/warehouses", response_model=list[Warehouse])
def get_warehouses(db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    return db.exec(select(Warehouses)).all()


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
    data = warehouse.model_dump()
    location = get_location_by_id(db, warehouse.location_id)

    if location:
        data["location"] = location.name
    elif warehouse.location:
        existing_location = get_existing_location_by_name(db, warehouse.location)
        if not existing_location:
            existing_location = WarehouseLocations(name=normalize_location_name(warehouse.location))
            db.add(existing_location)
            db.commit()
            db.refresh(existing_location)
        data["location_id"] = existing_location.warehouse_location_id
        data["location"] = existing_location.name

    db_warehouse = Warehouses(**data)

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

    if "location_id" in update_data:
        location = get_location_by_id(db, warehouse.location_id)
        update_data["location"] = location.name if location else None
    elif warehouse.location:
        existing_location = get_existing_location_by_name(db, warehouse.location)
        if not existing_location:
            existing_location = WarehouseLocations(name=normalize_location_name(warehouse.location))
            db.add(existing_location)
            db.commit()
            db.refresh(existing_location)
        update_data["location_id"] = existing_location.warehouse_location_id
        update_data["location"] = existing_location.name

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

    has_movements = db.exec(select(InventoryMovements).where(InventoryMovements.warehouse_id == warehouse_id)).first()

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
    movements = db.exec(select(InventoryMovements).order_by(InventoryMovements.created_at.desc())).all()

    return [movement_to_schema(db, movement) for movement in movements]


@router.get("/movements/{movement_id}", response_model=InventoryMovement)
def get_inventory_movement(
    movement_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    movement = db.exec(select(InventoryMovements).where(InventoryMovements.movement_id == movement_id)).first()

    if not movement:
        raise HTTPException(status_code=404, detail="Inventory movement not found")

    return movement_to_schema(db, movement)


@router.post("/movements", response_model=InventoryMovement)
def create_inventory_movement(
    movement: InventoryMovementCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
):
    movement_type = movement.movement_type.upper().strip()

    if movement_type not in VALID_MOVEMENT_TYPES:
        raise HTTPException(status_code=400, detail="movement_type must be IN, OUT, or ADJUSTMENT")

    if movement.quantity <= 0 and movement_type in {"IN", "OUT"}:
        raise HTTPException(status_code=400, detail="quantity must be greater than zero")

    product = db.exec(select(Products).where(Products.id == movement.product_id)).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    warehouse = None
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

    data = movement.model_dump(exclude={"min_stock"})
    data["movement_type"] = movement_type
    data["created_by"] = current_employee.display_name

    db_movement = InventoryMovements(**data)

    db.add(db_movement)
    db.commit()
    db.refresh(db_movement)

    if movement_type == "IN" and movement.min_stock is not None:
        product.min_stock = movement.min_stock
        db.add(product)
        db.commit()
        db.refresh(product)

    if warehouse:
        recipient_emails = get_movement_notification_emails(db, warehouse)
        if recipient_emails:
            background_tasks.add_task(
                notify_inventory_movement,
                movement_id=db_movement.movement_id,
                movement_type=movement_type,
                product_name=product.name,
                quantity=str(db_movement.quantity),
                to_emails=recipient_emails,
                product_code=getattr(product, "code", None),
                warehouse_name=warehouse.name,
                movement_date=str(db_movement.movement_date) if db_movement.movement_date else None,
                project=db_movement.project,
                po_number=db_movement.po_number,
                reference_type=db_movement.reference_type,
                notes=db_movement.notes,
                created_by_name=current_employee.display_name,
            )

    return movement_to_schema(db, db_movement)


@router.post("/entries", response_model=InventoryMovement)
def create_inventory_entry(
    movement: InventoryMovementCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
):
    movement.movement_type = "IN"
    return create_inventory_movement(movement, background_tasks, db, current_employee)


@router.post("/outputs", response_model=InventoryMovement)
def create_inventory_output(
    movement: InventoryMovementCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
):
    movement.movement_type = "OUT"
    return create_inventory_movement(movement, background_tasks, db, current_employee)


@router.post("/adjustments", response_model=InventoryMovement)
def create_inventory_adjustment(
    movement: InventoryMovementCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
):
    movement.movement_type = "ADJUSTMENT"

    if movement.quantity == 0:
        raise HTTPException(status_code=400, detail="Adjustment quantity cannot be zero")

    return create_inventory_movement(movement, background_tasks, db, current_employee)


# ----------------------------
# STOCK
# ----------------------------


@router.get("/stock", response_model=list[InventoryStock])
def get_inventory_stock(
    warehouse_id: int | None = None,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    products = db.exec(select(Products)).all()

    result: list[InventoryStock] = []

    for product in products:
        movements_query = select(InventoryMovements).where(InventoryMovements.product_id == product.id)
        if warehouse_id is not None:
            movements_query = movements_query.where(InventoryMovements.warehouse_id == warehouse_id)
        movements = db.exec(movements_query).all()

        total_in = Decimal(0)
        total_out = Decimal(0)
        total_adjustment = Decimal(0)

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
                family=get_product_family_name(db, product),
                category=get_product_category_name(db, product),
                size=getattr(product, "size", None),
                material_type=getattr(product, "material_type", None),
                unit=getattr(product, "unit", None),
                min_stock=min_stock,
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
