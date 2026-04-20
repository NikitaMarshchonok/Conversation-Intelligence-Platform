from app.services.llm.base import LLMProvider


class LocalGroundedLLMProvider(LLMProvider):
    def generate_grounded_answer(self, query: str, prompt: str, contexts: list[str]) -> str:
        _ = prompt
        _ = query
        if not contexts:
            return "Insufficient evidence in retrieved context to answer this question."

        # Minimal deterministic baseline until external LLM providers are plugged in.
        top_context = contexts[0].strip()
        if not top_context:
            return "Insufficient evidence in retrieved context to answer this question."
        return f"Based on the retrieved evidence: {top_context[:400]}"
