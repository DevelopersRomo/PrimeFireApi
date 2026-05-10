-- Migration: Add in_progress_at column to tickets table
-- Date: 2026-05-09
-- 
-- Run against ALL databases that have a dbo.tickets table:
--   1. Main database (PrimeFireCorp or whatever DB_DATABASE is set to)
--   2. Each tenant database (DB_DATABASE_CLIENTA, DB_DATABASE_CLIENTB, etc.)

ALTER TABLE dbo.tickets ADD in_progress_at DATETIME NULL;
