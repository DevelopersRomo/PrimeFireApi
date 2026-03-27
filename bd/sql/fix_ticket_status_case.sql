-- Fix: Normalize ticket status values to lowercase
-- The Python enum expects lowercase values but DB might have uppercase

-- Normalize Status values
UPDATE Tickets SET Status = 'todo' WHERE Status = 'TODO';
UPDATE Tickets SET Status = 'active' WHERE Status = 'ACTIVE';
UPDATE Tickets SET Status = 'inactive' WHERE Status = 'INACTIVE';
UPDATE Tickets SET Status = 'closed' WHERE Status = 'CLOSED';
UPDATE Tickets SET Status = 'done' WHERE Status = 'DONE';
UPDATE Tickets SET Status = 'in_progress' WHERE Status = 'IN_PROGRESS';
UPDATE Tickets SET Status = 'on_hold' WHERE Status = 'ON_HOLD';

-- Normalize Priority values (if any uppercase exist)
UPDATE Tickets SET Priority = 'low' WHERE Priority = 'LOW';
UPDATE Tickets SET Priority = 'normal' WHERE Priority = 'NORMAL';
UPDATE Tickets SET Priority = 'medium' WHERE Priority = 'MEDIUM';
UPDATE Tickets SET Priority = 'high' WHERE Priority = 'HIGH';
UPDATE Tickets SET Priority = 'urgent' WHERE Priority = 'URGENT';

-- Normalize SLA values (if any uppercase exist)
UPDATE Tickets SET SLA = '12h' WHERE SLA = '12H';
UPDATE Tickets SET SLA = '24h' WHERE SLA = '24H';
UPDATE Tickets SET SLA = '48h' WHERE SLA = '48H';
UPDATE Tickets SET SLA = '1w' WHERE SLA = '1W';
UPDATE Tickets SET SLA = '2w' WHERE SLA = '2W';
UPDATE Tickets SET SLA = '4w' WHERE SLA = '4W';

PRINT 'Status/Priority/SLA values normalized to lowercase';
