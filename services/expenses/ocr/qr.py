"""QR fast path.

Every Mexican CFDI invoice carries a QR pointing at the SAT verification page:

    https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx
        ?id=<UUID>&re=<issuer RFC>&rr=<receiver RFC>&tt=<TOTAL>&fe=<seal>

`tt` is the exact total. When this fires there is nothing to recognise and
nothing to second-guess, and the UUID gives perfect deduplication across
re-uploads of the same invoice.

Detection uses OpenCV's built-in QRCodeDetector rather than pyzbar, so no extra
system library is needed beyond OpenCV itself.
"""

import logging
from decimal import Decimal
from typing import TYPE_CHECKING
from urllib.parse import parse_qs, urlparse

from services.expenses.ocr.parser import normalize_amount

if TYPE_CHECKING:
    import numpy as np

logger = logging.getLogger(__name__)

SAT_HOST_FRAGMENT = "verificacfdi"


class SatQrData:
    def __init__(self, uuid: str | None, issuer_rfc: str | None, receiver_rfc: str | None, total: Decimal | None):
        self.uuid = uuid
        self.issuer_rfc = issuer_rfc
        self.receiver_rfc = receiver_rfc
        self.total = total


def read_payloads(image: "np.ndarray") -> list[str]:
    """All QR payloads found in an image."""
    import cv2

    detector = cv2.QRCodeDetector()
    try:
        ok, decoded, _, _ = detector.detectAndDecodeMulti(image)
    except Exception as exc:
        logger.debug("[EXPENSES] QR detection failed: %s", exc)
        return []

    if not ok or decoded is None:
        return []
    return [payload for payload in decoded if payload]


def parse_sat_payload(payload: str) -> SatQrData | None:
    """Pull UUID, both RFCs and the exact total out of a SAT verification URL."""
    if SAT_HOST_FRAGMENT not in payload.lower():
        return None

    try:
        query = parse_qs(urlparse(payload).query)
    except ValueError:
        return None

    # The SAT uses lowercase keys, but tolerate uppercase from odd generators.
    lowered = {key.lower(): values for key, values in query.items()}

    def first(key: str) -> str | None:
        values = lowered.get(key)
        return values[0].strip() if values and values[0].strip() else None

    raw_total = first("tt")
    total = normalize_amount(raw_total) if raw_total else None

    uuid = first("id")
    if not uuid and total is None:
        return None

    return SatQrData(
        uuid=uuid.upper() if uuid else None,
        issuer_rfc=(first("re") or "").upper() or None,
        receiver_rfc=(first("rr") or "").upper() or None,
        total=total,
    )


def scan(image: "np.ndarray") -> SatQrData | None:
    """First SAT QR found in the image, if any."""
    for payload in read_payloads(image):
        data = parse_sat_payload(payload)
        if data:
            return data
    return None
