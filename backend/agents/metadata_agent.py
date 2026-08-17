"""Metadata Agent (Phase 2 Step 6) — title, description, tags agent.

Takes a Script object and the CreatorDNAProfile and generates the publishing
metadata: final title (following the creator's title_formula exactly),
title_formula_match (the agent's own explanation of how the title maps to the
formula — evaluated by the scorer and shown in the decision log), the
description (in the creator's voice), and 10-15 relevant tags.

id/asset_id/scheduled_publish_time/platform_targets are stamped
deterministically — never trusted to the model (same as every other agent).
"""
from __future__ import annotations

import json

from pydantic import BaseModel

from backend.agents.core import AgentResult, call_agent, load_prompt
from backend.models.schemas import Metadata, Script


def build_metadata_input(script: dict | BaseModel, profile: dict | BaseModel) -> str:
    """Render the title_formula + voice sections (the conditioning) plus the
    full script JSON (the content the metadata must package) as input."""
    scr = script.model_dump() if isinstance(script, BaseModel) else script
    prof = profile.model_dump() if isinstance(profile, BaseModel) else profile
    lines = [
        "CREATOR TITLE FORMULA (JSON — the title must follow this exactly):",
        json.dumps(prof.get("title_formula", prof), indent=2),
        "\nCREATOR VOICE (JSON — the description must match this register):",
        json.dumps(prof.get("voice", {}), indent=2),
        "\nVIDEO SCRIPT (JSON — the content you are packaging):",
        json.dumps(scr, indent=2),
    ]
    return "\n".join(lines)


def run_metadata_agent(
    script: dict | BaseModel,
    profile: dict | BaseModel,
    *,
    asset_id: str = "asset_pending",
    temperature: float = 0.2,
) -> AgentResult:
    """Run the metadata agent and return one validated Metadata object (on
    result.validated). `script` is a Script (model or dict); `profile` is the
    CreatorDNAProfile (model or dict)."""
    scr_dict = script.model_dump() if isinstance(script, BaseModel) else script

    def _stamp_metadata(parsed: dict) -> None:
        parsed["id"] = f"meta_{scr_dict.get('id', '000').replace('scr_', '')}"
        parsed["asset_id"] = asset_id
        parsed["scheduled_publish_time"] = None
        parsed["platform_targets"] = ["youtube"]

    result = call_agent(
        load_prompt("metadata_system"),
        build_metadata_input(scr_dict, profile),
        Metadata,
        agent_name="metadata_agent",
        input_summary=(
            f"Script {scr_dict.get('id', '?')} + title_formula/voice for "
            f"{scr_dict.get('creator_id', '?')}"
        ),
        temperature=temperature,
        post_parse=_stamp_metadata,
    )
    return result
