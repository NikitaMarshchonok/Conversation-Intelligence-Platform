from qdrant_client import QdrantClient
from qdrant_client.http import models

from app.core.config import get_settings


class QdrantVectorStore:
    def __init__(self) -> None:
        settings = get_settings()
        self.collection_name = settings.qdrant_collection_name
        self.vector_size = settings.embedding_vector_size
        self.client = QdrantClient(url=settings.qdrant_url)

    def ensure_collection(self) -> None:
        if self.client.collection_exists(collection_name=self.collection_name):
            return
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(size=self.vector_size, distance=models.Distance.COSINE),
        )

    def delete_document_vectors(self, document_id: str) -> None:
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="document_id",
                            match=models.MatchValue(value=document_id),
                        )
                    ]
                )
            ),
        )

    def upsert_chunk_vectors(self, points: list[models.PointStruct]) -> None:
        if not points:
            return
        self.client.upsert(collection_name=self.collection_name, points=points)
