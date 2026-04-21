from app.core.config import get_settings
from app.services.reranking.base import RerankerProvider
from app.services.reranking.local_keyword_provider import LocalKeywordRerankerProvider


def get_reranker_provider() -> RerankerProvider:
    settings = get_settings()
    provider_name = settings.reranker_provider.strip().lower()
    if provider_name == "local_keyword":
        return LocalKeywordRerankerProvider()
    raise ValueError(f"Unsupported reranker provider: {settings.reranker_provider}")
