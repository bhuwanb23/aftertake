"""LLM provider layer (Phase 2).

All agent calls go through call_llm() — the ONE place that talks to a model.
Development default is a local Ollama server (OpenAI-compatible endpoint);
switching to the Anthropic API later is a config change (LLM_PROVIDER=anthropic
+ ANTHROPIC_API_KEY), not a code change.

Every call honors config.AGENT_CALL_TIMEOUT_SECONDS so a stalled model never
freezes the demo (Phase 1 Step 4, case 4).
"""
import os

import httpx

from backend import config


def call_llm(system: str, user: str, *, temperature: float = 0.2, json_mode: bool = True) -> str:
    """Run one LLM call and return the raw text content.

    json_mode=True asks the provider for a strict JSON object (the
    OpenAI-compatible / Ollama native 'format: json' support). The caller is
    still responsible for parsing + schema-validating (Phase 2 Step 1
    practices 2 and 3).
    """
    if config.LLM_PROVIDER == "anthropic":
        return _call_anthropic(system, user, temperature)
    return _call_ollama(system, user, temperature, json_mode)


def _call_ollama(system: str, user: str, temperature: float, json_mode: bool) -> str:
    """Local Ollama via the native /api/chat endpoint.

    The OpenAI-compatible endpoint is not used: it caps total context at 4096
    tokens (a 3388-token DNA prompt leaves ~700 for the profile JSON, which
    truncates mid-output). The native endpoint honors options.num_ctx, so the
    full prompt + complete JSON fit. "think": false stops reasoning models
    (e.g. gemma4) from dumping output into a thinking field and returning
    empty content; non-reasoning models (llama3.2) ignore it.
    """
    payload = {
        "model": config.OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "stream": False,
        "think": False,
        "options": {
            "temperature": temperature,
            "num_ctx": config.OLLAMA_NUM_CTX,
            "num_predict": config.LLM_MAX_TOKENS,
        },
    }
    if json_mode:
        payload["format"] = "json"
    base = config.OLLAMA_BASE_URL.rstrip("/")
    if base.endswith("/v1"):
        base = base[:-3]  # OLLAMA_BASE_URL points at /v1; /api/chat lives on the root
    with httpx.Client(timeout=config.OLLAMA_CALL_TIMEOUT_SECONDS) as client:
        resp = client.post(f"{base}/api/chat", json=payload)
        resp.raise_for_status()
        return resp.json()["message"]["content"]


def _call_anthropic(system: str, user: str, temperature: float) -> str:
    """Anthropic API (used when LLM_PROVIDER=anthropic — the production stack)."""
    import anthropic

    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError(
            "LLM_PROVIDER=anthropic but ANTHROPIC_API_KEY is not set in .env"
        )
    client = anthropic.Anthropic(api_key=key, timeout=config.AGENT_CALL_TIMEOUT_SECONDS)
    resp = client.messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=config.LLM_MAX_TOKENS,
        temperature=temperature,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(block.text for block in resp.content if block.type == "text")
