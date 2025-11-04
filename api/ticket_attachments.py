from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime, timezone
from fastapi.responses import FileResponse
import os
from uuid import uuid4
from pathlib import Path

from bd.dependencies import get_db
from api.dependencies import require_authentication, get_current_employee_with_permissions
from models.ticket_messages import TicketAttachments
from schemas.ticket_messages import TicketAttachmentCreate, TicketAttachment

router = APIRouter()


def attachment_to_schema(db_att: TicketAttachments) -> TicketAttachment:
    return TicketAttachment(
        TicketAttachmentId=db_att.TicketAttachmentId,
        TicketId=db_att.TicketId,
        TicketMessageId=db_att.TicketMessageId,
        FileName=db_att.FileName,
        FileType=db_att.FileType,
        FilePath=db_att.FilePath,
        CreatedAt=db_att.CreatedAt,
    )


@router.get("/tickets/{ticket_id}/attachments", response_model=List[TicketAttachment])
def list_attachments_for_ticket(ticket_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    atts = db.exec(select(TicketAttachments).where(TicketAttachments.TicketId == ticket_id).order_by(TicketAttachments.CreatedAt)).all()
    return [attachment_to_schema(a) for a in atts]


@router.get("/attachments/{attachment_id}")
def get_attachment(attachment_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    db_att = db.get(TicketAttachments, attachment_id)
    if not db_att:
        raise HTTPException(status_code=404, detail="Attachment not found")

    # If file exists on disk (FilePath set), return the file directly
    if db_att.FilePath:
        # FilePath is stored as relative path like 'tickets/{ticket_id}/...'
        storage_path = Path("uploads") / Path(db_att.FilePath)
        if storage_path.exists():
            # Use original filename for Content-Disposition
            return FileResponse(path=str(storage_path), filename=db_att.FileName or storage_path.name, media_type=db_att.FileType or "application/octet-stream")
        # if file missing, fall back to metadata
    return attachment_to_schema(db_att)


@router.post("/tickets/{ticket_id}/attachments", response_model=TicketAttachment)
def create_attachment(
    ticket_id: int,
    TicketMessageId: Optional[int] = Form(None),
    file: Optional[UploadFile] = File(None),
    file_name: Optional[str] = Form(None),
    file_type: Optional[str] = Form(None),
    file_path: Optional[str] = Form(None),
    user_permissions: dict = Depends(get_current_employee_with_permissions),
    db: Session = Depends(get_db)
):
    # If an UploadFile is provided, save it to uploads/tickets/{ticket_id}/ and set FilePath
    rel_path = None
    final_file_name = file_name
    final_file_type = file_type
    if file is not None:
        # ensure directory exists
        base_dir = Path("uploads") / "tickets" / str(ticket_id)
        base_dir.mkdir(parents=True, exist_ok=True)
        ext = Path(file.filename).suffix
        unique = f"{uuid4().hex}{ext}"
        storage_rel = Path("tickets") / str(ticket_id) / unique
        storage_path = Path("uploads") / storage_rel
        # write file to disk
        with open(storage_path, "wb") as out:
            content = file.file.read()
            out.write(content)
        rel_path = str(storage_rel).replace("\\", "/")
        final_file_name = file.filename
        final_file_type = file.content_type

    # If no upload, allow provided file_path (for metadata-only clients)
    if rel_path is None and file_path:
        rel_path = file_path

    db_att = TicketAttachments(
        TicketId=ticket_id,
        TicketMessageId=TicketMessageId,
        FileName=final_file_name,
        FileType=final_file_type,
        FilePath=rel_path,
        CreatedAt=datetime.now(timezone.utc)
    )
    db.add(db_att)
    db.commit()
    db.refresh(db_att)
    return attachment_to_schema(db_att)


@router.delete("/attachments/{attachment_id}")
def delete_attachment(attachment_id: int, user_permissions: dict = Depends(get_current_employee_with_permissions), db: Session = Depends(get_db)):
    db_att = db.get(TicketAttachments, attachment_id)
    if not db_att:
        raise HTTPException(status_code=404, detail="Attachment not found")

    # Require admin permission or leave deletion to admins/authorized users
    has_admin = False
    for perm in user_permissions.get("permissions", []):
        if perm.get("module_key") == "tickets":
            has_admin = perm.get("permissions", {}).get("AdminActions", False)
    if not has_admin:
        raise HTTPException(status_code=403, detail="Not allowed to delete attachment")

    db.delete(db_att)
    db.commit()
    return {"success": True, "message": "Attachment deleted"}
