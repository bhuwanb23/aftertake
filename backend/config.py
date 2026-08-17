"""Shared AfterTake configuration constants — changed in one place.

Values come from environment variables (.env) with sane local-dev defaults.
"""
import os

try:  # python-dotenv may not be installed yet; fall back to real env vars
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# --- Timeout policy (Phase 1 Step 4, case 4) --------------------------------
# Agent (LLM) calls must fail cleanly rather than freeze the demo. Every agent
# call passes this as the HTTP/SDK timeout; a timed-out call raises and the
# app's error handlers convert it into a clean {status: "error"} response.
AGENT_CALL_TIMEOUT_SECONDS = int(os.getenv("AGENT_CALL_TIMEOUT_SECONDS", "60"))

# --- LLM provider (Phase 2) --------------------------------------------------
# Development default is a local Ollama server (tiny model, free, fast enough
# for prompt iteration). To switch to the Anthropic API: set
# LLM_PROVIDER=anthropic and ANTHROPIC_API_KEY in .env. Everything downstream
# goes through backend.agents.llm.call_llm, so switching is one line.
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")  # "ollama" | "anthropic"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4")
