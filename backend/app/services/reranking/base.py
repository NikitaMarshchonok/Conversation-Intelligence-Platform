from abc import ABC, abstractmethod

from app.schemas.search import SearchResultItem


class RerankerProvider(ABC):
    @abstractmethod
    def rerank(self, query: str, candidates: list[SearchResultItem]) -> list[SearchResultItem]:
        raise NotImplementedError
