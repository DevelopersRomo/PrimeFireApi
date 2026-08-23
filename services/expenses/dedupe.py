"""Receipt deduplication.

Four independent fingerprints, because the same expense reaches the system in
four different shapes:

    sha256    the identical file, re-uploaded
    CFDI UUID the same invoice, re-issued as a different PDF
    pHash     the same photo, recropped or re-encoded by a chat app
    fuzzy key merchant + date + total, i.e. the same consumption uploaded once
              as a photo and once as an invoice

A match raises a flag for the approver. It never blocks the upload: chain
merchants legitimately produce near-identical receipts on the same day.
"""

import hashlib
import logging
import re
import unicodedata
from decimal import Decimal
from pathlib import Path

from sqlmodel import Session, select

from models.expenses import ExpenseReceiptExtractions, ExpenseReceipts, ExpenseReports

logger = logging.getLogger(__name__)

CHUNK_SIZE = 1024 * 1024


def file_sha256(path: Path) -> str | None:
    try:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            while chunk := handle.read(CHUNK_SIZE):
                digest.update(chunk)
    except OSError as exc:
        logger.warning("[EXPENSES] Could not hash %s: %s", path, exc)
        return None
    return digest.hexdigest()


def perceptual_hash(path: Path) -> str | None:
    """Perceptual hash, so a recompressed or recropped photo still matches."""
    if path.suffix.lower() == ".pdf":
        return None
    try:
        import imagehash
        from PIL import Image, ImageOps

        with Image.open(path) as handle:
            oriented = ImageOps.exif_transpose(handle).convert("RGB")
            return str(imagehash.phash(oriented))
    except Exception as exc:
        logger.debug("[EXPENSES] Could not compute pHash for %s: %s", path, exc)
        return None


def _normalize_merchant(value: str | None) -> str:
    if not value:
        return ""
    stripped = unicodedata.normalize("NFD", value)
    ascii_only = "".join(ch for ch in stripped if unicodedata.category(ch) != "Mn")
    return re.sub(r"[^A-Z0-9]", "", ascii_only.upper())[:24]


def fuzzy_key(merchant: str | None, expense_date, total: Decimal | None) -> str | None:
    """merchant + date + total, the signature of one real-world consumption."""
    if total is None or expense_date is None:
        return None
    merchant_key = _normalize_merchant(merchant)
    if not merchant_key:
        return None
    return f"{merchant_key}|{expense_date.isoformat()}|{total:.2f}"


def _hamming(left: str, right: str) -> int:
    try:
        return bin(int(left, 16) ^ int(right, 16)).count("1")
    except ValueError:
        return 999


def find_duplicates(
    db: Session,
    employee_id: int,
    receipt: ExpenseReceipts,
    extraction: ExpenseReceiptExtractions | None,
) -> list[str]:
    """Human-readable reasons this receipt looks like one already on file.

    Scoped to the same employee: two people expensing the same restaurant on the
    same night is a coincidence, one person doing it twice is not.
    """
    reasons: list[str] = []

    own_report_ids = db.exec(
        select(ExpenseReports.report_id).where(ExpenseReports.employee_id == employee_id)
    ).all()
    if not own_report_ids:
        return reasons

    # Only receipts filed earlier count as the original. Comparing against every
    # sibling made both halves of a pair flag each other, so one duplicate was
    # reported twice and the approver could not tell which copy to remove.
    siblings = db.exec(
        select(ExpenseReceipts)
        .where(ExpenseReceipts.report_id.in_(own_report_ids))  # type: ignore[attr-defined]
        .where(ExpenseReceipts.receipt_id < receipt.receipt_id)
    ).all()
    if not siblings:
        return reasons

    sibling_ids = [item.receipt_id for item in siblings]

    if receipt.sha256:
        for other in siblings:
            if other.sha256 and other.sha256 == receipt.sha256:
                reasons.append(f"Identical file already uploaded as receipt #{other.receipt_id}")
                break

    if receipt.phash:
        for other in siblings:
            if other.phash and _hamming(receipt.phash, other.phash) <= 5:
                reasons.append(f"Visually identical image already uploaded as receipt #{other.receipt_id}")
                break

    if extraction is None:
        return reasons

    others = db.exec(
        select(ExpenseReceiptExtractions).where(ExpenseReceiptExtractions.receipt_id.in_(sibling_ids))  # type: ignore[attr-defined]
    ).all()

    if extraction.detected_uuid:
        for other in others:
            if other.detected_uuid and other.detected_uuid == extraction.detected_uuid:
                reasons.append(f"Same fiscal invoice (UUID) as receipt #{other.receipt_id}")
                break

    own_key = fuzzy_key(extraction.detected_merchant, extraction.detected_date, extraction.detected_total)
    if own_key:
        for other in others:
            other_key = fuzzy_key(other.detected_merchant, other.detected_date, other.detected_total)
            if other_key and other_key == own_key:
                reasons.append(f"Same merchant, date and amount as receipt #{other.receipt_id}")
                break

    return reasons
