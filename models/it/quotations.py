from datetime import date, datetime
from decimal import Decimal

from sqlmodel import Field, SQLModel

IT_QUOTATION_STATUSES = (
    "DRAFT",
    "SENT",
    "VIEWED",
    "ACCEPTED",
    "REJECTED",
    "EXPIRED",
    "CANCELLED",
)

# Valid transitions: key -> allowed next statuses
IT_STATUS_TRANSITIONS: dict[str, tuple[str, ...]] = {
    "DRAFT": ("SENT", "CANCELLED"),
    "SENT": ("VIEWED", "ACCEPTED", "REJECTED", "EXPIRED", "CANCELLED"),
    "VIEWED": ("ACCEPTED", "REJECTED", "EXPIRED", "CANCELLED"),
    "ACCEPTED": (),
    "REJECTED": (),
    "EXPIRED": (),
    "CANCELLED": (),
}


class ITQuotations(SQLModel, table=True):
    __tablename__ = "quotations"
    __table_args__ = {"schema": "it"}

    quotation_id: int | None = Field(default=None, primary_key=True, index=True)
    tenant_id: int = Field(index=True)
    customer_id: int = Field(foreign_key="dbo.customers.customer_id", index=True)
    contact_id: int | None = Field(
        default=None,
        foreign_key="dbo.customer_alternate_contacts.customer_alternate_contact_id",
    )
    quotation_number: str = Field(max_length=50, index=True)
    status: str = Field(default="DRAFT", max_length=30, index=True)
    quote_date: date
    expiration_date: date
    currency: str = Field(default="USD", max_length=3)

    customer_name_snapshot: str = Field(max_length=200)
    contact_name_snapshot: str | None = Field(default=None, max_length=200)
    customer_email_snapshot: str | None = Field(default=None, max_length=200)
    customer_address_snapshot: str | None = Field(default=None, max_length=1000)

    one_time_subtotal: Decimal = Field(default=Decimal("0"), max_digits=18, decimal_places=2)
    monthly_recurring_subtotal: Decimal = Field(default=Decimal("0"), max_digits=18, decimal_places=2)
    annual_recurring_subtotal: Decimal = Field(default=Decimal("0"), max_digits=18, decimal_places=2)
    discount_total: Decimal = Field(default=Decimal("0"), max_digits=18, decimal_places=2)
    tax_total: Decimal = Field(default=Decimal("0"), max_digits=18, decimal_places=2)
    initial_total: Decimal = Field(default=Decimal("0"), max_digits=18, decimal_places=2)

    visible_notes: str | None = None
    internal_notes: str | None = None

    template_id: int | None = Field(default=None, foreign_key="it.pdf_templates.template_id")
    owner_employee_id: int | None = Field(default=None, foreign_key="dbo.employees.employee_id")
    created_by: int | None = Field(default=None, foreign_key="dbo.employees.employee_id")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None
    sent_at: datetime | None = None
    accepted_at: datetime | None = None
    rejected_at: datetime | None = None


class ITQuotationItems(SQLModel, table=True):
    __tablename__ = "quotation_items"
    __table_args__ = {"schema": "it"}

    quotation_item_id: int | None = Field(default=None, primary_key=True, index=True)
    quotation_id: int = Field(foreign_key="it.quotations.quotation_id", index=True)
    catalog_item_id: int | None = Field(default=None, foreign_key="it.catalog_items.catalog_item_id")
    item_type: str = Field(max_length=30)
    billing_cycle: str = Field(max_length=20)

    code_snapshot: str | None = Field(default=None, max_length=100)
    name_snapshot: str = Field(max_length=200)
    description_snapshot: str | None = Field(default=None, max_length=2000)
    scope_snapshot: str | None = None

    quantity: Decimal = Field(default=Decimal("1"), max_digits=18, decimal_places=2)
    unit: str = Field(default="EA", max_length=50)
    unit_price: Decimal = Field(default=Decimal("0"), max_digits=18, decimal_places=2)
    discount_percent: Decimal = Field(default=Decimal("0"), max_digits=5, decimal_places=2)
    tax_rate: Decimal = Field(default=Decimal("0"), max_digits=5, decimal_places=2)

    line_subtotal: Decimal = Field(default=Decimal("0"), max_digits=18, decimal_places=2)
    line_discount: Decimal = Field(default=Decimal("0"), max_digits=18, decimal_places=2)
    line_tax: Decimal = Field(default=Decimal("0"), max_digits=18, decimal_places=2)
    line_total: Decimal = Field(default=Decimal("0"), max_digits=18, decimal_places=2)

    term_months: int | None = None
    sort_order: int = Field(default=0)


class ITQuotationTerms(SQLModel, table=True):
    __tablename__ = "quotation_terms"
    __table_args__ = {"schema": "it"}

    quotation_id: int = Field(primary_key=True, foreign_key="it.quotations.quotation_id")
    delivery_time_text: str | None = Field(default=None, max_length=500)
    validity_days: int | None = None
    payment_terms_text: str | None = None
    exclusions_text: str | None = None
    tax_note: str | None = None
    recurring_note: str | None = None
    warranty_text: str | None = None
    acceptance_text: str | None = None


class ITPaymentSchedule(SQLModel, table=True):
    __tablename__ = "payment_schedule"
    __table_args__ = {"schema": "it"}

    payment_schedule_id: int | None = Field(default=None, primary_key=True, index=True)
    quotation_id: int = Field(foreign_key="it.quotations.quotation_id", index=True)
    sequence_number: int
    description: str = Field(max_length=250)
    percentage: Decimal | None = Field(default=None, max_digits=5, decimal_places=2)
    amount: Decimal | None = Field(default=None, max_digits=18, decimal_places=2)
    due_rule: str | None = Field(default=None, max_length=250)


class ITQuotationNotes(SQLModel, table=True):
    __tablename__ = "quotation_notes"
    __table_args__ = {"schema": "it"}

    note_id: int | None = Field(default=None, primary_key=True, index=True)
    quotation_id: int = Field(foreign_key="it.quotations.quotation_id", index=True)
    note_text: str
    created_by: int | None = Field(default=None, foreign_key="dbo.employees.employee_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ITQuotationStatusHistory(SQLModel, table=True):
    __tablename__ = "quotation_status_history"
    __table_args__ = {"schema": "it"}

    history_id: int | None = Field(default=None, primary_key=True, index=True)
    quotation_id: int = Field(foreign_key="it.quotations.quotation_id", index=True)
    previous_status: str | None = Field(default=None, max_length=30)
    new_status: str = Field(max_length=30)
    changed_by: int | None = Field(default=None, foreign_key="dbo.employees.employee_id")
    change_notes: str | None = Field(default=None, max_length=500)
    changed_at: datetime = Field(default_factory=datetime.utcnow)
