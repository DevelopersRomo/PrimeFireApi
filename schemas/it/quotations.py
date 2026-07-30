from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ItQuotationItemCreate(BaseModel):
    catalog_item_id: int | None = None
    item_type: str | None = None
    billing_cycle: str | None = None
    name: str | None = Field(default=None, max_length=200)
    description: str | None = None
    scope: str | None = None
    quantity: Decimal = Decimal(1)
    unit: str | None = None
    unit_price: Decimal | None = None
    discount_percent: Decimal = Decimal(0)
    tax_rate: Decimal | None = None
    term_months: int | None = None
    sort_order: int = 0


class ItQuotationItemUpdate(BaseModel):
    item_type: str | None = None
    billing_cycle: str | None = None
    name: str | None = None
    description: str | None = None
    scope: str | None = None
    quantity: Decimal | None = None
    unit: str | None = None
    unit_price: Decimal | None = None
    discount_percent: Decimal | None = None
    tax_rate: Decimal | None = None
    term_months: int | None = None
    sort_order: int | None = None


class ItQuotationItemRead(BaseModel):
    quotation_item_id: int
    quotation_id: int
    catalog_item_id: int | None = None
    item_type: str
    billing_cycle: str
    code_snapshot: str | None = None
    name_snapshot: str
    description_snapshot: str | None = None
    scope_snapshot: str | None = None
    quantity: Decimal
    unit: str
    unit_price: Decimal
    discount_percent: Decimal
    tax_rate: Decimal
    line_subtotal: Decimal
    line_discount: Decimal
    line_tax: Decimal
    line_total: Decimal
    term_months: int | None = None
    sort_order: int


class ItQuotationTermsPayload(BaseModel):
    delivery_time_text: str | None = None
    validity_days: int | None = None
    payment_terms_text: str | None = None
    exclusions_text: str | None = None
    tax_note: str | None = None
    recurring_note: str | None = None
    warranty_text: str | None = None
    acceptance_text: str | None = None


class ItPaymentScheduleEntry(BaseModel):
    sequence_number: int
    description: str = Field(max_length=250)
    percentage: Decimal | None = None
    amount: Decimal | None = None
    due_rule: str | None = None


class ItPaymentScheduleRead(ItPaymentScheduleEntry):
    payment_schedule_id: int
    quotation_id: int


class ItQuotationCreate(BaseModel):
    customer_id: int
    contact_id: int | None = None
    quote_date: date
    expiration_date: date
    currency: str = "USD"
    template_id: int | None = None
    owner_employee_id: int | None = None
    visible_notes: str | None = None
    internal_notes: str | None = None
    items: list[ItQuotationItemCreate] = []
    terms: ItQuotationTermsPayload | None = None
    payment_schedule: list[ItPaymentScheduleEntry] = []


class ItQuotationUpdate(BaseModel):
    contact_id: int | None = None
    quote_date: date | None = None
    expiration_date: date | None = None
    currency: str | None = None
    template_id: int | None = None
    owner_employee_id: int | None = None
    visible_notes: str | None = None
    internal_notes: str | None = None


class ItQuotationRead(BaseModel):
    quotation_id: int
    tenant_id: int
    customer_id: int
    contact_id: int | None = None
    quotation_number: str
    status: str
    quote_date: date
    expiration_date: date
    currency: str
    customer_name_snapshot: str
    contact_name_snapshot: str | None = None
    customer_email_snapshot: str | None = None
    customer_address_snapshot: str | None = None
    one_time_subtotal: Decimal
    monthly_recurring_subtotal: Decimal
    annual_recurring_subtotal: Decimal
    discount_total: Decimal
    tax_total: Decimal
    initial_total: Decimal
    visible_notes: str | None = None
    internal_notes: str | None = None
    template_id: int | None = None
    owner_employee_id: int | None = None
    created_by: int | None = None
    created_at: datetime
    updated_at: datetime | None = None
    sent_at: datetime | None = None
    accepted_at: datetime | None = None
    rejected_at: datetime | None = None


class ItQuotationReportMetrics(BaseModel):
    sent_count: int
    total_amount: Decimal
    monthly_recurring: Decimal
    annual_recurring: Decimal
    conversion_rate: Decimal
    sent_status_count: int
    viewed_status_count: int
    accepted_status_count: int
    rejected_status_count: int


class ItQuotationReportResponse(BaseModel):
    items: list[ItQuotationRead]
    total: int
    skip: int
    limit: int
    has_more: bool
    metrics: ItQuotationReportMetrics


class ItQuotationDetail(ItQuotationRead):
    items: list[ItQuotationItemRead] = []
    terms: ItQuotationTermsPayload | None = None
    payment_schedule: list[ItPaymentScheduleRead] = []


class ItQuotationStatusChange(BaseModel):
    status: str
    notes: str | None = None


class ItQuotationItemsReorder(BaseModel):
    item_ids: list[int]


class ItQuotationNoteCreate(BaseModel):
    note_text: str = Field(min_length=1)


class ItQuotationNoteRead(BaseModel):
    note_id: int
    quotation_id: int
    note_text: str
    created_by: int | None = None
    created_at: datetime


class ItStatusHistoryRead(BaseModel):
    history_id: int
    quotation_id: int
    previous_status: str | None = None
    new_status: str
    changed_by: int | None = None
    change_notes: str | None = None
    changed_at: datetime
