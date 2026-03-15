"""
Backup Scheduler - Ejecuta backups automáticos a las 12:00 UTC todos los días
Solo se ejecuta en producción (ENV=production).
"""

import logging
import os
import pathlib
import subprocess
import sys
import time

import schedule
from dotenv import load_dotenv

load_dotenv()

# Detectar entorno
ENV = os.getenv("ENVIRONMENT", "local").lower()
IS_PRODUCTION = ENV == "prod"

# Ruta de backups según el entorno
if IS_PRODUCTION:
    # Azure App Service Linux: usar variable UPLOADS_DIR o /home/home
    uploads_base = os.getenv("UPLOADS_DIR", "/home/home")
    BACKUP_DIR = pathlib.Path(uploads_base) / "sql_backups"
else:
    # En local: bd/sql/backups
    BACKUP_DIR = pathlib.Path(__file__).parent / "bd" / "sql" / "backups"

pathlib.Path(BACKUP_DIR).mkdir(exist_ok=True, parents=True)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(BACKUP_DIR / "scheduler.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def run_backup(db_prefix="DB") -> None:
    """Ejecuta el script de backup."""
    script_path = pathlib.Path(__file__).parent / "scripts" / "generate_complete_backup.py"

    logger.info(f"[START] Iniciando backup para {db_prefix}")

    try:
        result = subprocess.run(
            [sys.executable, script_path, "--db", db_prefix, "--backup-dir", str(BACKUP_DIR)],
            capture_output=True,
            text=True,
            check=False,
            cwd=pathlib.Path(pathlib.Path(__file__).parent).parent,
        )

        if result.returncode == 0:
            logger.info(f"[SUCCESS] Backup completado para {db_prefix}")
        else:
            logger.error(f"[ERROR] Backup falló para {db_prefix}")

    except Exception as e:
        logger.exception(f"[ERROR] Excepción al ejecutar backup para {db_prefix}: {e}")


def run_all_backups() -> None:
    """Ejecuta todos los backups configurados."""
    logger.info("[START] Iniciando ciclo de backups")

    # Backup para DB por defecto
    run_backup("DB")

    # Backup para PRIMEFIRE_DB
    run_backup("PRIMEFIRE_DB")

    logger.info("[COMPLETE] Ciclo de backups completado")


def main() -> None:
    """Inicia el scheduler."""
    # Verificar si es producción
    if not IS_PRODUCTION:
        logger.info("Scheduler no iniciado - modo local")
        return

    logger.info("Backup Scheduler iniciado en producción")

    # Programar ejecución a las 00:00 UTC todos los días
    schedule.every().day.at("00:00").do(run_all_backups)

    logger.info(f"Próximo backup: {schedule.next_run()}")

    # Loop infinito del scheduler
    while True:
        schedule.run_pending()
        time.sleep(60)  # Verificar cada minuto


if __name__ == "__main__":
    main()
