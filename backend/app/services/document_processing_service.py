from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk

SUPPORTED_EXTENSIONS = {
    ".txt",
    ".md",
    ".csv",
    ".json",
    ".log",
    ".yaml",
    ".yml",
    ".html",
}

CHUNK_SIZE_CHARS = 1200
CHUNK_OVERLAP_CHARS = 200


class DocumentProcessingService:
    @staticmethod
    def list_document_chunks(db: Session, document_id: UUID) -> list[DocumentChunk]:
        stmt = select(DocumentChunk).where(DocumentChunk.document_id == document_id).order_by(DocumentChunk.chunk_index.asc())
        return list(db.scalars(stmt).all())

    @staticmethod
    def process_document(db: Session, document_id: UUID) -> Document:
        document = db.get(Document, document_id)
        if document is None:
            raise ValueError("Document not found")

        try:
            text_content = DocumentProcessingService._load_text_content(document)
            chunks = DocumentProcessingService._split_into_chunks(text_content)

            db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document.id))

            for index, chunk in enumerate(chunks):
                db.add(
                    DocumentChunk(
                        document_id=document.id,
                        chunk_index=index,
                        content=chunk["content"],
                        char_start=chunk["char_start"],
                        char_end=chunk["char_end"],
                        token_estimate=chunk["token_estimate"],
                    )
                )

            document.status = "processed"
            document.chunk_count = len(chunks)
            document.processed_at = datetime.now(timezone.utc)
            document.processing_error = None
            document.is_indexed = False
            document.indexed_at = None
            document.indexing_error = None
            db.commit()
            db.refresh(document)
            return document
        except Exception as exc:  # noqa: BLE001 - status tracking for failed processing
            document.status = "failed"
            document.processing_error = str(exc)[:2000]
            document.processed_at = None
            document.chunk_count = 0
            document.is_indexed = False
            document.indexed_at = None
            document.indexing_error = None
            db.commit()
            db.refresh(document)
            return document

    @staticmethod
    def _load_text_content(document: Document) -> str:
        extension = Path(document.original_name).suffix.lower()
        if extension not in SUPPORTED_EXTENSIONS:
            raise ValueError("Unsupported file type for processing")

        source_path = Path(document.storage_path)
        if not source_path.exists():
            raise FileNotFoundError("Stored file not found on disk")

        raw_content = source_path.read_text(encoding="utf-8")
        normalized = raw_content.strip()
        if not normalized:
            raise ValueError("Document file is empty")

        return normalized

    @staticmethod
    def _split_into_chunks(text_content: str) -> list[dict[str, int | str]]:
        chunks: list[dict[str, int | str]] = []
        start = 0
        text_length = len(text_content)

        while start < text_length:
            end = min(start + CHUNK_SIZE_CHARS, text_length)
            content = text_content[start:end]
            if not content:
                break

            chunks.append(
                {
                    "content": content,
                    "char_start": start,
                    "char_end": end,
                    "token_estimate": max(1, len(content) // 4),
                }
            )

            if end == text_length:
                break
            start = max(end - CHUNK_OVERLAP_CHARS, start + 1)

        return chunks
