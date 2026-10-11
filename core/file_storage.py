"""Confine stored file paths to their upload root before serving or deleting them."""

import mimetypes
import pathlib

from fastapi import HTTPException, UploadFile
from fastapi.responses import FileResponse

MIB = 1024 * 1024
MAX_LOGO_BYTES = 5 * MIB


def read_upload(upload: UploadFile, max_bytes: int) -> bytes:
    """Read an upload into memory, stopping one byte past the limit so an oversized body is never fully held."""
    content = upload.file.read(max_bytes + 1)
    if len(content) > max_bytes:
        raise HTTPException(status_code=413, detail=f"File exceeds the {max_bytes // MIB} MiB limit")
    return content


def confine_to(root: str | pathlib.Path, stored_path: str | pathlib.Path) -> pathlib.Path:
    """Resolve stored_path under root and return it, or 404 if it points anywhere else.

    Relative paths are taken from root; absolute paths are accepted only when they already
    live under root (older rows store absolute paths). Symlinks are followed by resolve(),
    so a link pointing outside root is rejected too.
    """
    base = pathlib.Path(root).resolve()
    path = (base / stored_path).resolve()
    if path == base or not path.is_relative_to(base):
        raise HTTPException(status_code=404, detail="File not found")
    return path


_SIGNATURES = (
    (b"%PDF-", "application/pdf"),
    (b"\x89PNG\r\n\x1a\n", "image/png"),
    (b"\xff\xd8\xff", "image/jpeg"),
    (b"GIF87a", "image/gif"),
    (b"GIF89a", "image/gif"),
)
_SNIFFABLE = {mime for _, mime in _SIGNATURES} | {"image/webp"}
_ACTIVE_TYPES = {
    "text/html",
    "application/xhtml+xml",
    "text/xml",
    "application/xml",
    "text/javascript",
    "application/javascript",
}


def detect_content_type(path: str | pathlib.Path, declared: str | None = None) -> str:
    """Content type from the file's own bytes; a client-declared type only fills in what bytes cannot tell.

    A declared type we can verify (pdf, png, jpeg, gif, webp) or that a browser would execute (html, xml, js)
    is never trusted without matching bytes.
    """
    with pathlib.Path(path).open("rb") as stored:
        head = stored.read(12)
    for signature, mime in _SIGNATURES:
        if head.startswith(signature):
            return mime
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "image/webp"
    declared_mime = (declared or "").split(";", maxsplit=1)[0].strip().lower()
    if not declared_mime or declared_mime in _SNIFFABLE or declared_mime in _ACTIVE_TYPES:
        return "application/octet-stream"
    return declared_mime


def attachment_response(path: str | pathlib.Path, filename: str, declared_type: str | None = None) -> FileResponse:
    """Serve a stored upload as a download, typed by its bytes and never sniffed into something executable."""
    return FileResponse(
        path=path,
        filename=filename,
        media_type=detect_content_type(path, declared_type or mimetypes.guess_type(filename)[0]),
        headers={"X-Content-Type-Options": "nosniff"},
    )
