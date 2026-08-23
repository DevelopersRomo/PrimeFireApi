"""PDF handling via PyMuPDF.

PyMuPDF ships as a self-contained wheel and covers both jobs we need — reading an
embedded text layer and rasterising a scanned page — so it replaces pypdf plus
pdf2image plus a poppler system dependency.
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np

logger = logging.getLogger(__name__)

RENDER_DPI = 300

# Below this, a "text layer" is just stray metadata and the page is really a scan.
MIN_TEXT_LAYER_CHARS = 60


def _pymupdf():
    """PyMuPDF module. The legacy `fitz` alias is deprecated since 1.28."""
    try:
        import pymupdf

        return pymupdf
    except ImportError:
        import fitz

        return fitz


def _open(path):
    return _pymupdf().open(path)


def page_count(path) -> int:
    with _open(path) as document:
        return document.page_count


def extract_text_layer(path) -> str:
    """Concatenated embedded text, or an empty string when the PDF is a scan."""
    try:
        with _open(path) as document:
            chunks = [page.get_text("text") for page in document]
    except Exception as exc:
        logger.warning("[EXPENSES] Could not read PDF text layer: %s", exc)
        return ""

    text = "\n".join(chunk for chunk in chunks if chunk)
    return text if len(text.strip()) >= MIN_TEXT_LAYER_CHARS else ""


def render_pages(path, dpi: int = RENDER_DPI, max_pages: int = 5) -> list["np.ndarray"]:
    """Rasterise the PDF to BGR images for OCR or QR detection."""
    import cv2
    import numpy as np

    images: list[np.ndarray] = []
    zoom = dpi / 72
    matrix = _pymupdf().Matrix(zoom, zoom)

    try:
        with _open(path) as document:
            for page in list(document)[:max_pages]:
                pixmap = page.get_pixmap(matrix=matrix, alpha=False)
                buffer = np.frombuffer(pixmap.samples, dtype=np.uint8)
                array = buffer.reshape(pixmap.height, pixmap.width, pixmap.n)
                if pixmap.n == 1:
                    images.append(cv2.cvtColor(array, cv2.COLOR_GRAY2BGR))
                else:
                    images.append(cv2.cvtColor(array, cv2.COLOR_RGB2BGR))
    except Exception as exc:
        logger.warning("[EXPENSES] Could not rasterise PDF: %s", exc)

    return images
