"""Thumbnail Agent (Phase 2 Step 4) — the visual asset generation agent.

Takes one ContentOpportunity and the CreatorDNAProfile and generates exactly
THREE ThumbnailVariant objects. The SVG markup must be genuinely renderable
(1280x720, only standard elements, valid colors, well-formed XML) and must
directly reflect the profile's thumbnail_style — solid-color background from
the dominant palette, bold white all-caps text with black outline, and the
creator's face as a positioned placeholder rect (the real photo is inserted
at publish time).

png_path stays null here — the Phase 3 rendering step fills it in.
Metadata the model is not asked to produce (id, asset_id, variant_number,
png_path, selected, selection_reason) is stamped deterministically, exactly
as the DNA and opportunity agents stamp theirs.
"""
from __future__ import annotations

import json

from pydantic import BaseModel, Field

from backend.agents.core import AgentResult, call_agent, load_prompt
from backend.models.schemas import CreatorDNAProfile, ThumbnailVariant


class _ThumbnailSet(BaseModel):
    """Transient JSON envelope for a list-typed agent output.

    This is NOT a system schema (Phase 1 schemas are the only data shapes) —
    it exists solely so the shared call_agent pipeline can validate each item
    against ThumbnailVariant with the usual loud shape-drift errors.
    """
    variants: list[ThumbnailVariant] = Field(min_length=3, max_length=3)


def build_thumbnail_input(opportunity: dict | BaseModel, profile: dict | BaseModel) -> str:
    """Render the thumbnail_style section (the design brief) plus the video's
    topic/working title as the agent's input text."""
    opp = opportunity.model_dump() if isinstance(opportunity, BaseModel) else opportunity
    prof = profile.model_dump() if isinstance(profile, BaseModel) else profile
    lines = [
        "CREATOR THUMBNAIL STYLE (JSON — your design brief. Every design "
        "decision must trace back to a field here):",
        json.dumps(prof.get("thumbnail_style", prof), indent=2),
        "\nVIDEO THIS THUMBNAIL IS FOR:",
        f"- topic:          {opp.get('topic', '')}",
        f"- working_title:  {opp.get('working_title', '')}",
        f"- recommended_format: {opp.get('recommended_format', '')}",
    ]
    return "\n".join(lines)


def run_thumbnail_agent(
    opportunity: dict | BaseModel,
    profile: dict | BaseModel | CreatorDNAProfile,
    *,
    asset_id: str = "asset_pending",
    temperature: float = 0.2,
) -> AgentResult:
    """Run the thumbnail agent and return exactly three validated
    ThumbnailVariant objects (on result.validated).

    `opportunity` is a ContentOpportunity (model or dict); `profile` is the
    CreatorDNAProfile (model or dict). `asset_id` is stamped onto every
    variant — the orchestrator passes the real asset id; isolation runs leave
    the default.
    """
    opp_dict = opportunity.model_dump() if isinstance(opportunity, BaseModel) else opportunity

    def _stamp_metadata(parsed: dict) -> None:
        # Stamped per-variant before validation: ids by position, plus the
        # fields the model is not asked to produce.
        for i, variant in enumerate(parsed["variants"], 1):
            variant["id"] = f"thumb_{i:03d}"
            variant["asset_id"] = asset_id
            variant["variant_number"] = i
            variant["png_path"] = None
            variant["selected"] = False
            variant["selection_reason"] = None

    result = call_agent(
        load_prompt("thumbnail_system"),
        build_thumbnail_input(opp_dict, profile),
        _ThumbnailSet,
        agent_name="thumbnail_agent",
        input_summary=(
            f"ContentOpportunity {opp_dict.get('id', '?')} + thumbnail_style for "
            f"{opp_dict.get('creator_id', '?')}"
        ),
        temperature=temperature,
        post_parse=_stamp_metadata,
    )
    # Keep the API identical to the other agents: .validated is the list of
    # variants the caller cares about.
    result.validated = result.validated.variants  # type: ignore[attr-defined]
    return result
