"""The extraction cascade.

Four paths, cheapest and most exact first. The first one that produces a total
wins, so OCR only ever runs on documents nothing else could resolve:

1. SAT QR code        exact total, zero recognition       confidence 1.00
2. PDF text layer     digital receipts, no rasterising    confidence 0.90
3. Tesseract OCR      photographed receipts               confidence 0.35-0.95
4. Failure            manual capture, LOW_CONFIDENCE flag

Everything the rest of the system needs goes through `extract_receipt()`. Swapping
in a different engine later means touching this file and nothing else.
"""

import logging
import time
from pathlib import Path

from services.expenses.ocr import engine as ocr_engine
from services.expenses.ocr import parser, pdf, preprocess, qr
from services.expenses.ocr.result import Candidate, ExtractionResult

logger = logging.getLogger(__name__)

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff", ".heic", ".heif"}
PDF_SUFFIXES = {".pdf"}

# OCR pages beyond this are almost always terms and conditions.
MAX_OCR_PAGES = 3


def extract_receipt(file_path: Path, currency_default: str | None = None) -> ExtractionResult:
    """Read a receipt file and return the best structured reading available."""
    started = time.monotonic()

    try:
        result = _run_cascade(file_path, currency_default)
    except Exception as exc:
        logger.exception("[EXPENSES] Extraction crashed for %s", file_path)
        result = ExtractionResult(status="failed", error_message=str(exc)[:500])

    result.duration_ms = int((time.monotonic() - started) * 1000)
    return result


def _run_cascade(file_path: Path, currency_default: str | None) -> ExtractionResult:
    if not file_path.exists():
        return ExtractionResult(status="failed", error_message="File not found on disk")

    suffix = file_path.suffix.lower()

    if suffix in PDF_SUFFIXES:
        return _from_pdf(file_path, currency_default)
    if suffix in IMAGE_SUFFIXES:
        return _from_image(file_path, currency_default)

    return ExtractionResult(status="failed", error_message=f"Unsupported file type '{suffix}'")


def _from_pdf(file_path: Path, currency_default: str | None) -> ExtractionResult:
    pages = pdf.render_pages(file_path, max_pages=MAX_OCR_PAGES)
    total_pages = pdf.page_count(file_path)

    # 1. QR first: an invoice PDF resolves exactly, whether or not it has text.
    for index, image in enumerate(pages, start=1):
        sat = qr.scan(image)
        if sat and sat.total is not None:
            # The QR carries the amount but not the currency, so read it off the
            # document when there is a text layer, and leave it unset otherwise.
            currency = parser.detect_currency(pdf.extract_text_layer(file_path), currency_default)
            return _from_sat(sat, page=index, page_count=total_pages, currency=currency)

    # 2. Text layer: digital receipts never need to be rasterised or recognised.
    text = pdf.extract_text_layer(file_path)
    if text:
        result = parser.parse_plain_text(text, engine="pdf_text", currency_default=currency_default)
        result.page_count = total_pages
        if result.status == "done":
            return result

    # 3. Scanned PDF: fall through to OCR on the rendered pages.
    if not pages:
        return ExtractionResult(status="failed", error_message="PDF could not be read")

    return _ocr_images(pages, total_pages, currency_default)


def _from_image(file_path: Path, currency_default: str | None) -> ExtractionResult:
    if not preprocess.is_available():
        return ExtractionResult(
            status="failed",
            error_message="Image processing is unavailable on this host (OpenCV missing)",
        )

    image = preprocess.load_image(file_path)

    # 1. QR on the untouched image — thresholding can destroy a QR's finder patterns.
    sat = qr.scan(image)
    if sat and sat.total is not None:
        # No text layer on a photo, so the currency stays whatever the report says.
        return _from_sat(sat, page=1, page_count=1, currency=currency_default)

    # 2. OCR.
    return _ocr_images([image], 1, currency_default)


def _ocr_images(images: list, page_count: int, currency_default: str | None) -> ExtractionResult:
    if not preprocess.is_available():
        return ExtractionResult(
            status="failed",
            error_message="Image processing is unavailable on this host (OpenCV missing)",
        )
    if not ocr_engine.is_available():
        return ExtractionResult(
            status="failed",
            error_message="Tesseract is not installed on this host",
        )

    lines = []
    page_height = 0
    for index, image in enumerate(images[:MAX_OCR_PAGES], start=1):
        prepared = preprocess.prepare(image)
        page_lines = ocr_engine.recognise(prepared, page=index)
        lines.extend(page_lines)
        if index == 1:
            page_height = prepared.shape[0]

    return parser.parse_lines(
        lines,
        page_height=page_height,
        page_count=page_count,
        engine="tesseract",
        currency_default=currency_default,
    )


def _from_sat(
    sat: qr.SatQrData, page: int, page_count: int, currency: str | None = None
) -> ExtractionResult:
    """A verified SAT QR: the total is exact, so nothing else may override it.

    The currency is *not* part of the QR payload. A CFDI can be issued in any
    currency, so it is passed in from the document text or left unset rather
    than inferred from the fact that the invoice is Mexican.
    """
    return ExtractionResult(
        engine="qr_sat",
        status="done",
        total=sat.total,
        currency=currency,
        tax_id=sat.issuer_rfc,
        uuid=sat.uuid,
        confidence=1.0,
        arithmetic_ok=True,
        candidates=[Candidate(value=sat.total, label="SAT QR", score=10.0, page=page)],
        raw_text=f"SAT QR UUID={sat.uuid} RFC={sat.issuer_rfc} TOTAL={sat.total}",
        page_count=page_count,
    )
