"""Backup API - Endpoints para ejecutar backups manualmente."""

import logging
import os
import pathlib
import subprocess
import sys
from datetime import datetime
from typing import Literal

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlmodel import Session

from api.dependencies import employee_has_admin_role, get_current_employee
from bd.dependencies import PLATFORM_DB_ROUTES, get_db, get_db_route
from models.employees import Employees

logger = logging.getLogger(__name__)

# Load .env before accessing settings
load_dotenv()

# Detectar entorno
ENV = os.getenv("ENVIRONMENT", "local").lower()
IS_PRODUCTION = ENV == "prod"

# Directorio de backups según el entorno
if IS_PRODUCTION:
    # Azure App Service Linux: usar variable UPLOADS_DIR o /home/home
    uploads_base = os.getenv("UPLOADS_DIR", "/home/home")
    BACKUP_DIR = os.path.join(uploads_base, "sql_backups")  # noqa: PTH118
else:
    # En local: bd/sql/backups
    BACKUP_DIR = os.path.join(pathlib.Path(pathlib.Path(__file__).parent).parent, "bd", "sql", "backups")  # noqa: PTH118

pathlib.Path(BACKUP_DIR).mkdir(exist_ok=True, parents=True)

router = APIRouter(tags=["backups"])


async def require_platform_admin(
    request: Request,
    employee: Employees = Depends(get_current_employee),
    db: Session = Depends(get_db),
) -> Employees:
    """Backups dump the main and PrimeFire databases: Admins of those databases only."""
    if get_db_route(request) not in PLATFORM_DB_ROUTES or not employee_has_admin_role(db, employee.employee_id):
        raise HTTPException(status_code=403, detail="Backups require an administrator.")
    return employee


class BackupResponse(BaseModel):
    success: bool
    message: str
    backup_files: list = []


def run_backup(db_prefix: str, backup_type: str = "full") -> dict:
    """Ejecuta el script de backup para una base de datos específica."""
    script_path = pathlib.Path(__file__).parent.parent / "scripts" / "generate_complete_backup.py"

    try:
        result = subprocess.run(
            [sys.executable, str(script_path), "--db", db_prefix, "--type", backup_type, "--backup-dir", BACKUP_DIR],
            capture_output=True,
            text=True,
            check=False,
            cwd=pathlib.Path(pathlib.Path(__file__).parent).parent,
        )

        if result.returncode == 0:
            return {"success": True, "db": db_prefix, "output": result.stdout}
        # Script output can carry connection details: log it, never return it.
        logger.error("Backup script failed for %s: %s", db_prefix, result.stderr)
        return {"success": False, "db": db_prefix, "error": "backup script failed"}

    except Exception:
        logger.exception("Backup script could not run for %s", db_prefix)
        return {"success": False, "db": db_prefix, "error": "backup script could not run"}


@router.post("/trigger", response_model=BackupResponse)
async def trigger_backup(
    db_prefix: Literal["DB", "PRIMEFIRE_DB", "all"] = "all",
    backup_type: Literal["full", "structure"] = "full",
    _: Employees = Depends(require_platform_admin),
):
    """
    Trigger un backup manual de la base de datos.

    - **db_prefix**: "DB", "PRIMEFIRE_DB", o "all" (por defecto ejecuta ambos)
    - **backup_type**: "full" (estructura + datos) o "structure" (solo estructura)
    """
    results = []
    backup_files = []

    if db_prefix == "all":  # noqa: SIM108
        # Ejecutar ambos backups
        db_prefixes = ["DB", "PRIMEFIRE_DB"]
    else:
        db_prefixes = [db_prefix]

    for prefix in db_prefixes:
        result = run_backup(prefix, backup_type)
        results.append(result)

        if result["success"]:
            # Buscar archivos de backup creados recientemente
            prefix_lower = prefix.lower().replace("_", "")
            timestamp = datetime.now().strftime("%Y%m%d")  # noqa: DTZ005
            backup_files.extend(
                f for f in os.listdir(BACKUP_DIR) if f.endswith(".sql") and timestamp in f and prefix_lower in f.lower()
            )

    # Verificar si todos los backups fueron exitosos
    all_success = all(r["success"] for r in results)

    if all_success:
        return BackupResponse(
            success=True,
            message=f"Backup{'s' if len(db_prefixes) > 1 else ''} completed successfully",
            backup_files=backup_files,
        )
    errors = [f"{r['db']}: {r.get('error', 'Unknown error')}" for r in results if not r["success"]]
    return JSONResponse(
        status_code=500,
        content=BackupResponse(
            success=False, message=f"Backup error: {'; '.join(errors)}", backup_files=backup_files
        ).model_dump(),
    )


@router.get("/status")
async def get_backup_status(_: Employees = Depends(require_platform_admin)):
    """Get backup status and recent files."""
    files = []
    if pathlib.Path(BACKUP_DIR).exists():  # noqa: ASYNC240
        # Obtener archivos .sql ordenados por fecha de modificación (más recientes primero)
        sql_files = [f for f in os.listdir(BACKUP_DIR) if f.endswith(".sql")]
        sql_files.sort(key=lambda x: pathlib.Path(os.path.join(BACKUP_DIR, x)).stat().st_mtime, reverse=True)  # noqa: PTH118
        files = sql_files[:10]  # Últimos 10 archivos

    return {
        "environment": "production" if IS_PRODUCTION else "local",
        "recent_backups": files,
    }
