"""Shared AfterTake configuration constants — changed in one place.

Phase 1 Step 4 (error handling, case 4 — timeout): agent (LLM) calls take real
time and a stalled call must fail cleanly rather than freeze the demo. Every
Phase 2 agent passes this value as the timeout on its Anthropic/httpx call; a
timed-out call raises, and the app's error handlers convert it into a clean
{status: "error", message, detail} response instead of a hanging request.

60s per call is generous for normal operation (the plan: "so normal operation
is never affected, but cap it so a stalled call does not freeze the demo").
"""
AGENT_CALL_TIMEOUT_SECONDS = 60
