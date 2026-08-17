"""Phase 2 Step 1 — environment smoke test (standalone dev script).

Run directly:

    backend/.venv/Scripts/python backend/agents/dev/smoke_llm.py

Proves the three practices work end-to-end with the local Ollama model:
  1. a real LLM call returns JSON
  2. strict parse (no extraction from surrounding text)
  3. immediate schema validation against a Phase 1 model

Also demonstrates both failure paths (non-JSON output, shape drift) failing
loudly with the raw response / failing fields — so you know what a broken
prompt looks like before any agent is built.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from backend import config  # noqa: E402
from backend.agents import core  # noqa: E402
from backend.agents.llm import call_llm  # noqa: E402
from backend.models.schemas import Performance  # noqa: E402

ok = fail = 0


def check(name, cond, extra=""):
    global ok, fail
    if cond:
        ok += 1
        print(f"  PASS {name} {extra}")
    else:
        fail += 1
        print(f"  FAIL {name} {extra}")


def main():
    print(f"provider={config.LLM_PROVIDER} model={config.OLLAMA_MODEL} "
          f"base={config.OLLAMA_BASE_URL} timeout={config.AGENT_CALL_TIMEOUT_SECONDS}s\n")

    print("--- 1. success path: real call -> strict JSON -> schema validation ---")
    system = (
        "You are a test harness for a content analytics system. You produce "
        "JSON describing a YouTube video's performance metrics."
    )
    user = (
        'Return a JSON object with exactly these fields: "views" (integer), '
        '"likes" (integer), "comments" (integer), "watch_time_hours" (float). '
        'Example: {"views": 420000, "likes": 18400, "comments": 1240, "watch_time_hours": 68.0}'
    )
    result = core.call_agent(system, user, Performance)
    check("raw response is parseable JSON", result.validated.views > 0)
    print("    raw:", result.raw[:120].replace("\n", " "))
    print("    validated:", result.validated.model_dump())

    print("\n--- 2. failure path: non-JSON output is a prompt failure, surfaced loudly ---")
    text = call_llm("You output exactly one word.", "Say: hello", json_mode=False)
    try:
        core.parse_json(text)
        check("non-JSON output detected", False)
    except core.AgentOutputError as exc:
        check("non-JSON output detected", "was not valid JSON" in str(exc) and text in str(exc))
        print("    error surfaced with raw response")

    print("\n--- 3. failure path: shape drift names the failing fields ---")
    user_bad = 'Return a JSON object with only "views": 5.'
    try:
        core.call_agent(system, user_bad, Performance)
        check("missing required fields rejected", False)
    except core.AgentOutputError as exc:
        check("missing required fields rejected", "failed schema validation" in str(exc)
              and "likes" in str(exc) and "Performance" in str(exc))
        print("    error names fields:", str(exc).split(": ")[1][:90], "...")

    print(f"\n{ok} passed, {fail} failed")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
