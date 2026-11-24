"""Background job: keep the official US/MX/DO/PR holidays of this year and next loaded in every database.

Runs at startup and then once a day. Insert-only (see services.official_holidays.ensure_official_holidays),
so restarts are harmless. Disable with OFFICIAL_HOLIDAYS_AUTOLOAD=false.
"""

import asyncio
import logging

from sqlmodel import Session

from bd.connection import engine as main_engine
from core.datetime_utils import utcnow
from core.ticket_sla_scheduler import database_routes
from services.official_holidays import ensure_official_holidays

logger = logging.getLogger(__name__)

ONE_DAY_SECONDS = 24 * 60 * 60


def run_official_holidays_load() -> int:
    """One pass over every database. A failing database is logged and skipped."""
    year = utcnow().year
    total = 0
    with Session(main_engine) as main_db:
        routes = database_routes(main_db)
    for db_route, engine in routes:
        try:
            with Session(engine) as db:
                total += ensure_official_holidays(db, [year, year + 1])
        except Exception:
            logger.exception(f"[HOLIDAYS] Failed to load official holidays for '{db_route}'")
    return total


async def run_official_holidays_loop() -> None:
    """Runs until cancelled (see main.lifespan)."""
    logger.info("Starting official holidays job (startup, then daily)")
    while True:
        try:
            inserted = await asyncio.get_running_loop().run_in_executor(None, run_official_holidays_load)
            if inserted:
                logger.info(f"[HOLIDAYS] Inserted {inserted} official holiday(s)")
        except Exception:
            logger.exception("[HOLIDAYS] Official holidays job failed")
        await asyncio.sleep(ONE_DAY_SECONDS)
