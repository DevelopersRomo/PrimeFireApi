"""Image preparation for Tesseract.

With an open-source OCR this stage matters more than the recognition call. A
phone photo of a crumpled thermal receipt is skewed, unevenly lit, noisy and
often below the resolution Tesseract needs. Each step here targets one of those.

OpenCV and NumPy are imported inside the functions so a host without them can
still serve the API; receipt reading degrades to manual capture.
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image, ImageOps

if TYPE_CHECKING:
    import numpy as np

logger = logging.getLogger(__name__)

# Tesseract degrades sharply below roughly 300 DPI equivalent.
MIN_SHORT_SIDE = 1200
MAX_LONG_SIDE = 3500

try:  # Registers HEIC/HEIF support for iPhone photos.
    import pillow_heif

    pillow_heif.register_heif_opener()
except Exception:  # pragma: no cover - optional at import time
    logger.debug("pillow-heif not available; HEIC receipts will not be readable")


def is_available() -> bool:
    """True when OpenCV is installed, i.e. the image pipeline can run."""
    try:
        import cv2  # noqa: F401
    except ImportError:
        return False
    return True


def load_image(path: Path) -> "np.ndarray":
    """Read any supported image into BGR, honouring the EXIF orientation tag."""
    import cv2
    import numpy as np

    with Image.open(path) as handle:
        oriented = ImageOps.exif_transpose(handle)
        rgb = oriented.convert("RGB")
        array = np.array(rgb)
    return cv2.cvtColor(array, cv2.COLOR_RGB2BGR)


def _resize(image: "np.ndarray") -> "np.ndarray":
    import cv2

    height, width = image.shape[:2]
    short_side = min(height, width)
    long_side = max(height, width)

    scale = 1.0
    if short_side < MIN_SHORT_SIDE:
        scale = MIN_SHORT_SIDE / short_side
    if long_side * scale > MAX_LONG_SIDE:
        scale = MAX_LONG_SIDE / long_side

    if abs(scale - 1.0) < 0.01:
        return image

    interpolation = cv2.INTER_CUBIC if scale > 1 else cv2.INTER_AREA
    return cv2.resize(image, None, fx=scale, fy=scale, interpolation=interpolation)


def _deskew(gray: "np.ndarray") -> "np.ndarray":
    """Rotate the page so text lines are horizontal.

    Only small corrections are applied: a large angle usually means the contour
    detection latched onto background rather than text.
    """
    import cv2

    inverted = cv2.bitwise_not(gray)
    _, binary = cv2.threshold(inverted, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    coords = cv2.findNonZero(binary)
    if coords is None:
        return gray

    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = 90 + angle
    elif angle > 45:
        angle -= 90

    if abs(angle) < 0.5 or abs(angle) > 20:
        return gray

    height, width = gray.shape[:2]
    matrix = cv2.getRotationMatrix2D((width / 2, height / 2), angle, 1.0)
    return cv2.warpAffine(gray, matrix, (width, height), flags=cv2.INTER_CUBIC, borderValue=255)


def prepare(image: "np.ndarray") -> "np.ndarray":
    """Full pipeline: upscale, grey, denoise, deskew, adaptive threshold."""
    import cv2

    resized = _resize(image)
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

    # Thermal paper is grainy and phone sensors add noise at the edges.
    denoised = cv2.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21)

    deskewed = _deskew(denoised)

    # Adaptive beats a global threshold whenever lighting is uneven, which for a
    # receipt photographed on a desk is always.
    return cv2.adaptiveThreshold(
        deskewed,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        blockSize=31,
        C=15,
    )


def prepare_file(path: Path) -> "np.ndarray":
    return prepare(load_image(path))
