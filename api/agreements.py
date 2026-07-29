import hashlib
import io
import os
import re
import zipfile
from contextlib import suppress
from datetime import UTC, date, datetime
from pathlib import Path, PurePosixPath
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import func
from sqlmodel import Session, and_, col, exists, or_, select

from api.dependencies import require_module_permission
from bd.dependencies import get_db
from core.config import settings
from core.datetime_utils import utcnow
from models.agreements import AgreementAttachmentType, AgreementAttachments, AgreementType, Agreements
from models.customers import Customers
from models.employees import Employees
from schemas.agreements import (
    AgreementAttachmentRead,
    AgreementCreate,
    AgreementDetail,
    AgreementListResponse,
    AgreementOwnerUpdate,
    AgreementRead,
    AgreementTerminationUpdate,
    AgreementUpdate,
)

router = APIRouter()

MAX_FILE_SIZE = 25 * 1024 * 1024
MAX_OFFICE_UNCOMPRESSED_SIZE = 250 * 1024 * 1024
ALLOWED_FILE_TYPES = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}
OFFICE_REQUIRED_ENTRIES = {
    ".docx": "word/document.xml",
    ".xlsx": "xl/workbook.xml",
    ".pptx": "ppt/presentation.xml",
}

if os.getenv("ENVIRONMENT", "local").lower() == "prod":
    UPLOAD_DIR = Path(os.getenv("UPLOADS_DIR", "/home/home/uploads")) / "agreements"
else:
    UPLOAD_DIR = Path(__file__).resolve().parents[1] / settings.UPLOAD_DIR / "agreements"


def _employee_id(user_permissions: dict) -> int:
    return int(user_permissions["employee"]["employee_id"])


def _sanitize_filename(filename: str | None) -> str:
    if not filename:
        raise HTTPException(status_code=400, detail="Uploaded file must have a filename")
    basename = PurePosixPath(filename.replace("\\", "/")).name
    sanitized = re.sub(r"[\x00-\x1f<>:\"/\\|?*]+", "_", basename).strip(" .")
    sanitized = re.sub(r"\s+", " ", sanitized)
    if not sanitized:
        raise HTTPException(status_code=400, detail="Uploaded file must have a valid filename")
    if len(sanitized) > 255:
        suffix = Path(sanitized).suffix
        sanitized = f"{Path(sanitized).stem[: 255 - len(suffix)]}{suffix}"
    return sanitized


def _validate_office_container(content: bytes, extension: str) -> None:
    if not content.startswith(b"PK") or not zipfile.is_zipfile(io.BytesIO(content)):
        raise HTTPException(status_code=400, detail="Office file content does not match its extension")
    try:  # noqa: PLW0717
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            entries = set(archive.namelist())
            if "[Content_Types].xml" not in entries or OFFICE_REQUIRED_ENTRIES[extension] not in entries:
                raise HTTPException(status_code=400, detail="Office file content does not match its extension")
            if any(name.lower().endswith("vbaproject.bin") for name in entries):
                raise HTTPException(status_code=400, detail="Macro-enabled Office files are not allowed")
            if sum(entry.file_size for entry in archive.infolist()) > MAX_OFFICE_UNCOMPRESSED_SIZE:
                raise HTTPException(status_code=400, detail="Office file expands beyond the allowed size")
    except zipfile.BadZipFile as exc:
        raise HTTPException(status_code=400, detail="Office file container is invalid") from exc


def _read_and_validate_upload(upload: UploadFile) -> tuple[bytes, str, str, str, str]:
    original_filename = _sanitize_filename(upload.filename)
    extension = Path(original_filename).suffix.lower()
    expected_mime = ALLOWED_FILE_TYPES.get(extension)
    if not expected_mime:
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, XLSX, and PPTX files are allowed")
    declared_mime = (upload.content_type or "").split(";", maxsplit=1)[0].strip().lower()
    if declared_mime != expected_mime:
        raise HTTPException(status_code=400, detail="Declared file type does not match the file extension")

    content = upload.file.read(MAX_FILE_SIZE + 1)
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File exceeds the 25 MiB limit")
    if extension == ".pdf":
        if not content.startswith(b"%PDF-") or b"%%EOF" not in content[-2048:]:
            raise HTTPException(status_code=400, detail="PDF file signature is invalid")
    else:
        _validate_office_container(content, extension)

    return content, original_filename, extension, expected_mime, hashlib.sha256(content).hexdigest()


def _storage_path(relative_path: str) -> Path:
    root = UPLOAD_DIR.resolve()
    path = (root / relative_path).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Attachment file not found") from exc
    return path


def _write_file(agreement_id: int, extension: str, content: bytes) -> tuple[str, str, Path]:
    stored_filename = f"{uuid4().hex}{extension}"
    relative_path = f"{agreement_id}/{stored_filename}"
    path = _storage_path(relative_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_name(f".{stored_filename}.{uuid4().hex}.tmp")
    try:  # noqa: PLW0717
        with temporary_path.open("xb") as output:
            bytes_written = output.write(content)
            if bytes_written != len(content):
                raise OSError("Agreement document write was incomplete")
            output.flush()
            os.fsync(output.fileno())
        temporary_path.replace(path)
    except Exception:
        _remove_file(temporary_path)
        _remove_file(path)
        raise
    return stored_filename, relative_path, path


def _remove_file(path: Path | None) -> None:
    if not path:
        return
    with suppress(OSError):
        path.unlink(missing_ok=True)


def _lifecycle(agreement: Agreements, today: date | None = None) -> str:
    current_date = today or datetime.now(UTC).date()
    if agreement.terminated_on:
        return "TERMINATED"
    if agreement.effective_date > current_date:
        return "UPCOMING"
    if agreement.expiration_date and agreement.expiration_date < current_date:
        return "EXPIRED"
    return "ACTIVE"


def _customer_name(customer: Customers | None) -> str | None:
    if not customer:
        return None
    return customer.company_name or " ".join(filter(None, [customer.first_name, customer.last_name])) or None


def _employee_name(employee: Employees | None, fallback_id: int | None = None) -> str | None:
    if employee:
        return (
            employee.display_name or " ".join(filter(None, [employee.first_name, employee.last_name])) or employee.email
        )
    return f"Employee {fallback_id}" if fallback_id else None


def _serialize_agreements(db: Session, agreements: list[Agreements]) -> list[AgreementRead]:
    employee_ids = {
        actor_id
        for agreement in agreements
        for actor_id in (
            agreement.owner_employee_id,
            agreement.created_by,
            agreement.updated_by,
            agreement.archived_by,
        )
        if actor_id is not None
    }
    customer_ids = {agreement.customer_id for agreement in agreements if agreement.customer_id is not None}
    employees = {
        employee.employee_id: employee
        for employee in db.exec(select(Employees).where(col(Employees.employee_id).in_(employee_ids))).all()
    }
    customers = {
        customer.customer_id: customer
        for customer in db.exec(select(Customers).where(col(Customers.customer_id).in_(customer_ids))).all()
    }
    return [
        AgreementRead(
            agreement_id=agreement.agreement_id,
            title=agreement.title,
            agreement_type=agreement.agreement_type,
            customer_id=agreement.customer_id,
            customer_name=_customer_name(customers.get(agreement.customer_id)),
            counterparty_name=agreement.counterparty_name,
            owner_employee_id=agreement.owner_employee_id,
            owner_name=_employee_name(employees.get(agreement.owner_employee_id), agreement.owner_employee_id)
            or "Unknown",
            effective_date=agreement.effective_date,
            expiration_date=agreement.expiration_date,
            terminated_on=agreement.terminated_on,
            termination_reason=agreement.termination_reason,
            terminated_by=agreement.terminated_by,
            notes=agreement.notes,
            lifecycle_status=_lifecycle(agreement),
            created_at=agreement.created_at,
            created_by=agreement.created_by,
            created_by_name=_employee_name(employees.get(agreement.created_by), agreement.created_by) or "Unknown",
            updated_at=agreement.updated_at,
            updated_by=agreement.updated_by,
            updated_by_name=_employee_name(employees.get(agreement.updated_by), agreement.updated_by),
            archived_at=agreement.archived_at,
            archived_by=agreement.archived_by,
            archived_by_name=_employee_name(employees.get(agreement.archived_by), agreement.archived_by),
        )
        for agreement in agreements
    ]


def _serialize_attachment(attachment: AgreementAttachments) -> AgreementAttachmentRead:
    return AgreementAttachmentRead.model_validate(attachment, from_attributes=True)


def _get_agreement(db: Session, agreement_id: int) -> Agreements:
    agreement = db.get(Agreements, agreement_id)
    if not agreement:
        raise HTTPException(status_code=404, detail="Agreement not found")
    return agreement


def _get_attachment(db: Session, agreement_id: int, attachment_id: int) -> AgreementAttachments:
    attachment = db.get(AgreementAttachments, attachment_id)
    if not attachment or attachment.agreement_id != agreement_id:
        raise HTTPException(status_code=404, detail="Agreement attachment not found")
    return attachment


def _validate_references(db: Session, customer_id: int | None, owner_employee_id: int) -> None:
    if customer_id is not None and not db.get(Customers, customer_id):
        raise HTTPException(status_code=404, detail="Customer not found")
    if not db.get(Employees, owner_employee_id):
        raise HTTPException(status_code=404, detail="Owner employee not found")


def _detail(db: Session, agreement: Agreements) -> AgreementDetail:
    base = _serialize_agreements(db, [agreement])[0]
    attachments = db.exec(
        select(AgreementAttachments)
        .where(AgreementAttachments.agreement_id == agreement.agreement_id)
        .order_by(AgreementAttachments.created_at.desc())
    ).all()
    primary = [item for item in attachments if item.attachment_type == AgreementAttachmentType.PRIMARY]
    supporting = [
        item
        for item in attachments
        if item.attachment_type == AgreementAttachmentType.SUPPORTING and item.archived_at is None
    ]
    return AgreementDetail(
        **base.model_dump(),
        current_primary=next((_serialize_attachment(item) for item in primary if item.is_current), None),
        primary_versions=[_serialize_attachment(item) for item in primary],
        supporting_attachments=[_serialize_attachment(item) for item in supporting],
    )


@router.get("", response_model=list[AgreementRead] | AgreementListResponse)
def list_agreements(
    lifecycle_status: str | None = Query(None, pattern="^(UPCOMING|ACTIVE|EXPIRED|TERMINATED)$"),
    customer_id: int | None = None,
    counterparty: str | None = None,
    agreement_type: AgreementType | None = None,
    owner_employee_id: int | None = None,
    effective_from: date | None = None,
    effective_to: date | None = None,
    expiration_from: date | None = None,
    expiration_to: date | None = None,
    archived: bool = False,
    search: str | None = None,
    sort_by: str = Query(
        "updated_at",
        pattern="^(title|counterparty_name|agreement_type|owner_employee_id|effective_date|expiration_date|updated_at)$",
    ),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    with_meta: bool = False,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_module_permission("agreements", "can_view")),
):
    query = select(Agreements)
    filters = [Agreements.archived_at.is_not(None) if archived else Agreements.archived_at.is_(None)]
    today = datetime.now(UTC).date()
    if lifecycle_status == "TERMINATED":
        filters.append(Agreements.terminated_on.is_not(None))
    elif lifecycle_status == "UPCOMING":
        filters.extend([Agreements.terminated_on.is_(None), Agreements.effective_date > today])
    elif lifecycle_status == "EXPIRED":
        filters.extend(
            [
                Agreements.terminated_on.is_(None),
                Agreements.expiration_date.is_not(None),
                Agreements.expiration_date < today,
            ]
        )
    elif lifecycle_status == "ACTIVE":
        filters.extend(
            [
                Agreements.terminated_on.is_(None),
                Agreements.effective_date <= today,
                or_(Agreements.expiration_date.is_(None), Agreements.expiration_date >= today),
            ]
        )
    if customer_id is not None:
        filters.append(Agreements.customer_id == customer_id)
    if counterparty:
        filters.append(Agreements.counterparty_name.ilike(f"%{counterparty.strip()}%"))
    if agreement_type:
        filters.append(Agreements.agreement_type == agreement_type)
    if owner_employee_id is not None:
        filters.append(Agreements.owner_employee_id == owner_employee_id)
    if effective_from:
        filters.append(Agreements.effective_date >= effective_from)
    if effective_to:
        filters.append(Agreements.effective_date <= effective_to)
    if expiration_from:
        filters.append(Agreements.expiration_date >= expiration_from)
    if expiration_to:
        filters.append(Agreements.expiration_date <= expiration_to)
    if search:
        term = f"%{search.strip()}%"
        filename_match = exists().where(
            and_(
                AgreementAttachments.agreement_id == Agreements.agreement_id,
                AgreementAttachments.original_filename.ilike(term),
            )
        )
        filters.append(or_(Agreements.title.ilike(term), Agreements.counterparty_name.ilike(term), filename_match))

    query = query.where(and_(*filters))
    sort_column = getattr(Agreements, sort_by)
    order = sort_column.asc() if sort_dir == "asc" else sort_column.desc()
    query = query.order_by(order, Agreements.agreement_id.desc()).offset(skip).limit(limit)
    records = list(db.exec(query).all())
    items = _serialize_agreements(db, records)
    if not with_meta:
        return items

    total_result = db.exec(select(func.count()).select_from(Agreements).where(and_(*filters))).one()
    total = total_result if isinstance(total_result, int) else total_result[0]
    return AgreementListResponse(items=items, total=total, skip=skip, limit=limit, has_more=skip + len(items) < total)


@router.post("", response_model=AgreementDetail, status_code=201)
def create_agreement(
    title: str = Form(...),
    agreement_type: AgreementType = Form(...),
    counterparty_name: str = Form(...),
    owner_employee_id: int = Form(...),
    effective_date: date = Form(...),
    expiration_date: date | None = Form(None),
    customer_id: int | None = Form(None),
    notes: str | None = Form(None),
    primary_file: UploadFile = File(...),
    user_permissions: dict = Depends(require_module_permission("agreements", "can_create")),
    db: Session = Depends(get_db),
):
    payload = AgreementCreate(
        title=title,
        agreement_type=agreement_type,
        customer_id=customer_id,
        counterparty_name=counterparty_name,
        owner_employee_id=owner_employee_id,
        effective_date=effective_date,
        expiration_date=expiration_date,
        notes=notes,
    )
    content, original_filename, extension, mime_type, sha256 = _read_and_validate_upload(primary_file)
    _validate_references(db, payload.customer_id, payload.owner_employee_id)
    actor_id = _employee_id(user_permissions)
    saved_path: Path | None = None
    try:  # noqa: PLW0717
        agreement = Agreements(**payload.model_dump(), created_by=actor_id)
        db.add(agreement)
        db.flush()
        stored_filename, relative_path, saved_path = _write_file(agreement.agreement_id, extension, content)
        attachment = AgreementAttachments(
            agreement_id=agreement.agreement_id,
            attachment_type=AgreementAttachmentType.PRIMARY,
            version_number=1,
            is_current=True,
            original_filename=original_filename,
            stored_filename=stored_filename,
            storage_path=relative_path,
            file_extension=extension,
            mime_type=mime_type,
            file_size=len(content),
            sha256=sha256,
            created_by=actor_id,
        )
        db.add(attachment)
        db.flush()
        db.refresh(agreement)
        db.refresh(attachment)
        db.commit()
    except Exception as exc:
        db.rollback()
        _remove_file(saved_path)
        raise HTTPException(status_code=500, detail="Agreement could not be created") from exc
    return _detail(db, agreement)


@router.get("/{agreement_id}", response_model=AgreementDetail)
def get_agreement(
    agreement_id: int,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_module_permission("agreements", "can_view")),
):
    return _detail(db, _get_agreement(db, agreement_id))


@router.patch("/{agreement_id}", response_model=AgreementDetail)
def update_agreement(
    agreement_id: int,
    payload: AgreementUpdate,
    user_permissions: dict = Depends(require_module_permission("agreements", "can_edit")),
    db: Session = Depends(get_db),
):
    agreement = _get_agreement(db, agreement_id)
    update_data = payload.model_dump(exclude_unset=True)
    customer_id = update_data.get("customer_id", agreement.customer_id)
    _validate_references(db, customer_id, agreement.owner_employee_id)
    effective = update_data.get("effective_date", agreement.effective_date)
    expiration = update_data.get("expiration_date", agreement.expiration_date)
    if expiration and expiration < effective:
        raise HTTPException(status_code=422, detail="Expiration date cannot precede effective date")
    for field, value in update_data.items():
        setattr(agreement, field, value)
    agreement.updated_at = utcnow()
    agreement.updated_by = _employee_id(user_permissions)
    db.add(agreement)
    db.commit()
    db.refresh(agreement)
    return _detail(db, agreement)


@router.delete("/{agreement_id}", response_model=AgreementDetail)
def archive_agreement(
    agreement_id: int,
    user_permissions: dict = Depends(require_module_permission("agreements", "can_delete")),
    db: Session = Depends(get_db),
):
    agreement = _get_agreement(db, agreement_id)
    if agreement.archived_at is None:
        agreement.archived_at = utcnow()
        agreement.archived_by = _employee_id(user_permissions)
        agreement.updated_at = agreement.archived_at
        agreement.updated_by = agreement.archived_by
        db.add(agreement)
        db.commit()
        db.refresh(agreement)
    return _detail(db, agreement)


@router.post("/{agreement_id}/restore", response_model=AgreementDetail)
def restore_agreement(
    agreement_id: int,
    user_permissions: dict = Depends(require_module_permission("agreements", "admin_actions")),
    db: Session = Depends(get_db),
):
    agreement = _get_agreement(db, agreement_id)
    agreement.archived_at = None
    agreement.archived_by = None
    agreement.updated_at = utcnow()
    agreement.updated_by = _employee_id(user_permissions)
    db.add(agreement)
    db.commit()
    db.refresh(agreement)
    return _detail(db, agreement)


@router.patch("/{agreement_id}/termination", response_model=AgreementDetail)
def update_termination(
    agreement_id: int,
    payload: AgreementTerminationUpdate,
    user_permissions: dict = Depends(require_module_permission("agreements", "admin_actions")),
    db: Session = Depends(get_db),
):
    agreement = _get_agreement(db, agreement_id)
    if payload.terminated_on and payload.terminated_on < agreement.effective_date:
        raise HTTPException(status_code=422, detail="Termination date cannot precede effective date")
    actor_id = _employee_id(user_permissions)
    agreement.terminated_on = payload.terminated_on
    agreement.termination_reason = payload.termination_reason
    agreement.terminated_by = actor_id if payload.terminated_on else None
    agreement.updated_at = utcnow()
    agreement.updated_by = actor_id
    db.add(agreement)
    db.commit()
    db.refresh(agreement)
    return _detail(db, agreement)


@router.patch("/{agreement_id}/owner", response_model=AgreementDetail)
def reassign_owner(
    agreement_id: int,
    payload: AgreementOwnerUpdate,
    user_permissions: dict = Depends(require_module_permission("agreements", "admin_actions")),
    db: Session = Depends(get_db),
):
    agreement = _get_agreement(db, agreement_id)
    _validate_references(db, agreement.customer_id, payload.owner_employee_id)
    agreement.owner_employee_id = payload.owner_employee_id
    agreement.updated_at = utcnow()
    agreement.updated_by = _employee_id(user_permissions)
    db.add(agreement)
    db.commit()
    db.refresh(agreement)
    return _detail(db, agreement)


@router.get("/{agreement_id}/attachments", response_model=list[AgreementAttachmentRead])
def list_attachments(
    agreement_id: int,
    include_archived: bool = False,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_module_permission("agreements", "can_view")),
):
    _get_agreement(db, agreement_id)
    query = select(AgreementAttachments).where(AgreementAttachments.agreement_id == agreement_id)
    if not include_archived:
        query = query.where(AgreementAttachments.archived_at.is_(None))
    attachments = db.exec(query.order_by(AgreementAttachments.created_at.desc())).all()
    return [_serialize_attachment(item) for item in attachments]


@router.get("/{agreement_id}/attachments/versions", response_model=list[AgreementAttachmentRead])
def list_primary_versions(
    agreement_id: int,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_module_permission("agreements", "can_view")),
):
    _get_agreement(db, agreement_id)
    versions = db.exec(
        select(AgreementAttachments)
        .where(
            AgreementAttachments.agreement_id == agreement_id,
            AgreementAttachments.attachment_type == AgreementAttachmentType.PRIMARY,
        )
        .order_by(AgreementAttachments.version_number.desc())
    ).all()
    return [_serialize_attachment(item) for item in versions]


def _add_attachment(
    db: Session,
    agreement: Agreements,
    upload: UploadFile,
    actor_id: int,
    attachment_type: AgreementAttachmentType,
    replacement_reason: str | None = None,
) -> AgreementAttachmentRead:
    content, original_filename, extension, mime_type, sha256 = _read_and_validate_upload(upload)
    saved_path: Path | None = None
    try:  # noqa: PLW0717
        version_number = None
        if attachment_type == AgreementAttachmentType.PRIMARY:
            current = db.exec(
                select(AgreementAttachments).where(
                    AgreementAttachments.agreement_id == agreement.agreement_id,
                    AgreementAttachments.attachment_type == AgreementAttachmentType.PRIMARY,
                    AgreementAttachments.is_current.is_(True),
                )
            ).first()
            if current:
                current.is_current = False
                db.add(current)
            max_version = db.exec(
                select(func.max(AgreementAttachments.version_number)).where(
                    AgreementAttachments.agreement_id == agreement.agreement_id,
                    AgreementAttachments.attachment_type == AgreementAttachmentType.PRIMARY,
                )
            ).one()
            version_number = (max_version or 0) + 1

        stored_filename, relative_path, saved_path = _write_file(agreement.agreement_id, extension, content)
        attachment = AgreementAttachments(
            agreement_id=agreement.agreement_id,
            attachment_type=attachment_type,
            version_number=version_number,
            is_current=attachment_type == AgreementAttachmentType.PRIMARY,
            replacement_reason=replacement_reason,
            original_filename=original_filename,
            stored_filename=stored_filename,
            storage_path=relative_path,
            file_extension=extension,
            mime_type=mime_type,
            file_size=len(content),
            sha256=sha256,
            created_by=actor_id,
        )
        agreement.updated_at = utcnow()
        agreement.updated_by = actor_id
        db.add(attachment)
        db.add(agreement)
        db.flush()
        db.refresh(attachment)
        db.commit()
    except Exception as exc:
        db.rollback()
        _remove_file(saved_path)
        raise HTTPException(status_code=500, detail="Attachment could not be saved") from exc
    return _serialize_attachment(attachment)


@router.post("/{agreement_id}/attachments", response_model=AgreementAttachmentRead, status_code=201)
def add_supporting_attachment(
    agreement_id: int,
    file: UploadFile = File(...),
    user_permissions: dict = Depends(require_module_permission("agreements", "can_edit")),
    db: Session = Depends(get_db),
):
    agreement = _get_agreement(db, agreement_id)
    return _add_attachment(db, agreement, file, _employee_id(user_permissions), AgreementAttachmentType.SUPPORTING)


@router.post("/{agreement_id}/attachments/primary", response_model=AgreementAttachmentRead, status_code=201)
def replace_primary_attachment(
    agreement_id: int,
    replacement_reason: str = Form(..., min_length=1, max_length=1000),
    file: UploadFile = File(...),
    user_permissions: dict = Depends(require_module_permission("agreements", "can_edit")),
    db: Session = Depends(get_db),
):
    agreement = _get_agreement(db, agreement_id)
    reason = replacement_reason.strip()
    if not reason:
        raise HTTPException(status_code=422, detail="Replacement reason is required")
    return _add_attachment(
        db,
        agreement,
        file,
        _employee_id(user_permissions),
        AgreementAttachmentType.PRIMARY,
        reason,
    )


@router.delete("/{agreement_id}/attachments/{attachment_id}", response_model=AgreementAttachmentRead)
def archive_supporting_attachment(
    agreement_id: int,
    attachment_id: int,
    user_permissions: dict = Depends(require_module_permission("agreements", "can_edit")),
    db: Session = Depends(get_db),
):
    attachment = _get_attachment(db, agreement_id, attachment_id)
    if attachment.attachment_type != AgreementAttachmentType.SUPPORTING:
        raise HTTPException(status_code=400, detail="Primary agreement versions cannot be archived")
    if attachment.archived_at is None:
        attachment.archived_at = utcnow()
        attachment.archived_by = _employee_id(user_permissions)
        db.add(attachment)
        db.commit()
        db.refresh(attachment)
    return _serialize_attachment(attachment)


def _file_response(attachment: AgreementAttachments, preview: bool = False) -> FileResponse:
    path = _storage_path(attachment.storage_path)
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Attachment file not found")
    return FileResponse(
        path=path,
        filename=attachment.original_filename,
        media_type=attachment.mime_type,
        content_disposition_type="inline" if preview else "attachment",
    )


@router.get("/{agreement_id}/attachments/{attachment_id}/download")
def download_attachment(
    agreement_id: int,
    attachment_id: int,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_module_permission("agreements", "can_view")),
):
    return _file_response(_get_attachment(db, agreement_id, attachment_id))


@router.get("/{agreement_id}/attachments/{attachment_id}/preview")
def preview_attachment(
    agreement_id: int,
    attachment_id: int,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_module_permission("agreements", "can_view")),
):
    attachment = _get_attachment(db, agreement_id, attachment_id)
    if attachment.file_extension != ".pdf" or attachment.mime_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Preview is available only for PDF files")
    return _file_response(attachment, preview=True)
