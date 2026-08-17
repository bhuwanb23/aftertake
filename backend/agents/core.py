"""Shared agent discipline (Phase 2 Step 1). Every agent follows these practices:

Practice 1 — tested in isolation via standalone dev scripts (backend/agents/dev/).
Practice 2 — forced strict-JSON output: the JSON_ONLY_INSTRUCTION ends every
    system prompt (prompt files carry it verbatim; with_json_instruction() is
    the idempotent safety net for inline prompt strings), and parse_json()
    refuses to extract JSON from surrounding text. If the response is not
    parseable JSON, the prompt needs fixing — surfaced loudly with the raw text.
Practice 3 — every response is validated against its Phase 1 Pydantic model
    immediately; shape drift costs one prompt iteration here, not an hour in
    Phase 4.
Practice 4 — every agent call logs the raw LLM response (timestamp, agent,
    model, input summary, full raw text) to config.LLM_LOG_PATH BEFORE parsing,
    so a bad run can be debugged from the log without another call.
Practice 5 — one system prompt per agent in backend/prompts/<name>.txt, loaded
    at runtime, never hardcoded (see prompts/README.md for the file structure).
Practice 6 — run_stability(): no agent is done until it has run repeatedly
    across varied inputs with zero parse/validation failures.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from pydantic import BaseModel, ValidationError

from backend import config
from backend.agents.llm import call_llm

# Practice 2 — the exact closing instruction for every agent system prompt.
# Prompt files carry this verbatim at the end; if you edit it, keep the files
# and this constant in sync (with_json_instruction is idempotent either way).
JSON_ONLY_INSTRUCTION = (
    "Respond with only a valid JSON object. Do not include any text before or "
    "after the JSON. Do not wrap the JSON in markdown code fences. Do not "
    "include any explanation of your response."
)

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
BASE_DIR = PROMPTS_DIR.parent.parent  # repo root


class AgentError(Exception):
    """Base class for agent-layer failures."""


class AgentOutputError(AgentError):
    """The model's response could not be parsed as JSON or failed schema
    validation. The raw response is attached — it is the first thing to read
    when debugging a prompt."""


class AgentResult:
    """A completed agent call: the validated model plus the raw pieces a dev
    script prints (Practice 1)."""

    def __init__(self, raw: str, parsed: dict, validated: BaseModel):
        self.raw = raw
        self.parsed = parsed
        self.validated = validated


# --- Practice 4: raw-response logging ----------------------------------------
def _log_path() -> Path:
    p = Path(config.LLM_LOG_PATH)
    return p if p.is_absolute() else BASE_DIR / p


def log_llm_call(agent_name: str, input_summary: str, raw: str) -> None:
    """Append one raw LLM response to the log file. Plain text, append-only —
    the point is that it exists and is consulted before re-running."""
    path = _log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    model = config.ANTHROPIC_MODEL if config.LLM_PROVIDER == "anthropic" else config.OLLAMA_MODEL
    entry = (
        f"\n=== {ts} | agent={agent_name} | model={model} | provider={config.LLM_PROVIDER}\n"
        f"input: {input_summary}\n"
        f"raw:\n{raw}\n"
        f"=== end {agent_name} ===\n"
    )
    with open(path, "a", encoding="utf-8") as f:
        f.write(entry)


# --- Practice 5: prompt files ------------------------------------------------
def load_prompt(name: str) -> str:
    """Load a system prompt from backend/prompts/<name>.txt.

    Prompts live in files, never in code (Phase 0 Step 4 / Practice 5) —
    iterate on the prompt without touching Python. The file already ends with
    the JSON_ONLY_INSTRUCTION (see prompts/README.md for the structure).
    """
    path = PROMPTS_DIR / (name if name.endswith(".txt") else f"{name}.txt")
    return path.read_text(encoding="utf-8")


def with_json_instruction(system: str) -> str:
    """Practice 2 — append the JSON-only instruction. Idempotent: prompt files
    already carry it, so it is only appended for inline prompt strings."""
    if JSON_ONLY_INSTRUCTION in system:
        return system
    return f"{system}\n\n{JSON_ONLY_INSTRUCTION}"


# --- Practices 2 & 3: strict parse + schema gate -----------------------------
def parse_json(raw: str, context: str = "agent response") -> dict:
    """Practice 2 — strict JSON parse. No extraction from surrounding text:
    if the output is not parseable JSON, that is a prompt failure."""
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AgentOutputError(
            f"{context} was not valid JSON ({exc}). Raw response:\n{raw}"
        ) from exc


def validate(parsed: dict, output_model: type[BaseModel], context: str = "agent response") -> BaseModel:
    """Practice 3 — validate the parsed object against the Phase 1 model.
    On shape drift, name exactly which fields failed and why."""
    try:
        return output_model.model_validate(parsed)
    except ValidationError as exc:
        problems = "; ".join(
            f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}" for e in exc.errors()
        )
        raise AgentOutputError(
            f"{context} failed schema validation ({output_model.__name__}): {problems}.\n"
            f"Parsed object:\n{json.dumps(parsed, indent=2)}"
        ) from exc


def call_agent(
    system: str,
    user: str,
    output_model: type[BaseModel],
    *,
    agent_name: str = "unknown",
    input_summary: str = "",
    temperature: float = 0.2,
    json_mode: bool = True,
    post_parse: Callable[[dict], None] | None = None,
) -> AgentResult:
    """Practices 1-4 in one call: LLM call -> LOG RAW -> strict JSON parse ->
    Pydantic validation. Returns an AgentResult (raw text, parsed dict,
    validated model) for the dev scripts to print; raises AgentOutputError
    otherwise. Agent implementations pass their name and a short input summary
    so every log entry is attributable.

    post_parse(parsed) — optional hook called between parse and validation for
    fields the agent is not asked to produce (e.g. the orchestrator stamps
    creator_id deterministically instead of trusting the model to echo it)."""
    raw = call_llm(
        with_json_instruction(system), user, temperature=temperature, json_mode=json_mode
    )
    log_llm_call(agent_name, input_summary, raw)  # Practice 4 — before anything else
    parsed = parse_json(raw, context=agent_name)
    if post_parse is not None:
        post_parse(parsed)
    validated = validate(parsed, output_model, context=agent_name)
    return AgentResult(raw=raw, parsed=parsed, validated=validated)


# --- Practice 6: stability harness -------------------------------------------
class StabilitySummary:
    def __init__(self, total: int, failures: int, details: list[tuple]):
        self.total = total
        self.failures = failures
        self.details = details  # [(input_index, run_number, status, error_preview)]

    @property
    def passed(self) -> bool:
        return self.failures == 0

    def report(self) -> str:
        lines = [f"stability: {self.total - self.failures}/{self.total} runs OK"]
        for idx, run, status, err in self.details:
            if status != "ok":
                lines.append(f"  input {idx} run {run}: {status} {err}")
        return "\n".join(lines)


def run_stability(
    agent_fn,
    inputs: list,
    runs_per_input: int = 3,
    *,
    name: str = "agent",
) -> StabilitySummary:
    """Practice 6 — an agent is not done until it has run repeatedly across
    varied inputs with zero failures. agent_fn(input) must return an
    AgentResult (or anything) and may raise AgentOutputError; any exception is
    counted as a failed run. The caller prints summary.report()."""
    total = 0
    failures = 0
    details: list[tuple] = []
    for idx, inp in enumerate(inputs, 1):
        for run in range(1, runs_per_input + 1):
            total += 1
            try:
                agent_fn(inp)
                details.append((idx, run, "ok", None))
            except AgentOutputError as exc:
                failures += 1
                details.append((idx, run, "OUTPUT-FAIL", str(exc)[:160]))
            except Exception as exc:  # noqa: BLE001 — any failure counts (e.g. API down)
                failures += 1
                details.append((idx, run, f"ERROR {type(exc).__name__}", str(exc)[:160]))
    return StabilitySummary(total, failures, details)
