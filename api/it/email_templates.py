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
from core.datetime_utils import utcnow
from models.customers import Customers
from models.it.email_templates import ITEmailCustomerTemplate, ITEmailDefault
from schemas.it.email_templates import (
    EmailCustomerTemplateRead,
    EmailDefaultRead,
    EmailTemplateBase,
    EmailTemplateRowRead,
)
from schemas.pagination import PaginatedResponse

ENV = os.getenv("ENVIRONMENT", "local").lower()
IS_PRODUCTION = ENV == "prod"

if IS_PRODUCTION:
    uploads_base = os.getenv("UPLOADS_DIR", "/home/home/uploads")
    LOGO_UPLOAD_DIR = Path(uploads_base) / "it" / "email-templates"
else:
    BASE_DIR = Path(__file__).resolve().parents[2]
    LOGO_UPLOAD_DIR = BASE_DIR / settings.UPLOAD_DIR / "it" / "email-templates"

LOGO_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_LOGO_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg", ".webp"}

router = APIRouter()


def _save_logo(logo_file: UploadFile, previous_path: str | None) -> str:
    file_extension = Path(logo_file.filename or "").suffix.lower()
    if file_extension not in ALLOWED_LOGO_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PNG, JPG, JPEG, SVG and WEBP files are allowed.",
        )

    file_path = LOGO_UPLOAD_DIR / f"{uuid.uuid4()}{file_extension}"
    file_path.write_bytes(logo_file.file.read())

    if previous_path and Path(previous_path).exists():
        Path(previous_path).unlink(missing_ok=True)

    return str(file_path).replace("\\", "/")


def _logo_response(logo_path: str | None) -> FileResponse:
    if not logo_path or not Path(logo_path).exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No uploaded logo file")

    return FileResponse(path=logo_path, filename=Path(logo_path).name)


# ---------------------------------------------------------------------------
# Default template (tenant-wide, singleton)
# ---------------------------------------------------------------------------


@router.get("/default", response_model=EmailDefaultRead | None)
def get_default_template(
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_email_templates", "can_view")),
):
    return db.exec(
        select(ITEmailDefault).where(ITEmailDefault.tenant_id == tenant_id)
    ).first()


@router.put("/default", response_model=EmailDefaultRead)
def upsert_default_template(
    payload: EmailTemplateBase,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_email_templates", "can_edit")),
):
    template = db.exec(
        select(ITEmailDefault).where(ITEmailDefault.tenant_id == tenant_id)
    ).first()

    if template is None:
        template = ITEmailDefault(tenant_id=tenant_id, **payload.model_dump())
    else:
        for key, value in payload.model_dump().items():
            setattr(template, key, value)
        template.updated_at = utcnow()

    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.post("/default/logo", response_model=EmailDefaultRead)
def upload_default_logo(
    logo_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_email_templates", "can_edit")),
):
    template = db.exec(
        select(ITEmailDefault).where(ITEmailDefault.tenant_id == tenant_id)
    ).first()
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

    template.logo_path = _save_logo(logo_file, template.logo_path)
    template.updated_at = utcnow()
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.get("/default/logo")
def get_default_logo(
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_email_templates", "can_view")),
):
    template = db.exec(
        select(ITEmailDefault).where(ITEmailDefault.tenant_id == tenant_id)
    ).first()
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

    return _logo_response(template.logo_path)


# ---------------------------------------------------------------------------
# Per-customer overrides
# ---------------------------------------------------------------------------


@router.get("/rows", response_model=PaginatedResponse[EmailTemplateRowRead])
def list_template_rows(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_email_templates", "can_view")),
):
    customer_total = db.exec(
        select(func.count())
        .select_from(ITEmailCustomerTemplate)
        .where(ITEmailCustomerTemplate.tenant_id == tenant_id)
    ).one()
    total = customer_total + 1
    rows: list[EmailTemplateRowRead] = []

    customer_skip = max(skip - 1, 0)
    customer_limit = limit
    if skip == 0:
        default_template = db.exec(
            select(ITEmailDefault).where(ITEmailDefault.tenant_id == tenant_id)
        ).first()
        rows.append(
            EmailTemplateRowRead(
                kind="default",
                configured=default_template is not None,
                template=(
                    EmailDefaultRead.model_validate(default_template, from_attributes=True)
                    if default_template
                    else None
                ),
            )
        )
        customer_limit -= 1

    if customer_limit > 0:
        customer_templates = db.exec(
            select(ITEmailCustomerTemplate)
            .where(ITEmailCustomerTemplate.tenant_id == tenant_id)
            .order_by(
                ITEmailCustomerTemplate.customer_id,
                ITEmailCustomerTemplate.template_id,
            )
            .offset(customer_skip)
            .limit(customer_limit)
        ).all()
        rows.extend(
            EmailTemplateRowRead(
                kind="customer",
                customer_id=template.customer_id,
                configured=True,
                template=EmailCustomerTemplateRead.model_validate(template, from_attributes=True),
            )
            for template in customer_templates
        )

    return PaginatedResponse[EmailTemplateRowRead](
        items=rows,
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + len(rows) < total,
    )


@router.get("/customer-ids", response_model=list[int])
def list_configured_customer_ids(
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_email_templates", "can_view")),
):
    return list(
        db.exec(
            select(ITEmailCustomerTemplate.customer_id)
            .where(ITEmailCustomerTemplate.tenant_id == tenant_id)
            .order_by(ITEmailCustomerTemplate.customer_id)
        ).all()
    )


@router.get("/customer", response_model=list[EmailCustomerTemplateRead])
def list_customer_templates(
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_email_templates", "can_view")),
):
    return db.exec(
        select(ITEmailCustomerTemplate)
        .where(ITEmailCustomerTemplate.tenant_id == tenant_id)
        .order_by(ITEmailCustomerTemplate.customer_id)
    ).all()


@router.get("/customer/{customer_id}", response_model=EmailCustomerTemplateRead | None)
def get_customer_template(
    customer_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_email_templates", "can_view")),
):
    return db.exec(
        select(ITEmailCustomerTemplate).where(
            ITEmailCustomerTemplate.tenant_id == tenant_id,
            ITEmailCustomerTemplate.customer_id == customer_id,
        )
    ).first()


@router.put("/customer/{customer_id}", response_model=EmailCustomerTemplateRead)
def upsert_customer_template(
    customer_id: int,
    payload: EmailTemplateBase,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_email_templates", "can_edit")),
):
    if db.get(Customers, customer_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    template = db.exec(
        select(ITEmailCustomerTemplate).where(
            ITEmailCustomerTemplate.tenant_id == tenant_id,
            ITEmailCustomerTemplate.customer_id == customer_id,
        )
    ).first()

    if template is None:
        template = ITEmailCustomerTemplate(
            tenant_id=tenant_id,
            customer_id=customer_id,
            **payload.model_dump(),
        )
    else:
        for key, value in payload.model_dump().items():
            setattr(template, key, value)
        template.updated_at = utcnow()

    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.post("/customer/{customer_id}/logo", response_model=EmailCustomerTemplateRead)
def upload_customer_logo(
    customer_id: int,
    logo_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_email_templates", "can_edit")),
):
    template = db.exec(
        select(ITEmailCustomerTemplate).where(
            ITEmailCustomerTemplate.tenant_id == tenant_id,
            ITEmailCustomerTemplate.customer_id == customer_id,
        )
    ).first()
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

    template.logo_path = _save_logo(logo_file, template.logo_path)
    template.updated_at = utcnow()
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.get("/customer/{customer_id}/logo")
def get_customer_logo(
    customer_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_email_templates", "can_view")),
):
    template = db.exec(
        select(ITEmailCustomerTemplate).where(
            ITEmailCustomerTemplate.tenant_id == tenant_id,
            ITEmailCustomerTemplate.customer_id == customer_id,
        )
    ).first()
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

    return _logo_response(template.logo_path)


@router.delete("/customer/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer_template(
    customer_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_email_templates", "can_delete")),
):
    template = db.exec(
        select(ITEmailCustomerTemplate).where(
            ITEmailCustomerTemplate.tenant_id == tenant_id,
            ITEmailCustomerTemplate.customer_id == customer_id,
        )
    ).first()
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

    if template.logo_path and Path(template.logo_path).exists():
        Path(template.logo_path).unlink(missing_ok=True)
    db.delete(template)
    db.commit()
