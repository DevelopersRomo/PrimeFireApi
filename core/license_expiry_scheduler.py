"""Background job: a daily digest of expired licenses (dbo.licenses.expiry_date < today, UTC).

Every recipient (an employee whose roles can view the "licenses" module) gets one email and one
Novu in-app notification per database. It repeats every day until the license is renewed or
deleted. The job runs at LICENSE_EXPIRY_DIGEST_HOUR_UTC, never at startup, so restarts do not
resend. License keys, passwords and notes are never sent.
"""

import asyncio
import html
import logging
from datetime import date, datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from bd.connection import engine as main_engine
from core.config import settings
from core.datetime_utils import utcnow
from core.mail_profiles import DEFAULT_MAIL_PROFILE
from core.ticket_sla_scheduler import database_routes
from models.employees import EmployeeRoles, Employees
from models.licenses import Licenses
from models.modules import Modules, RoleModules
from models.tenants import Tenants
from services.notifications import novu
from services.notifications.email_functions import send_outlook_email
from services.notifications.mail_profile import resolve_mail_profile
from services.notifications.notifications import generate_notification_html

logger = logging.getLogger(__name__)

LICENSES_MODULE_KEY = "licenses"


def seconds_until_next_run(now: datetime, hour: int) -> float:
    """Seconds until the next `hour`:00. Exactly at the hour counts as already run (tomorrow)."""
    target = now.replace(hour=hour, minute=0, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return (target - now).total_seconds()


def find_expired_licenses(db: Session, today: date) -> list[Licenses]:
    return list(
        db.exec(
            select(Licenses)
            .options(selectinload(Licenses.employee))
            .where(Licenses.expiry_date < today)
            .order_by(Licenses.expiry_date, Licenses.license_id)
        ).all()
    )


def find_recipients(db: Session) -> list[Employees]:
    """Same rule as get_current_employee_with_permissions: any role with can_view on the module
    (OR across roles, no admin bypass). Employees without an email cannot receive the digest.
    """
    rows = db.exec(
        select(Employees)
        .join(EmployeeRoles, EmployeeRoles.employee_id == Employees.employee_id)
        .join(RoleModules, RoleModules.role_id == EmployeeRoles.role_id)
        .join(Modules, Modules.module_id == RoleModules.module_id)
        .where(
            Modules.module_key == LICENSES_MODULE_KEY,
            RoleModules.can_view,
            Employees.email.is_not(None),
            Employees.email != "",  # noqa: PLC1901 - SQL comparison, not a Python truthiness check
        )
        .order_by(Employees.employee_id)
    ).all()
    return list({e.employee_id: e for e in rows}.values())  # one row per granting role


def mail_profile_for(main_db: Session, db_route: str) -> str:
    """Mail profile of the tenant whose db_connection_key is this route (case-insensitive)."""
    tenant = main_db.exec(select(Tenants).where(func.lower(Tenants.db_connection_key) == db_route.lower())).first()
    if tenant is None:
        return DEFAULT_MAIL_PROFILE
    return resolve_mail_profile(main_db, tenant_id=tenant.tenant_id)


def build_email_body(licenses: list[Licenses], today: date, url: str) -> str:
    def cell(value: object) -> str:
        return f'<td style="padding: 6px 10px; border-bottom: 1px solid #eee;">{html.escape(str(value or "-"))}</td>'

    rows = "".join(
        "<tr>"
        + cell(lic.software)
        + cell(lic.version)
        + cell(lic.expiry_date.isoformat())
        + cell((today - lic.expiry_date).days)
        + cell(lic.account)
        + cell(lic.employee.display_name if lic.employee else None)
        + "</tr>"
        for lic in licenses
    )
    headers = "".join(
        f'<th style="padding: 6px 10px; text-align: left;">{h}</th>'
        for h in ("Software", "Version", "Expired on", "Days expired", "Account", "Assigned to")
    )
    table = f'<table style="border-collapse: collapse; width: 100%;"><tr>{headers}</tr>{rows}</table>'
    return generate_notification_html(
        title="Expired licenses",
        sub_title=f"{len(licenses)} license(s) past their expiry date",
        action_type="warning",
        message_body=f"<p>These licenses have expired and need to be renewed or removed.</p>{table}",
        action_url=url,
        action_text="View licenses",
    )


def send_license_digests(db: Session, db_route: str, today: date, mail_profile: str) -> int:
    """Send the digest to every recipient in this database. Returns recipients emailed."""
    licenses = find_expired_licenses(db, today)
    if not licenses:
        return 0

    url = f"{settings.APP_URL}/licenses"
    body = build_email_body(licenses, today, url)
    subject = f"{len(licenses)} expired license(s)"
    emailed = 0
    for employee in find_recipients(db):
        try:
            success, _message_id, error = asyncio.run(
                send_outlook_email(
                    send_as_email=settings.BOT_EMAIL,
                    to_emails=[employee.email],
                    subject=subject,
                    body=body,
                    mail_profile=mail_profile,
                )
            )
            if success:
                emailed += 1
            else:
                logger.warning(f"[LICENSES] Digest email to employee {employee.employee_id} failed: {error}")
        except Exception:
            logger.exception(f"[LICENSES] Digest email to employee {employee.employee_id} failed")

        if novu.is_configured():
            novu.trigger(
                novu.WORKFLOW_LICENSE_EXPIRED_DIGEST,
                db_route,
                [novu.Recipient.from_employee(employee)],
                {"count": len(licenses), "url": url},
                f"license-expired-digest-{db_route}-{employee.employee_id}-{today.isoformat()}",
            )
    return emailed


def run_license_expiry_digests() -> int:
    """One pass over every database. A failing database is logged and skipped."""
    today = utcnow().date()
    total = 0
    with Session(main_engine) as main_db:
        routes = [(route, engine, mail_profile_for(main_db, route)) for route, engine in database_routes(main_db)]
    for db_route, engine, mail_profile in routes:
        try:
            with Session(engine) as db:
                total += send_license_digests(db, db_route, today, mail_profile)
        except Exception:
            logger.exception(f"[LICENSES] Failed to send the expired license digest for '{db_route}'")
    return total


async def run_license_expiry_digest_loop() -> None:
    """Runs until cancelled (see main.lifespan)."""
    hour = settings.LICENSE_EXPIRY_DIGEST_HOUR_UTC
    logger.info(f"Starting expired license digest job (daily at {hour:02d}:00 UTC)")
    while True:
        await asyncio.sleep(seconds_until_next_run(utcnow(), hour))
        try:
            sent = await asyncio.get_running_loop().run_in_executor(None, run_license_expiry_digests)
            if sent:
                logger.info(f"[LICENSES] Sent {sent} expired license digest email(s)")
        except Exception:
            logger.exception("[LICENSES] Expired license digest job failed")
