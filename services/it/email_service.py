"""Send IT quotations to customers by email with the PDF attached."""

import base64
import html as htmllib
import mimetypes
from pathlib import Path

from fastapi import HTTPException, status
from sqlmodel import Session, select

from core.config import settings
from models.it.documents import ITQuotationDocuments
from models.it.email_templates import ITEmailCustomerTemplate, ITEmailDefault
from models.it.quotations import ITQuotations
from services.it.pdf_service import generate_quotation_pdf
from services.it.quote_number_service import next_customer_quotation_number
from services.it.quote_service import change_status
from services.notifications.email_functions import send_outlook_email
from services.notifications.notifications import generate_notification_html
from services.notifications.schemas import EmailAttachment, NotificationField

# Fallback template used when neither a per-customer override nor a tenant
# default has been configured. Placeholders below get replaced at send time.
_FALLBACK_SUBJECT = "Quotation {quotation_number}"
_FALLBACK_TITLE = "Quotation {quotation_number}"
_FALLBACK_BODY = (
    "Dear {contact_name},\n\n"
    "Please find attached quotation {quotation_number}, valid until {expiration_date}.\n\n"
    "Feel free to reply to this email with any questions."
)


def _latest_document(db: Session, quotation_id: int) -> ITQuotationDocuments | None:
    return db.exec(
        select(ITQuotationDocuments)
        .where(ITQuotationDocuments.quotation_id == quotation_id)
        .order_by(ITQuotationDocuments.document_version.desc())
    ).first()


def _resolve_template(
    db: Session, tenant_id: int, customer_id: int | None
) -> tuple[str, str, str, str | None, str | None, str | None]:
    """Return subject, content, color and logo path for the given customer.

    Customer-specific override wins over tenant default, which wins over the
    hardcoded fallback.
    """
    if customer_id is not None:
        override = db.exec(
            select(ITEmailCustomerTemplate).where(
                ITEmailCustomerTemplate.tenant_id == tenant_id,
                ITEmailCustomerTemplate.customer_id == customer_id,
                ITEmailCustomerTemplate.is_active == True,  # noqa: E712
            )
        ).first()
        if override:
            return (
                override.subject,
                override.title,
                override.message_body,
                override.footer,
                override.header_color,
                override.logo_path,
            )

    default = db.exec(
        select(ITEmailDefault).where(
            ITEmailDefault.tenant_id == tenant_id,
            ITEmailDefault.is_active == True,  # noqa: E712
        )
    ).first()
    if default:
        return (
            default.subject,
            default.title,
            default.message_body,
            default.footer,
            default.header_color,
            default.logo_path,
        )

    return _FALLBACK_SUBJECT, _FALLBACK_TITLE, _FALLBACK_BODY, None, None, None


def _build_placeholders(quotation: ITQuotations) -> dict[str, str]:
    total_value = getattr(quotation, "initial_total", None)
    return {
        "quotation_number": quotation.quotation_number or "",
        "customer_name": quotation.customer_name_snapshot or "",
        "contact_name": (
            quotation.contact_name_snapshot or quotation.customer_name_snapshot or ""
        ),
        "expiration_date": (
            quotation.expiration_date.strftime("%B %d, %Y")
            if quotation.expiration_date
            else ""
        ),
        "total": f"{total_value:,.2f}" if total_value is not None else "",
        "currency": quotation.currency or "",
    }


def _apply_placeholders(template: str, context: dict[str, str]) -> str:
    result = template or ""
    for key, value in context.items():
        result = result.replace("{" + key + "}", value)
    return result


def _plain_to_html(text: str) -> str:
    """Escape user-provided plain text and convert newlines to <br>."""
    return htmllib.escape(text or "").replace("\n", "<br>")


def _build_email_body(
    title: str,
    message_body: str,
    footer: str | None,
    placeholders: dict[str, str],
    quotation: ITQuotations,
    header_color: str | None = None,
    header_image_cid: str | None = None,
) -> str:
    resolved_title = _apply_placeholders(title, placeholders)
    resolved_body_html = _plain_to_html(_apply_placeholders(message_body, placeholders))

    if footer:
        resolved_footer_html = _plain_to_html(_apply_placeholders(footer, placeholders))
        combined_body_html = (
            f"{resolved_body_html}"
            f"<br><br>"
            f"<span style=\"color:#888; font-size:13px;\">{resolved_footer_html}</span>"
        )
    else:
        combined_body_html = resolved_body_html

    fields: list[NotificationField] = [
        NotificationField(label="Quotation #", value=placeholders["quotation_number"]),
    ]
    if placeholders["expiration_date"]:
        fields.append(NotificationField(label="Valid Until", value=placeholders["expiration_date"]))
    if placeholders["total"]:
        currency = placeholders["currency"]
        fields.append(
            NotificationField(
                label="Amount",
                value=f"{currency} {placeholders['total']}".strip(),
            )
        )

    return generate_notification_html(
        title=resolved_title,
        action_type="info",
        message_body=combined_body_html,
        fields=fields,
        color_override=header_color,
        header_image_cid=header_image_cid,
    )


async def send_quotation_email(
    db: Session,
    quotation: ITQuotations,
    sent_by: int | None = None,
) -> ITQuotations:
    """Generate/attach the latest PDF, email the customer and mark SENT."""
    recipient = quotation.customer_email_snapshot
    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Quotation has no customer email to send to",
        )

    # First send: replace the internal Q-IT-YYYY-NNNNNN with the customer-scoped
    # number and force PDF regeneration so the file/header carry the new one.
    was_first_send = quotation.sent_at is None
    if was_first_send:
        quotation.quotation_number = next_customer_quotation_number(
            db,
            tenant_id=quotation.tenant_id,
            customer_id=quotation.customer_id,
            customer_name=quotation.customer_name_snapshot,
        )
        db.add(quotation)
        db.flush()
        document = generate_quotation_pdf(db, quotation, generated_by=sent_by)
    else:
        document = _latest_document(db, quotation.quotation_id)
        if not document or not Path(document.storage_path).exists():
            document = generate_quotation_pdf(db, quotation, generated_by=sent_by)

    pdf_bytes = Path(document.storage_path).read_bytes()
    attachments = [
        EmailAttachment(
            name=document.file_name,
            content_type="application/pdf",
            content_bytes=base64.b64encode(pdf_bytes).decode("ascii"),
        )
    ]

    subject_tpl, title_tpl, body_tpl, footer_tpl, header_color, logo_path = _resolve_template(
        db, quotation.tenant_id, quotation.customer_id
    )
    placeholders = _build_placeholders(quotation)

    subject = _apply_placeholders(subject_tpl, placeholders)
    if logo_path and Path(logo_path).exists():
        logo_file = Path(logo_path)
        logo_cid = f"quotation-logo-{quotation.quotation_id}"
        attachments.append(
            EmailAttachment(
                name=logo_file.name,
                content_type=mimetypes.guess_type(logo_file.name)[0] or "image/*",
                content_bytes=base64.b64encode(logo_file.read_bytes()).decode("ascii"),
                content_id=logo_cid,
                is_inline=True,
            )
        )
    else:
        logo_cid = None

    body_html = _build_email_body(
        title_tpl,
        body_tpl,
        footer_tpl,
        placeholders,
        quotation,
        header_color=header_color,
        header_image_cid=logo_cid,
    )

    success, _message_id, error = await send_outlook_email(
        send_as_email=settings.BOT_EMAIL,
        to_emails=[recipient],
        subject=subject,
        body=body_html,
        attachments=attachments,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Email send failed: {error}",
        )

    change_status(db, quotation, "SENT", changed_by=sent_by, notes=f"Sent to {recipient}")
    db.commit()
    db.refresh(quotation)
    return quotation
