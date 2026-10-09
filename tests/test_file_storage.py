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
