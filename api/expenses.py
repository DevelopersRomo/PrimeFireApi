"""Travel expense reimbursement endpoints."""

import logging
from datetime import date
from decimal import Decimal
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request, status
from sqlalchemy import or_
from sqlmodel import Session, func, select

from api.dependencies import (
    get_current_employee,
    get_request_app_url,
    require_module_permission,
)
from bd.dependencies import get_db
from core.datetime_utils import utcnow
from models.employees import Employees
from models.expenses import (
    BASE_CURRENCY,
    ExpenseApprovalRules,
    ExpenseCategories,
    ExpenseReceiptExtractions,
    ExpenseReceipts,
    ExpenseReimbursements,
    ExpenseReportApprovals,
    ExpenseReportFlags,
    ExpenseReportItems,
    ExpenseReportMessages,
    ExpenseReports,
)
from models.jobs import Jobs
from schemas.expenses import (
    ExpenseApproval,
    ExpenseApprovalRule,
    ExpenseApprovalRuleCreate,
    ExpenseApprovalRuleUpdate,
    ExpenseCategory,
    ExpenseCategoryCreate,
    ExpenseCategoryUpdate,
    ExpenseFlag,
    ExpenseItem,
    ExpenseItemCreate,
    ExpenseItemUpdate,
    ExpenseReceipt,
    ExpenseReimbursement,
    ExpenseReimbursementCreate,
    ExpenseReport,
    ExpenseReportCreate,
    ExpenseReportDetail,
    ExpenseReportUpdate,
    ExpenseReview,
    ExpenseStats,
)
from schemas.pagination import PaginatedResponse
from services.expenses import approvals, fx, policies
from services.expenses.folio import next_folio
from services.notifications.expenses import (
    notify_expense_approved,
    notify_expense_paid,
    notify_expense_partially_approved,
    notify_expense_rejected,
    notify_expense_submitted,
)

logger = logging.getLogger(__name__)

router = APIRouter()

MODULE_KEY = "expenses"
EDITABLE_STATUSES = {"draft", "rejected"}


# --- Helpers ----------------------------------------------------------------


def _settle_amount(item: ExpenseReportItems) -> None:
    """Resolve the rate for a foreign line, then restate it in the base currency.

    The rate is looked up for the day the money was spent and frozen on the line,
    so the figure the approver decided on never moves afterwards. When the feed
    cannot answer, the rate is left at 1 and the policy engine raises
    FX_RATE_UNAVAILABLE — an unconverted amount is visible, an invented one is not.
    """
    if item.currency and item.currency.upper() != BASE_CURRENCY:
        resolved = fx.rate_to_base(item.currency, item.expense_date)
        if resolved is not None:
            # Quantized to the column's own scale before the amount is derived,
            # so an approver multiplying the rate they can see reproduces the
            # figure to the cent.
            item.fx_rate = resolved.quantize(Decimal("0.000001"))
    else:
        item.fx_rate = Decimal(1)

    item.amount_base = (item.amount_original * item.fx_rate).quantize(Decimal("0.01"))


def _get_report_or_404(db: Session, report_id: int) -> ExpenseReports:
    report = db.get(ExpenseReports, report_id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense report not found")
    return report


def _assert_owner_or_admin(report: ExpenseReports, employee: Employees, user_permissions: dict) -> None:
    if report.employee_id == employee.employee_id:
        return
    if approvals.has_admin_actions(user_permissions):
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This expense report belongs to another employee")


def _assert_editable(report: ExpenseReports) -> None:
    if report.status not in EDITABLE_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A report in status '{report.status}' can no longer be edited",
        )


def _employee_lookup(db: Session, employee_ids: list[int]) -> dict[int, Employees]:
    if not employee_ids:
        return {}
    rows = db.exec(select(Employees).where(Employees.employee_id.in_(set(employee_ids)))).all()  # type: ignore[attr-defined]
    return {row.employee_id: row for row in rows}


def _job_lookup(db: Session, job_ids: list[int]) -> dict[int, Jobs]:
    clean = [job_id for job_id in job_ids if job_id]
    if not clean:
        return {}
    rows = db.exec(select(Jobs).where(Jobs.job_id.in_(set(clean)))).all()  # type: ignore[attr-defined]
    return {row.job_id: row for row in rows}


def _report_to_schema(
    report: ExpenseReports,
    employee: Employees | None = None,
    job: Jobs | None = None,
    receipt_count: int = 0,
    flag_count: int = 0,
) -> ExpenseReport:
    return ExpenseReport(
        **report.model_dump(),
        employee_name=(employee.display_name if employee else None),
        employee_title=(employee.title if employee else None),
        employee_email=(employee.email if employee else None),
        job_name=(job.title if job else report.project),
        job_code=report.po_number,
        receipt_count=receipt_count,
        flag_count=flag_count,
    )


def _item_to_schema(item: ExpenseReportItems, category_name: str | None = None, receipt_count: int = 0) -> ExpenseItem:
    return ExpenseItem(**item.model_dump(), category_name=category_name, receipt_count=receipt_count)


def _approval_to_schema(db: Session, approval: ExpenseReportApprovals) -> ExpenseApproval:
    approver = db.get(Employees, approval.approver_id) if approval.approver_id else None
    return ExpenseApproval(
        **approval.model_dump(),
        role_name=approvals.role_name(db, approval.role_id),
        approver_name=(approver.display_name if approver else None),
    )


def _assert_can_review(
    db: Session,
    report: ExpenseReports,
    employee: Employees,
    user_permissions: dict,
    action: str,
) -> None:
    """Reject a review attempt with the reason, not a bare 403.

    Separation of duty is invisible to the person it blocks, so each rule says
    exactly why it fired.
    """
    if report.employee_id == employee.employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot review your own expense report",
        )
    if approvals.has_already_decided(db, report, employee.employee_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You already decided one level of this report; the remaining level needs a different approver",
        )
    if not approvals.can_review(db, report, employee, user_permissions):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"This report is not waiting on your role, so you cannot {action} it",
        )


def _touch(report: ExpenseReports) -> None:
    report.updated_at = utcnow()


def _assert_valid_date_range(start: date | None, end: date | None, label: str) -> None:
    if start is not None and end is not None and start > end:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"{label} start date must be on or before its end date",
        )


# --- Categories -------------------------------------------------------------


@router.get("/categories", response_model=list[ExpenseCategory])
def list_categories(
    include_inactive: bool = Query(default=False),
    db: Session = Depends(get_db),
    _perm=Depends(require_module_permission(MODULE_KEY, "can_view")),
):
    query = select(ExpenseCategories)
    if not include_inactive:
        query = query.where(ExpenseCategories.is_active == True)  # noqa: E712
    rows = db.exec(query).all()
    rows.sort(key=lambda row: (row.display_order, row.name))
    return [ExpenseCategory(**row.model_dump()) for row in rows]


@router.post("/categories", response_model=ExpenseCategory)
def create_category(
    payload: ExpenseCategoryCreate,
    db: Session = Depends(get_db),
    _perm=Depends(require_module_permission(MODULE_KEY, "admin_actions")),
):
    category = ExpenseCategories(**payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return ExpenseCategory(**category.model_dump())


@router.patch("/categories/{category_id}", response_model=ExpenseCategory)
def update_category(
    category_id: int,
    payload: ExpenseCategoryUpdate,
    db: Session = Depends(get_db),
    _perm=Depends(require_module_permission(MODULE_KEY, "admin_actions")),
):
    category = db.get(ExpenseCategories, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(category, field, value)

    db.add(category)
    db.commit()
    db.refresh(category)
    return ExpenseCategory(**category.model_dump())


# --- Approval rules ---------------------------------------------------------


@router.get("/approval-rules", response_model=list[ExpenseApprovalRule])
def list_approval_rules(
    db: Session = Depends(get_db),
    _perm=Depends(require_module_permission(MODULE_KEY, "admin_actions")),
):
    rows = db.exec(select(ExpenseApprovalRules)).all()
    rows.sort(key=lambda row: (row.min_amount, row.level))
    return [
        ExpenseApprovalRule(**row.model_dump(), role_name=approvals.role_name(db, row.role_id))
        for row in rows
    ]


@router.post("/approval-rules", response_model=ExpenseApprovalRule)
def create_approval_rule(
    payload: ExpenseApprovalRuleCreate,
    db: Session = Depends(get_db),
    _perm=Depends(require_module_permission(MODULE_KEY, "admin_actions")),
):
    rule = ExpenseApprovalRules(**payload.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return ExpenseApprovalRule(**rule.model_dump(), role_name=approvals.role_name(db, rule.role_id))


@router.patch("/approval-rules/{rule_id}", response_model=ExpenseApprovalRule)
def update_approval_rule(
    rule_id: int,
    payload: ExpenseApprovalRuleUpdate,
    db: Session = Depends(get_db),
    _perm=Depends(require_module_permission(MODULE_KEY, "admin_actions")),
):
    rule = db.get(ExpenseApprovalRules, rule_id)
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval rule not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(rule, field, value)

    db.add(rule)
    db.commit()
    db.refresh(rule)
    return ExpenseApprovalRule(**rule.model_dump(), role_name=approvals.role_name(db, rule.role_id))


@router.delete("/approval-rules/{rule_id}")
def delete_approval_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    _perm=Depends(require_module_permission(MODULE_KEY, "admin_actions")),
):
    rule = db.get(ExpenseApprovalRules, rule_id)
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval rule not found")
    db.delete(rule)
    db.commit()
    return {"success": True, "message": "Approval rule deleted"}


# --- Reports ----------------------------------------------------------------


@router.get("/reports", response_model=PaginatedResponse[ExpenseReport])
def list_reports(
    employee_id: int | None = Query(default=None),
    job_id: int | None = Query(default=None),
    report_status: str | None = Query(default=None, alias="status"),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    search: str | None = Query(default=None),
    mine_only: bool = Query(default=False),
    pending_for_me: bool = Query(default=False),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=25, ge=1, le=200),
    db: Session = Depends(get_db),
    current_employee: Employees = Depends(get_current_employee),
    user_permissions: dict = Depends(require_module_permission(MODULE_KEY, "can_view")),
):
    _assert_valid_date_range(date_from, date_to, "Filter")
    query = select(ExpenseReports)

    if mine_only:
        query = query.where(ExpenseReports.employee_id == current_employee.employee_id)
    elif not approvals.has_admin_actions(user_permissions):
        # An approver must see the queue assigned to their role, not just their
        # own claims, or a chain level nobody can see is a chain that stalls.
        reviewable = approvals.reviewable_report_ids(db, current_employee)
        own = ExpenseReports.employee_id == current_employee.employee_id
        query = query.where(
            or_(own, ExpenseReports.report_id.in_(reviewable)) if reviewable else own  # type: ignore[attr-defined]
        )
    elif employee_id:
        query = query.where(ExpenseReports.employee_id == employee_id)

    if job_id:
        query = query.where(ExpenseReports.job_id == job_id)
    if report_status:
        query = query.where(ExpenseReports.status == report_status)
    if date_from:
        query = query.where(ExpenseReports.trip_start_date >= date_from)
    if date_to:
        query = query.where(ExpenseReports.trip_start_date <= date_to)
    if search:
        pattern = f"%{search.strip()}%"
        query = query.where(
            ExpenseReports.folio.like(pattern) | ExpenseReports.title.like(pattern)  # type: ignore[attr-defined]
        )

    rows = db.exec(query).all()

    if pending_for_me:
        rows = [
            row
            for row in rows
            if row.status in {"submitted", "in_review"}
            and approvals.can_review(db, row, current_employee, user_permissions)
        ]

    rows.sort(key=lambda row: (row.created_at or utcnow()), reverse=True)
    total = len(rows)
    page = rows[skip : skip + limit]

    employees = _employee_lookup(db, [row.employee_id for row in page])
    jobs = _job_lookup(db, [row.job_id for row in page])
    report_ids = [row.report_id for row in page]

    receipt_counts: dict[int, int] = {}
    flag_counts: dict[int, int] = {}
    if report_ids:
        for report_id, count in db.exec(
            select(ExpenseReceipts.report_id, func.count(ExpenseReceipts.receipt_id))
            .where(ExpenseReceipts.report_id.in_(report_ids))  # type: ignore[attr-defined]
            .group_by(ExpenseReceipts.report_id)
        ).all():
            receipt_counts[report_id] = count
        for report_id, count in db.exec(
            select(ExpenseReportFlags.report_id, func.count(ExpenseReportFlags.flag_id))
            .where(ExpenseReportFlags.report_id.in_(report_ids))  # type: ignore[attr-defined]
            .group_by(ExpenseReportFlags.report_id)
        ).all():
            flag_counts[report_id] = count

    items = [
        _report_to_schema(
            row,
            employees.get(row.employee_id),
            jobs.get(row.job_id) if row.job_id else None,
            receipt_counts.get(row.report_id, 0),
            flag_counts.get(row.report_id, 0),
        )
        for row in page
    ]

    return PaginatedResponse[ExpenseReport](
        items=items,
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + limit < total,
    )


@router.get("/reports/{report_id}", response_model=ExpenseReportDetail)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_employee: Employees = Depends(get_current_employee),
    user_permissions: dict = Depends(require_module_permission(MODULE_KEY, "can_view")),
):
    report = _get_report_or_404(db, report_id)

    # An approver in the chain must be able to open it even if it is not theirs.
    if report.employee_id != current_employee.employee_id and not approvals.has_admin_actions(user_permissions):
        if not approvals.can_review(db, report, current_employee, user_permissions):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to view this report")

    employee = db.get(Employees, report.employee_id)
    job = db.get(Jobs, report.job_id) if report.job_id else None

    items = db.exec(select(ExpenseReportItems).where(ExpenseReportItems.report_id == report_id)).all()
    receipts = db.exec(select(ExpenseReceipts).where(ExpenseReceipts.report_id == report_id)).all()
    flags = db.exec(select(ExpenseReportFlags).where(ExpenseReportFlags.report_id == report_id)).all()
    chain = db.exec(select(ExpenseReportApprovals).where(ExpenseReportApprovals.report_id == report_id)).all()
    reimbursement = db.exec(
        select(ExpenseReimbursements).where(ExpenseReimbursements.report_id == report_id)
    ).first()

    categories = {row.category_id: row.name for row in db.exec(select(ExpenseCategories)).all()}
    receipts_per_item: dict[int, int] = {}
    for receipt in receipts:
        if receipt.item_id:
            receipts_per_item[receipt.item_id] = receipts_per_item.get(receipt.item_id, 0) + 1

    base = _report_to_schema(report, employee, job, len(receipts), len(flags))

    detail = ExpenseReportDetail(**base.model_dump())
    detail.items = [
        _item_to_schema(item, categories.get(item.category_id), receipts_per_item.get(item.item_id, 0))
        for item in sorted(items, key=lambda row: (row.expense_date or date.min, row.item_id or 0))
    ]
    # Carry the reading status: it is how the capture form knows which receipts
    # already have a total waiting and have not become an expense line yet.
    extraction_statuses = {
        row.receipt_id: row.status
        for row in db.exec(
            select(ExpenseReceiptExtractions).where(
                ExpenseReceiptExtractions.receipt_id.in_([r.receipt_id for r in receipts] or [0])  # type: ignore[attr-defined]
            )
        ).all()
    }
    detail.receipts = [
        ExpenseReceipt(
            **receipt.model_dump(),
            extraction_status=extraction_statuses.get(receipt.receipt_id),
        )
        for receipt in receipts
    ]
    detail.flags = [ExpenseFlag(**flag.model_dump()) for flag in flags]
    detail.approvals = sorted(
        [_approval_to_schema(db, approval) for approval in chain], key=lambda row: row.level
    )
    if reimbursement:
        paid_by = db.get(Employees, reimbursement.paid_by) if reimbursement.paid_by else None
        detail.reimbursement = ExpenseReimbursement(
            **reimbursement.model_dump(),
            paid_by_name=(paid_by.display_name if paid_by else None),
        )

    # Resolve the viewer's capabilities here: separation of duty is a server
    # rule, and the UI must not carry a second, drifting copy of it.
    pending = approvals.current_step(db, report)
    detail.pending_level = pending.level if pending else None
    detail.pending_role_name = approvals.role_name(db, pending.role_id) if pending else None
    detail.can_review = report.status in {"submitted", "in_review"} and approvals.can_review(
        db, report, current_employee, user_permissions
    )
    detail.can_reimburse = report.status in {"approved", "partially_approved"} and approvals.has_admin_actions(
        user_permissions
    )

    return detail


@router.post("/reports", response_model=ExpenseReport)
def create_report(
    payload: ExpenseReportCreate,
    db: Session = Depends(get_db),
    current_employee: Employees = Depends(get_current_employee),
    user_permissions: dict = Depends(require_module_permission(MODULE_KEY, "can_create")),
):
    _assert_valid_date_range(payload.trip_start_date, payload.trip_end_date, "Trip")
    # Filing on behalf of someone else is an admin action.
    employee_id = current_employee.employee_id
    if payload.employee_id and payload.employee_id != current_employee.employee_id:
        if not approvals.has_admin_actions(user_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only an administrator can file a report on behalf of another employee",
            )
        employee_id = payload.employee_id

    data = payload.model_dump(exclude={"employee_id"})
    report = ExpenseReports(**data, employee_id=employee_id, folio=next_folio(db))

    db.add(report)
    db.commit()
    db.refresh(report)

    employee = db.get(Employees, report.employee_id)
    job = db.get(Jobs, report.job_id) if report.job_id else None
    return _report_to_schema(report, employee, job)


@router.patch("/reports/{report_id}", response_model=ExpenseReport)
def update_report(
    report_id: int,
    payload: ExpenseReportUpdate,
    db: Session = Depends(get_db),
    current_employee: Employees = Depends(get_current_employee),
    user_permissions: dict = Depends(require_module_permission(MODULE_KEY, "can_edit")),
):
    report = _get_report_or_404(db, report_id)
    _assert_owner_or_admin(report, current_employee, user_permissions)
    _assert_editable(report)

    changes = payload.model_dump(exclude_unset=True)
    _assert_valid_date_range(
        changes.get("trip_start_date", report.trip_start_date),
        changes.get("trip_end_date", report.trip_end_date),
        "Trip",
    )

    for field, value in changes.items():
        setattr(report, field, value)
    _touch(report)

    db.add(report)
    db.commit()
    db.refresh(report)

    employee = db.get(Employees, report.employee_id)
    job = db.get(Jobs, report.job_id) if report.job_id else None
    return _report_to_schema(report, employee, job)


@router.delete("/reports/{report_id}")
def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_employee: Employees = Depends(get_current_employee),
    user_permissions: dict = Depends(require_module_permission(MODULE_KEY, "can_delete")),
):
    report = _get_report_or_404(db, report_id)
    _assert_owner_or_admin(report, current_employee, user_permissions)

    if report.status != "draft":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only a draft report can be deleted")

    receipts = db.exec(select(ExpenseReceipts).where(ExpenseReceipts.report_id == report_id)).all()
    stored_files = [receipt.file_path for receipt in receipts if receipt.file_path]

    # Extractions reference receipts, and both flags and receipts reference items,
    # so each level has to be gone before the one it points at. Flushing between
    # levels keeps that order instead of leaving it to the unit of work.
    for extraction in db.exec(
        select(ExpenseReceiptExtractions).where(
            ExpenseReceiptExtractions.receipt_id.in_([r.receipt_id for r in receipts] or [0])  # type: ignore[attr-defined]
        )
    ).all():
        db.delete(extraction)
    db.flush()

    for receipt in receipts:
        db.delete(receipt)
    db.flush()

    for model in (
        ExpenseReportFlags,
        ExpenseReportApprovals,
        ExpenseReportMessages,
        ExpenseReportItems,
    ):
        for row in db.exec(select(model).where(model.report_id == report_id)).all():
            db.delete(row)
        db.flush()

    db.delete(report)
    db.commit()

    # Same convention as single-receipt deletion: never keep the metadata when the
    # file is gone, but make a storage cleanup failure visible instead of silent.
    for file_path in stored_files:
        stored = Path(file_path)
        if stored.exists():
            try:
                stored.unlink()
            except OSError as exc:
                logger.warning("[EXPENSES] Could not remove %s: %s", stored, exc)

    return {"success": True, "message": "Expense report deleted"}


# --- Items ------------------------------------------------------------------


@router.post("/reports/{report_id}/items", response_model=ExpenseItem)
def create_item(
    report_id: int,
    payload: ExpenseItemCreate,
    db: Session = Depends(get_db),
    current_employee: Employees = Depends(get_current_employee),
    user_permissions: dict = Depends(require_module_permission(MODULE_KEY, "can_create")),
):
    report = _get_report_or_404(db, report_id)
    _assert_owner_or_admin(report, current_employee, user_permissions)
    _assert_editable(report)

    data = payload.model_dump(exclude={"receipt_id"})
    item = ExpenseReportItems(**data, report_id=report_id)
    _settle_amount(item)

    db.add(item)
    db.commit()
    db.refresh(item)

    # Bind the receipt that produced this line, when the client uploaded one first.
    if payload.receipt_id:
        receipt = db.get(ExpenseReceipts, payload.receipt_id)
        if receipt and receipt.report_id == report_id:
            receipt.item_id = item.item_id
            db.add(receipt)

    approvals.recalculate_totals(db, report)
    _touch(report)
    db.add(report)
    db.commit()
    db.refresh(item)

    categories = {row.category_id: row.name for row in db.exec(select(ExpenseCategories)).all()}
    return _item_to_schema(item, categories.get(item.category_id))


@router.patch("/items/{item_id}", response_model=ExpenseItem)
def update_item(
    item_id: int,
    payload: ExpenseItemUpdate,
    db: Session = Depends(get_db),
    current_employee: Employees = Depends(get_current_employee),
    user_permissions: dict = Depends(require_module_permission(MODULE_KEY, "can_edit")),
):
    item = db.get(ExpenseReportItems, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense line not found")

    report = _get_report_or_404(db, item.report_id)
    _assert_owner_or_admin(report, current_employee, user_permissions)
    _assert_editable(report)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)

    _settle_amount(item)
    item.updated_at = utcnow()

    db.add(item)
    db.commit()

    approvals.recalculate_totals(db, report)
    _touch(report)
    db.add(report)
    db.commit()
    db.refresh(item)

    categories = {row.category_id: row.name for row in db.exec(select(ExpenseCategories)).all()}
    return _item_to_schema(item, categories.get(item.category_id))


@router.delete("/items/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_employee: Employees = Depends(get_current_employee),
    user_permissions: dict = Depends(require_module_permission(MODULE_KEY, "can_delete")),
):
    item = db.get(ExpenseReportItems, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense line not found")

    report = _get_report_or_404(db, item.report_id)
    _assert_owner_or_admin(report, current_employee, user_permissions)
    _assert_editable(report)

    # Flags can reference this item. Remove the complete derived set before the
    # line so the item FK cannot block deletion; the policy engine rebuilds it.
    for flag in db.exec(select(ExpenseReportFlags).where(ExpenseReportFlags.report_id == report.report_id)).all():
        db.delete(flag)

    for receipt in db.exec(select(ExpenseReceipts).where(ExpenseReceipts.item_id == item_id)).all():
        receipt.item_id = None
        db.add(receipt)

    db.delete(item)
    db.commit()

    approvals.recalculate_totals(db, report)
    _touch(report)
    db.add(report)
    db.commit()
    policies.replace_flags(db, report)
    return {"success": True, "message": "Expense line deleted"}


# --- Workflow ---------------------------------------------------------------


@router.post("/reports/{report_id}/submit", response_model=ExpenseReportDetail)
def submit_report(
    report_id: int,
    http_request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_employee: Employees = Depends(get_current_employee),
    user_permissions: dict = Depends(require_module_permission(MODULE_KEY, "can_create")),
):
    report = _get_report_or_404(db, report_id)
    _assert_owner_or_admin(report, current_employee, user_permissions)
    _assert_editable(report)

    items = db.exec(select(ExpenseReportItems).where(ExpenseReportItems.report_id == report_id)).all()
    if not items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Add at least one expense line first")

    approvals.recalculate_totals(db, report)

    chain = approvals.build_chain(db, report)
    report.status = "submitted"
    report.current_level = min(step.level for step in chain)
    report.submitted_at = utcnow()
    _touch(report)

    db.add(report)
    db.commit()
    db.refresh(report)

    policies.replace_flags(db, report)

    app_url = get_request_app_url(http_request)
    employee = db.get(Employees, report.employee_id)
    job = db.get(Jobs, report.job_id) if report.job_id else None
    first_step = approvals.current_step(db, report)

    if first_step:
        for _name, email in approvals.approver_emails(db, first_step.role_id):
            background_tasks.add_task(
                notify_expense_submitted,
                report_id=report.report_id,
                folio=report.folio,
                employee_name=(employee.display_name if employee else "An employee"),
                total=float(report.total_requested),
                currency=BASE_CURRENCY,
                to_email=email,
                destination=report.destination,
                job_name=(job.title if job else report.project),
                level=first_step.level,
                app_url=app_url,
            )

    return get_report(report_id, db, current_employee, user_permissions)


@router.post("/reports/{report_id}/recall", response_model=ExpenseReportDetail)
def recall_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_employee: Employees = Depends(get_current_employee),
    user_permissions: dict = Depends(require_module_permission(MODULE_KEY, "can_create")),
):
    """Pull a sent report back to draft so its owner can fix it.

    Allowed only while the chain is untouched. Once an approver has decided a
    level, that decision is a record: recalling would let the employee change
    amounts after somebody signed off, and the signature would still be there.
    From that point the way back is a rejection, which is itself recorded.
    """
    report = _get_report_or_404(db, report_id)
    _assert_owner_or_admin(report, current_employee, user_permissions)

    if report.status not in {"submitted", "in_review"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A report in status '{report.status}' cannot be pulled back to draft",
        )

    chain = db.exec(
        select(ExpenseReportApprovals).where(ExpenseReportApprovals.report_id == report_id)
    ).all()
    decided = [step for step in chain if step.decision != "pending"]
    if decided:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "This report has already been reviewed at one level, so it can no longer be "
                "pulled back. Ask an approver to reject it if it needs changes."
            ),
        )

    # The chain is rebuilt from scratch on the next submit, and the amount may
    # change in between, so keeping these rows would pin an outdated band.
    for step in chain:
        db.delete(step)

    report.status = "draft"
    report.current_level = 0
    report.submitted_at = None
    _touch(report)

    db.add(report)
    db.commit()
    db.refresh(report)

    policies.replace_flags(db, report)

    return get_report(report_id, db, current_employee, user_permissions)


@router.post("/reports/{report_id}/approve", response_model=ExpenseReportDetail)
def approve_report(
    report_id: int,
    review: ExpenseReview,
    http_request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_employee: Employees = Depends(get_current_employee),
    user_permissions: dict = Depends(require_module_permission(MODULE_KEY, "can_view")),
):
    report = _get_report_or_404(db, report_id)

    if report.status not in {"submitted", "in_review"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A report in status '{report.status}' cannot be approved",
        )
    _assert_can_review(db, report, current_employee, user_permissions, "approve")

    items = {item.item_id: item for item in db.exec(
        select(ExpenseReportItems).where(ExpenseReportItems.report_id == report_id)
    ).all()}

    decided_ids = {decision.item_id for decision in review.item_decisions}
    reduced_or_rejected = False

    for decision in review.item_decisions:
        item = items.get(decision.item_id)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Expense line {decision.item_id} does not belong to this report",
            )

        if decision.decision == "rejected":
            if not (decision.note or review.note):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"A reason is required to reject expense line {decision.item_id}",
                )
            item.status = "rejected"
            item.approved_amount = Decimal(0)
            reduced_or_rejected = True
        else:
            item.status = "approved"
            approved = decision.approved_amount if decision.approved_amount is not None else item.amount_base
            if approved > item.amount_base:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Approved amount cannot exceed the claimed amount on line {decision.item_id}",
                )
            if approved < item.amount_base:
                if not (decision.note or review.note):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"A reason is required to reduce expense line {decision.item_id}",
                    )
                reduced_or_rejected = True
            item.approved_amount = approved

        item.review_note = decision.note or item.review_note
        item.updated_at = utcnow()
        db.add(item)

    # Lines the approver did not touch are approved in full.
    for item_id, item in items.items():
        if item_id in decided_ids:
            continue
        item.status = "approved"
        item.approved_amount = item.amount_base
        db.add(item)

    step = approvals.current_step(db, report)
    if step is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This report has no pending approval step")

    approvals.recalculate_totals(db, report)

    step.decision = "partially_approved" if reduced_or_rejected else "approved"
    step.approver_id = current_employee.employee_id
    step.amount_approved = report.total_approved
    step.note = review.note
    step.decided_at = utcnow()
    db.add(step)
    db.commit()

    upcoming = approvals.next_level(db, report, step.level)
    app_url = get_request_app_url(http_request)
    employee = db.get(Employees, report.employee_id)
    job = db.get(Jobs, report.job_id) if report.job_id else None

    if upcoming is not None:
        report.status = "in_review"
        report.current_level = upcoming
        next_step = approvals.current_step(db, report)
        if next_step:
            for _name, email in approvals.approver_emails(db, next_step.role_id):
                background_tasks.add_task(
                    notify_expense_submitted,
                    report_id=report.report_id,
                    folio=report.folio,
                    employee_name=(employee.display_name if employee else "An employee"),
                    total=float(report.total_requested),
                    currency=BASE_CURRENCY,
                    to_email=email,
                    destination=report.destination,
                    job_name=(job.title if job else report.project),
                    level=next_step.level,
                    app_url=app_url,
                )
    else:
        report.status = approvals.settle_status(db, report)
        if employee and employee.email:
            if report.status == "partially_approved":
                rejected = sum(1 for item in items.values() if item.status == "rejected")
                background_tasks.add_task(
                    notify_expense_partially_approved,
                    report_id=report.report_id,
                    folio=report.folio,
                    employee_name=employee.display_name,
                    total_requested=float(report.total_requested),
                    total_approved=float(report.total_approved),
                        currency=BASE_CURRENCY,
                    to_email=employee.email,
                    reviewed_by_name=current_employee.display_name,
                    reviewed_by_email=current_employee.email,
                    note=review.note,
                    rejected_lines=rejected,
                    app_url=app_url,
                )
            else:
                background_tasks.add_task(
                    notify_expense_approved,
                    report_id=report.report_id,
                    folio=report.folio,
                    employee_name=employee.display_name,
                    total_approved=float(report.total_approved),
                    currency=BASE_CURRENCY,
                    to_email=employee.email,
                    reviewed_by_name=current_employee.display_name,
                    reviewed_by_email=current_employee.email,
                    note=review.note,
                    app_url=app_url,
                )

    _touch(report)
    db.add(report)
    db.commit()

    policies.replace_flags(db, report)

    return get_report(report_id, db, current_employee, user_permissions)


@router.post("/reports/{report_id}/reject", response_model=ExpenseReportDetail)
def reject_report(
    report_id: int,
    review: ExpenseReview,
    http_request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_employee: Employees = Depends(get_current_employee),
    user_permissions: dict = Depends(require_module_permission(MODULE_KEY, "can_view")),
):
    report = _get_report_or_404(db, report_id)

    if report.status not in {"submitted", "in_review"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A report in status '{report.status}' cannot be rejected",
        )
    _assert_can_review(db, report, current_employee, user_permissions, "reject")
    if not (review.note or "").strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A reason is required to reject a report")

    step = approvals.current_step(db, report)
    if step is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This report has no pending approval step")

    step.decision = "rejected"
    step.approver_id = current_employee.employee_id
    step.note = review.note
    step.decided_at = utcnow()
    db.add(step)

    # A rejection terminates the chain; later levels never get a turn.
    for pending in db.exec(
        select(ExpenseReportApprovals)
        .where(ExpenseReportApprovals.report_id == report_id)
        .where(ExpenseReportApprovals.decision == "pending")
    ).all():
        if pending.approval_id != step.approval_id:
            db.delete(pending)

    report.status = "rejected"
    report.total_approved = Decimal(0)
    _touch(report)
    db.add(report)
    db.commit()

    employee = db.get(Employees, report.employee_id)
    if employee and employee.email:
        background_tasks.add_task(
            notify_expense_rejected,
            report_id=report.report_id,
            folio=report.folio,
            employee_name=employee.display_name,
            total=float(report.total_requested),
            currency=BASE_CURRENCY,
            to_email=employee.email,
            reviewed_by_name=current_employee.display_name,
            reviewed_by_email=current_employee.email,
            note=review.note,
            app_url=get_request_app_url(http_request),
        )

    return get_report(report_id, db, current_employee, user_permissions)


@router.post("/reports/{report_id}/reimburse", response_model=ExpenseReportDetail)
def reimburse_report(
    report_id: int,
    payload: ExpenseReimbursementCreate,
    http_request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_employee: Employees = Depends(get_current_employee),
    user_permissions: dict = Depends(require_module_permission(MODULE_KEY, "admin_actions")),
):
    report = _get_report_or_404(db, report_id)

    if report.status not in {"approved", "partially_approved"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only an approved report can be reimbursed",
        )
    if payload.amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reimbursement amount must be positive")
    if payload.amount > report.total_approved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Reimbursement cannot exceed the approved total of {report.total_approved}",
        )

    reimbursement = ExpenseReimbursements(
        report_id=report_id,
        amount=payload.amount,
        currency=BASE_CURRENCY,
        payment_method=payload.payment_method,
        reference=payload.reference,
        note=payload.note,
        paid_by=current_employee.employee_id,
    )
    db.add(reimbursement)

    report.total_reimbursed = payload.amount
    report.status = "paid"
    _touch(report)
    db.add(report)
    db.commit()

    employee = db.get(Employees, report.employee_id)
    if employee and employee.email:
        background_tasks.add_task(
            notify_expense_paid,
            report_id=report.report_id,
            folio=report.folio,
            amount=float(payload.amount),
            currency=BASE_CURRENCY,
            to_email=employee.email,
            payment_method=payload.payment_method,
            reference=payload.reference,
            paid_by_name=current_employee.display_name,
            paid_by_email=current_employee.email,
            app_url=get_request_app_url(http_request),
        )

    return get_report(report_id, db, current_employee, user_permissions)


# --- Stats ------------------------------------------------------------------


@router.get("/dashboard/stats", response_model=ExpenseStats)
def dashboard_stats(
    db: Session = Depends(get_db),
    current_employee: Employees = Depends(get_current_employee),
    user_permissions: dict = Depends(require_module_permission(MODULE_KEY, "can_view")),
):
    """The four cards at the top of the list screen."""
    query = select(ExpenseReports)
    if not approvals.has_admin_actions(user_permissions):
        query = query.where(ExpenseReports.employee_id == current_employee.employee_id)

    rows = db.exec(query).all()
    now = utcnow()

    stats = ExpenseStats()
    for row in rows:
        if row.status in {"submitted", "in_review"}:
            stats.pending_count += 1
            stats.pending_amount += row.total_requested
        elif row.status in {"approved", "partially_approved"}:
            stats.approved_count += 1
            stats.approved_amount += row.total_approved

        if row.status == "paid" and row.updated_at and row.updated_at.year == now.year:
            if row.updated_at.month == now.month:
                stats.reimbursed_month_count += 1
                stats.reimbursed_month_amount += row.total_reimbursed

        if row.created_at and row.created_at.year == now.year:
            stats.requested_year_amount += row.total_requested

    return stats
