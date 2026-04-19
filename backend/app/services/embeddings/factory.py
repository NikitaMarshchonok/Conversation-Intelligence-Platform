from app.core.config import get_settings
from app.services.embeddings.base import EmbeddingProvider
from app.services.embeddings.local_provider import LocalDeterministicEmbeddingProvider


def get_embedding_provider() -> EmbeddingProvider:
    settings = get_settings()
    return LocalDeterministicEmbeddingProvider(vector_size=settings.embedding_vector_size)
