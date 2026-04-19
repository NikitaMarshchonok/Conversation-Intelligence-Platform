import math

from app.services.embeddings.base import EmbeddingProvider


class LocalDeterministicEmbeddingProvider(EmbeddingProvider):
    def __init__(self, vector_size: int) -> None:
        self.vector_size = vector_size

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_single_text(text) for text in texts]

    def _embed_single_text(self, text: str) -> list[float]:
        vector = [0.0] * self.vector_size
        encoded = text.encode("utf-8")
        for index, byte_value in enumerate(encoded):
            vector[index % self.vector_size] += byte_value / 255.0

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]
