"""Bulk import engine for products.

Two phases, both driven off the same planner:

- `run_analysis` parses the uploaded file and produces the preview.
- `run_apply` re-plans against the *current* database and writes the changes.

Re-planning at apply time is deliberate: minutes can pass between the preview and
the confirmation, and the database may have moved. The plan the user confirmed is
a forecast, not a frozen transaction.

Products present in the database but absent from the file are ignored. This
importer never deletes and never deactivates by omission.
"""

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from sqlmodel import Session, select

from api.products import sync_product_catalog_from_product
from core.datetime_utils import utcnow
from models.product_bulk_imports import ProductBulkImportRows, ProductBulkImports
from models.products import ProductCategories, ProductFamilies, Products
from services.products.excel import (
    InvalidWorkbookError,
    ParsedFile,
    ParsedRow,
    build_error_report,
    parse_import_workbook,
)

BATCH_SIZE = 200
VALID_TYPES = {"product": "Product", "service": "Service"}
# "verdadero"/"falso" show up when Excel localises a real boolean cell.
TRUE_VALUES = {"true", "1", "yes", "y", "si", "sí", "active", "activo", "verdadero"}
FALSE_VALUES = {"false", "0", "no", "n", "inactive", "inactivo", "falso"}

# Mirrors the max_length constraints on models.products.Products.
MAX_LENGTHS = {
    "name": 200,
    "description": 2000,
    "type": 50,
    "sku": 100,
    "code": 50,
    "size": 100,
    "material_type": 100,
    "specification": 100,
    "manufacturer": 100,
    "model": 100,
    "unit": 20,
}

# Written by the import. stock_quantity and min_stock are excluded on purpose:
# they belong to the inventory movement flow, which has its own approvals.
SCALAR_FIELDS = [
    "name",
    "description",
    "type",
    "sku",
    "code",
    "size",
    "material_type",
    "specification",
    "manufacturer",
    "model",
    "unit",
]
MONEY_FIELDS = ["unit_price", "cost", "tax_rate"]


@dataclass
class RowPlan:
    row_number: int
    action: str  # create | update | unchanged | error
    payload: dict[str, Any] = field(default_factory=dict)
    product_id: int | None = None
    code: str | None = None
    name: str | None = None
    message: str | None = None
    conflict: bool = False
    # Taxonomy this row needs but that does not exist yet.
    pending_family: str | None = None
    pending_category: tuple[str, str] | None = None  # (family name, category name)


@dataclass
class Plan:
    rows: list[RowPlan] = field(default_factory=list)
    unknown_families: dict[str, int] = field(default_factory=dict)
    unknown_categories: dict[tuple[str, str], int] = field(default_factory=dict)

    @property
    def create_count(self) -> int:
        return sum(1 for row in self.rows if row.action == "create")

    @property
    def update_count(self) -> int:
        return sum(1 for row in self.rows if row.action == "update")

    @property
    def unchanged_count(self) -> int:
        return sum(1 for row in self.rows if row.action == "unchanged")

    @property
    def error_count(self) -> int:
        return sum(1 for row in self.rows if row.action == "error")

    @property
    def conflict_count(self) -> int:
        # Only rows that would actually be written can overwrite anything. A row
        # that changes nothing is not a conflict, however old the file is.
        return sum(1 for row in self.rows if row.conflict and row.action == "update")


# ----------------------------
# Phase entry points
# ----------------------------
def run_analysis(import_id: int, session_factory: Callable[[], Session]) -> None:
    """Parse the file and store the preview. Runs outside the request."""
    with session_factory() as db:
        job = db.get(ProductBulkImports, import_id)
        if not job or job.status != "analyzing":
            return

        job.started_at = utcnow()
        job.heartbeat_at = utcnow()
        db.commit()

        try:
            parsed = parse_import_workbook(job.stored_path)
        except InvalidWorkbookError as exc:
            _fail(db, job, str(exc))
            return
        except Exception as exc:
            _fail(db, job, f"Could not read the file: {exc}")
            return

        try:
            job.exported_at = parsed.exported_at
            job.export_scope = parsed.export_scope

            plan = build_plan(db, parsed, job.exported_at)
            _store_plan_rows(db, job, plan)

            job.total_rows = len(plan.rows)
            job.create_count = plan.create_count
            job.update_count = plan.update_count
            job.unchanged_count = plan.unchanged_count
            job.error_count = plan.error_count
            job.conflict_count = plan.conflict_count
            job.unknown_taxonomy = json.dumps(_serialize_unknown(plan))
            job.status = "awaiting_confirmation"
            job.heartbeat_at = utcnow()
            db.commit()
        except Exception as exc:
            db.rollback()
            _fail(db, job, f"Analysis failed: {exc}")


def run_apply(import_id: int, session_factory: Callable[[], Session]) -> None:
    """Re-plan against the current database and write the changes."""
    with session_factory() as db:
        job = db.get(ProductBulkImports, import_id)
        if not job or job.status != "applying":
            return

        job.heartbeat_at = utcnow()
        db.commit()

        try:
            parsed = parse_import_workbook(job.stored_path)
            plan = build_plan(db, parsed, job.exported_at)
        except Exception as exc:
            _fail(db, job, f"Could not re-read the file: {exc}")
            return

        try:
            if job.create_missing_taxonomy:
                _create_missing_taxonomy(db, plan)
                # Newly created families/categories change how rows resolve.
                plan = build_plan(db, parsed, job.exported_at)

            _apply_plan(db, job, plan)
        except Exception as exc:
            db.rollback()
            _fail(db, job, f"Import failed: {exc}")


# ----------------------------
# Planning
# ----------------------------
def build_plan(db: Session, parsed: ParsedFile, exported_at: datetime | None) -> Plan:
    families = db.exec(select(ProductFamilies)).all()
    categories = db.exec(select(ProductCategories)).all()
    products = db.exec(select(Products)).all()

    families_by_name = {family.name.strip().lower(): family for family in families}
    families_by_id = {family.id: family for family in families}
    categories_by_key = {
        (category.family_id, category.name.strip().lower()): category for category in categories
    }
    categories_by_id = {category.id: category for category in categories}
    products_by_id = {product.id: product for product in products}

    products_by_code: dict[str, list[Products]] = {}
    for product in products:
        if product.code and product.code.strip():
            products_by_code.setdefault(product.code.strip().lower(), []).append(product)

    duplicate_codes = _duplicate_codes_in_file(parsed.rows)

    plan = Plan()
    for parsed_row in parsed.rows:
        plan.rows.append(
            _plan_row(
                parsed_row,
                plan=plan,
                duplicate_codes=duplicate_codes,
                families_by_name=families_by_name,
                families_by_id=families_by_id,
                categories_by_key=categories_by_key,
                categories_by_id=categories_by_id,
                products_by_id=products_by_id,
                products_by_code=products_by_code,
                exported_at=exported_at,
            )
        )
    return plan


def _plan_row(
    parsed_row: ParsedRow,
    *,
    plan: Plan,
    duplicate_codes: set[str],
    families_by_name: dict[str, ProductFamilies],
    families_by_id: dict[int | None, ProductFamilies],
    categories_by_key: dict[tuple[int | None, str], ProductCategories],
    categories_by_id: dict[int | None, ProductCategories],
    products_by_id: dict[int | None, Products],
    products_by_code: dict[str, list[Products]],
    exported_at: datetime | None,
) -> RowPlan:
    values = parsed_row.values
    code = _text(values.get("code"))
    name = _text(values.get("name"))
    row = RowPlan(row_number=parsed_row.row_number, action="error", code=code, name=name)

    if not name:
        row.message = "name is required"
        return row

    payload: dict[str, Any] = {}
    for field_name in SCALAR_FIELDS:
        value = _text(values.get(field_name))
        limit = MAX_LENGTHS.get(field_name)
        if value and limit and len(value) > limit:
            row.message = f"{field_name} exceeds {limit} characters"
            return row
        payload[field_name] = value

    raw_type = (payload.get("type") or "").strip().lower()
    if raw_type not in VALID_TYPES:
        row.message = "type must be 'Product' or 'Service'"
        return row
    payload["type"] = VALID_TYPES[raw_type]

    for field_name in MONEY_FIELDS:
        try:
            payload[field_name] = _decimal(values.get(field_name))
        except (InvalidOperation, ValueError):
            row.message = f"{field_name} is not a valid number"
            return row
        if payload[field_name] < 0:
            row.message = f"{field_name} cannot be negative"
            return row
    if payload["tax_rate"] > 100:
        row.message = "tax_rate must be between 0 and 100"
        return row

    if not payload.get("unit"):
        payload["unit"] = "pieza"

    is_active = _boolean(values.get("is_active"))
    if is_active is None and _text(values.get("is_active")):
        row.message = "is_active must be TRUE or FALSE"
        return row

    # A code repeated inside the file is ambiguous for the product catalog, which
    # is keyed by code. Rejecting here beats silently overwriting a catalog entry.
    if code and code.lower() in duplicate_codes:
        row.message = f"code '{code}' appears more than once in the file"
        return row

    target, note, error = _resolve_target(values, code, products_by_id, products_by_code)
    if error:
        row.message = error
        return row
    row.message = note

    family, category, taxonomy_error = _resolve_taxonomy(
        values, row, plan, families_by_name, families_by_id, categories_by_key
    )
    if taxonomy_error:
        row.message = taxonomy_error
        return row

    payload["family_id"] = family.id if family else None
    payload["category_id"] = category.id if category else None
    payload["is_active"] = is_active if is_active is not None else (target.is_active if target else True)
    row.payload = payload

    if target is None:
        row.action = "create"
        return row

    row.product_id = target.id
    if exported_at and target.updated_at and target.updated_at > exported_at:
        row.conflict = True
        conflict = "Changed by someone else after this file was exported"
        row.message = f"{row.message}. {conflict}" if row.message else conflict

    changes = _changed_fields(target, payload, families_by_id, categories_by_id)
    if not changes:
        row.action = "unchanged"
        return row

    row.action = "update"
    # Spell out what will change: "it says update and I edited nothing" must be
    # answerable from the preview, not by reading the database.
    summary = "; ".join(changes[:4])
    if len(changes) > 4:
        summary += f" (+{len(changes) - 4} more)"
    row.message = f"{row.message}. {summary}" if row.message else summary
    return row


def _resolve_target(
    values: dict[str, Any],
    code: str | None,
    products_by_id: dict[int | None, Products],
    products_by_code: dict[str, list[Products]],
) -> tuple[Products | None, str | None, str | None]:
    """Match the row to an existing product: by id first, then by code.

    Returns (target, note, error). An id that does not resolve is *not* an error:
    the column is hidden, so nobody can be asked to fix it. The row falls back to
    the code — the identifier the user can actually see — and is created if that
    finds nothing either.
    """
    note: str | None = None
    raw_id = values.get("id")

    if raw_id is not None and str(raw_id).strip():
        try:
            product_id = int(float(str(raw_id).strip()))
        except ValueError:
            note = f"Ignored unreadable id '{raw_id}'"
        else:
            target = products_by_id.get(product_id)
            if target:
                return target, None, None
            note = f"Product id {product_id} no longer exists; matched by code instead"

    if code:
        matches = products_by_code.get(code.lower(), [])
        if len(matches) > 1:
            return None, note, f"code '{code}' matches {len(matches)} products and is ambiguous"
        if matches:
            return matches[0], note, None

    return None, note, None


def _resolve_taxonomy(
    values: dict[str, Any],
    row: RowPlan,
    plan: Plan,
    families_by_name: dict[str, ProductFamilies],
    families_by_id: dict[int | None, ProductFamilies],
    categories_by_key: dict[tuple[int | None, str], ProductCategories],
) -> tuple[ProductFamilies | None, ProductCategories | None, str | None]:
    family_name = _text(values.get("family"))
    category_name = _text(values.get("category"))

    if category_name and not family_name:
        return None, None, "category requires a family"

    if not family_name:
        return None, None, None

    family = families_by_name.get(family_name.lower())
    if not family:
        row.pending_family = family_name
        plan.unknown_families[family_name] = plan.unknown_families.get(family_name, 0) + 1
        if category_name:
            key = (family_name, category_name)
            row.pending_category = key
            plan.unknown_categories[key] = plan.unknown_categories.get(key, 0) + 1
        return None, None, None

    if not category_name:
        return family, None, None

    category = categories_by_key.get((family.id, category_name.lower()))
    if not category:
        key = (family.name, category_name)
        row.pending_category = key
        plan.unknown_categories[key] = plan.unknown_categories.get(key, 0) + 1
        return family, None, None

    return family, category, None


def _normalized_current(target: Products, key: str) -> Any:
    """Put the stored value through the same normalisation the file goes through.

    Comparing a normalised file value against a raw database value invents
    differences: a stored code with a trailing space, a lowercase `type` or an
    empty `unit` would all look like edits nobody made.
    """
    current = getattr(target, key)

    if key in MONEY_FIELDS:
        return Decimal(str(current))
    if key == "type":
        return VALID_TYPES.get((current or "").strip().lower(), current)
    if key == "unit":
        return _text(current) or "pieza"
    if key in SCALAR_FIELDS:
        return _text(current)
    return current


def _changed_fields(
    target: Products,
    payload: dict[str, Any],
    families_by_id: dict[int | None, ProductFamilies],
    categories_by_id: dict[int | None, ProductCategories],
) -> list[str]:
    """Human-readable `field: old -> new` for everything the row would change."""
    changes: list[str] = []

    for key, value in payload.items():
        current = _normalized_current(target, key)
        if current == value or (current or None) == (value or None):
            continue

        if key == "family_id":
            changes.append(f"family: {_name_of(families_by_id, current)} -> {_name_of(families_by_id, value)}")
        elif key == "category_id":
            changes.append(
                f"category: {_name_of(categories_by_id, current)} -> {_name_of(categories_by_id, value)}"
            )
        else:
            changes.append(f"{key}: {_display(current)} -> {_display(value)}")

    return changes


def _name_of(lookup: dict[int | None, Any], key: Any) -> str:
    entry = lookup.get(key)
    return entry.name if entry else "(none)"


def _display(value: Any) -> str:
    if value is None or not str(value):
        return "(empty)"
    return str(value)


def _duplicate_codes_in_file(rows: list[ParsedRow]) -> set[str]:
    seen: dict[str, int] = {}
    for parsed_row in rows:
        code = _text(parsed_row.values.get("code"))
        if code:
            seen[code.lower()] = seen.get(code.lower(), 0) + 1
    return {code for code, count in seen.items() if count > 1}


# ----------------------------
# Applying
# ----------------------------
def _create_missing_taxonomy(db: Session, plan: Plan) -> None:
    for family_name in plan.unknown_families:
        existing = db.exec(
            select(ProductFamilies).where(ProductFamilies.name == family_name)
        ).first()
        if not existing:
            db.add(ProductFamilies(name=family_name[:100]))
    db.commit()

    for family_name, category_name in plan.unknown_categories:
        family = db.exec(select(ProductFamilies).where(ProductFamilies.name == family_name)).first()
        if not family:
            continue
        existing = db.exec(
            select(ProductCategories).where(
                ProductCategories.family_id == family.id,
                ProductCategories.name == category_name,
            )
        ).first()
        if not existing:
            db.add(ProductCategories(family_id=family.id, name=category_name[:100]))
    db.commit()


def _apply_plan(db: Session, job: ProductBulkImports, plan: Plan) -> None:
    _clear_rows(db, job)

    # Every row that produced an outcome, in file order. Each row's final
    # `action` is the record of what actually happened, so the counters are
    # derived from it at the end instead of being tracked by hand.
    processed: list[RowPlan] = []
    pending: list[RowPlan] = []

    def flush() -> None:
        if not pending:
            return
        try:
            for row in pending:
                _write_product(db, row, None if row.action == "create" else db.get(Products, row.product_id))
            db.commit()
        except Exception as exc:
            db.rollback()
            reason = f"Database rejected this batch: {exc}"[:500]
            for row in pending:
                row.action = "error"
                row.message = reason
        pending.clear()

    for row in plan.rows:
        if row.action == "unchanged":
            continue

        processed.append(row)

        if row.action == "error":
            continue

        if row.pending_family or row.pending_category:
            row.action = "error"
            unknown = row.pending_category[1] if row.pending_category else row.pending_family
            row.message = f"Unknown family/category: {unknown}"
            continue

        if row.conflict and not job.apply_conflicts:
            row.action = "skipped"
            continue

        pending.append(row)
        if len(pending) >= BATCH_SIZE:
            flush()
            _heartbeat(db, job)

    flush()

    db.add_all([_row_record(job, row, row.action) for row in processed])

    job.created_count = sum(1 for row in processed if row.action == "create")
    job.updated_count = sum(1 for row in processed if row.action == "update")
    job.failed_count = sum(1 for row in processed if row.action == "error")
    job.skipped_count = sum(1 for row in processed if row.action == "skipped")
    job.unchanged_count = plan.unchanged_count
    job.total_rows = len(plan.rows)
    job.status = "completed"
    job.finished_at = utcnow()
    job.heartbeat_at = utcnow()
    db.commit()

    if job.failed_count:
        _write_error_report(db, job)


def _write_product(db: Session, row: RowPlan, target: Products | None) -> None:
    product = target
    if product is None:
        product = Products(**row.payload)
        db.add(product)
    else:
        for key, value in row.payload.items():
            setattr(product, key, value)

    product.updated_at = utcnow()
    db.flush()
    row.product_id = product.id
    sync_product_catalog_from_product(db, product)


def _row_record(job: ProductBulkImports, row: RowPlan, action: str) -> ProductBulkImportRows:
    return ProductBulkImportRows(
        import_id=job.id or 0,
        row_number=row.row_number,
        action=action,
        product_id=row.product_id,
        code=row.code[:100] if row.code else None,
        name=row.name[:255] if row.name else None,
        message=row.message[:500] if row.message else None,
    )


def _write_error_report(db: Session, job: ProductBulkImports) -> None:
    failed_rows = db.exec(
        select(ProductBulkImportRows)
        .where(ProductBulkImportRows.import_id == job.id, ProductBulkImportRows.action == "error")
        .order_by(ProductBulkImportRows.row_number)
    ).all()
    if not failed_rows:
        return

    report_path = Path(job.stored_path).with_name(f"{Path(job.stored_path).stem}_errors.xlsx")
    report_path.write_bytes(build_error_report(failed_rows))
    job.error_report_path = str(report_path)
    db.commit()


# ----------------------------
# Persistence helpers
# ----------------------------
def _store_plan_rows(db: Session, job: ProductBulkImports, plan: Plan) -> None:
    _clear_rows(db, job)
    db.add_all(
        [_row_record(job, row, row.action) for row in plan.rows if row.action != "unchanged"]
    )


def _clear_rows(db: Session, job: ProductBulkImports) -> None:
    for existing in db.exec(
        select(ProductBulkImportRows).where(ProductBulkImportRows.import_id == job.id)
    ).all():
        db.delete(existing)
    db.flush()


def _serialize_unknown(plan: Plan) -> list[dict[str, Any]]:
    unknown = [
        {"kind": "family", "name": name, "family": None, "row_count": count}
        for name, count in sorted(plan.unknown_families.items())
    ]
    unknown.extend(
        {"kind": "category", "name": category, "family": family, "row_count": count}
        for (family, category), count in sorted(plan.unknown_categories.items())
    )
    return unknown


def _fail(db: Session, job: ProductBulkImports, reason: str) -> None:
    job.status = "failed"
    job.failure_reason = reason[:500]
    job.finished_at = utcnow()
    db.commit()


def _heartbeat(db: Session, job: ProductBulkImports) -> None:
    job.heartbeat_at = utcnow()
    db.commit()


# ----------------------------
# Value coercion
# ----------------------------
def _text(value: Any) -> str | None:
    r"""Normalise a cell into comparable text.

    Line endings collapse to "\n": a description stored with Windows "\r\n"
    cannot survive an XML round trip unchanged, so comparing the two forms as
    different text would report an edit nobody made.
    """
    if value is None:
        return None
    text = str(value).replace("\r\n", "\n").replace("\r", "\n").strip()
    return text or None


def _decimal(value: Any) -> Decimal:
    if value is None or not str(value).strip():
        return Decimal("0.00")
    return Decimal(str(value).strip().replace(",", ""))


def _boolean(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    text = _text(value)
    if text is None:
        return None
    lowered = text.lower()
    if lowered in TRUE_VALUES:
        return True
    if lowered in FALSE_VALUES:
        return False
    return None
