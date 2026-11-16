"""LLM providers — zero dependencies (stdlib urllib only).

Supported:
  anthropic  -> Claude (ANTHROPIC_API_KEY)
  openai     -> GPT (OPENAI_API_KEY)
  gemini     -> Google Gemini (GEMINI_API_KEY)
  ollama     -> Local models (no key)
  openrouter -> 100s of models (OPENROUTER_API_KEY)
  custom     -> Any OpenAI-compatible endpoint (base_url + api_key)
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-4-5",
    "openai": "gpt-4o",
    "gemini": "gemini-2.5-flash",
    "ollama": "llama3.1",
    "openrouter": "anthropic/claude-sonnet-4.5",
    "custom": "",
}

ENV_KEYS = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "custom": "LLM_API_KEY",
}


class ProviderError(RuntimeError):
    pass


def _post(url: str, payload: dict, headers: dict, timeout: int = 180) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise ProviderError(f"HTTP {e.code}: {e.read().decode(errors='ignore')[:500]}") from e
    except urllib.error.URLError as e:
        raise ProviderError(f"Connection failed: {e.reason}") from e


def _openai_compatible(base_url, key, model, system, user, temperature, max_tokens):
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    data = _post(
        base_url.rstrip("/") + "/chat/completions",
        {
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        },
        headers,
    )
    return data["choices"][0]["message"]["content"]


def complete(
    system: str,
    user: str,
    provider: str = "anthropic",
    model: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    temperature: float = 0.4,
    max_tokens: int = 4000,
) -> str:
    """Send one system+user message to the chosen provider and return text."""
    provider = provider.lower()
    if provider not in DEFAULT_MODELS:
        raise ProviderError(f"Unknown provider '{provider}'. Use one of: {', '.join(DEFAULT_MODELS)}")
    model = model or os.getenv("PA_MODEL") or DEFAULT_MODELS[provider]
    key = api_key or os.getenv(ENV_KEYS.get(provider, ""), "")

    if provider not in ("ollama",) and not key:
        raise ProviderError(f"API key missing. Set {ENV_KEYS[provider]} or pass api_key.")

    if provider == "anthropic":
        data = _post(
            "https://api.anthropic.com/v1/messages",
            {
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "system": system,
                "messages": [{"role": "user", "content": user}],
            },
            {"x-api-key": key, "anthropic-version": "2023-06-01"},
        )
        return "".join(b.get("text", "") for b in data.get("content", []))

    if provider == "gemini":
        data = _post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",
            {
                "systemInstruction": {"parts": [{"text": system}]},
                "contents": [{"role": "user", "parts": [{"text": user}]}],
                "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
            },
            {},
        )
        return "".join(p.get("text", "") for p in data["candidates"][0]["content"]["parts"])

    if provider == "openai":
        return _openai_compatible(base_url or "https://api.openai.com/v1", key, model, system, user, temperature, max_tokens)
    if provider == "openrouter":
        return _openai_compatible(base_url or "https://openrouter.ai/api/v1", key, model, system, user, temperature, max_tokens)
    if provider == "ollama":
        return _openai_compatible(base_url or "http://localhost:11434/v1", key, model, system, user, temperature, max_tokens)
    if provider == "custom":
        base = base_url or os.getenv("LLM_BASE_URL")
        if not base or not model:
            raise ProviderError("custom provider needs base_url (or LLM_BASE_URL) and model.")
        return _openai_compatible(base, key, model, system, user, temperature, max_tokens)
    raise ProviderError("unreachable")
