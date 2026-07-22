from datetime import datetime

from pydantic import BaseModel


class ItQuotationDocumentRead(BaseModel):
    document_id: int
    quotation_id: int
    document_type: str
    file_name: str
    document_version: int
    file_hash: str | None = None
    generated_by: int | None = None
    generated_at: datetime
