import io
import os
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from api.dependencies import get_current_employee_with_permissions, require_authentication
from bd.dependencies import get_db
from core.datetime_utils import utcnow
from models.products import ProductAttachments, Products
from schemas.products import ProductAttachment, ProductEmployee

load_dotenv()

ENV = os.getenv("ENVIRONMENT", "local").lower()
IS_PRODUCTION = ENV == "prod"

if IS_PRODUCTION:
    uploads_base = os.getenv("UPLOADS_DIR", "/home/home/uploads")
    UPLOAD_DIR = Path(uploads_base) / "products"
    BASE_DIR = Path(uploads_base)
else:
    from core.config import settings

    BASE_DIR = Path(__file__).resolve().parents[1]
    UPLOAD_DIR = BASE_DIR / settings.UPLOAD_DIR / "products"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter()

MAX_IMAGES_PER_PRODUCT = 3
ALLOWED_EXTENSIONS = {".heic", ".heif", ".png", ".jpg", ".jpeg"}
HEIC_EXTENSIONS = {".heic", ".heif"}


def attachment_to_schema(db_att: ProductAttachments) -> ProductAttachment:
    return ProductAttachment(
        product_attachment_id=db_att.product_attachment_id,
        product_id=db_att.product_id,
        file_name=db_att.file_name,
        file_type=db_att.file_type,
        file_path=db_att.file_path,
        created_at=db_att.created_at,
        created_by=db_att.created_by,
        creator=ProductEmployee(
            employee_id=db_att.creator.employee_id,
            display_name=db_att.creator.display_name,
            email=db_att.creator.email,
            title=db_att.creator.title,
        )
        if db_att.creator
        else None,
    )


def convert_heic_to_png(raw_bytes: bytes) -> bytes:
    """Convert HEIC/HEIF bytes to PNG bytes. Browsers can't render HEIC natively."""
    try:
        import pillow_heif
        from PIL import Image

        pillow_heif.register_heif_opener()
        image = Image.open(io.BytesIO(raw_bytes))
        output = io.BytesIO()
        image.save(output, format="PNG")
        return output.getvalue()
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Could not convert HEIC/HEIF image. Please try another file.",
        ) from exc


@router.get("/products/{product_id}/attachments", response_model=list[ProductAttachment])
def list_attachments_for_product(
    product_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)
):
    product = db.get(Products, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    atts = db.exec(
        select(ProductAttachments)
        .options(selectinload(ProductAttachments.creator))
        .where(ProductAttachments.product_id == product_id)
        .order_by(ProductAttachments.created_at)
    ).all()

    return [attachment_to_schema(a) for a in atts]


@router.get("/products/attachments/{attachment_id}")
def get_attachment(attachment_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    db_att = db.get(ProductAttachments, attachment_id)
    if not db_att:
        raise HTTPException(status_code=404, detail="Attachment not found")

    if db_att.file_path:
        storage_path = Path(db_att.file_path)
        if not storage_path.is_absolute():
            storage_path = BASE_DIR / storage_path
        if storage_path.exists():
            return FileResponse(
                path=str(storage_path),
                filename=db_att.file_name or storage_path.name,
                media_type=db_att.file_type or "application/octet-stream",
            )

    return attachment_to_schema(db_att)


@router.post("/products/{product_id}/attachments", response_model=ProductAttachment)
def create_attachment(
    product_id: int,
    file: UploadFile | None = File(None),
    user_permissions: dict = Depends(get_current_employee_with_permissions),
    db: Session = Depends(get_db),
):
    product = db.get(Products, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if file is None or not file.filename:
        raise HTTPException(status_code=400, detail="File is required")

    existing_count = db.exec(
        select(func.count()).select_from(ProductAttachments).where(ProductAttachments.product_id == product_id)
    ).one()
    if existing_count >= MAX_IMAGES_PER_PRODUCT:
        raise HTTPException(
            status_code=409,
            detail=f"Maximum of {MAX_IMAGES_PER_PRODUCT} images per product reached",
        )

    original_ext = Path(file.filename).suffix.lower()
    if original_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only HEIC, HEIF, PNG, JPG and JPEG images are allowed",
        )

    current_employee_id = user_permissions["employee"]["employee_id"]

    base_dir = UPLOAD_DIR / str(product_id)
    base_dir.mkdir(parents=True, exist_ok=True)

    raw_bytes = file.file.read()

    if original_ext in HEIC_EXTENSIONS:
        raw_bytes = convert_heic_to_png(raw_bytes)
        final_ext = ".png"
        final_file_name = f"{Path(file.filename).stem}.png"
        final_file_type = "image/png"
    else:
        final_ext = original_ext
        final_file_name = file.filename
        final_file_type = file.content_type or f"image/{final_ext.lstrip('.')}"

    unique = f"{uuid4().hex}{final_ext}"
    storage_path = base_dir / unique

    with Path(storage_path).open("wb") as out:  # noqa: FURB103
        out.write(raw_bytes)

    rel_path = str(storage_path).replace("\\", "/")

    db_att = ProductAttachments(
        product_id=product_id,
        file_name=final_file_name,
        file_type=final_file_type,
        file_path=rel_path,
        created_by=current_employee_id,
        created_at=utcnow(),
    )

    db.add(db_att)
    db.commit()
    db.refresh(db_att)

    db_att = db.exec(
        select(ProductAttachments)
        .options(selectinload(ProductAttachments.creator))
        .filter(ProductAttachments.product_attachment_id == db_att.product_attachment_id)
    ).first()

    return attachment_to_schema(db_att)


@router.delete("/products/attachments/{attachment_id}")
def delete_attachment(
    attachment_id: int,
    user_permissions: dict = Depends(get_current_employee_with_permissions),
    db: Session = Depends(get_db),
):
    db_att = db.get(ProductAttachments, attachment_id)
    if not db_att:
        raise HTTPException(status_code=404, detail="Attachment not found")

    if db_att.file_path:
        storage_path = Path(db_att.file_path)
        if not storage_path.is_absolute():
            storage_path = BASE_DIR / storage_path
        if storage_path.exists():
            try:
                storage_path.unlink()
            except OSError:
                pass

    db.delete(db_att)
    db.commit()
    return {"success": True, "message": "Attachment deleted successfully"}
