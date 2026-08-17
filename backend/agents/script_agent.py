"""Script Agent (Phase 2 Step 5) — the content generation agent.

Takes one ContentOpportunity and the CreatorDNAProfile and writes a complete
video script in the creator's learned voice: hook + scenes + outro, with
scene types chosen to serve the content (these map to HyperFrames rendering
templates in Phase 3).

This is where the DNA agent's voice learning becomes visible — the script
must sound like the specific creator from the seed catalog, never like a
generic AI script. The prompt conditions on voice (hook_pattern,
signature_phrases, what_to_avoid as a hard prohibition) and content_patterns
(optimal_duration_range).

Facts are computed deterministically, never trusted to the model (same
principle as the DNA agent's benchmarks):
  - full_voiceover_text = hook + scenes + outro voiceovers concatenated
    (this exact string is what TTS reads in Phase 3 — it must equal the
    spoken sections)
  - estimated_duration_seconds = sum of all section durations
  - word_count = word count of full_voiceover_text
  - scene_number = position in the scenes list
Metadata (id, creator_id, opportunity_id) is stamped by the orchestrator,
exactly as the other agents stamp theirs.
"""
from __future__ import annotations

import json

from pydantic import BaseModel

from backend.agents.core import AgentResult, call_agent, load_prompt
from backend.models.schemas import Script


def build_script_input(opportunity: dict | BaseModel, profile: dict | BaseModel) -> str:
    """Render the voice + content_patterns sections (the conditioning) plus
    the opportunity as the agent's input text."""
    opp = opportunity.model_dump() if isinstance(opportunity, BaseModel) else opportunity
    prof = profile.model_dump() if isinstance(profile, BaseModel) else profile
    lines = [
        "CREATOR VOICE (JSON — write every line as if THIS creator wrote it):",
        json.dumps(prof.get("voice", prof), indent=2),
        "\nCREATOR CONTENT PATTERNS (JSON — format and duration constraints):",
        json.dumps(prof.get("content_patterns", {}), indent=2),
        "\nVIDEO TO SCRIPT (the opportunity):",
        f"- topic:                       {opp.get('topic', '')}",
        f"- working_title:               {opp.get('working_title', '')}",
        f"- recommended_format:          {opp.get('recommended_format', '')}",
        f"- recommended_duration_seconds: {opp.get('recommended_duration_seconds', '')}",
        f"- target_hook:                 {opp.get('target_hook', '')}",
    ]
    return "\n".join(lines)


def run_script_agent(
    opportunity: dict | BaseModel,
    profile: dict | BaseModel,
    *,
    creator_id: str = "creator_001",
    temperature: float = 0.2,
) -> AgentResult:
    """Run the script agent and return one validated Script object (on
    result.validated). `opportunity` is a ContentOpportunity (model or dict);
    `profile` is the CreatorDNAProfile (model or dict)."""
    opp_dict = opportunity.model_dump() if isinstance(opportunity, BaseModel) else opportunity

    def _stamp_metadata(parsed: dict) -> None:
        # Deterministic facts + metadata the model is not asked to produce.
        hook = parsed["hook"]
        scenes = parsed["scenes"]
        outro = parsed["outro"]
        sections = [hook["voiceover_text"]] + [s["voiceover_text"] for s in scenes] + [outro["voiceover_text"]]
        full = " ".join(s.strip() for s in sections if s and s.strip())
        for i, scene in enumerate(scenes, 1):
            scene["scene_number"] = i
        parsed["id"] = f"scr_{opp_dict.get('id', '000').replace('opp_', '')}"
        parsed["opportunity_id"] = opp_dict.get("id", "")
        parsed["creator_id"] = creator_id
        parsed["full_voiceover_text"] = full
        parsed["estimated_duration_seconds"] = (
            hook["duration_seconds"] + sum(s["duration_seconds"] for s in scenes) + outro["duration_seconds"]
        )
        parsed["word_count"] = len(full.split())

    result = call_agent(
        load_prompt("script_system"),
        build_script_input(opp_dict, profile),
        Script,
        agent_name="script_agent",
        input_summary=(
            f"ContentOpportunity {opp_dict.get('id', '?')} + voice/content_patterns for "
            f"{opp_dict.get('creator_id', creator_id)}"
        ),
        temperature=temperature,
        post_parse=_stamp_metadata,
    )
    return result
