-- Auth Tokens table for password recovery and magic link
-- Run this script to create the table in SQL Server

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='auth_tokens' AND xtype='U')
BEGIN
    CREATE TABLE [dbo].[auth_tokens](
        [id] [int] IDENTITY(1,1) NOT NULL,
        [email] [nvarchar](255) NOT NULL,
        [token] [nvarchar](512) NOT NULL,
        [token_type] [nvarchar](50) NOT NULL,
        [expires_at] [datetime2](6) NOT NULL,
        [used_at] [datetime2](6) NULL,
        [created_at] [datetime2](6) NOT NULL DEFAULT GETUTCDATE(),
        CONSTRAINT [PK_auth_tokens] PRIMARY KEY CLUSTERED ([id] ASC),
        CONSTRAINT [UQ_auth_tokens_token] UNIQUE NONCLUSTERED ([token] ASC)
    );

    CREATE NONCLUSTERED INDEX [IX_auth_tokens_email] ON [dbo].[auth_tokens]([email] ASC);
    CREATE NONCLUSTERED INDEX [IX_auth_tokens_token] ON [dbo].[auth_tokens]([token] ASC) WHERE [token] IS NOT NULL;
END
GO
