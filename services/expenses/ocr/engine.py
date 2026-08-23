"""Tesseract wrapper: image in, text lines with bounding boxes out.

Heavy third-party imports stay inside the functions on purpose. A host without
OpenCV or Tesseract must still be able to import the API: receipt reading then
degrades to manual capture instead of taking the whole service down.
"""

import logging
import os
from typing import TYPE_CHECKING

from services.expenses.ocr.result import TextLine

if TYPE_CHECKING:
    import numpy as np

logger = logging.getLogger(__name__)

# --oem 1 selects the LSTM engine; --psm 6 treats the image as a single uniform
# block of text, which is what a receipt is.
TESSERACT_CONFIG = "--oem 1 --psm 6"
TESSERACT_LANGS = "spa+eng"

MIN_WORD_CONFIDENCE = 30.0

# Where the binary lives. Empty means "whatever is on PATH", which is the normal
# case; the setting exists because a portable or per-user install (scoop, a
# plain unzip, a container layer) is often reachable without being on PATH, and
# there is no reason to make that a dead end.
TESSERACT_CMD = os.getenv("TESSERACT_CMD", "").strip()


def _configure(pytesseract) -> None:
    if TESSERACT_CMD:
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


def is_available() -> bool:
    """True when the Tesseract binary is installed and reachable."""
    try:
        import pytesseract

        _configure(pytesseract)
        pytesseract.get_tesseract_version()
    except Exception:
        return False
    return True


def recognise(image: "np.ndarray", page: int = 1) -> list[TextLine]:
    """Run OCR and group the recognised words into lines."""
    import pytesseract

    _configure(pytesseract)

    data = pytesseract.image_to_data(
        image,
        lang=TESSERACT_LANGS,
        config=TESSERACT_CONFIG,
        output_type=pytesseract.Output.DICT,
    )

    grouped: dict[tuple[int, int, int], list[int]] = {}
    for index, text in enumerate(data["text"]):
        if not text or not text.strip():
            continue
        try:
            confidence = float(data["conf"][index])
        except (TypeError, ValueError):
            confidence = -1.0
        if confidence < MIN_WORD_CONFIDENCE:
            continue

        key = (data["block_num"][index], data["par_num"][index], data["line_num"][index])
        grouped.setdefault(key, []).append(index)

    lines: list[TextLine] = []
    for indices in grouped.values():
        words = [data["text"][i].strip() for i in indices]
        lefts = [data["left"][i] for i in indices]
        tops = [data["top"][i] for i in indices]
        rights = [data["left"][i] + data["width"][i] for i in indices]
        bottoms = [data["top"][i] + data["height"][i] for i in indices]
        confidences = [float(data["conf"][i]) for i in indices]

        left, top = min(lefts), min(tops)
        lines.append(
            TextLine(
                text=" ".join(words),
                box=(left, top, max(rights) - left, max(bottoms) - top),
                page=page,
                confidence=sum(confidences) / len(confidences),
            )
        )

    lines.sort(key=lambda line: (line.page, line.box[1], line.box[0]))
    return lines
