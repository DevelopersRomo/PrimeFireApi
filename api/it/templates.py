import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from api.dependencies import require_module_permission
from api.it.dependencies import get_tenant_id
from bd.dependencies import get_db
from core.config import settings
from models.it.templates import ITPdfTemplates
from schemas.it.templates import ItPdfTemplateCreate, ItPdfTemplateRead, ItPdfTemplateUpdate

# Upload directory per environment (same convention as curriculums)
ENV = os.getenv("ENVIRONMENT", "local").lower()
if ENV == "prod":
    uploads_base = os.getenv("UPLOADS_DIR", "/home/home/uploads")
    LOGO_UPLOAD_DIR = Path(uploads_base) / "it" / "templates"
else:
    LOGO_UPLOAD_DIR = Path(settings.UPLOAD_DIR) / "it" / "templates"

LOGO_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_LOGO_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg", ".webp"}

router = APIRouter()


def _clear_default(db: Session, tenant_id: int) -> None:
    current_defaults = db.exec(
        select(ITPdfTemplates).where(
            ITPdfTemplates.tenant_id == tenant_id,
            ITPdfTemplates.is_default == True,  # noqa: E712
        )
    ).all()
    for template in current_defaults:
        template.is_default = False
        db.add(template)


@router.get("/", response_model=list[ItPdfTemplateRead])
def list_templates(
    include_inactive: bool = Query(default=False),
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_templates", "can_view")),
):
    statement = select(ITPdfTemplates).where(ITPdfTemplates.tenant_id == tenant_id)
    if not include_inactive:
        statement = statement.where(ITPdfTemplates.is_active == True)  # noqa: E712
    return db.exec(statement.order_by(ITPdfTemplates.name)).all()


@router.get("/{template_id}", response_model=ItPdfTemplateRead)
def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_templates", "can_view")),
):
    template = db.get(ITPdfTemplates, template_id)
    if not template or template.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    return template


@router.post("/", response_model=ItPdfTemplateRead, status_code=status.HTTP_201_CREATED)
def create_template(
    payload: ItPdfTemplateCreate,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_templates", "can_create")),
):
    if payload.is_default:
        _clear_default(db, tenant_id)
    template = ITPdfTemplates(tenant_id=tenant_id, **payload.model_dump())
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.post("/{template_id}/logo", response_model=ItPdfTemplateRead)
def upload_template_logo(
    template_id: int,
    logo_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_templates", "can_edit")),
):
    """Upload a logo image file and point logo_url to the stored file."""
    template = db.get(ITPdfTemplates, template_id)
    if not template or template.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

    file_extension = Path(logo_file.filename or "").suffix.lower()
    if file_extension not in ALLOWED_LOGO_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PNG, JPG, JPEG, SVG and WEBP files are allowed.",
        )

    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = LOGO_UPLOAD_DIR / unique_filename
    file_path.write_bytes(logo_file.file.read())

    # Remove the previously uploaded file if the template had one.
    previous = template.logo_url
    if previous and not previous.startswith("http") and Path(previous).exists():
        Path(previous).unlink(missing_ok=True)

    template.logo_url = str(file_path).replace("\\", "/")
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.get("/{template_id}/logo")
def get_template_logo(
    template_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_templates", "can_view")),
):
    """Serve the uploaded logo file (404 when logo_url is an external URL or missing)."""
    template = db.get(ITPdfTemplates, template_id)
    if not template or template.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

    logo = template.logo_url
    if not logo or logo.startswith("http") or not Path(logo).exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No uploaded logo file")

    return FileResponse(path=logo, filename=Path(logo).name)


@router.patch("/{template_id}", response_model=ItPdfTemplateRead)
def update_template(
    template_id: int,
    payload: ItPdfTemplateUpdate,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_templates", "can_edit")),
):
    template = db.get(ITPdfTemplates, template_id)
    if not template or template.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

    data = payload.model_dump(exclude_unset=True)
    if data.get("is_default"):
        _clear_default(db, tenant_id)
    for key, value in data.items():
        setattr(template, key, value)

    db.add(template)
    db.commit()
    db.refresh(template)
    return template
