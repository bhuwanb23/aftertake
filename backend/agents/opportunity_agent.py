"""Opportunity Agent (Phase 2 Step 3) — the "what to make next" agent.

Takes the CreatorDNAProfile (from the DNA agent) plus a static niche trends
list and recommends EXACTLY THREE ContentOpportunity objects, ranked by
fit_score descending.

The critical requirement: every rationale must cite specific profile fields
by name (content_patterns.format_preferences, title_formula.structure, ...).
If a rationale would apply equally to any creator, the agent failed its
purpose. The prompt enforces this; the verification script counts field
citations.

Metadata the model is not asked to produce (id, creator_id, created_at,
status) is stamped deterministically, exactly as the DNA agent stamps its
metadata — never trusted to a model echo.
"""
from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field

from backend.agents.core import AgentResult, call_agent, load_prompt
from backend.models.schemas import ContentOpportunity


class _OpportunitySet(BaseModel):
    """Transient JSON envelope for a list-typed agent output.

    This is NOT a system schema (Phase 1 schemas are the only data shapes) —
    it exists solely so the shared call_agent pipeline can validate each
    item against ContentOpportunity with the usual loud shape-drift errors.
    """
    opportunities: list[ContentOpportunity] = Field(min_length=3, max_length=3)


def build_opportunity_input(profile: dict, trends: list[dict] | None) -> str:
    """Render the profile (as JSON, so the model can cite field names
    exactly) plus the optional trends list as the agent's input text."""
    import json

    lines = [
        "CREATOR DNA PROFILE (JSON — this is the primary filter; cite its "
        "field names in your rationale):",
        json.dumps(profile, indent=2),
    ]
    if trends:
        lines.append("\nCURRENT TRENDS IN THE NICHE (raw material — optional, "
                     "the profile is the primary filter):")
        for t in trends:
            lines.append(
                f"- {t.get('topic')}: {t.get('why_now', '')} "
                f"[formats: {', '.join(t.get('suggested_formats', []))}]"
            )
    return "\n".join(lines)


def run_opportunity_agent(
    profile: dict | BaseModel,
    trends: list[dict] | None,
    *,
    creator_id: str = "creator_001",
    temperature: float = 0.2,
) -> AgentResult:
    """Run the opportunity agent and return exactly three validated
    ContentOpportunity objects (on result.validated.opportunities).

    `profile` is the CreatorDNAProfile as a model or its dict dump; `trends`
    is the static trends list (data/seed/trends.json) or None.
    """
    profile_dict = profile.model_dump() if isinstance(profile, BaseModel) else profile
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    def _stamp_metadata(parsed: dict) -> None:
        # Stamped per-item before validation: ids by rank, plus fields the
        # model is not asked to produce.
        for i, opp in enumerate(parsed["opportunities"], 1):
            opp["id"] = f"opp_{i:03d}"
            opp["creator_id"] = creator_id
            opp["created_at"] = now
            opp["status"] = "pending"

    result = call_agent(
        load_prompt("opportunity_system"),
        build_opportunity_input(profile_dict, trends),
        _OpportunitySet,
        agent_name="opportunity_agent",
        input_summary=f"CreatorDNAProfile for {creator_id}"
                      + (f" + {len(trends)} trends" if trends else " + NO trends"),
        temperature=temperature,
        post_parse=_stamp_metadata,
    )
    # Keep the API identical to other agents: .validated is the model the
    # caller cares about. Here that is the list of opportunities.
    result.validated = result.validated.opportunities  # type: ignore[attr-defined]
    return result
