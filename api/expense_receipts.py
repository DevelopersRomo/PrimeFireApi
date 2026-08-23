"""Receipt upload, download and extraction.

Upload returns as soon as the file is on disk; extraction runs in a background
task because Tesseract costs one to four seconds per page. The frontend polls
`/expenses/receipts/{id}/extraction` until the status leaves `pending`.
"""

import json
import logging
import os
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from api.dependencies import get_current_employee, require_module_permission
from bd.dependencies import get_db
from core.datetime_utils import utcnow
from models.employees import Employees
from models.expenses import (
    ExpenseReceiptExtractions,
    ExpenseReceipts,
    ExpenseReportItems,
    ExpenseReports,
)
from schemas.expenses import ExpenseReceipt, ExpenseReceiptExtraction, ExtractionCandidate
from services.expenses import approvals, dedupe, policies
from services.expenses.ocr.extract import extract_receipt

logger = logging.getLogger(__name__)

router = APIRouter()

MODULE_KEY = "expenses"
EDITABLE_STATUSES = {"draft", "rejected"}

ALLOWED_SUFFIXES = {".pdf", ".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".bmp", ".tif", ".tiff"}
MAX_UPLOAD_BYTES = 20 * 1024 * 1024

ENV = os.getenv("ENVIRONMENT", "local").lower()
IS_PRODUCTION = ENV == "prod"

if IS_PRODUCTION:
    UPLOAD_DIR = Path(os.getenv("UPLOADS_DIR", "/home/home/uploads")) / "expenses"
else:
    from core.config import settings

    UPLOAD_DIR = Path(settings.UPLOAD_DIR) / "expenses"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _get_report_or_404(db: Session, report_id: int) -> ExpenseReports:
    report = db.get(ExpenseReports, report_id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense report not found")
    return report


def _assert_owner_or_admin(report: ExpenseReports, employee: Employees, user_permissions: dict) -> None:
    if report.employee_id == employee.employee_id or approvals.has_admin_actions(user_permissions):
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This expense report belongs to another employee")


def _assert_can_view(
    db: Session, report: ExpenseReports, employee: Employees, user_permissions: dict
) -> None:
    """Same audience as the report itself: its owner, an admin, or its approver.

    Module-level `can_view` alone is not enough. Receipts are addressed by a bare
    integer id, so without this any colleague holding the permission could walk
    the range and download somebody else's invoices, bank references and RFC.
    """
    if report.employee_id == employee.employee_id or approvals.has_admin_actions(user_permissions):
        return
    if approvals.can_review(db, report, employee, user_permissions):
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="This expense report belongs to another employee"
    )


def _assert_editable(report: ExpenseReports) -> None:
    if report.status not in EDITABLE_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A report in status '{report.status}' can no longer be edited",
        )


def _delete_receipt(db: Session, report: ExpenseReports, receipt: ExpenseReceipts) -> None:
    for row in db.exec(
        select(ExpenseReceiptExtractions).where(ExpenseReceiptExtractions.receipt_id == receipt.receipt_id)
    ).all():
        db.delete(row)

    # Clear every report flag before deleting its item-linked receipt state.
    # replace_flags below recreates the current advisory set after the commit.
    from models.expenses import ExpenseReportFlags

    for flag in db.exec(select(ExpenseReportFlags).where(ExpenseReportFlags.report_id == report.report_id)).all():
        db.delete(flag)

    if receipt.file_path:
        stored = Path(receipt.file_path)
        if stored.exists():
            try:
                stored.unlink()
            except OSError as exc:
                # Match the established attachment convention: retain no stale
                # metadata when storage cleanup is unavailable, but make it visible.
                logger.warning("[EXPENSES] Could not remove %s: %s", stored, exc)

    # The line this receipt produced goes with it. Lines are created from a
    # reading now, so a receipt the user removes would otherwise leave its amount
    # in the report total with nothing backing it. A line another receipt still
    # points at is kept: only the last one standing takes it down.
    orphaned_item_id = receipt.item_id
    db.delete(receipt)
    db.flush()

    if orphaned_item_id:
        remaining = db.exec(
            select(ExpenseReceipts).where(ExpenseReceipts.item_id == orphaned_item_id)
        ).all()
        if not remaining:
            item = db.get(ExpenseReportItems, orphaned_item_id)
            if item:
                db.delete(item)
                db.flush()

    approvals.recalculate_totals(db, report)
    report.updated_at = utcnow()
    db.add(report)
    db.commit()

    # Duplicate alerts are scoped to every report of the employee, so removing
    # one receipt can invalidate an alert stored on a different report too.
    affected_reports = db.exec(
        select(ExpenseReports).where(ExpenseReports.employee_id == report.employee_id)
    ).all()
    for affected_report in affected_reports:
        policies.replace_flags(db, affected_report)


def _extraction_to_schema(row: ExpenseReceiptExtractions) -> ExpenseReceiptExtraction:
    candidates: list[ExtractionCandidate] = []
    if row.candidates_json:
        try:
            for entry in json.loads(row.candidates_json):
                candidates.append(
                    ExtractionCandidate(
                        value=entry["value"],
                        label=entry.get("label"),
                        score=entry.get("score", 0.0),
                        box=entry.get("box"),
                        page=entry.get("page", 1),
                    )
                )
        except (ValueError, KeyError, TypeError):
            logger.warning("[EXPENSES] Malformed candidates_json on extraction %s", row.extraction_id)

    return ExpenseReceiptExtraction(
        **row.model_dump(exclude={"candidates_json", "raw_text", "created_at"}),
        candidates=candidates,
    )


def _run_extraction(receipt_id: int, currency_default: str | None) -> None:
    """Background worker: extract, persist, then re-run the policy engine.

    Opens its own session because the request session is already closed by the
    time a background task runs.
    """
    from bd.connection import SessionLocal
    from services.expenses import policies

    db = SessionLocal()
    try:
        receipt = db.get(ExpenseReceipts, receipt_id)
        if not receipt or not receipt.file_path:
            return

        row = db.exec(
            select(ExpenseReceiptExtractions).where(ExpenseReceiptExtractions.receipt_id == receipt_id)
        ).first()
        if row is None:
            row = ExpenseReceiptExtractions(receipt_id=receipt_id)

        result = extract_receipt(Path(receipt.file_path), currency_default=currency_default)

        row.engine = result.engine
        row.status = result.status
        row.raw_text = result.raw_text[:100000] if result.raw_text else None
        row.detected_total = result.total
        row.detected_subtotal = result.subtotal
        row.detected_tax = result.tax
        row.detected_tip = result.tip
        row.detected_currency = result.currency
        row.detected_date = result.expense_date
        row.detected_merchant = result.merchant
        row.detected_tax_id = result.tax_id
        row.detected_uuid = result.uuid
        row.confidence = round(result.confidence, 4)
        row.arithmetic_ok = result.arithmetic_ok
        row.candidates_json = json.dumps([candidate.as_dict() for candidate in result.candidates])
        row.error_message = result.error_message
        row.duration_ms = result.duration_ms
        row.processed_at = utcnow()

        receipt.page_count = result.page_count

        db.add(row)
        db.add(receipt)
        db.commit()

        report = db.get(ExpenseReports, receipt.report_id)
        if report:
            policies.replace_flags(db, report)

    except Exception:
        logger.exception("[EXPENSES] Background extraction failed for receipt %s", receipt_id)
    finally:
        db.close()


@router.post("/reports/{report_id}/receipts", response_model=ExpenseReceipt)
def upload_receipt(
    report_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    item_id: int | None = Form(None),
    db: Session = Depends(get_db),
    current_employee: Employees = Depends(get_current_employee),
    user_permissions: dict = Depends(require_module_permission(MODULE_KEY, "can_create")),
):
    report = _get_report_or_404(db, report_id)
    # Uploading is an edit of somebody's claim: same gate as every other edit.
    _assert_owner_or_admin(report, current_employee, user_permissions)
    _assert_editable(report)

    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{suffix}'. Upload a PDF or an image.",
        )

    content = file.file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Receipt exceeds the 20 MB limit",
        )

    base_dir = UPLOAD_DIR / str(report_id)
    base_dir.mkdir(parents=True, exist_ok=True)
    storage_path = base_dir / f"{uuid4().hex}{suffix}"
    storage_path.write_bytes(content)

    receipt = ExpenseReceipts(
        report_id=report_id,
        item_id=item_id,
        file_name=file.filename or storage_path.name,
        file_type=file.content_type,
        file_path=str(storage_path).replace("\\", "/"),
        file_size=len(content),
        sha256=dedupe.file_sha256(storage_path),
        phash=dedupe.perceptual_hash(storage_path),
        uploaded_by=current_employee.employee_id,
    )
    db.add(receipt)
    db.commit()
    db.refresh(receipt)

    # Placeholder row so the frontend can start polling immediately.
    db.add(ExpenseReceiptExtractions(receipt_id=receipt.receipt_id, status="pending"))
    db.commit()

    background_tasks.add_task(_run_extraction, receipt.receipt_id, report.currency)

    return ExpenseReceipt(**receipt.model_dump(), extraction_status="pending")


@router.get("/reports/{report_id}/receipts", response_model=list[ExpenseReceipt])
def list_receipts(
    report_id: int,
    db: Session = Depends(get_db),
    current_employee: Employees = Depends(get_current_employee),
    user_permissions: dict = Depends(require_module_permission(MODULE_KEY, "can_view")),
):
    report = _get_report_or_404(db, report_id)
    _assert_can_view(db, report, current_employee, user_permissions)
    receipts = db.exec(
        select(ExpenseReceipts)
        .where(ExpenseReceipts.report_id == report_id)
        .order_by(ExpenseReceipts.created_at)
    ).all()

    statuses = {
        row.receipt_id: row.status
        for row in db.exec(
            select(ExpenseReceiptExtractions).where(
                ExpenseReceiptExtractions.receipt_id.in_([r.receipt_id for r in receipts] or [0])  # type: ignore[attr-defined]
            )
        ).all()
    }

    return [
        ExpenseReceipt(**receipt.model_dump(), extraction_status=statuses.get(receipt.receipt_id))
        for receipt in receipts
    ]


@router.get("/receipts/{receipt_id}")
def download_receipt(
    receipt_id: int,
    db: Session = Depends(get_db),
    current_employee: Employees = Depends(get_current_employee),
    user_permissions: dict = Depends(require_module_permission(MODULE_KEY, "can_view")),
):
    receipt = db.get(ExpenseReceipts, receipt_id)
    if not receipt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receipt not found")

    _assert_can_view(db, _get_report_or_404(db, receipt.report_id), current_employee, user_permissions)

    if receipt.file_path:
        stored = Path(receipt.file_path)
        if stored.exists():
            return FileResponse(
                path=str(stored),
                filename=receipt.file_name or stored.name,
                media_type=receipt.file_type or "application/octet-stream",
            )

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receipt file is missing from storage")


@router.get("/receipts/{receipt_id}/extraction", response_model=ExpenseReceiptExtraction)
def get_extraction(
    receipt_id: int,
    db: Session = Depends(get_db),
    current_employee: Employees = Depends(get_current_employee),
    user_permissions: dict = Depends(require_module_permission(MODULE_KEY, "can_view")),
):
    receipt = db.get(ExpenseReceipts, receipt_id)
    if not receipt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receipt not found")
    _assert_can_view(db, _get_report_or_404(db, receipt.report_id), current_employee, user_permissions)

    row = db.exec(
        select(ExpenseReceiptExtractions).where(ExpenseReceiptExtractions.receipt_id == receipt_id)
    ).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No extraction for this receipt")
    return _extraction_to_schema(row)


@router.post("/receipts/{receipt_id}/reprocess", response_model=ExpenseReceiptExtraction)
def reprocess_receipt(
    receipt_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_employee: Employees = Depends(get_current_employee),
    user_permissions: dict = Depends(require_module_permission(MODULE_KEY, "can_edit")),
):
    receipt = db.get(ExpenseReceipts, receipt_id)
    if not receipt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receipt not found")

    report = db.get(ExpenseReports, receipt.report_id)
    if report:
        _assert_owner_or_admin(report, current_employee, user_permissions)

    row = db.exec(
        select(ExpenseReceiptExtractions).where(ExpenseReceiptExtractions.receipt_id == receipt_id)
    ).first()
    if row is None:
        row = ExpenseReceiptExtractions(receipt_id=receipt_id)

    row.status = "pending"
    row.error_message = None
    db.add(row)
    db.commit()
    db.refresh(row)

    background_tasks.add_task(_run_extraction, receipt_id, report.currency if report else None)
    return _extraction_to_schema(row)


@router.delete("/reports/{report_id}/receipts/{receipt_id}")
def delete_report_receipt(
    report_id: int,
    receipt_id: int,
    db: Session = Depends(get_db),
    current_employee: Employees = Depends(get_current_employee),
    user_permissions: dict = Depends(require_module_permission(MODULE_KEY, "can_delete")),
):
    report = _get_report_or_404(db, report_id)
    _assert_owner_or_admin(report, current_employee, user_permissions)
    _assert_editable(report)

    receipt = db.get(ExpenseReceipts, receipt_id)
    if not receipt or receipt.report_id != report_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receipt not found on this expense report")

    _delete_receipt(db, report, receipt)
    return {"success": True, "message": "Receipt deleted"}
