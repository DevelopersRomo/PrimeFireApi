from datetime import date, datetime
from decimal import Decimal

from sqlmodel import SQLModel


class ExpenseCategoryCreate(SQLModel):
    name: str
    code: str | None = None
    requires_invoice: bool = False
    per_item_cap: Decimal | None = None
    daily_cap: Decimal | None = None
    display_order: int = 0


class ExpenseCategoryUpdate(SQLModel):
    name: str | None = None
    code: str | None = None
    requires_invoice: bool | None = None
    per_item_cap: Decimal | None = None
    daily_cap: Decimal | None = None
    display_order: int | None = None
    is_active: bool | None = None


class ExpenseCategory(SQLModel):
    category_id: int | None = None
    name: str
    code: str | None = None
    requires_invoice: bool = False
    per_item_cap: Decimal | None = None
    daily_cap: Decimal | None = None
    display_order: int = 0
    is_active: bool = True


class ExpenseApprovalRuleCreate(SQLModel):
    min_amount: Decimal = Decimal(0)
    max_amount: Decimal | None = None
    level: int = 1
    role_id: int


class ExpenseApprovalRuleUpdate(SQLModel):
    min_amount: Decimal | None = None
    max_amount: Decimal | None = None
    level: int | None = None
    role_id: int | None = None
    is_active: bool | None = None


class ExpenseApprovalRule(SQLModel):
    rule_id: int | None = None
    min_amount: Decimal = Decimal(0)
    max_amount: Decimal | None = None
    level: int = 1
    role_id: int
    is_active: bool = True

    role_name: str | None = None


class ExpenseItemCreate(SQLModel):
    category_id: int | None = None
    expense_date: date | None = None
    merchant: str | None = None
    description: str | None = None
    currency: str = "USD"
    amount_original: Decimal = Decimal(0)
    fx_rate: Decimal = Decimal(1)
    subtotal_amount: Decimal | None = None
    tax_amount: Decimal | None = None
    tip_amount: Decimal | None = None
    has_invoice: bool = False
    tax_id: str | None = None
    source: str = "manual"
    extraction_confidence: Decimal | None = None
    receipt_id: int | None = None


class ExpenseItemUpdate(SQLModel):
    category_id: int | None = None
    expense_date: date | None = None
    merchant: str | None = None
    description: str | None = None
    currency: str | None = None
    amount_original: Decimal | None = None
    fx_rate: Decimal | None = None
    subtotal_amount: Decimal | None = None
    tax_amount: Decimal | None = None
    tip_amount: Decimal | None = None
    has_invoice: bool | None = None
    tax_id: str | None = None


class ExpenseItem(SQLModel):
    item_id: int | None = None
    report_id: int
    category_id: int | None = None
    expense_date: date | None = None
    merchant: str | None = None
    description: str | None = None
    currency: str = "USD"
    amount_original: Decimal = Decimal(0)
    fx_rate: Decimal = Decimal(1)
    amount_base: Decimal = Decimal(0)  # USD base amount; currency applies only to amount_original.
    subtotal_amount: Decimal | None = None
    tax_amount: Decimal | None = None
    tip_amount: Decimal | None = None
    has_invoice: bool = False
    tax_id: str | None = None
    status: str = "pending"
    approved_amount: Decimal | None = None
    review_note: str | None = None
    source: str = "manual"
    extraction_confidence: Decimal | None = None
    created_at: datetime | None = None

    category_name: str | None = None
    receipt_count: int = 0


class ExpenseReceipt(SQLModel):
    receipt_id: int | None = None
    report_id: int
    item_id: int | None = None
    file_name: str
    file_type: str | None = None
    file_path: str | None = None
    file_size: int | None = None
    page_count: int = 1
    uploaded_by: int | None = None
    created_at: datetime | None = None

    extraction_status: str | None = None


class ExtractionCandidate(SQLModel):
    """One total candidate with its score and bounding box, for UI evidence."""

    value: Decimal
    label: str | None = None
    score: float = 0.0
    box: list[int] | None = None
    page: int = 1


class ExpenseReceiptExtraction(SQLModel):
    extraction_id: int | None = None
    receipt_id: int
    engine: str | None = None
    status: str = "pending"
    detected_total: Decimal | None = None
    detected_subtotal: Decimal | None = None
    detected_tax: Decimal | None = None
    detected_tip: Decimal | None = None
    detected_currency: str | None = None
    detected_date: date | None = None
    detected_merchant: str | None = None
    detected_tax_id: str | None = None
    detected_uuid: str | None = None
    confidence: Decimal = Decimal(0)
    arithmetic_ok: bool = False
    candidates: list[ExtractionCandidate] = []
    error_message: str | None = None
    duration_ms: int | None = None
    processed_at: datetime | None = None


class ExpenseFlag(SQLModel):
    flag_id: int | None = None
    report_id: int
    item_id: int | None = None
    code: str
    severity: str = "warning"
    message: str
    created_at: datetime | None = None


class ExpenseApproval(SQLModel):
    approval_id: int | None = None
    report_id: int
    level: int = 1
    role_id: int | None = None
    approver_id: int | None = None
    decision: str = "pending"
    amount_approved: Decimal | None = None
    note: str | None = None
    decided_at: datetime | None = None

    role_name: str | None = None
    approver_name: str | None = None


class ExpenseMessage(SQLModel):
    message_id: int | None = None
    report_id: int
    user_id: int
    message_txt: str | None = None
    created_at: datetime | None = None
    edited_at: datetime | None = None

    user_name: str | None = None
    user_email: str | None = None


class ExpenseMessageCreate(SQLModel):
    message_txt: str


class ExpenseReimbursement(SQLModel):
    reimbursement_id: int | None = None
    report_id: int
    amount: Decimal = Decimal(0)
    currency: str = "USD"
    payment_method: str | None = None
    reference: str | None = None
    note: str | None = None
    paid_by: int | None = None
    paid_at: datetime | None = None

    paid_by_name: str | None = None


class ExpenseReimbursementCreate(SQLModel):
    amount: Decimal
    payment_method: str | None = None
    reference: str | None = None
    note: str | None = None


class ExpenseReportCreate(SQLModel):
    title: str
    employee_id: int | None = None
    job_id: int | None = None
    po_number: str | None = None
    project: str | None = None
    trip_type: str = "national"
    destination: str | None = None
    trip_start_date: date | None = None
    trip_end_date: date | None = None
    currency: str = "USD"
    notes: str | None = None


class ExpenseReportUpdate(SQLModel):
    title: str | None = None
    job_id: int | None = None
    po_number: str | None = None
    project: str | None = None
    trip_type: str | None = None
    destination: str | None = None
    trip_start_date: date | None = None
    trip_end_date: date | None = None
    currency: str | None = None
    notes: str | None = None


class ExpenseReport(SQLModel):
    report_id: int | None = None
    folio: str
    employee_id: int
    job_id: int | None = None
    title: str
    po_number: str | None = None
    project: str | None = None
    trip_type: str = "national"
    destination: str | None = None
    trip_start_date: date | None = None
    trip_end_date: date | None = None
    currency: str = "USD"
    total_requested: Decimal = Decimal(0)  # Consolidated USD base amount.
    total_approved: Decimal = Decimal(0)  # Consolidated USD base amount.
    total_reimbursed: Decimal = Decimal(0)  # Consolidated USD base amount.
    status: str = "draft"
    current_level: int = 0
    notes: str | None = None
    submitted_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    employee_name: str | None = None
    employee_title: str | None = None
    employee_email: str | None = None
    job_name: str | None = None
    job_code: str | None = None
    receipt_count: int = 0
    flag_count: int = 0


class ExpenseReportDetail(ExpenseReport):
    items: list[ExpenseItem] = []
    receipts: list[ExpenseReceipt] = []
    approvals: list[ExpenseApproval] = []
    flags: list[ExpenseFlag] = []
    reimbursement: ExpenseReimbursement | None = None

    # Resolved server-side so the UI never re-implements separation of duty.
    can_review: bool = False
    can_reimburse: bool = False
    pending_level: int | None = None
    pending_role_name: str | None = None


class ExpenseItemDecision(SQLModel):
    item_id: int
    decision: str  # approved, rejected
    approved_amount: Decimal | None = None
    note: str | None = None


class ExpenseReview(SQLModel):
    note: str | None = None
    item_decisions: list[ExpenseItemDecision] = []


class ExpenseStats(SQLModel):
    pending_count: int = 0
    pending_amount: Decimal = Decimal(0)
    approved_count: int = 0
    approved_amount: Decimal = Decimal(0)
    reimbursed_month_amount: Decimal = Decimal(0)
    reimbursed_month_count: int = 0
    requested_year_amount: Decimal = Decimal(0)
    currency: str = "USD"
