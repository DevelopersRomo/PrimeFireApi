IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[Employees]') AND name = 'Anydesk')
BEGIN
    ALTER TABLE [dbo].[Employees] ADD [Anydesk] NVARCHAR(50) NULL;
END
