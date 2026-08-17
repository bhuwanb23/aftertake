"""Shared agent discipline (Phase 2 Step 1). Every agent follows these practices:

Practice 1 — tested in isolation via standalone dev scripts (backend/agents/dev/).
Practice 2 — forced strict-JSON output: the JSON_ONLY_INSTRUCTION is appended
    to every system prompt, and parse_json() refuses to extract JSON from
    surrounding text. If the response is not parseable JSON, the prompt needs
    fixing — surfaced loudly with the raw response.
Practice 3 — every response is validated against its Phase 1 Pydantic model
    immediately; shape drift costs one prompt iteration here, not an hour of
    tracing in Phase 4.
"""
import json
from pathlib import Path

from pydantic import BaseModel, ValidationError

from backend.agents.llm import call_llm

# Practice 2 — the exact closing instruction for every agent system prompt.
JSON_ONLY_INSTRUCTION = (
    "Respond with only a valid JSON object. Do not include any text before or "
    "after the JSON. Do not wrap the JSON in markdown code fences. Do not "
    "include any explanation of your response."
)

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


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


def load_prompt(name: str) -> str:
    """Load a system prompt from backend/prompts/<name>.txt.

    Prompts live in files, never in code (Phase 0 Step 4) — iterate on the
    prompt without touching Python.
    """
    path = PROMPTS_DIR / (name if name.endswith(".txt") else f"{name}.txt")
    return path.read_text(encoding="utf-8")


def with_json_instruction(system: str) -> str:
    """Append Practice 2's JSON-only instruction to a system prompt."""
    return f"{system}\n\n{JSON_ONLY_INSTRUCTION}"


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
    temperature: float = 0.2,
    json_mode: bool = True,
) -> AgentResult:
    """Practices 1-3 in one call: LLM call -> strict JSON parse -> Pydantic
    validation. Returns an AgentResult (raw text, parsed dict, validated
    model) for the dev scripts to print; raises AgentOutputError otherwise."""
    raw = call_llm(
        with_json_instruction(system), user, temperature=temperature, json_mode=json_mode
    )
    parsed = parse_json(raw)
    validated = validate(parsed, output_model)
    return AgentResult(raw=raw, parsed=parsed, validated=validated)
