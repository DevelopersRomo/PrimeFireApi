"""Excel export and bulk import of products, plus the history of past imports.

Routes are declared with their full path (no router prefix) and registered
*before* the products router: `/products/export` would otherwise be swallowed by
`/products/{product_id}`.
"""

import json
import os
from collections.abc import Callable
from datetime import timedelta
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse, Response
from sqlalchemy import func
from sqlmodel import Session, select

from api.dependencies import get_current_employee_with_permissions, require_authentication
from api.products import build_product_filters, product_to_read
from bd.dependencies import get_db, get_session_factory
from core.datetime_utils import utcnow
from models.employees import Employees
from models.product_bulk_imports import ProductBulkImportRows, ProductBulkImports
from models.products import ProductCategories, ProductFamilies, Products
from schemas.pagination import PaginatedResponse
from schemas.product_bulk_imports import (
    BulkImportConfirm,
    BulkImportRead,
    BulkImportRowRead,
    UnknownTaxonomy,
)
from schemas.products import ProductEmployee
from services.products.bulk_import import run_analysis, run_apply
from services.products.excel import (
    InvalidWorkbookError,
    build_export_workbook,
    count_data_rows,
    workbook_to_bytes,
)

load_dotenv()

ENV = os.getenv("ENVIRONMENT", "local").lower()
IS_PRODUCTION = ENV == "prod"

if IS_PRODUCTION:
    uploads_base = os.getenv("UPLOADS_DIR", "/home/home/uploads")
    UPLOAD_DIR = Path(uploads_base) / "products" / "bulk-imports"
else:
    from core.config import settings

    BASE_DIR = Path(__file__).resolve().parents[1]
    UPLOAD_DIR = BASE_DIR / settings.UPLOAD_DIR / "products" / "bulk-imports"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter()

XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
MAX_FILE_BYTES = 10 * 1024 * 1024
MAX_DATA_ROWS = 10_000
# Only work that is actually touching the database blocks a new upload. A preview
# nobody answered has written nothing, so it must never hold the door shut.
RUNNING_STATUSES = ("analyzing", "applying")
# A job whose heartbeat went quiet for this long died with its process.
STALE_AFTER = timedelta(minutes=5)


def require_bulk_import_permission(
    user_permissions: dict = Depends(get_current_employee_with_permissions),
) -> dict:
    """A bulk import both creates and updates products, so it needs both rights."""
    for perm in user_permissions.get("permissions", []):
        if perm.get("module_key") != "products":
            continue
        actions = perm.get("permissions", {})
        if actions.get("can_create") and actions.get("can_edit"):
            return user_permissions
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Bulk import requires 'can_create' and 'can_edit' on module 'products'.",
    )


def require_export_permission(
    user_permissions: dict = Depends(get_current_employee_with_permissions),
) -> dict:
    for perm in user_permissions.get("permissions", []):
        if perm.get("module_key") == "products" and perm.get("permissions", {}).get("can_export"):
            return user_permissions
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Missing 'can_export' permission for module 'products'.",
    )


# ----------------------------
# Export
# ----------------------------
@router.get("/products/export")
def export_products(
    search: str | None = Query(None),
    family_id: int | None = Query(None),
    category_id: int | None = Query(None),
    type: str | None = Query(None),
    is_active: bool | None = Query(None),
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_export_permission),
):
    """Export the complete filtered set, not just the page the list has loaded."""
    filters = build_product_filters(search, family_id, category_id, type, is_active)

    statement = (
        select(Products)
        .join(ProductFamilies, Products.family_id == ProductFamilies.id, isouter=True)
        .join(ProductCategories, Products.category_id == ProductCategories.id, isouter=True)
    )
    if filters:
        statement = statement.where(*filters)
    products = db.exec(statement.order_by(Products.name)).all()

    families = db.exec(select(ProductFamilies).order_by(ProductFamilies.name)).all()
    families_by_id = {family.id: family.name for family in families}
    categories = [
        (families_by_id.get(category.family_id, ""), category.name)
        for category in db.exec(select(ProductCategories).order_by(ProductCategories.name)).all()
    ]

    exported_at = utcnow()
    workbook = build_export_workbook(
        [product_to_read(db, product) for product in products],
        exported_at=exported_at,
        export_scope={
            "search": search,
            "family_id": family_id,
            "category_id": category_id,
            "type": type,
            "is_active": is_active,
        },
        families=families,
        categories=categories,
    )

    file_name = f"products_{exported_at.strftime('%Y%m%d_%H%M%S')}.xlsx"
    return Response(
        content=workbook_to_bytes(workbook),
        media_type=XLSX_MEDIA_TYPE,
        headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
    )


# ----------------------------
# Import lifecycle
# ----------------------------
@router.post("/products/bulk-imports", response_model=BulkImportRead, status_code=status.HTTP_202_ACCEPTED)
async def start_bulk_import(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    session_factory: Callable[[], Session] = Depends(get_session_factory),
    permissions: dict = Depends(require_bulk_import_permission),
):
    if not (file.filename or "").lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only .xlsx files are supported.")

    raw = await file.read()
    if len(raw) > MAX_FILE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File is larger than {MAX_FILE_BYTES // (1024 * 1024)} MB.",
        )

    _expire_stale_jobs(db)
    running = db.exec(select(ProductBulkImports).where(ProductBulkImports.status.in_(RUNNING_STATUSES))).first()
    if running:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Bulk import #{running.id} is still {running.status}. Wait for it to finish — "
                "it is released automatically if it stops responding."
            ),
        )

    _supersede_pending_previews(db)

    stored_path = UPLOAD_DIR / f"{uuid4().hex}.xlsx"
    stored_path.write_bytes(raw)

    try:
        row_count = count_data_rows(str(stored_path))
    except InvalidWorkbookError as exc:
        stored_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        stored_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=400, detail=f"The file could not be read as an Excel workbook: {exc}"
        ) from exc

    if row_count > MAX_DATA_ROWS:
        stored_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=400,
            detail=f"The file has {row_count} rows; the limit is {MAX_DATA_ROWS}.",
        )

    job = ProductBulkImports(
        file_name=file.filename or "import.xlsx",
        stored_path=str(stored_path),
        status="analyzing",
        created_by=permissions["employee"]["employee_id"],
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    background_tasks.add_task(run_analysis, job.id, session_factory)
    return _to_read(db, job)


@router.get("/products/bulk-imports", response_model=PaginatedResponse[BulkImportRead])
def list_bulk_imports(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    _expire_stale_jobs(db)

    # Cancelled imports changed nothing, so they are not history. The list is
    # what actually happened to the catalog: what ran, and what broke trying.
    visible = ProductBulkImports.status != "cancelled"

    total = db.exec(select(func.count()).select_from(ProductBulkImports).where(visible)).one()
    jobs = db.exec(
        select(ProductBulkImports)
        .where(visible)
        .order_by(ProductBulkImports.created_at.desc(), ProductBulkImports.id.desc())
        .offset(skip)
        .limit(limit)
    ).all()

    return PaginatedResponse[BulkImportRead](
        items=[_to_read(db, job) for job in jobs],
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + len(jobs) < total,
    )


@router.get("/products/bulk-imports/{import_id}", response_model=BulkImportRead)
def get_bulk_import(
    import_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    _expire_stale_jobs(db)
    return _to_read(db, _get_job_or_404(db, import_id))


@router.get("/products/bulk-imports/{import_id}/rows", response_model=PaginatedResponse[BulkImportRowRead])
def get_bulk_import_rows(
    import_id: int,
    action: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    _get_job_or_404(db, import_id)

    filters = [ProductBulkImportRows.import_id == import_id]
    if action:
        filters.append(ProductBulkImportRows.action == action)

    total = db.exec(select(func.count()).select_from(ProductBulkImportRows).where(*filters)).one()
    rows = db.exec(
        select(ProductBulkImportRows)
        .where(*filters)
        .order_by(ProductBulkImportRows.row_number)
        .offset(skip)
        .limit(limit)
    ).all()

    return PaginatedResponse[BulkImportRowRead](
        items=[BulkImportRowRead.model_validate(row, from_attributes=True) for row in rows],
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + len(rows) < total,
    )


@router.post("/products/bulk-imports/{import_id}/confirm", response_model=BulkImportRead, status_code=status.HTTP_202_ACCEPTED)
def confirm_bulk_import(
    import_id: int,
    confirmation: BulkImportConfirm,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    session_factory: Callable[[], Session] = Depends(get_session_factory),
    _permissions: dict = Depends(require_bulk_import_permission),
):
    job = _get_job_or_404(db, import_id)
    if job.status != "awaiting_confirmation":
        raise HTTPException(status_code=409, detail=f"Bulk import is '{job.status}' and cannot be confirmed.")

    job.create_missing_taxonomy = confirmation.create_missing_taxonomy
    job.apply_conflicts = confirmation.apply_conflicts
    job.status = "applying"
    job.heartbeat_at = utcnow()
    db.commit()
    db.refresh(job)

    background_tasks.add_task(run_apply, job.id, session_factory)
    return _to_read(db, job)


@router.post("/products/bulk-imports/{import_id}/cancel", response_model=BulkImportRead)
def cancel_bulk_import(
    import_id: int,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_bulk_import_permission),
):
    job = _get_job_or_404(db, import_id)
    if job.status != "awaiting_confirmation":
        raise HTTPException(status_code=409, detail=f"Bulk import is '{job.status}' and cannot be cancelled.")

    job.status = "cancelled"
    job.finished_at = utcnow()
    db.commit()
    db.refresh(job)
    return _to_read(db, job)


@router.get("/products/bulk-imports/{import_id}/error-report")
def download_error_report(
    import_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    job = _get_job_or_404(db, import_id)
    if not job.error_report_path or not Path(job.error_report_path).exists():
        raise HTTPException(status_code=404, detail="This import has no error report.")

    return FileResponse(
        job.error_report_path,
        media_type=XLSX_MEDIA_TYPE,
        filename=f"bulk_import_{import_id}_errors.xlsx",
    )


# ----------------------------
# Helpers
# ----------------------------
def _get_job_or_404(db: Session, import_id: int) -> ProductBulkImports:
    job = db.get(ProductBulkImports, import_id)
    if not job:
        raise HTTPException(status_code=404, detail="Bulk import not found")
    return job


def _expire_stale_jobs(db: Session) -> None:
    """Fail jobs whose worker died mid-run.

    There is no supervisor process: a restart during analysis or apply would
    otherwise leave the job spinning forever and block every future import.
    """
    cutoff = utcnow() - STALE_AFTER
    stale = db.exec(
        select(ProductBulkImports).where(
            ProductBulkImports.status.in_(RUNNING_STATUSES),
            ProductBulkImports.heartbeat_at < cutoff,
        )
    ).all()
    if not stale:
        return

    for job in stale:
        job.status = "failed"
        job.failure_reason = "Interrupted: the server restarted while this import was running."
        job.finished_at = utcnow()
    db.commit()


def _supersede_pending_previews(db: Session) -> None:
    """Retire previews nobody answered.

    Uploading a new file is the user saying "use this one instead". A preview
    that was never confirmed changed nothing, so closing it costs nothing — and
    leaving it open would deadlock every future import.
    """
    pending = db.exec(
        select(ProductBulkImports).where(ProductBulkImports.status == "awaiting_confirmation")
    ).all()
    if not pending:
        return

    for job in pending:
        job.status = "cancelled"
        job.failure_reason = "Superseded by a newer upload. Nothing was changed."
        job.finished_at = utcnow()
    db.commit()


def _to_read(db: Session, job: ProductBulkImports) -> BulkImportRead:
    creator = db.get(Employees, job.created_by)
    unknown = json.loads(job.unknown_taxonomy) if job.unknown_taxonomy else []

    return BulkImportRead(
        id=job.id or 0,
        file_name=job.file_name,
        status=job.status,
        exported_at=job.exported_at,
        export_scope=job.export_scope,
        total_rows=job.total_rows,
        create_count=job.create_count,
        update_count=job.update_count,
        unchanged_count=job.unchanged_count,
        error_count=job.error_count,
        conflict_count=job.conflict_count,
        unknown_taxonomy=[UnknownTaxonomy(**entry) for entry in unknown],
        create_missing_taxonomy=job.create_missing_taxonomy,
        apply_conflicts=job.apply_conflicts,
        created_count=job.created_count,
        updated_count=job.updated_count,
        failed_count=job.failed_count,
        skipped_count=job.skipped_count,
        has_error_report=bool(job.error_report_path),
        failure_reason=job.failure_reason,
        created_by=job.created_by,
        creator=ProductEmployee(
            employee_id=creator.employee_id,
            display_name=creator.display_name,
            email=creator.email,
            title=creator.title,
        )
        if creator
        else None,
        created_at=job.created_at,
        started_at=job.started_at,
        finished_at=job.finished_at,
    )
