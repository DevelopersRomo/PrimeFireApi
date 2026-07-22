"""Send IT quotations to customers by email with the PDF attached."""

import base64
from pathlib import Path

from fastapi import HTTPException, status
from sqlmodel import Session, select

from core.config import settings
from models.it.documents import ITQuotationDocuments
from models.it.quotations import ITQuotations
from services.it.pdf_service import generate_quotation_pdf
from services.it.quote_service import change_status
from services.notifications.email_functions import send_outlook_email
from services.notifications.schemas import EmailAttachment


def _latest_document(db: Session, quotation_id: int) -> ITQuotationDocuments | None:
    return db.exec(
        select(ITQuotationDocuments)
        .where(ITQuotationDocuments.quotation_id == quotation_id)
        .order_by(ITQuotationDocuments.document_version.desc())
    ).first()


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

    document = _latest_document(db, quotation.quotation_id)
    if not document or not Path(document.storage_path).exists():
        document = generate_quotation_pdf(db, quotation, generated_by=sent_by)

    pdf_bytes = Path(document.storage_path).read_bytes()
    attachment = EmailAttachment(
        name=document.file_name,
        content_type="application/pdf",
        content_bytes=base64.b64encode(pdf_bytes).decode("ascii"),
    )

    subject = f"Quotation {quotation.quotation_number}"
    body = (
        f"<p>Dear {quotation.contact_name_snapshot or quotation.customer_name_snapshot},</p>"
        f"<p>Please find attached quotation <strong>{quotation.quotation_number}</strong>, "
        f"valid until {quotation.expiration_date.strftime('%B %d, %Y')}.</p>"
        "<p>Feel free to reply to this email with any questions.</p>"
    )

    success, _message_id, error = await send_outlook_email(
        send_as_email=settings.BOT_EMAIL,
        to_emails=[recipient],
        subject=subject,
        body=body,
        attachments=[attachment],
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
