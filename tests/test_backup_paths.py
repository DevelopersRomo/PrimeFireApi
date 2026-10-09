"""Backups hold production data: they must never be written inside the source tree."""

import pathlib

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


def _inside_repo(path: pathlib.Path) -> bool:
    return pathlib.Path(path).resolve().is_relative_to(REPO_ROOT)


@pytest.fixture
def clean_env(monkeypatch):
    for name in ("BACKUP_DIR", "ENVIRONMENT", "UPLOADS_DIR"):
        monkeypatch.delenv(name, raising=False)
    return monkeypatch


def test_local_default_is_outside_the_repo(clean_env) -> None:
    from core.backup_paths import resolve_backup_dir

    assert not _inside_repo(resolve_backup_dir())


def test_backup_dir_env_var_wins(clean_env, tmp_path) -> None:
    from core.backup_paths import resolve_backup_dir

    clean_env.setenv("BACKUP_DIR", str(tmp_path / "custom"))
    clean_env.setenv("ENVIRONMENT", "prod")

    assert resolve_backup_dir() == tmp_path / "custom"


def test_prod_uses_the_persistent_home_volume(clean_env) -> None:
    from core.backup_paths import resolve_backup_dir

    clean_env.setenv("ENVIRONMENT", "prod")
    assert resolve_backup_dir().as_posix() == "/home/home/sql_backups"

    clean_env.setenv("UPLOADS_DIR", "/home/site/data")
    assert resolve_backup_dir().as_posix() == "/home/site/data/sql_backups"


def test_api_backup_dir_is_outside_the_repo() -> None:
    from api.backups import BACKUP_DIR

    assert not _inside_repo(BACKUP_DIR)
