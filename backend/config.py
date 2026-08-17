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
# 60s is the plan's per-agent-call policy for the fast Anthropic API. Local
# Ollama models (gemma4:12b ~17 tok/s) can take 90-120s for a full profile, so
# the Ollama path uses a separate, longer timeout.
AGENT_CALL_TIMEOUT_SECONDS = int(os.getenv("AGENT_CALL_TIMEOUT_SECONDS", "60"))
OLLAMA_CALL_TIMEOUT_SECONDS = int(os.getenv("OLLAMA_CALL_TIMEOUT_SECONDS", "300"))

# --- LLM provider (Phase 2) --------------------------------------------------
# Development default is a local Ollama server (tiny model, free, fast enough
# for prompt iteration). To switch to the Anthropic API: set
# LLM_PROVIDER=anthropic and ANTHROPIC_API_KEY in .env. Everything downstream
# goes through backend.agents.llm.call_llm, so switching is one line.
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")  # "ollama" | "anthropic"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
# gemma4:12b is the verified dev default (user-confirmed): llama3.2:1b produced
# unusable DNA profiles (omits fields, echoes prompt placeholders); gemma4:12b
# produces complete, evidence-cited profiles. The real API (LLM_PROVIDER=
# anthropic) remains the production target.
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:12b")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4")

# --- Generation limits ------------------------------------------------------
# Structured outputs (e.g. the full CreatorDNAProfile) can run long; keep the
# cap generous so generation never truncates mid-JSON. The 60s timeout still
# guards against a stalled call (Phase 1 Step 4, case 4).
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "4096"))
# Ollama context window (num_ctx). Defaults are often too small: the DNA
# prompt alone is ~3400 tokens, so a 4096 window leaves ~700 for the JSON
# profile and truncates mid-output (finish_reason="length"). 16384 fits the
# full prompt + a complete profile. Ignored by the Anthropic path.
OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "16384"))

# --- Raw-response log (Phase 2 Step 1, Practice 4) --------------------------
# Every agent call appends its raw LLM response here (timestamp, agent, model,
# input summary, full raw text) BEFORE anything else happens with it — so a
# bad output can be debugged from the log without spending another call.
# Relative paths resolve against the repo root; output/ is gitignored.
LLM_LOG_PATH = os.getenv("LLM_LOG_PATH", "output/llm_log.txt")
