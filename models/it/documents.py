from datetime import datetime

from sqlmodel import Field, SQLModel


class ITQuotationDocuments(SQLModel, table=True):
    __tablename__ = "quotation_documents"
    __table_args__ = {"schema": "it"}

    document_id: int | None = Field(default=None, primary_key=True, index=True)
    quotation_id: int = Field(foreign_key="it.quotations.quotation_id", index=True)
    document_type: str = Field(default="PDF", max_length=30)
    file_name: str = Field(max_length=255)
    storage_path: str = Field(max_length=1000)
    document_version: int = Field(default=1)
    file_hash: str | None = Field(default=None, max_length=128)
    generated_by: int | None = Field(default=None, foreign_key="dbo.employees.employee_id")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
