-- Drop existing time off tables to recreate with compatible types
USE [PrimeFireCorp];
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'TimeOffRequests')
BEGIN
    DROP TABLE [dbo].[TimeOffRequests];
END
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'TimeOffBalances')
BEGIN
    DROP TABLE [dbo].[TimeOffBalances];
END
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'Holidays')
BEGIN
    DROP TABLE [dbo].[Holidays];
END
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'Departments')
BEGIN
    DROP TABLE [dbo].[Departments];
END
GO
