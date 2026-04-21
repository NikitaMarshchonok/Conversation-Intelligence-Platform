from app.schemas.search import SearchResultItem
from app.services.reranking.base import RerankerProvider


class LocalKeywordRerankerProvider(RerankerProvider):
    def rerank(self, query: str, candidates: list[SearchResultItem]) -> list[SearchResultItem]:
        query_terms = [term for term in query.lower().split() if term]
        if not query_terms:
            return candidates

        def rank_score(item: SearchResultItem) -> tuple[float, float]:
            content_lower = item.content.lower()
            keyword_hits = sum(content_lower.count(term) for term in query_terms)
            # Primary: simple lexical overlap; secondary: original vector score.
            return float(keyword_hits), item.score

        return sorted(candidates, key=rank_score, reverse=True)
