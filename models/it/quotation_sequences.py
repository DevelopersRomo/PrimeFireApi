from datetime import datetime

from sqlmodel import Field, SQLModel


class ITCustomerQuotationSequence(SQLModel, table=True):
    """Per-customer counter used to number quotations at send time."""

    __tablename__ = "customer_quotation_sequences"
    __table_args__ = {"schema": "it"}

    tenant_id: int = Field(primary_key=True)
    customer_id: int = Field(primary_key=True)
    last_number: int = Field(default=0)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
