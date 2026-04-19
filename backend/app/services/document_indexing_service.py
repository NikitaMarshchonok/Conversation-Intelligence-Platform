from datetime import datetime, timezone
from uuid import UUID

from qdrant_client.http import models as qdrant_models
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.embeddings.factory import get_embedding_provider
from app.services.vector_store.qdrant_service import QdrantVectorStore


class DocumentIndexingService:
    @staticmethod
    def index_document(db: Session, document_id: UUID) -> Document:
        return DocumentIndexingService._run_indexing(db, document_id=document_id, reindex=False)

    @staticmethod
    def reindex_document(db: Session, document_id: UUID) -> Document:
        return DocumentIndexingService._run_indexing(db, document_id=document_id, reindex=True)

    @staticmethod
    def _run_indexing(db: Session, document_id: UUID, reindex: bool) -> Document:
        _ = reindex
        document = db.get(Document, document_id)
        if document is None:
            raise ValueError("Document not found")

        if document.status != "processed":
            raise ValueError("Document must be processed before indexing")

        stmt = select(DocumentChunk).where(DocumentChunk.document_id == document_id).order_by(DocumentChunk.chunk_index.asc())
        chunks = list(db.scalars(stmt).all())
        if not chunks:
            raise ValueError("Document has no chunks to index")

        try:
            embedding_provider = get_embedding_provider()
            vector_store = QdrantVectorStore()
            vector_store.ensure_collection()

            # Always clear existing vectors for this document before upsert to avoid duplicates.
            vector_store.delete_document_vectors(document_id=str(document.id))

            embeddings = embedding_provider.embed_texts([chunk.content for chunk in chunks])

            points = []
            for chunk, vector in zip(chunks, embeddings, strict=True):
                points.append(
                    qdrant_models.PointStruct(
                        id=str(chunk.id),
                        vector=vector,
                        payload={
                            "document_id": str(document.id),
                            "project_id": str(document.project_id),
                            "chunk_id": str(chunk.id),
                            "chunk_index": chunk.chunk_index,
                        },
                    )
                )

            vector_store.upsert_chunk_vectors(points)

            document.is_indexed = True
            document.indexed_at = datetime.now(timezone.utc)
            document.indexing_error = None
            db.commit()
            db.refresh(document)
            return document
        except Exception as exc:  # noqa: BLE001 - capture indexing failures in document metadata
            document.is_indexed = False
            document.indexed_at = None
            document.indexing_error = str(exc)[:2000]
            db.commit()
            db.refresh(document)
            return document
