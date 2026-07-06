from __future__ import annotations

import json

import httpx

from app.core.config import get_settings
from app.llm.base import LLMProvider, LLMResponse, LLMError

settings = get_settings()


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL
        if not self.api_key:
            raise LLMError("OPENAI_API_KEY is not configured")

    def complete(self, system: str, prompt: str, max_tokens: int = 1000) -> LLMResponse:
        try:
            resp = httpx.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "max_tokens": max_tokens,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ],
                },
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            text = data["choices"][0]["message"]["content"]
            return LLMResponse(text=text, provider=self.name, model=self.model, raw=data)
        except httpx.HTTPError as exc:
            raise LLMError(f"OpenAI request failed: {exc}") from exc


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.model = model or settings.ANTHROPIC_MODEL
        if not self.api_key:
            raise LLMError("ANTHROPIC_API_KEY is not configured")

    def complete(self, system: str, prompt: str, max_tokens: int = 1000) -> LLMResponse:
        try:
            resp = httpx.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": self.model,
                    "max_tokens": max_tokens,
                    "system": system,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            text = "".join(block.get("text", "") for block in data.get("content", []))
            return LLMResponse(text=text, provider=self.name, model=self.model, raw=data)
        except httpx.HTTPError as exc:
            raise LLMError(f"Anthropic request failed: {exc}") from exc


class OllamaProvider(LLMProvider):
    name = "ollama"

    def __init__(self, base_url: str | None = None, model: str | None = None):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model = model or settings.OLLAMA_MODEL

    def complete(self, system: str, prompt: str, max_tokens: int = 1000) -> LLMResponse:
        try:
            resp = httpx.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": f"{system}\n\n{prompt}",
                    "stream": False,
                },
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
            return LLMResponse(text=data.get("response", ""), provider=self.name, model=self.model, raw=data)
        except httpx.HTTPError as exc:
            raise LLMError(f"Ollama request failed: {exc}") from exc


class MockProvider(LLMProvider):
    """
    Deterministic offline provider used for tests and for running the app
    with zero external dependencies / API keys.
    """
    name = "mock"

    def __init__(self, model: str = "mock-1"):
        self.model = model

    def complete(self, system: str, prompt: str, max_tokens: int = 1000) -> LLMResponse:
        summary = {
            "note": "mock LLM response - no external API called",
            "system_excerpt": system[:120],
            "prompt_excerpt": prompt[:200],
        }
        return LLMResponse(text=json.dumps(summary), provider=self.name, model=self.model, raw=summary)


def get_provider(name: str | None = None) -> LLMProvider:
    provider_name = (name or settings.DEFAULT_LLM_PROVIDER).lower()
    if provider_name == "openai":
        return OpenAIProvider()
    if provider_name == "anthropic":
        return AnthropicProvider()
    if provider_name == "ollama":
        return OllamaProvider()
    return MockProvider()
