-- Migration: Add time_off_settings table
-- Holds module-wide Time Off settings. allow_weekends = 0 (default) blocks requests that
-- start or end on Saturday/Sunday and counts only weekdays in a request's total_days.
-- Admins (timeoff.admin_actions) toggle it from the Time Off calendar.
--
-- Run against ALL databases that have a dbo.time_off_requests table:
--   1. Main database (DB_DATABASE)
--   2. Each tenant database
-- The API also creates the table at startup via SQLModel.metadata.create_all.
IF NOT EXISTS (
    SELECT 1
    FROM sys.tables
    WHERE name = 'time_off_settings'
    AND schema_id = SCHEMA_ID('dbo')
)
BEGIN
    CREATE TABLE [dbo].[time_off_settings] (
        [setting_id] INT IDENTITY(1,1) NOT NULL CONSTRAINT [pk_time_off_settings] PRIMARY KEY,
        [allow_weekends] BIT NOT NULL CONSTRAINT [df_time_off_settings_allow_weekends] DEFAULT (0),
        [created_at] VARCHAR(19) NOT NULL,
        [updated_at] VARCHAR(19) NOT NULL
    );
END
GO
