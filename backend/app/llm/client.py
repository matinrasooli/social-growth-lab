from __future__ import annotations

import json
import re
import time
from collections import deque

from app.core.config import get_settings
from app.llm.base import LLMError
from app.llm.providers import get_provider

settings = get_settings()

_call_timestamps: deque[float] = deque()


def _rate_limit():
    now = time.time()
    window = 60.0
    while _call_timestamps and now - _call_timestamps[0] > window:
        _call_timestamps.popleft()
    if len(_call_timestamps) >= settings.LLM_MAX_CALLS_PER_MINUTE:
        sleep_for = window - (now - _call_timestamps[0])
        if sleep_for > 0:
            time.sleep(min(sleep_for, 5))
    _call_timestamps.append(time.time())


def call_llm_json(system: str, prompt: str, provider_name: str | None = None, max_tokens: int = 1200) -> dict:
    """
    Call an LLM provider expecting a JSON object back. Includes rate limiting
    and bounded retries, and gracefully degrades to a structured fallback if
    parsing fails (never raises out to the caller for a malformed response).
    """
    provider = get_provider(provider_name)
    last_error: Exception | None = None

    for attempt in range(settings.LLM_MAX_RETRIES + 1):
        try:
            _rate_limit()
            response = provider.complete(system=system, prompt=prompt, max_tokens=max_tokens)
            cleaned = re.sub(r"^```(json)?|```$", "", response.text.strip(), flags=re.MULTILINE).strip()
            try:
                return {"ok": True, "data": json.loads(cleaned), "provider": provider.name, "model": provider.model}
            except json.JSONDecodeError:
                return {
                    "ok": False,
                    "error": "non_json_response",
                    "raw_text": cleaned[:1000],
                    "provider": provider.name,
                    "model": provider.model,
                }
        except LLMError as exc:
            last_error = exc
            continue

    return {"ok": False, "error": str(last_error) if last_error else "unknown_error", "provider": provider.name}
