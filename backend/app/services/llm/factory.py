from app.core.config import get_settings
from app.services.llm.base import LLMProvider
from app.services.llm.local_grounded_provider import LocalGroundedLLMProvider


def get_llm_provider() -> LLMProvider:
    settings = get_settings()
    provider_name = settings.llm_provider.strip().lower()
    if provider_name == "local_grounded":
        return LocalGroundedLLMProvider()
    raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
