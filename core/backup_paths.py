"""Where database backups are written. Never inside the source tree: dumps hold production data."""

import os
import pathlib


def resolve_backup_dir() -> pathlib.Path:
    """BACKUP_DIR if set; in prod the persistent /home volume; locally a folder outside the repo."""
    explicit = os.getenv("BACKUP_DIR")
    if explicit:
        return pathlib.Path(explicit)
    if os.getenv("ENVIRONMENT", "local").lower() == "prod":
        # Azure App Service Linux persists only /home
        return pathlib.Path(os.getenv("UPLOADS_DIR", "/home/home")) / "sql_backups"
    return pathlib.Path.home() / "PrimeFire-backups"
