"""Filesystem storage for generated IT quotation documents."""

import hashlib
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv("ENVIRONMENT", "local").lower()
IS_PRODUCTION = ENV == "prod"

if IS_PRODUCTION:
    _uploads_base = os.getenv("UPLOADS_DIR", "/home/home/uploads")
    BASE_DIR = Path(_uploads_base) / "it" / "quotations"
else:
    from core.config import settings

    BASE_DIR = Path(settings.UPLOAD_DIR) / "it" / "quotations"


def quotation_dir(quotation_id: int) -> Path:
    path = BASE_DIR / str(quotation_id)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_pdf(quotation_id: int, file_name: str, content: bytes) -> tuple[str, str]:
    """Write the PDF and return (storage_path, sha256 hash)."""
    path = quotation_dir(quotation_id) / file_name
    path.write_bytes(content)
    file_hash = hashlib.sha256(content).hexdigest()
    return str(path), file_hash
