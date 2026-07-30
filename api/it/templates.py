import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import func
from sqlmodel import Session, select

from api.dependencies import require_module_permission
from api.it.dependencies import get_tenant_id
from bd.dependencies import get_db
from core.config import settings
from models.it.templates import ITPdfTemplates
from schemas.it.templates import ItPdfTemplateCreate, ItPdfTemplateRead, ItPdfTemplateUpdate
from schemas.pagination import PaginatedResponse

# Upload directory per environment. Mirrors customer_attachments /
# product_attachments so behaviour is consistent across modules.
ENV = os.getenv("ENVIRONMENT", "local").lower()
IS_PRODUCTION = ENV == "prod"

if IS_PRODUCTION:
    # Azure App Service Linux: usar variable UPLOADS_DIR o /home/home/uploads
    uploads_base = os.getenv("UPLOADS_DIR", "/home/home/uploads")
    LOGO_UPLOAD_DIR = Path(uploads_base) / "it" / "templates"
else:
    # Local: anchor to API root so files land in PrimeFireApi/uploads/it/templates
    BASE_DIR = Path(__file__).resolve().parents[2]
    LOGO_UPLOAD_DIR = BASE_DIR / settings.UPLOAD_DIR / "it" / "templates"

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


@router.get("/", response_model=list[ItPdfTemplateRead] | PaginatedResponse[ItPdfTemplateRead])
def list_templates(
    include_inactive: bool = Query(default=False),
    skip: int = Query(0, ge=0),
    limit: int = Query(24, ge=1, le=1000),
    with_meta: bool = Query(False),
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_templates", "can_view")),
):
    filters = [ITPdfTemplates.tenant_id == tenant_id]
    if not include_inactive:
        filters.append(ITPdfTemplates.is_active == True)  # noqa: E712
    statement = select(ITPdfTemplates).where(*filters).order_by(
        ITPdfTemplates.name,
        ITPdfTemplates.template_id,
    )
    if with_meta:
        statement = statement.offset(skip).limit(limit)
    template_rows = db.exec(statement).all()
    if not with_meta:
        return template_rows

    items = [ItPdfTemplateRead.model_validate(row, from_attributes=True) for row in template_rows]
    total = db.exec(select(func.count()).select_from(ITPdfTemplates).where(*filters)).one()
    return PaginatedResponse[ItPdfTemplateRead](
        items=items,
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + len(items) < total,
    )


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
