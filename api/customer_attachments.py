import os
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from api.dependencies import get_current_employee_with_permissions, require_authentication
from bd.dependencies import get_db
from models.customers import CustomerAttachments, Customers
from schemas.customers import CustomerAttachment, CustomerEmployee

# Load .env
load_dotenv()

# Detectar entorno
ENV = os.getenv("ENVIRONMENT", "local").lower()
IS_PRODUCTION = ENV == "prod"

# Directorio de uploads según el entorno
if IS_PRODUCTION:
    # Azure App Service Linux: usar variable UPLOADS_DIR o /home/home/uploads
    uploads_base = os.getenv("UPLOADS_DIR", "/home/home/uploads")
    UPLOAD_DIR = Path(uploads_base) / "customers"
else:
    # Local: uploads/customers
    from core.config import settings

    BASE_DIR = Path(__file__).resolve().parents[1]
    UPLOAD_DIR = BASE_DIR / settings.UPLOAD_DIR / "customers"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter()


def resolve_upload_root() -> Path:
    """Resolve uploads directory path."""
    return UPLOAD_DIR


def attachment_to_schema(db_att: CustomerAttachments) -> CustomerAttachment:
    """Convert CustomerAttachments model to CustomerAttachment schema."""
    return CustomerAttachment(
        CustomerAttachmentId=db_att.CustomerAttachmentId,
        CustomerId=db_att.CustomerId,
        FileName=db_att.FileName,
        FileType=db_att.FileType,
        FilePath=db_att.FilePath,
        CreatedAt=db_att.CreatedAt,
        CreatedBy=db_att.CreatedBy,
        creator=CustomerEmployee(
            EmployeeId=db_att.creator.EmployeeId,
            DisplayName=db_att.creator.DisplayName,
            Email=db_att.creator.Email,
            Title=db_att.creator.Title,
        )
        if db_att.creator
        else None,
    )


@router.get("/customers/{customer_id}/attachments", response_model=list[CustomerAttachment])
def list_attachments_for_customer(
    customer_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)
):
    """List all attachments for a customer."""
    customer = db.get(Customers, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    atts = db.exec(
        select(CustomerAttachments)
        .options(selectinload(CustomerAttachments.creator))
        .where(CustomerAttachments.CustomerId == customer_id)
        .order_by(CustomerAttachments.CreatedAt)
    ).all()

    return [attachment_to_schema(a) for a in atts]


@router.get("/customers/attachments/{attachment_id}")
def get_attachment(attachment_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    """Get attachment metadata or download file."""
    db_att = db.get(CustomerAttachments, attachment_id)
    if not db_att:
        raise HTTPException(status_code=404, detail="Attachment not found")

    if db_att.FilePath:
        storage_path = Path(db_att.FilePath)
        if not storage_path.is_absolute():
            storage_path = BASE_DIR / storage_path
        if storage_path.exists():
            return FileResponse(
                path=str(storage_path),
                filename=db_att.FileName or storage_path.name,
                media_type=db_att.FileType or "application/octet-stream",
            )

    return attachment_to_schema(db_att)


@router.post("/customers/{customer_id}/attachments", response_model=CustomerAttachment)
def create_attachment(
    customer_id: int,
    file: UploadFile | None = File(None),
    file_name: str | None = Form(None),
    file_type: str | None = Form(None),
    file_path: str | None = Form(None),
    user_permissions: dict = Depends(get_current_employee_with_permissions),
    db: Session = Depends(get_db),
):
    """Create a new attachment for a customer."""
    customer = db.get(Customers, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    current_employee_id = user_permissions["employee"]["EmployeeId"]

    rel_path = None
    final_file_name = file_name
    final_file_type = file_type

    if file is not None:
        base_dir = resolve_upload_root() / "customers" / str(customer_id)
        base_dir.mkdir(parents=True, exist_ok=True)
        ext = Path(file.filename).suffix
        unique = f"{uuid4().hex}{ext}"
        storage_path = base_dir / unique

        with Path(storage_path).open("wb") as out:  # noqa: FURB103
            content = file.file.read()
            out.write(content)

        rel_path = str(storage_path).replace("\\", "/")
        final_file_name = file.filename
        final_file_type = file.content_type

    if rel_path is None and file_path:
        rel_path = file_path

    if not final_file_name:
        raise HTTPException(status_code=400, detail="File name is required")

    db_att = CustomerAttachments(
        CustomerId=customer_id,
        FileName=final_file_name,
        FileType=final_file_type,
        FilePath=rel_path,
        CreatedBy=current_employee_id,
        CreatedAt=datetime.now(UTC),
    )

    db.add(db_att)
    db.commit()
    db.refresh(db_att)

    db_att = db.exec(
        select(CustomerAttachments)
        .options(selectinload(CustomerAttachments.creator))
        .filter(CustomerAttachments.CustomerAttachmentId == db_att.CustomerAttachmentId)
    ).first()

    return attachment_to_schema(db_att)


@router.delete("/customers/attachments/{attachment_id}")
def delete_attachment(
    attachment_id: int,
    user_permissions: dict = Depends(get_current_employee_with_permissions),
    db: Session = Depends(get_db),
):
    """Delete a customer attachment."""
    db_att = db.get(CustomerAttachments, attachment_id)
    if not db_att:
        raise HTTPException(status_code=404, detail="Attachment not found")

    db.delete(db_att)
    db.commit()
    return {"success": True, "message": "Attachment deleted successfully"}
