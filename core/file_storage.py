"""Confine stored file paths to their upload root before serving or deleting them."""

import pathlib

from fastapi import HTTPException


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
