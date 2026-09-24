-- Migration: ticket history (ticket_events) and tickets.resolved_at
-- resolved_at: set when a ticket reaches done/closed/inactive, cleared when it is reopened.
-- ticket_events: one row per ticket creation and per change of status, priority,
-- assigned_to, sla or ticket_type.
--
-- Run against ALL databases that have a dbo.tickets table:
--   1. Main database (DB_DATABASE)
--   2. Each tenant database
-- The API also creates missing tables at startup via SQLModel.metadata.create_all,
-- but it never adds columns to existing tables, so resolved_at needs this script.
IF NOT EXISTS (
    SELECT 1
    FROM sys.columns
    WHERE object_id = OBJECT_ID('dbo.tickets')
    AND name = 'resolved_at'
)
BEGIN
    ALTER TABLE [dbo].[tickets] ADD [resolved_at] DATETIME NULL;
END
GO

-- Backfill: already-resolved tickets get their last update as an approximate resolution time
UPDATE [dbo].[tickets]
SET [resolved_at] = [updated_at]
WHERE [resolved_at] IS NULL
AND [status] IN ('done', 'closed', 'inactive');
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.tables
    WHERE name = 'ticket_events'
    AND schema_id = SCHEMA_ID('dbo')
)
BEGIN
    CREATE TABLE [dbo].[ticket_events] (
        [event_id] INT IDENTITY(1,1) NOT NULL CONSTRAINT [pk_ticket_events] PRIMARY KEY,
        [ticket_id] INT NOT NULL
            CONSTRAINT [fk_ticket_events_ticket] FOREIGN KEY REFERENCES [dbo].[tickets] ([ticket_id]),
        [employee_id] INT NOT NULL
            CONSTRAINT [fk_ticket_events_employee] FOREIGN KEY REFERENCES [dbo].[employees] ([employee_id]),
        [event_type] VARCHAR(20) NOT NULL,
        [field] VARCHAR(50) NULL,
        [from_value] VARCHAR(100) NULL,
        [to_value] VARCHAR(100) NULL,
        [created_at] DATETIME NOT NULL
    );
    CREATE INDEX [ix_ticket_events_ticket_id] ON [dbo].[ticket_events] ([ticket_id]);
END
GO

-- sla_warning_sent_at: when the one-time "SLA at risk" Novu notice was sent (NULL = not sent)
IF NOT EXISTS (
    SELECT 1
    FROM sys.columns
    WHERE object_id = OBJECT_ID('dbo.tickets')
    AND name = 'sla_warning_sent_at'
)
BEGIN
    ALTER TABLE [dbo].[tickets] ADD [sla_warning_sent_at] DATETIME NULL;
END
GO

-- SLA clock: time only passes while a ticket is active / in_progress.
-- sla_elapsed_seconds = time banked in finished stretches; sla_running_since = start of the
-- current stretch (NULL while stopped). Elapsed = sla_elapsed_seconds + (now - sla_running_since).
IF NOT EXISTS (
    SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('dbo.tickets') AND name = 'sla_elapsed_seconds'
)
BEGIN
    ALTER TABLE [dbo].[tickets] ADD [sla_elapsed_seconds] INT NOT NULL
        CONSTRAINT [df_tickets_sla_elapsed_seconds] DEFAULT (0);
END
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('dbo.tickets') AND name = 'sla_running_since'
)
BEGIN
    ALTER TABLE [dbo].[tickets] ADD [sla_running_since] DATETIME NULL;

    -- Backfill (approximate: no status history exists for older tickets)
    EXEC('
        UPDATE [dbo].[tickets]
        SET [sla_running_since] = COALESCE([in_progress_at], [updated_at])
        WHERE [status] IN (''active'', ''in_progress'');

        UPDATE [dbo].[tickets]
        SET [sla_elapsed_seconds] = DATEDIFF(SECOND, [in_progress_at], COALESCE([resolved_at], [updated_at]))
        WHERE [status] NOT IN (''active'', ''in_progress'')
        AND [in_progress_at] IS NOT NULL
        AND COALESCE([resolved_at], [updated_at]) > [in_progress_at];
    ');
END
GO
