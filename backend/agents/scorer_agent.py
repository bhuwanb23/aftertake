"""Scorer Agent (Phase 2 Step 7) — the quality gate / critic agent.

Takes the generated asset's pieces (selected thumbnail layout description,
metadata title + title_formula_match, script full voiceover) plus the
CreatorDNAProfile, and scores three dimensions against the profile. This is
the differentiation layer: it is BUILT to reject output that does not match
the creator's learned style, with a specific, field-citing rejection reason.

Deterministic facts (same principle as the DNA agent's benchmarks):
  - overall_score is the WEIGHTED COMPOSITE (thumbnail 35%, title 35%,
    voice 30%) computed here from the model's three dimension scores — the
    LLM does not do the arithmetic. The weights mirror the system prompt
    (the plan's tuning surface); keep the two in sync.
  - passed is computed by the QualityScore model itself from
    overall_score vs threshold_used — the model never sets it.
  - threshold_used (0.75 default), regeneration_count (0), and asset_id are
    stamped deterministically.
The model must supply a non-empty rejection_reason whenever the composite
fails — the schema's model_validator enforces this loudly.
"""
from __future__ import annotations

import json

from pydantic import BaseModel

from backend.agents.core import AgentResult, call_agent, load_prompt
from backend.models.schemas import QUALITY_THRESHOLD_DEFAULT, QualityScore

# Weighted composite — mirrors the weights stated in scorer_system.txt
# (the plan: "These weights can be adjusted by updating the system prompt").
SCORE_WEIGHTS = {"thumbnail": 0.35, "title": 0.35, "voice": 0.30}


def build_scorer_input(
    thumbnail_description: str,
    title: str,
    title_formula_match: str,
    full_voiceover_text: str,
    profile: dict | BaseModel,
) -> str:
    """Render the full profile (the standard) plus the asset pieces to score."""
    prof = profile.model_dump() if isinstance(profile, BaseModel) else profile
    lines = [
        "CREATOR DNA PROFILE (JSON — the standard every dimension is scored "
        "against):",
        json.dumps(prof, indent=2),
        "\nGENERATED ASSET TO SCORE:",
        f"- THUMBNAIL (layout_description): {thumbnail_description}",
        f"- TITLE: {title}",
        f"- TITLE_FORMULA_MATCH (the metadata agent's explanation): {title_formula_match}",
        f"- SCRIPT (full_voiceover_text): {full_voiceover_text}",
    ]
    return "\n".join(lines)


def run_scorer_agent(
    thumbnail_description: str,
    title: str,
    title_formula_match: str,
    full_voiceover_text: str,
    profile: dict | BaseModel,
    *,
    asset_id: str = "asset_pending",
    threshold: float = QUALITY_THRESHOLD_DEFAULT,
    temperature: float = 0.1,
) -> AgentResult:
    """Run the scorer agent and return one validated QualityScore object (on
    result.validated). Explicit params make the deliberate-rejection tests
    trivial: pass any piece as a crafted bad input.

    The profile is a CreatorDNAProfile (model or dict). The orchestrator
    extracts the four asset pieces from the GeneratedAsset when wiring this
    into the pipeline (Phase 4).
    """
    prof_dict = profile.model_dump() if isinstance(profile, BaseModel) else profile

    def _stamp_metadata(parsed: dict) -> None:
        parsed["asset_id"] = asset_id
        parsed["threshold_used"] = threshold
        parsed["regeneration_count"] = 0
        parsed["overall_score"] = round(
            SCORE_WEIGHTS["thumbnail"] * parsed["thumbnail_fit_score"]
            + SCORE_WEIGHTS["title"] * parsed["title_fit_score"]
            + SCORE_WEIGHTS["voice"] * parsed["voice_fit_score"],
            3,
        )

    result = call_agent(
        load_prompt("scorer_system"),
        build_scorer_input(thumbnail_description, title, title_formula_match,
                           full_voiceover_text, prof_dict),
        QualityScore,
        agent_name="scorer",
        input_summary=f"Quality gate for {prof_dict.get('creator_id', '?')} "
                      f"(asset {asset_id})",
        temperature=temperature,
        post_parse=_stamp_metadata,
    )
    return result
