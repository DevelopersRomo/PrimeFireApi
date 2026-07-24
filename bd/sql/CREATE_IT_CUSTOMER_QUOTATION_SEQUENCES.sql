-- Per-customer sequence used to number quotations at send time.
-- Format assigned on first send: Q-{FIRST3(customer_name)}-{customer_id}-{seq:05d}
-- Existing Q-IT-{year}-{seq} numbers are preserved and remain valid.
IF OBJECT_ID('it.customer_quotation_sequences', 'U') IS NULL
BEGIN
    CREATE TABLE it.customer_quotation_sequences (
        tenant_id   INT NOT NULL,
        customer_id INT NOT NULL,
        last_number INT NOT NULL DEFAULT 0,
        updated_at  DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
        CONSTRAINT PK_customer_quotation_sequences
            PRIMARY KEY (tenant_id, customer_id)
    );
END;
GO

PRINT 'it.customer_quotation_sequences created.';
GO
