from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from core.datetime_utils import utcnow

if TYPE_CHECKING:
    from models.employees import Employees


class ProductBulkImports(SQLModel, table=True):
    """Header of one bulk import job.

    The job runs outside the request, so every piece of its state lives here:
    the frontend polls this row instead of holding a connection open.
    """

    __tablename__ = "product_bulk_imports"
    __table_args__ = {"schema": "dbo"}

    id: int | None = Field(default=None, primary_key=True)

    file_name: str = Field(max_length=255)
    stored_path: str = Field(max_length=500)
    # analyzing | awaiting_confirmation | applying | completed | failed | cancelled
    status: str = Field(default="analyzing", max_length=30, index=True)

    # Stamped by the export; absent when the file was built by hand.
    exported_at: datetime | None = Field(default=None)
    export_scope: str | None = Field(default=None, max_length=1000)

    # Analysis results
    total_rows: int = 0
    create_count: int = 0
    update_count: int = 0
    unchanged_count: int = 0
    error_count: int = 0
    conflict_count: int = 0
    unknown_taxonomy: str | None = Field(default=None)

    # Answers given at confirmation time
    create_missing_taxonomy: bool = False
    apply_conflicts: bool = False

    # Apply results
    created_count: int = 0
    updated_count: int = 0
    failed_count: int = 0
    skipped_count: int = 0

    error_report_path: str | None = Field(default=None, max_length=500)
    failure_reason: str | None = Field(default=None, max_length=500)

    created_by: int = Field(foreign_key="dbo.employees.employee_id", index=True)
    created_at: datetime = Field(default_factory=utcnow)
    started_at: datetime | None = Field(default=None)
    finished_at: datetime | None = Field(default=None)
    # Bumped on every batch. A stale heartbeat is how an interrupted job is detected.
    heartbeat_at: datetime | None = Field(default=None)

    creator: Optional["Employees"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "ProductBulkImports.created_by"}
    )


class ProductBulkImportRows(SQLModel, table=True):
    """Per-row outcome of a bulk import.

    Rows resolved as `unchanged` are only counted on the header: they affected
    nothing, and persisting them would bloat the detail for no gain.
    """

    __tablename__ = "product_bulk_import_rows"
    __table_args__ = {"schema": "dbo"}

    id: int | None = Field(default=None, primary_key=True)
    import_id: int = Field(foreign_key="dbo.product_bulk_imports.id", index=True)
    row_number: int
    # create | update | error | skipped
    action: str = Field(max_length=20, index=True)
    product_id: int | None = Field(default=None)
    code: str | None = Field(default=None, max_length=100)
    name: str | None = Field(default=None, max_length=255)
    message: str | None = Field(default=None, max_length=500)
