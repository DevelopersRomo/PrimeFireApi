"""Background job: warn when a ticket's SLA clock reaches 75% of its budget.

SLA time only passes while the ticket is active / in_progress (sla_elapsed_seconds banked
plus the running stretch since sla_running_since). Only tickets whose clock is running are
warned, at most once each (sla_warning_sent_at). Every database is scanned: main, PrimeFire
and each active tenant.
"""

import asyncio
import logging
from datetime import datetime, timedelta

from sqlalchemy.engine import Engine
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from bd.connection import engine as main_engine
from bd.connection import primefire_engine
from bd.multitenancy import ConnectionManager
from core.config import settings
from core.datetime_utils import utcnow
from models.tenants import Tenants
from models.tickets import RESOLVED_STATUSES, TicketSLA, Tickets
from services.notifications import novu

logger = logging.getLogger(__name__)

SLA_WARNING_THRESHOLD = 0.75

# Fixed budgets: with pauses a calendar month has no meaning, so 1m is 30 days (as in the UI)
SLA_BUDGET: dict[TicketSLA, timedelta] = {
    TicketSLA.HOURS_1: timedelta(hours=1),
    TicketSLA.HOURS_4: timedelta(hours=4),
    TicketSLA.HOURS_8: timedelta(hours=8),
    TicketSLA.HOURS_12: timedelta(hours=12),
    TicketSLA.HOURS_24: timedelta(hours=24),
    TicketSLA.HOURS_48: timedelta(hours=48),
    TicketSLA.WEEKS_1: timedelta(weeks=1),
    TicketSLA.WEEKS_2: timedelta(weeks=2),
    TicketSLA.WEEKS_4: timedelta(weeks=4),
    TicketSLA.MONTH_1: timedelta(days=30),
}


def sla_elapsed(ticket: Tickets, now: datetime) -> timedelta:
    """Time spent in active/in_progress so far."""
    elapsed = timedelta(seconds=ticket.sla_elapsed_seconds or 0)
    if ticket.sla_running_since is not None:
        elapsed += now - ticket.sla_running_since
    return elapsed


def format_time_left(remaining: timedelta) -> str:
    """Readable remaining time, same shape as the frontend SLA chip (no minutes once in days)."""
    total_minutes = max(0, int(remaining.total_seconds() // 60))
    days, rest = divmod(total_minutes, 24 * 60)
    hours, minutes = divmod(rest, 60)

    def plural(value: int, unit: str) -> str:
        return f"{value} {unit}{'' if value == 1 else 's'}"

    parts = []
    if days:
        parts.append(plural(days, "day"))
    if hours:
        parts.append(plural(hours, "hour"))
    if minutes and not days:
        parts.append(plural(minutes, "minute"))
    return " ".join(parts) or "less than 1 minute"


def find_tickets_at_risk(db: Session, now: datetime) -> list[Tickets]:
    """Tickets with an SLA whose clock is running, not yet warned, past the warning threshold."""
    candidates = db.exec(
        select(Tickets)
        .options(selectinload(Tickets.creator), selectinload(Tickets.assignee))
        .where(
            Tickets.sla.is_not(None),
            Tickets.sla_running_since.is_not(None),
            Tickets.sla_warning_sent_at.is_(None),
            Tickets.status.notin_(RESOLVED_STATUSES),
        )
        .order_by(Tickets.ticket_id)
    ).all()

    return [
        ticket
        for ticket in candidates
        if sla_elapsed(ticket, now) >= SLA_BUDGET[ticket.sla] * SLA_WARNING_THRESHOLD
    ]


def send_sla_warnings(db: Session, db_route: str, now: datetime) -> int:
    """Warn the assignee (or the creator when unassigned) once per ticket. Returns tickets warned.

    Nothing is marked while Novu is not configured, so enabling it later still warns open tickets.
    """
    if not novu.is_configured():
        return 0

    warned = 0
    for ticket in find_tickets_at_risk(db, now):
        employee = ticket.assignee or ticket.creator
        if employee is None:
            continue
        remaining = SLA_BUDGET[ticket.sla] - sla_elapsed(ticket, now)
        deadline = now + remaining  # if the clock keeps running
        sent = novu.trigger(
            novu.WORKFLOW_TICKET_SLA_AT_RISK,
            db_route,
            [novu.Recipient.from_employee(employee)],
            {
                "ticket_id": ticket.ticket_id,
                "title": ticket.title,
                "sla": ticket.sla.value,
                "deadline": deadline.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "minutes_left": max(0, int(remaining.total_seconds() // 60)),
                "time_left": format_time_left(remaining),
                "url": f"{settings.APP_URL}/tickets/{ticket.ticket_id}",
            },
            f"ticket-{ticket.ticket_id}-sla-at-risk",
        )
        if not sent:
            continue  # not marked: retried on the next run
        ticket.sla_warning_sent_at = now
        db.add(ticket)
        db.commit()
        warned += 1
    return warned


def database_routes(main_db: Session) -> list[tuple[str, Engine]]:
    """Every database that holds tickets, keyed like get_db_route: main, primefire, tenant keys."""
    routes: list[tuple[str, Engine]] = [("main", main_engine)]
    if primefire_engine is not None:
        routes.append(("primefire", primefire_engine))
    tenant_keys = main_db.exec(
        select(Tenants.db_connection_key).where(Tenants.is_active).order_by(Tenants.tenant_id)
    ).all()
    for tenant_key in tenant_keys:
        if tenant_key.lower() == "main":
            continue  # the main database, already covered by the "main" route (see get_db_route)
        try:
            routes.append((tenant_key, ConnectionManager.get_engine(tenant_key)))
        except ValueError:
            logger.warning(f"[SLA] Skipping tenant '{tenant_key}': no database configured")
    return routes


def run_sla_warnings() -> int:
    """One pass over every database. A failing database is logged and skipped."""
    now = utcnow()
    total = 0
    with Session(main_engine) as main_db:
        routes = database_routes(main_db)
    for db_route, engine in routes:
        try:
            with Session(engine) as db:
                total += send_sla_warnings(db, db_route, now)
        except Exception:
            logger.exception(f"[SLA] Failed to process SLA warnings for '{db_route}'")
    return total


async def run_sla_warning_loop() -> None:
    """Runs until cancelled (see main.lifespan)."""
    interval = settings.SLA_WARNING_JOB_INTERVAL_MINUTES * 60
    logger.info(f"Starting SLA warning job (interval: {interval}s)")
    while True:
        try:
            warned = await asyncio.get_running_loop().run_in_executor(None, run_sla_warnings)
            if warned:
                logger.info(f"[SLA] Sent {warned} SLA-at-risk warning(s)")
        except Exception:
            logger.exception("[SLA] SLA warning job failed")
        await asyncio.sleep(interval)
