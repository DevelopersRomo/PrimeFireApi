"""
Backup Scheduler - Ejecuta backups automáticos a las 12:00 UTC todos los días
Solo se ejecuta en producción (ENV=production)
"""
import schedule
import time
import subprocess
import sys
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Detectar entorno
ENV = os.getenv("ENVIRONMENT", "local").lower()
IS_PRODUCTION = ENV == "prod"

# Ruta de backups según el entorno
if IS_PRODUCTION:
    # Azure App Service Linux: usar variable UPLOADS_DIR o /home/home
    uploads_base = os.getenv("UPLOADS_DIR", "/home/home")
    BACKUP_DIR = os.path.join(uploads_base, "sql_backups")
else:
    # En local: bd/sql/backups
    BACKUP_DIR = os.path.join(os.path.dirname(__file__), "bd", "sql", "backups")

os.makedirs(BACKUP_DIR, exist_ok=True)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BACKUP_DIR, 'scheduler.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_backup(db_prefix="DB"):
    """Ejecuta el script de backup."""
    script_path = os.path.join(os.path.dirname(__file__), "scripts", "generate_complete_backup.py")

    logger.info(f"[START] Iniciando backup para {db_prefix}")
    print(f"\n{'='*50}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Ejecutando backup: {db_prefix}")
    print(f"[ENV] {ENV} - Backup dir: {BACKUP_DIR}")
    print(f"{'='*50}\n")

    try:
        result = subprocess.run(
            [sys.executable, script_path, "--db", db_prefix, "--backup-dir", BACKUP_DIR],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(__file__))
        )

        if result.returncode == 0:
            logger.info(f"[SUCCESS] Backup completado para {db_prefix}")
            print(result.stdout)
        else:
            logger.error(f"[ERROR] Backup falló para {db_prefix}")
            print(result.stderr)

    except Exception as e:
        logger.error(f"[ERROR] Excepción al ejecutar backup para {db_prefix}: {e}")


def run_all_backups():
    """Ejecuta todos los backups configurados."""
    logger.info("[START] Iniciando ciclo de backups")

    # Backup para DB por defecto
    run_backup("DB")

    # Backup para PRIMEFIRE_DB
    run_backup("PRIMEFIRE_DB")

    logger.info("[COMPLETE] Ciclo de backups completado")


def main():
    """Inicia el scheduler."""
    # Verificar si es producción
    if not IS_PRODUCTION:
        print("\n" + "="*50)
        print("  BACKUP SCHEDULER - MODO LOCAL")
        print("  No se ejecutará automáticamente en local")
        print("  Set ENV=production para habilitar")
        print("="*50 + "\n")
        logger.info("Scheduler no iniciado - modo local")
        return

    print("\n" + "="*50)
    print("  BACKUP SCHEDULER INICIADO (PRODUCCIÓN)")
    print(f"  Entorno: {ENV}")
    print(f"  Backup dir: {BACKUP_DIR}")
    print("  Ejecutando backups a las 00:00 UTC todos los días")
    print("="*50 + "\n")

    logger.info("Backup Scheduler iniciado en producción")

    # Programar ejecución a las 00:00 UTC todos los días
    schedule.every().day.at("00:00").do(run_all_backups)

    logger.info("Próximo backup: " + str(schedule.next_run()))

    # Loop infinito del scheduler
    while True:
        schedule.run_pending()
        time.sleep(60)  # Verificar cada minuto


if __name__ == "__main__":
    main()
