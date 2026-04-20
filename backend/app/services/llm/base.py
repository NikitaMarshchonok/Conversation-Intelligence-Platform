from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def generate_grounded_answer(self, query: str, prompt: str, contexts: list[str]) -> str:
        raise NotImplementedError
