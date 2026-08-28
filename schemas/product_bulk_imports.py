from datetime import datetime

from sqlmodel import SQLModel

from schemas.products import ProductEmployee


class UnknownTaxonomy(SQLModel):
    """A family/category name present in the file but missing in the database."""

    kind: str  # family | category
    name: str
    family: str | None = None  # parent family name, for categories
    row_count: int


class BulkImportRowRead(SQLModel):
    id: int
    row_number: int
    action: str
    product_id: int | None = None
    code: str | None = None
    name: str | None = None
    message: str | None = None


class BulkImportRead(SQLModel):
    id: int
    file_name: str
    status: str
    exported_at: datetime | None = None
    export_scope: str | None = None

    total_rows: int
    create_count: int
    update_count: int
    unchanged_count: int
    error_count: int
    conflict_count: int
    unknown_taxonomy: list[UnknownTaxonomy] = []

    create_missing_taxonomy: bool
    apply_conflicts: bool

    created_count: int
    updated_count: int
    failed_count: int
    skipped_count: int

    has_error_report: bool = False
    failure_reason: str | None = None

    created_by: int
    creator: ProductEmployee | None = None
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None


class BulkImportConfirm(SQLModel):
    create_missing_taxonomy: bool = False
    apply_conflicts: bool = False
