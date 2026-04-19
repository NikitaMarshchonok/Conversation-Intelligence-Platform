from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.document import DocumentChunkRead, DocumentIndexStatusRead, DocumentRead
from app.services.document_indexing_service import DocumentIndexingService
from app.services.document_processing_service import DocumentProcessingService
from app.services.documents_service import DocumentsService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/{document_id}", response_model=DocumentRead)
def get_document(document_id: UUID, db: Session = Depends(get_db)) -> DocumentRead:
    document = DocumentsService.get_document_by_id(db, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


@router.post("/{document_id}/process", response_model=DocumentRead)
def process_document(document_id: UUID, db: Session = Depends(get_db)) -> DocumentRead:
    document = DocumentsService.get_document_by_id(db, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return DocumentProcessingService.process_document(db, document_id)


@router.get("/{document_id}/chunks", response_model=list[DocumentChunkRead])
def list_document_chunks(document_id: UUID, db: Session = Depends(get_db)) -> list[DocumentChunkRead]:
    document = DocumentsService.get_document_by_id(db, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return DocumentProcessingService.list_document_chunks(db, document_id)


@router.post("/{document_id}/index", response_model=DocumentRead)
def index_document(document_id: UUID, db: Session = Depends(get_db)) -> DocumentRead:
    document = DocumentsService.get_document_by_id(db, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    try:
        return DocumentIndexingService.index_document(db, document_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/{document_id}/reindex", response_model=DocumentRead)
def reindex_document(document_id: UUID, db: Session = Depends(get_db)) -> DocumentRead:
    document = DocumentsService.get_document_by_id(db, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    try:
        return DocumentIndexingService.reindex_document(db, document_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{document_id}/index-status", response_model=DocumentIndexStatusRead)
def get_document_index_status(document_id: UUID, db: Session = Depends(get_db)) -> DocumentIndexStatusRead:
    document = DocumentsService.get_document_by_id(db, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document
