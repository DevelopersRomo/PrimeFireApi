"""confine_to must only ever return paths inside the storage root."""

import pathlib

import pytest
from fastapi import HTTPException


@pytest.fixture
def root(tmp_path):
    storage = tmp_path / "uploads"
    (storage / "customers").mkdir(parents=True)
    (storage / "customers" / "a.pdf").write_bytes(b"%PDF")
    (tmp_path / "secret.env").write_text("SECRET=1")
    return storage


def test_relative_path_inside_root_is_returned(root) -> None:
    from core.file_storage import confine_to

    assert confine_to(root, "customers/a.pdf") == (root / "customers" / "a.pdf").resolve()


def test_absolute_path_inside_root_is_accepted(root) -> None:
    """Existing rows store absolute paths under the upload root."""
    from core.file_storage import confine_to

    stored = str(root / "customers" / "a.pdf")
    assert confine_to(root, stored) == (root / "customers" / "a.pdf").resolve()


@pytest.mark.parametrize(
    "stored",
    [
        "../secret.env",
        "customers/../../secret.env",
        "../uploads-evil/x",
        "",
    ],
)
def test_paths_escaping_the_root_are_rejected(root, stored) -> None:
    from core.file_storage import confine_to

    with pytest.raises(HTTPException) as exc:
        confine_to(root, stored)
    assert exc.value.status_code == 404


def test_absolute_path_outside_root_is_rejected(root, tmp_path) -> None:
    from core.file_storage import confine_to

    with pytest.raises(HTTPException):
        confine_to(root, str(tmp_path / "secret.env"))


def test_symlink_escaping_the_root_is_rejected(root, tmp_path) -> None:
    from core.file_storage import confine_to

    link = root / "customers" / "link.env"
    try:
        pathlib.Path(link).symlink_to(tmp_path / "secret.env")
    except (OSError, NotImplementedError):
        pytest.skip("symlinks not permitted on this platform")

    with pytest.raises(HTTPException):
        confine_to(root, "customers/link.env")


@pytest.mark.parametrize(
    ("content", "declared", "expected"),
    [
        (b"%PDF-1.7 body", "text/html", "application/pdf"),
        (b"\x89PNG\r\n\x1a\n....", "application/pdf", "image/png"),
        (b"\xff\xd8\xff\xe0....", None, "image/jpeg"),
        (b"RIFF\x00\x00\x00\x00WEBPVP8 ", "text/html", "image/webp"),
        (b"<html><script>alert(1)</script>", "application/pdf", "application/octet-stream"),
        (b"<html><script>alert(1)</script>", "image/png", "application/octet-stream"),
        (b"<html><script>alert(1)</script>", "text/html; charset=utf-8", "application/octet-stream"),
        (b"<svg/>", "image/svg+xml", "image/svg+xml"),
        (b"PK\x03\x04docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
         "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
        (b"hello", "text/plain", "text/plain"),
        (b"hello", None, "application/octet-stream"),
    ],
)
def test_attachment_response_uses_detected_content_type(tmp_path, content, declared, expected) -> None:
    """The type comes from the bytes; a client-declared active type is never echoed back."""
    from core.file_storage import attachment_response

    stored = tmp_path / "file.bin"
    stored.write_bytes(content)

    response = attachment_response(stored, "file.bin", declared)

    assert response.media_type == expected
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["content-disposition"].startswith("attachment;")


def test_read_upload_returns_content_within_the_limit() -> None:
    import io

    from fastapi import UploadFile

    from core.file_storage import read_upload

    assert read_upload(UploadFile(io.BytesIO(b"x" * 10), filename="a.bin"), 10) == b"x" * 10


def test_read_upload_refuses_more_than_the_limit_without_reading_it_all() -> None:
    import io

    from fastapi import UploadFile

    from core.file_storage import read_upload

    source = io.BytesIO(b"x" * 1000)

    with pytest.raises(HTTPException) as caught:
        read_upload(UploadFile(source, filename="a.bin"), 10)

    assert caught.value.status_code == 413
    assert source.tell() == 11  # one byte past the limit, never the whole body
