from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlmodel import Session

from api.dependencies import require_module_permission
from api.it.dependencies import get_tenant_id
from bd.dependencies import get_db
from models.it.documents import ITQuotationDocuments
from models.it.quotations import ITQuotations

router = APIRouter()


def _get_document(db: Session, tenant_id: int, document_id: int) -> ITQuotationDocuments:
    document = db.get(ITQuotationDocuments, document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    quotation = db.get(ITQuotations, document.quotation_id)
    if not quotation or quotation.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


@router.get("/{document_id}/download")
def download_document(
    document_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_documents", "can_view")),
):
    document = _get_document(db, tenant_id, document_id)
    path = Path(document.storage_path)
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found on storage")
    return FileResponse(
        path=path,
        filename=document.file_name,
        media_type="application/pdf",
    )
