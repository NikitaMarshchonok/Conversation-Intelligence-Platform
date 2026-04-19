from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk
from app.schemas.search import SearchRequest, SearchResponse, SearchResultItem
from app.services.embeddings.factory import get_embedding_provider
from app.services.vector_store.qdrant_service import QdrantVectorStore


class SearchService:
    @staticmethod
    def search(db: Session, payload: SearchRequest) -> SearchResponse:
        query = payload.query.strip()
        if not query:
            raise ValueError("Query must not be empty")

        embedding_provider = get_embedding_provider()
        query_vector = embedding_provider.embed_texts([query])[0]

        vector_store = QdrantVectorStore()
        vector_store.ensure_collection()
        scored_points = vector_store.search(
            query_vector=query_vector,
            top_k=payload.top_k,
            project_id=str(payload.project_id),
            document_ids=[str(document_id) for document_id in payload.document_ids] if payload.document_ids else None,
        )

        chunk_ids: list[UUID] = []
        for point in scored_points:
            point_chunk_id = (point.payload or {}).get("chunk_id")
            if isinstance(point_chunk_id, str):
                chunk_ids.append(UUID(point_chunk_id))

        chunk_map: dict[UUID, DocumentChunk] = {}
        if chunk_ids:
            stmt = select(DocumentChunk).where(DocumentChunk.id.in_(chunk_ids))
            db_chunks = list(db.scalars(stmt).all())
            chunk_map = {chunk.id: chunk for chunk in db_chunks}

        results: list[SearchResultItem] = []
        for point in scored_points:
            point_payload = point.payload or {}
            chunk_id_value = point_payload.get("chunk_id")
            document_id_value = point_payload.get("document_id")
            chunk_index_value = point_payload.get("chunk_index")
            if not isinstance(chunk_id_value, str):
                continue
            if not isinstance(document_id_value, str):
                continue
            if not isinstance(chunk_index_value, int):
                continue

            chunk_id = UUID(chunk_id_value)
            db_chunk = chunk_map.get(chunk_id)
            if db_chunk is None:
                continue

            results.append(
                SearchResultItem(
                    document_id=UUID(document_id_value),
                    chunk_id=chunk_id,
                    chunk_index=chunk_index_value,
                    score=float(point.score),
                    content=db_chunk.content,
                )
            )

        return SearchResponse(
            query=payload.query,
            top_k=payload.top_k,
            total_results=len(results),
            results=results,
        )
