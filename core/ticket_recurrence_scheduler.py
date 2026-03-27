import asyncio
import logging
from datetime import UTC, datetime
from dateutil.relativedelta import relativedelta

from sqlmodel import Session, select

from bd.connection import sync_engine as engine
from models.tickets import TicketRecurrenceConfig, TicketRecurrenceType, TicketStatus, Tickets

logger = logging.getLogger(__name__)

# How often the scheduler checks for due tickets (in seconds)
DEFAULT_INTERVAL_SECONDS = 3600  # 1 hour


def _calculate_next_occurrence(from_date: datetime, recurrence_type: TicketRecurrenceType) -> datetime:
    """Calculate the next occurrence date based on recurrence type."""
    if recurrence_type == TicketRecurrenceType.DAILY:
        return from_date + relativedelta(days=1)
    elif recurrence_type == TicketRecurrenceType.WEEKLY:
        return from_date + relativedelta(weeks=1)
    elif recurrence_type == TicketRecurrenceType.BIWEEKLY:
        return from_date + relativedelta(weeks=2)
    elif recurrence_type == TicketRecurrenceType.TRIWEEKLY:
        return from_date + relativedelta(weeks=3)
    elif recurrence_type == TicketRecurrenceType.MONTHLY:
        return from_date + relativedelta(months=1)
    elif recurrence_type == TicketRecurrenceType.BIMONTHLY:
        return from_date + relativedelta(months=2)
    elif recurrence_type == TicketRecurrenceType.YEARLY:
        return from_date + relativedelta(years=1)
    return from_date


class TicketRecurrenceScheduler:
    """Background task scheduler that generates recurring tickets when they are due."""

    def __init__(self) -> None:
        self.is_running = False
        self.last_run: datetime | None = None
        self._task: asyncio.Task | None = None
        self.interval_seconds = DEFAULT_INTERVAL_SECONDS

    def process_recurring_tickets(self) -> dict:
        """
        Find all active recurrence configs whose next_occurrence is due,
        generate child tickets, and update the next_occurrence.
        Returns statistics about the processed tickets.
        """
        now = datetime.now(UTC)
        stats = {"processed": 0, "created": 0, "errors": 0, "skipped": 0}

        try:
            with Session(engine) as db:
                # Find all configs that are due (next_occurrence <= now)
                configs = db.exec(
                    select(TicketRecurrenceConfig).where(
                        TicketRecurrenceConfig.is_active == True,
                        TicketRecurrenceConfig.next_occurrence != None,
                        TicketRecurrenceConfig.next_occurrence <= now,
                    )
                ).all()

                for config in configs:
                    stats["processed"] += 1
                    try:
                        # Load the parent ticket
                        parent_ticket = db.exec(
                            select(Tickets).where(Tickets.ticket_id == config.ticket_id)
                        ).first()

                        if not parent_ticket:
                            # Parent ticket was deleted, deactivate this config
                            config.is_active = False
                            db.commit()
                            stats["skipped"] += 1
                            continue

                        # Only create child ticket if parent is still open (not closed/done)
                        if parent_ticket.status in (TicketStatus.CLOSED, TicketStatus.DONE):
                            # Parent ticket is closed — deactivate recurrence
                            config.is_active = False
                            db.commit()
                            stats["skipped"] += 1
                            continue

                        # Create the child ticket
                        child_ticket = Tickets(
                            title=parent_ticket.title,
                            description=parent_ticket.description,
                            status=TicketStatus.TODO,
                            priority=parent_ticket.priority,
                            ticket_type=parent_ticket.ticket_type,
                            sla=parent_ticket.sla,
                            created_by=parent_ticket.created_by,
                            assigned_to=parent_ticket.assigned_to,
                            created_at=datetime.now(UTC),
                            updated_at=datetime.now(UTC),
                        )
                        db.add(child_ticket)
                        db.flush()  # Get the new ticket_id

                        # Update the parent's config with new next_occurrence
                        config.next_occurrence = _calculate_next_occurrence(
                            config.next_occurrence, config.recurrence_type
                        )
                        config.parent_ticket_id = child_ticket.ticket_id

                        db.commit()
                        stats["created"] += 1
                        logger.info(
                            f"Created recurring ticket #{child_ticket.ticket_id} "
                            f"(parent #{parent_ticket.ticket_id}, "
                            f"next occurrence: {config.next_occurrence})"
                        )

                    except Exception as e:
                        stats["errors"] += 1
                        logger.exception(f"Error processing recurrence config #{config.config_id}: {e}")
                        db.rollback()
                        continue

            self.last_run = datetime.now(UTC)
            return stats

        except Exception as e:
            logger.exception(f"Failed to process recurring tickets: {e}")
            return stats

    async def _periodic_loop(self) -> None:
        """Background loop that checks for due recurring tickets."""
        while self.is_running:
            try:
                # Run the processor in a thread pool (it's synchronous DB code)
                loop = asyncio.get_event_loop()
                stats = await loop.run_in_executor(None, self.process_recurring_tickets)

                if stats["processed"] > 0:
                    logger.info(
                        f"Recurrence job completed: processed={stats['processed']}, "
                        f"created={stats['created']}, errors={stats['errors']}, skipped={stats['skipped']}"
                    )

                await asyncio.sleep(self.interval_seconds)

            except asyncio.CancelledError:
                logger.info("Recurrence scheduler cancelled")
                break
            except Exception as e:
                logger.exception(f"Error in recurrence loop: {e}")
                await asyncio.sleep(self.interval_seconds)

    async def start(self, interval_seconds: int | None = None) -> None:
        """
        Start the periodic recurrence scheduler.

        Args:
            interval_seconds: Seconds between checks (default: 3600 = 1 hour)
        """
        if self.is_running:
            logger.warning("Recurrence scheduler already running")
            return

        self.is_running = True
        if interval_seconds is not None:
            self.interval_seconds = interval_seconds

        logger.info(f"Starting ticket recurrence scheduler (interval: {self.interval_seconds}s)")

        # Run an initial check immediately
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.process_recurring_tickets)

        self._task = asyncio.create_task(self._periodic_loop())

    async def stop(self) -> None:
        """Stop the periodic recurrence scheduler."""
        if not self.is_running:
            return

        self.is_running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        logger.info("Ticket recurrence scheduler stopped")


# Singleton instance — imported by main.py to register in lifespan
recurrence_scheduler = TicketRecurrenceScheduler()
