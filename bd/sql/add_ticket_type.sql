-- Migration: Add ticket_type column to Tickets table
-- Safe to run multiple times - includes existence checks

-- Step 1: Add the column if it doesn't exist
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('Tickets') AND name = 'ticket_type')
BEGIN
    ALTER TABLE Tickets ADD ticket_type NVARCHAR(20) NOT NULL DEFAULT 'request';
    PRINT 'Column ticket_type added successfully';
END
ELSE
BEGIN
    PRINT 'Column ticket_type already exists, skipping';
END
GO

-- Step 2: Add CHECK constraint if it doesn't exist
IF NOT EXISTS (SELECT * FROM sys.check_constraints WHERE object_id = OBJECT_ID('CK_Tickets_TicketType'))
BEGIN
    ALTER TABLE Tickets ADD CONSTRAINT CK_Tickets_TicketType CHECK (ticket_type IN ('issue', 'request', 'improvement'));
    PRINT 'Constraint CK_Tickets_TicketType added successfully';
END
ELSE
BEGIN
    PRINT 'Constraint CK_Tickets_TicketType already exists, skipping';
END
GO

-- Step 3: Create index if it doesn't exist
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE object_id = OBJECT_ID('Tickets') AND name = 'IX_Tickets_TicketType')
BEGIN
    CREATE NONCLUSTERED INDEX IX_Tickets_TicketType ON Tickets(ticket_type);
    PRINT 'Index IX_Tickets_TicketType created successfully';
END
ELSE
BEGIN
    PRINT 'Index IX_Tickets_TicketType already exists, skipping';
END
GO

PRINT 'Migration completed!';
