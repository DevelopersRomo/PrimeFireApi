from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlmodel import Session, select

from api.dependencies import require_authentication, require_module_permission
from bd.dependencies import get_db
from models.products import ProductCatalog, ProductCategories, ProductFamilies, ProductSpecifications, Products
from schemas.pagination import PaginatedResponse
from schemas.products import (
    Product,
    ProductCatalogCreate,
    ProductCatalogRead,
    ProductCatalogUpdate,
    ProductCategoryCreate,
    ProductCategoryRead,
    ProductCategoryUpdate,
    ProductCreate,
    ProductFamilyCreate,
    ProductFamilyRead,
    ProductFamilyUpdate,
    ProductRead,
    ProductSpecificationCreate,
    ProductSpecificationOptionRead,
    ProductSpecificationRead,
    ProductSpecificationUpdate,
    ProductUpdate,
)

router = APIRouter()


def get_family_or_404(db: Session, family_id: int) -> ProductFamilies:
    family = db.get(ProductFamilies, family_id)
    if not family:
        raise HTTPException(status_code=404, detail="Product family not found")
    return family


def get_category_or_404(db: Session, category_id: int) -> ProductCategories:
    category = db.get(ProductCategories, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Product category not found")
    return category


def get_family_by_name(db: Session, name: str) -> ProductFamilies | None:
    return db.exec(select(ProductFamilies).where(func.lower(ProductFamilies.name) == name.strip().lower())).first()


def get_category_by_family_and_name(db: Session, family_id: int, name: str) -> ProductCategories | None:
    return db.exec(
        select(ProductCategories).where(
            ProductCategories.family_id == family_id,
            func.lower(ProductCategories.name) == name.strip().lower(),
        )
    ).first()


def validate_product_catalog_refs(
    db: Session,
    family_id: int | None,
    category_id: int | None,
) -> None:
    if family_id is not None:
        get_family_or_404(db, family_id)

    if category_id is None:
        return

    category = get_category_or_404(db, category_id)
    if family_id is not None and category.family_id != family_id:
        raise HTTPException(status_code=400, detail="Product category does not belong to selected family")


def product_to_read(db: Session, product: Products) -> ProductRead:
    family = db.get(ProductFamilies, product.family_id) if product.family_id else None
    category = db.get(ProductCategories, product.category_id) if product.category_id else None

    return ProductRead(
        id=product.id or 0,
        name=product.name,
        description=product.description,
        type=product.type,
        sku=product.sku,
        code=product.code,
        family_id=product.family_id,
        category_id=product.category_id,
        family_name=family.name if family else None,
        category_name=category.name if category else None,
        size=product.size,
        material_type=product.material_type,
        specification=product.specification,
        manufacturer=product.manufacturer,
        model=product.model,
        unit_price=product.unit_price,
        cost=product.cost,
        tax_rate=product.tax_rate,
        unit=product.unit,
        is_active=product.is_active,
        created_at=product.created_at,
    )


def catalog_to_read(db: Session, product: ProductCatalog) -> ProductCatalogRead:
    family = db.get(ProductFamilies, product.family_id) if product.family_id else None
    category = db.get(ProductCategories, product.category_id) if product.category_id else None
    spec = db.exec(select(ProductSpecifications).where(ProductSpecifications.product_id == product.id)).first()

    return ProductCatalogRead(
        id=product.id or 0,
        code=product.code,
        name=product.name,
        family_id=product.family_id,
        category_id=product.category_id,
        family_name=family.name if family else None,
        category_name=category.name if category else None,
        unit=product.unit,
        min_stock=product.min_stock,
        active=product.active,
        description=product.description,
        created_at=product.created_at,
        specification=ProductSpecificationRead(
            id=spec.id or 0,
            product_id=spec.product_id,
            specification=spec.specification,
            size=spec.size,
            material=spec.material,
            manufacturer=spec.manufacturer,
            model=spec.model,
            notes=spec.notes,
        )
        if spec
        else None,
    )


def resolve_catalog_code(product: Products) -> str:
    for value in (product.code, product.sku):
        if value and value.strip() and value.strip().upper() not in {"NA", "N/A", "NONE", "NULL"}:
            return value.strip()
    return f"P-{product.id}"


def sync_product_catalog_from_product(db: Session, product: Products) -> None:
    code = resolve_catalog_code(product)
    catalog_item = db.exec(select(ProductCatalog).where(ProductCatalog.code == code)).first()

    if not catalog_item:
        catalog_item = ProductCatalog(code=code, name=product.name)
        db.add(catalog_item)

    catalog_item.name = product.name
    catalog_item.family_id = product.family_id
    catalog_item.category_id = product.category_id
    catalog_item.unit = product.unit
    catalog_item.min_stock = product.min_stock
    catalog_item.active = product.is_active
    catalog_item.description = product.description

    db.flush()

    catalog_spec = db.exec(
        select(ProductSpecifications).where(ProductSpecifications.product_id == catalog_item.id)
    ).first()
    if not catalog_spec:
        catalog_spec = ProductSpecifications(product_id=catalog_item.id or 0)
        db.add(catalog_spec)

    catalog_spec.specification = product.specification
    catalog_spec.size = product.size
    catalog_spec.material = product.material_type
    catalog_spec.manufacturer = product.manufacturer
    catalog_spec.model = product.model
    db.flush()


def commit_product_with_catalog(db: Session, product: Products) -> None:
    try:
        db.flush()
        sync_product_catalog_from_product(db, product)
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Product could not be saved because its data conflicts with the product catalog",
        ) from exc


@router.get("/families", response_model=list[ProductFamilyRead])
def get_product_families(
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    statement = select(ProductFamilies)
    if active_only:
        statement = statement.where(ProductFamilies.active == True)  # noqa: E712
    return db.exec(statement.order_by(ProductFamilies.name)).all()


@router.post("/families", response_model=ProductFamilyRead)
def create_product_family(
    family: ProductFamilyCreate,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_module_permission("products", "can_create")),
):
    if get_family_by_name(db, family.name):
        raise HTTPException(status_code=409, detail="Product family already exists")

    db_family = ProductFamilies(**family.model_dump())
    db.add(db_family)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Product family already exists") from exc
    db.refresh(db_family)
    return db_family


@router.patch("/families/{family_id}", response_model=ProductFamilyRead)
def update_product_family(
    family_id: int,
    family: ProductFamilyUpdate,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_module_permission("products", "can_edit")),
):
    db_family = get_family_or_404(db, family_id)
    update_data = family.model_dump(exclude_unset=True)
    if "name" in update_data:
        existing = get_family_by_name(db, update_data["name"])
        if existing and existing.id != family_id:
            raise HTTPException(status_code=409, detail="Product family already exists")
    for key, value in update_data.items():
        setattr(db_family, key, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Product family already exists") from exc
    db.refresh(db_family)
    return db_family


@router.delete("/families/{family_id}")
def delete_product_family(
    family_id: int,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_module_permission("products", "can_delete")),
):
    db_family = get_family_or_404(db, family_id)
    has_products = db.exec(select(Products).where(Products.family_id == family_id)).first()
    has_catalog_products = db.exec(select(ProductCatalog).where(ProductCatalog.family_id == family_id)).first()
    if has_products or has_catalog_products:
        raise HTTPException(status_code=400, detail="Product family is in use")
    categories = db.exec(select(ProductCategories).where(ProductCategories.family_id == family_id)).all()
    for category in categories:
        db.delete(category)
    db.delete(db_family)
    db.commit()
    return {"message": "Product family deleted successfully"}


@router.get("/categories", response_model=list[ProductCategoryRead])
def get_product_categories(
    family_id: int | None = Query(None),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    statement = select(ProductCategories)
    if family_id is not None:
        statement = statement.where(ProductCategories.family_id == family_id)
    if active_only:
        statement = statement.where(ProductCategories.active == True)  # noqa: E712
    return db.exec(statement.order_by(ProductCategories.name)).all()


@router.post("/categories", response_model=ProductCategoryRead)
def create_product_category(
    category: ProductCategoryCreate,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_module_permission("products", "can_create")),
):
    get_family_or_404(db, category.family_id)
    if get_category_by_family_and_name(db, category.family_id, category.name):
        raise HTTPException(status_code=409, detail="Product category already exists for this family")

    db_category = ProductCategories(**category.model_dump())
    db.add(db_category)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Product category already exists for this family") from exc
    db.refresh(db_category)
    return db_category


@router.patch("/categories/{category_id}", response_model=ProductCategoryRead)
def update_product_category(
    category_id: int,
    category: ProductCategoryUpdate,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_module_permission("products", "can_edit")),
):
    db_category = get_category_or_404(db, category_id)
    update_data = category.model_dump(exclude_unset=True)
    if "family_id" in update_data:
        get_family_or_404(db, update_data["family_id"])
    next_family_id = update_data.get("family_id", db_category.family_id)
    next_name = update_data.get("name", db_category.name)
    existing = get_category_by_family_and_name(db, next_family_id, next_name)
    if existing and existing.id != category_id:
        raise HTTPException(status_code=409, detail="Product category already exists for this family")
    for key, value in update_data.items():
        setattr(db_category, key, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Product category already exists for this family") from exc
    db.refresh(db_category)
    return db_category


@router.delete("/categories/{category_id}")
def delete_product_category(
    category_id: int,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_module_permission("products", "can_delete")),
):
    db_category = get_category_or_404(db, category_id)
    has_products = db.exec(select(Products).where(Products.category_id == category_id)).first()
    has_catalog_products = db.exec(select(ProductCatalog).where(ProductCatalog.category_id == category_id)).first()
    if has_products or has_catalog_products:
        raise HTTPException(status_code=400, detail="Product category is in use")
    db.delete(db_category)
    db.commit()
    return {"message": "Product category deleted successfully"}


@router.get("/catalog", response_model=list[ProductCatalogRead])
def get_product_catalog(
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    products = db.exec(select(ProductCatalog).order_by(ProductCatalog.name)).all()
    return [catalog_to_read(db, product) for product in products]


@router.post("/catalog", response_model=ProductCatalogRead)
def create_product_catalog_item(
    product: ProductCatalogCreate,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_module_permission("products", "can_create")),
):
    validate_product_catalog_refs(db, product.family_id, product.category_id)
    data = product.model_dump(exclude={"specification"})
    db_product = ProductCatalog(**data)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    if product.specification:
        db_spec = ProductSpecifications(product_id=db_product.id or 0, **product.specification.model_dump())
        db.add(db_spec)
        db.commit()

    db.refresh(db_product)
    return catalog_to_read(db, db_product)


@router.patch("/catalog/{product_id}", response_model=ProductCatalogRead)
def update_product_catalog_item(
    product_id: int,
    product: ProductCatalogUpdate,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_module_permission("products", "can_edit")),
):
    db_product = db.get(ProductCatalog, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product catalog item not found")

    update_data = product.model_dump(exclude_unset=True, exclude={"specification"})
    family_id = update_data.get("family_id", db_product.family_id)
    category_id = update_data.get("category_id", db_product.category_id)
    validate_product_catalog_refs(db, family_id, category_id)

    for key, value in update_data.items():
        setattr(db_product, key, value)

    if product.specification is not None:
        db_spec = db.exec(select(ProductSpecifications).where(ProductSpecifications.product_id == product_id)).first()
        if not db_spec:
            db_spec = ProductSpecifications(product_id=product_id)
            db.add(db_spec)
        for key, value in product.specification.model_dump().items():
            setattr(db_spec, key, value)

    db.commit()
    db.refresh(db_product)
    return catalog_to_read(db, db_product)


@router.delete("/catalog/{product_id}")
def delete_product_catalog_item(
    product_id: int,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_module_permission("products", "can_delete")),
):
    db_product = db.get(ProductCatalog, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product catalog item not found")
    db_spec = db.exec(select(ProductSpecifications).where(ProductSpecifications.product_id == product_id)).first()
    if db_spec:
        db.delete(db_spec)
    db.delete(db_product)
    db.commit()
    return {"message": "Product catalog item deleted successfully"}


@router.get("/specifications", response_model=list[ProductSpecificationOptionRead])
def get_product_specification_options(
    search: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    statement = (
        select(ProductSpecifications)
        .where(ProductSpecifications.specification.is_not(None))
        .order_by(ProductSpecifications.specification)
    )
    rows = db.exec(statement).all()
    search_term = search.strip().lower() if search else ""
    specifications: list[ProductSpecificationOptionRead] = []
    seen: set[str] = set()

    for row in rows:
        if not row:
            continue

        specification = row.specification.strip() if row.specification else ""
        if not specification:
            continue

        normalized = "|".join(
            [
                specification.lower(),
                (row.size or "").strip().lower(),
                (row.material or "").strip().lower(),
                (row.manufacturer or "").strip().lower(),
                (row.model or "").strip().lower(),
            ]
        )
        if normalized in seen:
            continue

        if search_term and search_term not in normalized:
            continue

        seen.add(normalized)
        specifications.append(
            ProductSpecificationOptionRead(
                id=row.id or 0,
                product_id=row.product_id,
                specification=specification,
                size=row.size,
                material=row.material,
                manufacturer=row.manufacturer,
                model=row.model,
                notes=row.notes,
            )
        )

        if len(specifications) >= limit:
            break

    return specifications


@router.post("/specifications", response_model=ProductSpecificationRead)
def create_product_specification(
    specification: ProductSpecificationCreate,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_module_permission("products", "can_create")),
):
    if specification.product_id is not None and not db.get(ProductCatalog, specification.product_id):
        raise HTTPException(status_code=404, detail="Product catalog item not found")

    db_specification = ProductSpecifications(**specification.model_dump())
    db.add(db_specification)
    db.commit()
    db.refresh(db_specification)
    return db_specification


@router.patch("/specifications/{specification_id}", response_model=ProductSpecificationRead)
def update_product_specification(
    specification_id: int,
    specification: ProductSpecificationUpdate,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_module_permission("products", "can_edit")),
):
    db_specification = db.get(ProductSpecifications, specification_id)
    if not db_specification:
        raise HTTPException(status_code=404, detail="Product specification not found")

    update_data = specification.model_dump(exclude_unset=True)
    product_id = update_data.get("product_id")
    if product_id is not None and not db.get(ProductCatalog, product_id):
        raise HTTPException(status_code=404, detail="Product catalog item not found")

    for key, value in update_data.items():
        setattr(db_specification, key, value)

    db.commit()
    db.refresh(db_specification)
    return db_specification


@router.delete("/specifications/{specification_id}")
def delete_product_specification(
    specification_id: int,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_module_permission("products", "can_delete")),
):
    db_specification = db.get(ProductSpecifications, specification_id)
    if not db_specification:
        raise HTTPException(status_code=404, detail="Product specification not found")

    db.delete(db_specification)
    db.commit()
    return {"message": "Product specification deleted successfully"}


# ----------------------------
# CREATE
# ----------------------------
@router.post("", response_model=Product)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_module_permission("products", "can_create")),
):
    validate_product_catalog_refs(db, product.family_id, product.category_id)
    db_product = Products(**product.model_dump())
    db.add(db_product)
    commit_product_with_catalog(db, db_product)
    db.refresh(db_product)
    return product_to_read(db, db_product)


# ----------------------------
# READ ALL
# ----------------------------
@router.get("", response_model=list[ProductRead] | PaginatedResponse[ProductRead])
def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=1000),
    with_meta: bool = Query(False),
    search: str | None = Query(None),
    family_id: int | None = Query(None),
    category_id: int | None = Query(None),
    type: str | None = Query(None),
    is_active: bool | None = Query(None),
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    filters = []
    if family_id is not None:
        filters.append(Products.family_id == family_id)
    if category_id is not None:
        filters.append(Products.category_id == category_id)
    if type and type.strip():
        filters.append(Products.type == type.strip())
    if is_active is not None:
        filters.append(Products.is_active == is_active)
    if search and search.strip():
        term = f"%{search.strip()}%"
        filters.append(
            or_(
                Products.name.ilike(term),
                Products.description.ilike(term),
                Products.type.ilike(term),
                Products.sku.ilike(term),
                Products.code.ilike(term),
                Products.size.ilike(term),
                Products.material_type.ilike(term),
                Products.specification.ilike(term),
                Products.manufacturer.ilike(term),
                Products.model.ilike(term),
                Products.unit.ilike(term),
                ProductFamilies.name.ilike(term),
                ProductCategories.name.ilike(term),
            )
        )

    statement = (
        select(Products)
        .join(ProductFamilies, Products.family_id == ProductFamilies.id, isouter=True)
        .join(ProductCategories, Products.category_id == ProductCategories.id, isouter=True)
    )
    if filters:
        statement = statement.where(*filters)
    statement = statement.order_by(Products.created_at.desc(), Products.id.desc()).offset(skip).limit(limit)
    items = db.exec(statement).all()
    read_items = [product_to_read(db, item) for item in items]

    if not with_meta:
        return read_items

    count_query = (
        select(func.count())
        .select_from(Products)
        .join(ProductFamilies, Products.family_id == ProductFamilies.id, isouter=True)
        .join(ProductCategories, Products.category_id == ProductCategories.id, isouter=True)
    )
    if filters:
        count_query = count_query.where(*filters)
    total = db.exec(count_query).one()
    return PaginatedResponse[ProductRead](
        items=read_items,
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + len(items) < total,
    )


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

    return product_to_read(db, product)


# ----------------------------
# UPDATE (PUT)
# ----------------------------
@router.put("/{product_id}", response_model=Product)
def update_product(
    product_id: int,
    product: ProductCreate,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_module_permission("products", "can_edit")),
):
    db_product = db.get(Products, product_id)

    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    validate_product_catalog_refs(db, product.family_id, product.category_id)

    for key, value in product.model_dump().items():
        setattr(db_product, key, value)

    commit_product_with_catalog(db, db_product)
    db.refresh(db_product)
    return product_to_read(db, db_product)


# ----------------------------
# PATCH
# ----------------------------
@router.patch("/{product_id}", response_model=Product)
def patch_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_module_permission("products", "can_edit")),
):
    db_product = db.get(Products, product_id)

    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = product.model_dump(exclude_unset=True)
    family_id = update_data.get("family_id", db_product.family_id)
    category_id = update_data.get("category_id", db_product.category_id)
    validate_product_catalog_refs(db, family_id, category_id)

    for key, value in update_data.items():
        setattr(db_product, key, value)

    commit_product_with_catalog(db, db_product)
    db.refresh(db_product)
    return product_to_read(db, db_product)


# ----------------------------
# DELETE
# ----------------------------
@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_module_permission("products", "can_delete")),
):
    product = db.get(Products, product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    catalog_code = resolve_catalog_code(product)
    catalog_item = db.exec(select(ProductCatalog).where(ProductCatalog.code == catalog_code)).first()
    if catalog_item:
        catalog_spec = db.exec(
            select(ProductSpecifications).where(ProductSpecifications.product_id == catalog_item.id)
        ).first()
        if catalog_spec:
            db.delete(catalog_spec)
        db.delete(catalog_item)

    db.delete(product)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Product is in use and cannot be deleted") from exc

    return {"message": "Product deleted successfully"}
