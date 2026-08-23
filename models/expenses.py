"""Travel expense reimbursement tables.

An `ExpenseReports` row is one reimbursement claim (folio VIA-YYYY-NNNN). It owns
expense lines, uploaded receipts, an amount-tiered approval chain, policy flags,
a message thread and, once paid, a reimbursement record.
"""

from datetime import date, datetime
from decimal import Decimal

from sqlmodel import Field, SQLModel

from core.datetime_utils import utcnow

BASE_CURRENCY = "USD"


class ExpenseCategories(SQLModel, table=True):
    __tablename__ = "expense_categories"
    __table_args__ = {"schema": "dbo"}

    category_id: int | None = Field(default=None, primary_key=True, index=True)
    name: str = Field(max_length=100)
    code: str | None = Field(default=None, max_length=30)
    requires_invoice: bool = Field(default=False)
    per_item_cap: Decimal | None = Field(default=None, max_digits=18, decimal_places=2)
    daily_cap: Decimal | None = Field(default=None, max_digits=18, decimal_places=2)
    display_order: int = Field(default=0)
    is_active: bool = Field(default=True)


class ExpenseApprovalRules(SQLModel, table=True):
    """One row per (amount band, level). Drives the escalation chain on submit."""

    __tablename__ = "expense_approval_rules"
    __table_args__ = {"schema": "dbo"}

    rule_id: int | None = Field(default=None, primary_key=True, index=True)
    min_amount: Decimal = Field(default=Decimal(0), max_digits=18, decimal_places=2)
    max_amount: Decimal | None = Field(default=None, max_digits=18, decimal_places=2)
    level: int = Field(default=1)
    role_id: int = Field(foreign_key="dbo.roles.role_id")
    is_active: bool = Field(default=True)


class ExpenseReports(SQLModel, table=True):
    __tablename__ = "expense_reports"
    __table_args__ = {"schema": "dbo"}

    report_id: int | None = Field(default=None, primary_key=True, index=True)
    folio: str = Field(max_length=30, unique=True, index=True)
    employee_id: int = Field(foreign_key="dbo.employees.employee_id", index=True)
    job_id: int | None = Field(default=None, foreign_key="dbo.jobs.job_id")

    title: str = Field(max_length=200)
    po_number: str | None = Field(default=None, max_length=100)
    project: str | None = Field(default=None, max_length=150)
    trip_type: str = Field(default="national", max_length=20)  # national, international
    destination: str | None = Field(default=None, max_length=200)
    trip_start_date: date | None = Field(default=None)
    trip_end_date: date | None = Field(default=None)

    currency: str = Field(default=BASE_CURRENCY, max_length=3)
    total_requested: Decimal = Field(default=Decimal(0), max_digits=18, decimal_places=2)
    total_approved: Decimal = Field(default=Decimal(0), max_digits=18, decimal_places=2)
    total_reimbursed: Decimal = Field(default=Decimal(0), max_digits=18, decimal_places=2)

    # draft, submitted, in_review, approved, partially_approved, rejected, paid, cancelled
    status: str = Field(default="draft", max_length=25, index=True)
    current_level: int = Field(default=0)

    notes: str | None = Field(default=None, max_length=2000)
    submitted_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class ExpenseReportItems(SQLModel, table=True):
    """One expense line. Partial approval happens here, per line and per amount."""

    __tablename__ = "expense_report_items"
    __table_args__ = {"schema": "dbo"}

    item_id: int | None = Field(default=None, primary_key=True, index=True)
    report_id: int = Field(foreign_key="dbo.expense_reports.report_id", index=True)
    category_id: int | None = Field(default=None, foreign_key="dbo.expense_categories.category_id")

    expense_date: date | None = Field(default=None)
    merchant: str | None = Field(default=None, max_length=200)
    description: str | None = Field(default=None, max_length=500)

    currency: str = Field(default=BASE_CURRENCY, max_length=3)
    amount_original: Decimal = Field(default=Decimal(0), max_digits=18, decimal_places=2)
    fx_rate: Decimal = Field(default=Decimal(1), max_digits=18, decimal_places=6)
    amount_base: Decimal = Field(default=Decimal(0), max_digits=18, decimal_places=2)
    subtotal_amount: Decimal | None = Field(default=None, max_digits=18, decimal_places=2)
    tax_amount: Decimal | None = Field(default=None, max_digits=18, decimal_places=2)
    tip_amount: Decimal | None = Field(default=None, max_digits=18, decimal_places=2)

    has_invoice: bool = Field(default=False)
    tax_id: str | None = Field(default=None, max_length=20)

    status: str = Field(default="pending", max_length=20)  # pending, approved, rejected
    approved_amount: Decimal | None = Field(default=None, max_digits=18, decimal_places=2)
    review_note: str | None = Field(default=None, max_length=500)

    source: str = Field(default="manual", max_length=20)  # manual, ocr, qr, pdf_text
    extraction_confidence: Decimal | None = Field(default=None, max_digits=5, decimal_places=4)

    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class ExpenseReceipts(SQLModel, table=True):
    """Uploaded proof file. Mirrors TicketAttachments plus dedupe fingerprints."""

    __tablename__ = "expense_receipts"
    __table_args__ = {"schema": "dbo"}

    receipt_id: int | None = Field(default=None, primary_key=True, index=True)
    report_id: int = Field(foreign_key="dbo.expense_reports.report_id", index=True)
    item_id: int | None = Field(default=None, foreign_key="dbo.expense_report_items.item_id")

    file_name: str = Field(max_length=255)
    file_type: str | None = Field(default=None, max_length=100)
    file_path: str | None = Field(default=None, max_length=500)
    file_size: int | None = Field(default=None)

    sha256: str | None = Field(default=None, max_length=64, index=True)
    phash: str | None = Field(default=None, max_length=32)
    page_count: int = Field(default=1)

    uploaded_by: int | None = Field(default=None, foreign_key="dbo.employees.employee_id")
    created_at: datetime = Field(default_factory=utcnow)


class ExpenseReceiptExtractions(SQLModel, table=True):
    """OCR output, kept apart so raw text never pollutes the receipt row."""

    __tablename__ = "expense_receipt_extractions"
    __table_args__ = {"schema": "dbo"}

    extraction_id: int | None = Field(default=None, primary_key=True, index=True)
    receipt_id: int = Field(foreign_key="dbo.expense_receipts.receipt_id", index=True)

    engine: str | None = Field(default=None, max_length=20)  # qr_sat, pdf_text, tesseract
    status: str = Field(default="pending", max_length=20)  # pending, done, failed

    raw_text: str | None = Field(default=None)
    detected_total: Decimal | None = Field(default=None, max_digits=18, decimal_places=2)
    detected_subtotal: Decimal | None = Field(default=None, max_digits=18, decimal_places=2)
    detected_tax: Decimal | None = Field(default=None, max_digits=18, decimal_places=2)
    detected_tip: Decimal | None = Field(default=None, max_digits=18, decimal_places=2)
    detected_currency: str | None = Field(default=None, max_length=3)
    detected_date: date | None = Field(default=None)
    detected_merchant: str | None = Field(default=None, max_length=200)
    detected_tax_id: str | None = Field(default=None, max_length=20)
    detected_uuid: str | None = Field(default=None, max_length=36, index=True)

    confidence: Decimal = Field(default=Decimal(0), max_digits=5, decimal_places=4)
    arithmetic_ok: bool = Field(default=False)
    candidates_json: str | None = Field(default=None)

    error_message: str | None = Field(default=None, max_length=500)
    duration_ms: int | None = Field(default=None)
    processed_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=utcnow)


class ExpenseReportApprovals(SQLModel, table=True):
    """Audit trail: one row per level of the resolved chain."""

    __tablename__ = "expense_report_approvals"
    __table_args__ = {"schema": "dbo"}

    approval_id: int | None = Field(default=None, primary_key=True, index=True)
    report_id: int = Field(foreign_key="dbo.expense_reports.report_id", index=True)
    level: int = Field(default=1)
    role_id: int | None = Field(default=None, foreign_key="dbo.roles.role_id")
    approver_id: int | None = Field(default=None, foreign_key="dbo.employees.employee_id")

    # pending, approved, partially_approved, rejected
    decision: str = Field(default="pending", max_length=25)
    amount_approved: Decimal | None = Field(default=None, max_digits=18, decimal_places=2)
    note: str | None = Field(default=None, max_length=1000)
    decided_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=utcnow)


class ExpenseReportFlags(SQLModel, table=True):
    """Policy engine output. The approver screen leads with these."""

    __tablename__ = "expense_report_flags"
    __table_args__ = {"schema": "dbo"}

    flag_id: int | None = Field(default=None, primary_key=True, index=True)
    report_id: int = Field(foreign_key="dbo.expense_reports.report_id", index=True)
    item_id: int | None = Field(default=None, foreign_key="dbo.expense_report_items.item_id")

    code: str = Field(max_length=40)
    severity: str = Field(default="warning", max_length=10)  # info, warning, critical
    message: str = Field(max_length=500)
    created_at: datetime = Field(default_factory=utcnow)


class ExpenseReportMessages(SQLModel, table=True):
    __tablename__ = "expense_report_messages"
    __table_args__ = {"schema": "dbo"}

    message_id: int | None = Field(default=None, primary_key=True, index=True)
    report_id: int = Field(foreign_key="dbo.expense_reports.report_id", index=True)
    user_id: int = Field(foreign_key="dbo.employees.employee_id")
    message_txt: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime | None = None
    edited_at: datetime | None = None


class ExpenseReimbursements(SQLModel, table=True):
    __tablename__ = "expense_reimbursements"
    __table_args__ = {"schema": "dbo"}

    reimbursement_id: int | None = Field(default=None, primary_key=True, index=True)
    report_id: int = Field(foreign_key="dbo.expense_reports.report_id", index=True)

    amount: Decimal = Field(default=Decimal(0), max_digits=18, decimal_places=2)
    currency: str = Field(default=BASE_CURRENCY, max_length=3)
    payment_method: str | None = Field(default=None, max_length=50)
    reference: str | None = Field(default=None, max_length=100)
    note: str | None = Field(default=None, max_length=500)
    paid_by: int | None = Field(default=None, foreign_key="dbo.employees.employee_id")
    paid_at: datetime = Field(default_factory=utcnow)
