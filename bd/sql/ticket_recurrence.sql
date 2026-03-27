-- ============================================================
-- Migration: Ticket Recurrence System
-- Adds TicketRecurrenceConfig table for recurring tickets
-- Run after rename_columns_to_snake_case migration
-- ============================================================

-- Create TicketRecurrenceConfig table
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[ticket_recurrence_config]') AND type IN (N'U'))
BEGIN
    CREATE TABLE [dbo].[ticket_recurrence_config](
        [config_id] INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        [ticket_id] INT NULL,                           -- nullable so SET NULL works on FK delete
        [recurrence_type] NVARCHAR(20) NOT NULL DEFAULT ('none'),
        [next_occurrence] DATETIME2(7) NULL,
        [parent_ticket_id] INT NULL,                   -- no FK: app handles referential integrity
        [is_active] BIT NOT NULL DEFAULT (1),
        [created_at] DATETIME2(7) NOT NULL DEFAULT SYSUTCDATETIME(),
        CONSTRAINT [FK_ticket_recurrence_config_tickets] FOREIGN KEY ([ticket_id])
            REFERENCES [dbo].[tickets]([ticket_id]) ON DELETE SET NULL
    );

    -- Unique constraint: one config per ticket (NULLs excluded from uniqueness)
    CREATE UNIQUE NONCLUSTERED INDEX [IX_ticket_recurrence_config_ticket_id]
        ON [dbo].[ticket_recurrence_config]([ticket_id])
        WHERE [ticket_id] IS NOT NULL;

    -- Index for the scheduler query (find due configs efficiently)
    CREATE NONCLUSTERED INDEX [IX_ticket_recurrence_config_next_occurrence_is_active]
        ON [dbo].[ticket_recurrence_config]([next_occurrence], [is_active])
        WHERE [is_active] = 1;

    -- CHECK constraint for recurrence_type values
    ALTER TABLE [dbo].[ticket_recurrence_config] ADD CONSTRAINT [CK_ticket_recurrence_config_recurrence_type]
        CHECK ([recurrence_type] IN ('none', 'daily', 'weekly', 'biweekly', 'triweekly', 'monthly', 'bimonthly', 'yearly'));
END
GO
