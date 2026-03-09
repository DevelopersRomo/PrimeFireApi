"""Backup API - Endpoints para ejecutar backups manualmente"""
import os
import subprocess
import sys
from datetime import datetime
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from api.dependencies import require_authentication

# Load .env before accessing settings
load_dotenv()

# Detectar entorno
ENV = os.getenv("ENVIRONMENT", "local").lower()
IS_PRODUCTION = ENV == "prod"

# Directorio de backups según el entorno
if IS_PRODUCTION:
    # Azure App Service Linux: usar variable UPLOADS_DIR o /home/home
    uploads_base = os.getenv("UPLOADS_DIR", "/home/home")
    BACKUP_DIR = os.path.join(uploads_base, "sql_backups")
else:
    # En local: bd/sql/backups
    BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "bd", "sql", "backups")

os.makedirs(BACKUP_DIR, exist_ok=True)

router = APIRouter(prefix="/backups", tags=["backups"])


class BackupResponse(BaseModel):
    success: bool
    message: str
    backup_files: list = []


def run_backup(db_prefix: str) -> dict:
    """Ejecuta el script de backup para una base de datos específica."""
    script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts", "generate_complete_backup.py")

    try:
        result = subprocess.run(
            [sys.executable, script_path, "--db", db_prefix, "--backup-dir", BACKUP_DIR],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(__file__))
        )

        if result.returncode == 0:
            return {"success": True, "db": db_prefix, "output": result.stdout}
        else:
            return {"success": False, "db": db_prefix, "error": result.stderr}

    except Exception as e:
        return {"success": False, "db": db_prefix, "error": str(e)}


@router.post("/trigger", response_model=BackupResponse)
async def trigger_backup(db_prefix: str = "all", _: dict = Depends(require_authentication)):
    """
    Trigger un backup manual de la base de datos.

    - **db_prefix**: "DB", "PRIMEFIRE_DB", o "all" (por defecto ejecuta ambos)
    """
    results = []
    backup_files = []

    if db_prefix == "all":
        # Ejecutar ambos backups
        db_prefixes = ["DB", "PRIMEFIRE_DB"]
    else:
        db_prefixes = [db_prefix]

    for prefix in db_prefixes:
        result = run_backup(prefix)
        results.append(result)

        if result["success"]:
            # Buscar archivos de backup creados recientemente
            prefix_lower = prefix.lower().replace("_", "")
            timestamp = datetime.now().strftime("%Y%m%d")
            for f in os.listdir(BACKUP_DIR):
                if f.endswith(".sql") and timestamp in f and prefix_lower in f.lower():
                    backup_files.append(f)

    # Verificar si todos los backups fueron exitosos
    all_success = all(r["success"] for r in results)

    if all_success:
        return BackupResponse(
            success=True,
            message=f"Backup{'s' if len(db_prefixes) > 1 else ''} completed successfully",
            backup_files=backup_files
        )
    else:
        errors = [f"{r['db']}: {r.get('error', 'Unknown error')}" for r in results if not r["success"]]
        return JSONResponse(
            status_code=500,
            content=BackupResponse(
                success=False,
                message=f"Backup error: {'; '.join(errors)}",
                backup_files=backup_files
            ).model_dump()
        )


@router.get("/status")
async def get_backup_status(_: dict = Depends(require_authentication)):
    """Get backup status and recent files."""
    files = []
    if os.path.exists(BACKUP_DIR):
        # Obtener archivos .sql ordenados por fecha de modificación (más recientes primero)
        sql_files = [f for f in os.listdir(BACKUP_DIR) if f.endswith(".sql")]
        sql_files.sort(key=lambda x: os.path.getmtime(os.path.join(BACKUP_DIR, x)), reverse=True)
        files = sql_files[:10]  # Últimos 10 archivos

    return {
        "environment": "production" if IS_PRODUCTION else "local",
        "backup_dir": BACKUP_DIR,
        "recent_backups": files
    }
