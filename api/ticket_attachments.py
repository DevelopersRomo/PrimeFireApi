import os
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from api.dependencies import get_current_employee_with_permissions, require_authentication
from bd.dependencies import get_db
from models.ticket_messages import TicketAttachments
from schemas.ticket_messages import TicketAttachment

# Load .env
load_dotenv()

# Detectar entorno
ENV = os.getenv("ENVIRONMENT", "local").lower()
IS_PRODUCTION = ENV == "prod"

# Directorio de uploads según el entorno
if IS_PRODUCTION:
    # Azure App Service Linux: usar variable UPLOADS_DIR o /home/home/uploads
    uploads_base = os.getenv("UPLOADS_DIR", "/home/home/uploads")
    UPLOAD_DIR = Path(uploads_base) / "tickets"
else:
    # Local: uploads/tickets
    from core.config import settings

    UPLOAD_DIR = Path(settings.UPLOAD_DIR) / "tickets"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter()


def attachment_to_schema(db_att: TicketAttachments) -> TicketAttachment:
    return TicketAttachment(
        ticket_attachment_id=db_att.ticket_attachment_id,
        ticket_id=db_att.ticket_id,
        ticket_message_id=db_att.ticket_message_id,
        file_name=db_att.file_name,
        file_type=db_att.file_type,
        file_path=db_att.file_path,
        created_at=db_att.created_at,
    )


@router.get("/tickets/{ticket_id}/attachments", response_model=list[TicketAttachment])
def list_attachments_for_ticket(ticket_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    atts = db.exec(
        select(TicketAttachments).where(TicketAttachments.ticket_id == ticket_id).order_by(TicketAttachments.created_at)
    ).all()
    return [attachment_to_schema(a) for a in atts]


@router.get("/attachments/{attachment_id}")
def get_attachment(attachment_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    db_att = db.get(TicketAttachments, attachment_id)
    if not db_att:
        raise HTTPException(status_code=404, detail="Attachment not found")

    # If file exists on disk (file_path set), return the file directly
    if db_att.file_path:
        # Check if path in DB is absolute or relative
        saved_path = Path(db_att.file_path)

        # If path starts with uploads/ but UPLOAD_DIR is different, we might fail to find it if we just join.
        # But if we assume db_att.file_path is the full relative path from app root as stored previously:
        storage_path = saved_path

        # If not absolute, try joining with current working directory or check if it exists as is
        if not storage_path.is_absolute() and not storage_path.exists():
            # Fallback: maybe it's relative to UPLOAD_DIR but stored as relative string?
            # For now, rely on file_path being what was returned by create_attachment
            pass

        if storage_path.exists():
            # Use original filename for Content-Disposition
            return FileResponse(
                path=str(storage_path),
                filename=db_att.file_name or storage_path.name,
                media_type=db_att.file_type or "application/octet-stream",
            )
        # if file missing, fall back to metadata
    return attachment_to_schema(db_att)


@router.post("/tickets/{ticket_id}/attachments", response_model=TicketAttachment)
def create_attachment(
    ticket_id: int,
    ticket_message_id: int | None = Form(None),
    file: UploadFile | None = File(None),
    file_name: str | None = Form(None),
    file_type: str | None = Form(None),
    file_path: str | None = Form(None),
    user_permissions: dict = Depends(get_current_employee_with_permissions),
    db: Session = Depends(get_db),
):
    # If an UploadFile is provided, save it to UPLOAD_DIR/{ticket_id}/ and set file_path
    rel_path = None
    final_file_name = file_name
    final_file_type = file_type
    if file is not None:
        # ensure directory exists
        base_dir = UPLOAD_DIR / str(ticket_id)
        base_dir.mkdir(parents=True, exist_ok=True)
        ext = Path(file.filename).suffix
        unique = f"{uuid4().hex}{ext}"
        storage_path = base_dir / unique

        # write file to disk
        with Path(storage_path).open("wb") as out:  # noqa: FURB103
            content = file.file.read()
            out.write(content)
        # Store the path that can be used to retrieve it later (relative to CWD or absolute)
        rel_path = str(storage_path).replace("\\", "/")
        final_file_name = file.filename
        final_file_type = file.content_type

    # If no upload, allow provided file_path (for metadata-only clients)
    if rel_path is None and file_path:
        rel_path = file_path

    db_att = TicketAttachments(
        ticket_id=ticket_id,
        ticket_message_id=ticket_message_id,
        file_name=final_file_name,
        file_type=final_file_type,
        file_path=rel_path,
        created_at=datetime.now(UTC),
    )
    db.add(db_att)
    db.commit()
    db.refresh(db_att)
    return attachment_to_schema(db_att)


@router.delete("/attachments/{attachment_id}")
def delete_attachment(
    attachment_id: int,
    user_permissions: dict = Depends(get_current_employee_with_permissions),
    db: Session = Depends(get_db),
):
    db_att = db.get(TicketAttachments, attachment_id)
    if not db_att:
        raise HTTPException(status_code=404, detail="Attachment not found")

    # Require admin permission or leave deletion to admins/authorized users
    has_admin = False
    for perm in user_permissions.get("permissions", []):
        if perm.get("module_key") == "tickets":
            has_admin = perm.get("permissions", {}).get("admin_actions", False)
    if not has_admin:
        raise HTTPException(status_code=403, detail="Not allowed to delete attachment")

    db.delete(db_att)
    db.commit()
    return {"success": True, "message": "Attachment deleted"}
