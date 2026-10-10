import contextlib
import os
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from api.dependencies import get_current_employee_with_permissions
from api.tickets import ensure_ticket_visible
from bd.dependencies import get_db
from core.datetime_utils import utcnow
from core.file_storage import confine_to
from models.ticket_messages import TicketAttachments
from models.tickets import Tickets
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


def _confined_path(file_path: str) -> Path:
    """Resolve a stored file_path (written relative to CWD, or absolute) and confine it to UPLOAD_DIR."""
    return confine_to(UPLOAD_DIR, Path(file_path).resolve())


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
def list_attachments_for_ticket(
    ticket_id: int,
    user_permissions: dict = Depends(get_current_employee_with_permissions),
    db: Session = Depends(get_db),
):
    ticket = db.get(Tickets, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    ensure_ticket_visible(ticket, user_permissions, db)

    atts = db.exec(
        select(TicketAttachments).where(TicketAttachments.ticket_id == ticket_id).order_by(TicketAttachments.created_at)
    ).all()
    return [attachment_to_schema(a) for a in atts]


@router.get("/attachments/{attachment_id}")
def get_attachment(
    attachment_id: int,
    user_permissions: dict = Depends(get_current_employee_with_permissions),
    db: Session = Depends(get_db),
):
    db_att = db.get(TicketAttachments, attachment_id)
    if not db_att:
        raise HTTPException(status_code=404, detail="Attachment not found")
    ticket = db.get(Tickets, db_att.ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    ensure_ticket_visible(ticket, user_permissions, db)

    if db_att.file_path:
        storage_path = _confined_path(db_att.file_path)
        if not storage_path.is_file():
            raise HTTPException(status_code=404, detail="File not found")
        # Use original filename for Content-Disposition
        return FileResponse(
            path=str(storage_path),
            filename=db_att.file_name or storage_path.name,
            media_type=db_att.file_type or "application/octet-stream",
        )
    return attachment_to_schema(db_att)


@router.post("/tickets/{ticket_id}/attachments", response_model=TicketAttachment)
def create_attachment(
    ticket_id: int,
    ticket_message_id: int | None = Form(None),
    file: UploadFile | None = File(None),
    file_name: str | None = Form(None),
    file_type: str | None = Form(None),
    user_permissions: dict = Depends(get_current_employee_with_permissions),
    db: Session = Depends(get_db),
):
    ticket = db.get(Tickets, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    ensure_ticket_visible(ticket, user_permissions, db)

    if file is None:
        raise HTTPException(status_code=400, detail="File is required")

    # Save the upload to UPLOAD_DIR/{ticket_id}/ and set file_path
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

    db_att = TicketAttachments(
        ticket_id=ticket_id,
        ticket_message_id=ticket_message_id,
        file_name=final_file_name,
        file_type=final_file_type,
        file_path=rel_path,
        created_at=utcnow(),
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
    ticket = db.get(Tickets, db_att.ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    ensure_ticket_visible(ticket, user_permissions, db)

    # Require admin permission or leave deletion to admins/authorized users
    has_admin = False
    for perm in user_permissions.get("permissions", []):
        if perm.get("module_key") == "tickets":
            has_admin = perm.get("permissions", {}).get("admin_actions", False)
    if not has_admin:
        raise HTTPException(status_code=403, detail="Not allowed to delete attachment")

    file_path = db_att.file_path
    db.delete(db_att)
    db.commit()
    if file_path:
        # A stored path that escapes the upload root raises 404 in confine_to: never touch it
        with contextlib.suppress(HTTPException):
            _confined_path(file_path).unlink(missing_ok=True)
    return {"success": True, "message": "Attachment deleted"}
