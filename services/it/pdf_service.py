"""PDF generation for IT quotations using Jinja2 + WeasyPrint."""

import ipaddress
import socket
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import url2pathname

import httpx

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
MAX_REMOTE_ASSET_BYTES = 5 * 1024 * 1024

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

    # Resolve amounts from percentages when only percentage is stored, and
    # compute a total so the template can render a footer row.
    initial_total = Decimal(str(quotation.initial_total or 0))
    schedule_rows = []
    schedule_total = Decimal("0")
    for entry in schedule:
        resolved_amount = entry.amount
        if resolved_amount is None and entry.percentage is not None:
            resolved_amount = (initial_total * Decimal(str(entry.percentage))) / Decimal("100")
        if resolved_amount is not None:
            schedule_total += Decimal(str(resolved_amount))
        schedule_rows.append(
            {
                "sequence_number": entry.sequence_number,
                "description": entry.description,
                "percentage": entry.percentage,
                "amount": resolved_amount,
                "due_rule": entry.due_rule,
            }
        )

    template_config: ITPdfTemplates | None = None
    if quotation.template_id:
        template_config = db.get(ITPdfTemplates, quotation.template_id)
    else:
        template_config = db.exec(
            select(ITPdfTemplates).where(
                ITPdfTemplates.tenant_id == quotation.tenant_id,
                ITPdfTemplates.is_default == True,  # noqa: E712
                ITPdfTemplates.is_active == True,  # noqa: E712
            )
        ).first()

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
        payment_schedule=schedule_rows,
        payment_schedule_total=schedule_total,
        config=template_config,
        logo_src=logo_src,
        generated_at=datetime.utcnow(),
    )


def _is_public_host(host: str | None) -> bool:
    """Every address the host resolves to must be globally routable (no loopback, private or metadata IPs)."""
    if not host:
        return False
    try:
        addresses = {info[4][0] for info in socket.getaddrinfo(host, None)}
    except OSError:
        return False
    return bool(addresses) and all(ipaddress.ip_address(address.split("%")[0]).is_global for address in addresses)


def safe_url_fetcher(url: str) -> dict:
    """WeasyPrint fetcher: template assets, uploaded logos, data: URIs and public http(s) images only.

    Raising makes WeasyPrint skip the resource, so a bad logo_url never reaches local files or
    internal network services.
    """
    from weasyprint import default_url_fetcher  # heavy native import, keep lazy

    import api.it.templates  # read the current LOGO_UPLOAD_DIR at call time

    parsed = urlparse(url)
    if parsed.scheme == "data":
        return default_url_fetcher(url)
    if parsed.scheme == "file":
        path = Path(url2pathname(parsed.path)).resolve()
        allowed_roots = (TEMPLATES_DIR.resolve(), Path(api.it.templates.LOGO_UPLOAD_DIR).resolve())
        if not any(path.is_relative_to(root) for root in allowed_roots):
            raise ValueError(f"Refusing to load local file outside the template and logo folders: {url}")
        return default_url_fetcher(url)
    if parsed.scheme in {"http", "https"}:
        if not _is_public_host(parsed.hostname):
            raise ValueError(f"Refusing to fetch a non-public address: {url}")
        # Known limit: httpx resolves the host again, so a DNS-rebinding host could still race this check.
        response = httpx.get(url, follow_redirects=False, timeout=10.0)
        if response.status_code != 200:
            raise ValueError(f"Remote asset returned HTTP {response.status_code}: {url}")
        if len(response.content) > MAX_REMOTE_ASSET_BYTES:
            raise ValueError(f"Remote asset is larger than {MAX_REMOTE_ASSET_BYTES} bytes: {url}")
        mime_type = response.headers.get("content-type", "").split(";")[0].strip() or None
        return {"string": response.content, "mime_type": mime_type, "redirected_url": url}
    raise ValueError(f"Unsupported URL scheme for PDF assets: {url}")


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

    pdf_bytes = HTML(string=html, base_url=str(TEMPLATES_DIR), url_fetcher=safe_url_fetcher).write_pdf()

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
