"""PDF generation for IT quotations using Jinja2 + WeasyPrint."""

from datetime import datetime
from pathlib import Path

from fastapi import HTTPException, status
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlmodel import Session, select

from models.it.documents import ITQuotationDocuments
from models.it.quotations import (
    ITPaymentSchedule,
    ITQuotationItems,
    ITQuotations,
    ITQuotationTerms,
)
from models.it.templates import ITPdfTemplates
from services.it.document_storage import save_pdf

TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates" / "it"
DEFAULT_TEMPLATE_KEY = "quotation_standard"

_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html"]),
)


def render_quotation_html(db: Session, quotation: ITQuotations) -> str:
    """Render the quotation HTML (separate from PDF for testability)."""
    items = db.exec(
        select(ITQuotationItems)
        .where(ITQuotationItems.quotation_id == quotation.quotation_id)
        .order_by(ITQuotationItems.sort_order)
    ).all()
    terms = db.get(ITQuotationTerms, quotation.quotation_id)
    schedule = db.exec(
        select(ITPaymentSchedule)
        .where(ITPaymentSchedule.quotation_id == quotation.quotation_id)
        .order_by(ITPaymentSchedule.sequence_number)
    ).all()

    template_config: ITPdfTemplates | None = None
    if quotation.template_id:
        template_config = db.get(ITPdfTemplates, quotation.template_id)

    template_key = template_config.template_key if template_config else DEFAULT_TEMPLATE_KEY
    template_file = f"{template_key}.html"
    if not (TEMPLATES_DIR / template_file).exists():
        template_file = f"{DEFAULT_TEMPLATE_KEY}.html"

    # Logo can be an external URL or a locally uploaded file path.
    logo_src = template_config.logo_url if template_config else None
    if logo_src and not logo_src.startswith("http"):
        logo_path = Path(logo_src)
        logo_src = logo_path.resolve().as_uri() if logo_path.exists() else None

    template = _env.get_template(template_file)
    return template.render(
        quotation=quotation,
        items=items,
        terms=terms,
        payment_schedule=schedule,
        config=template_config,
        logo_src=logo_src,
        generated_at=datetime.utcnow(),
    )


def generate_quotation_pdf(
    db: Session,
    quotation: ITQuotations,
    generated_by: int | None = None,
) -> ITQuotationDocuments:
    """Render HTML, produce the PDF, store it and register the document row."""
    html = render_quotation_html(db, quotation)

    try:
        from weasyprint import HTML  # noqa: PLC0415 (heavy native import, keep lazy)
    except (ImportError, OSError) as exc:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"PDF engine not available: {exc}",
        ) from exc

    pdf_bytes = HTML(string=html, base_url=str(TEMPLATES_DIR)).write_pdf()

    last_version = db.exec(
        select(ITQuotationDocuments)
        .where(ITQuotationDocuments.quotation_id == quotation.quotation_id)
        .order_by(ITQuotationDocuments.document_version.desc())
    ).first()
    version = (last_version.document_version if last_version else 0) + 1

    file_name = f"{quotation.quotation_number}-v{version}.pdf"
    storage_path, file_hash = save_pdf(quotation.quotation_id, file_name, pdf_bytes)

    document = ITQuotationDocuments(
        quotation_id=quotation.quotation_id,
        document_type="PDF",
        file_name=file_name,
        storage_path=storage_path,
        document_version=version,
        file_hash=file_hash,
        generated_by=generated_by,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document
