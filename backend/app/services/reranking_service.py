from app.schemas.search import SearchResultItem
from app.services.reranking.factory import get_reranker_provider


class RerankingService:
    @staticmethod
    def rerank(query: str, candidates: list[SearchResultItem]) -> list[SearchResultItem]:
        if not candidates:
            return []
        reranker = get_reranker_provider()
        return reranker.rerank(query=query, candidates=candidates)
