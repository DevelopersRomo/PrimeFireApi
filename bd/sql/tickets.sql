-- Tickets table creation
-- Generated on: 2025-10-28
-- Creates the Tickets table with proper constraints and indexes

USE [PrimeFireCorp]
GO

/****** Object:  Table [dbo].[Tickets]    Script Date: 10/28/2025 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[Tickets](
	[TicketId] [int] IDENTITY(1,1) NOT NULL,
	[Title] [nvarchar](200) NOT NULL,
	[Description] [nvarchar](2000) NULL,
	[Status] [nvarchar](20) NOT NULL CONSTRAINT [DF_Tickets_Status] DEFAULT ('todo'),
	[Priority] [nvarchar](20) NOT NULL CONSTRAINT [DF_Tickets_Priority] DEFAULT ('normal'),
	[SLA] [nvarchar](10) NULL,
	[CreatedBy] [int] NOT NULL,
	[AssignedTo] [int] NULL,
	[CreatedAt] [datetime2](7) NOT NULL CONSTRAINT [DF_Tickets_CreatedAt] DEFAULT (SYSUTCDATETIME()),
	[UpdatedAt] [datetime2](7) NOT NULL CONSTRAINT [DF_Tickets_UpdatedAt] DEFAULT (SYSUTCDATETIME()),
 CONSTRAINT [PK_Tickets] PRIMARY KEY CLUSTERED
(
	[TicketId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- Add constraints for Status enum values
ALTER TABLE [dbo].[Tickets] ADD CONSTRAINT [CK_Tickets_Status]
    CHECK ([Status] IN ('todo', 'active', 'inactive', 'closed', 'done', 'in_progress', 'on_hold'))
GO

-- Add constraints for Priority enum values
ALTER TABLE [dbo].[Tickets] ADD CONSTRAINT [CK_Tickets_Priority]
    CHECK ([Priority] IN ('low', 'normal', 'medium', 'high', 'urgent'))
GO

-- Add constraints for SLA enum values
ALTER TABLE [dbo].[Tickets] ADD CONSTRAINT [CK_Tickets_SLA]
    CHECK ([SLA] IS NULL OR [SLA] IN ('12h', '24h', '48h', '1w', '2w', '4w'))
GO

-- Add foreign key constraints
ALTER TABLE [dbo].[Tickets] WITH CHECK ADD CONSTRAINT [FK_Tickets_CreatedBy_Employees]
    FOREIGN KEY([CreatedBy]) REFERENCES [dbo].[Employees] ([EmployeeId])
GO

ALTER TABLE [dbo].[Tickets] WITH CHECK ADD CONSTRAINT [FK_Tickets_AssignedTo_Employees]
    FOREIGN KEY([AssignedTo]) REFERENCES [dbo].[Employees] ([EmployeeId])
GO

-- Add indexes for better performance
CREATE NONCLUSTERED INDEX [IX_Tickets_Status] ON [dbo].[Tickets]
(
	[Status] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO

CREATE NONCLUSTERED INDEX [IX_Tickets_Priority] ON [dbo].[Tickets]
(
	[Priority] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO

CREATE NONCLUSTERED INDEX [IX_Tickets_CreatedBy] ON [dbo].[Tickets]
(
	[CreatedBy] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO

CREATE NONCLUSTERED INDEX [IX_Tickets_AssignedTo] ON [dbo].[Tickets]
(
	[AssignedTo] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO

CREATE NONCLUSTERED INDEX [IX_Tickets_CreatedAt] ON [dbo].[Tickets]
(
	[CreatedAt] DESC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO

CREATE NONCLUSTERED INDEX [IX_Tickets_SLA] ON [dbo].[Tickets]
(
	[SLA] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO



