from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResponse:
    text: str
    provider: str
    model: str
    raw: dict | None = None


class LLMProvider(ABC):
    name: str = "base"

    @abstractmethod
    def complete(self, system: str, prompt: str, max_tokens: int = 1000) -> LLMResponse:
        ...


class LLMError(Exception):
    pass
