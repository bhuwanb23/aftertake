"""DNA Agent (Phase 2 Step 2) — the foundational agent.

Takes a creator's catalog of SourceVideo objects plus the PRE-CALCULATED
performance benchmarks and produces a validated CreatorDNAProfile. This
profile is the input to every other agent — if it is wrong, weak, or vague,
everything downstream is wrong, weak, or vague. Get this right first.

Inputs:
  - videos:     list of dicts shaped like SourceVideo (from the catalog)
  - benchmarks: dict of the five pre-calculated values (backend/agents/benchmarks.py)
                — the LLM receives them as facts, never derives them.

Output:
  - AgentResult with .validated = CreatorDNAProfile (every field populated).

The benchmarks are computed in Python BEFORE the prompt is built — the model
never does arithmetic on the numbers (Phase 2 Step 2). Same rule applies to
the average duration, which is also computed here in Python.
"""
from __future__ import annotations

from datetime import datetime, timezone

from backend.agents.core import AgentResult, call_agent, load_prompt
from backend.models.schemas import CreatorDNAProfile


def compute_avg_duration_seconds(videos: list[dict]) -> int:
    """Average video length in seconds, computed in Python (never by the LLM)."""
    durations = [v["duration_seconds"] for v in videos if v.get("duration_seconds") is not None]
    return round(sum(durations) / len(durations)) if durations else 0


def build_dna_input(videos: list[dict], benchmarks: dict, avg_duration_seconds: int) -> str:
    """Render the catalog + pre-calculated facts as the agent's input text."""
    lines = [f"CATALOG FOR CREATOR — {len(videos)} videos:", ""]
    for v in videos:
        p = v.get("performance", {})
        thumb = v.get("thumbnail", {})
        lines.append(f"VIDEO {v['id']} — \"{v['title']}\"")
        lines.append(
            f"  published {v['published_at']} | {v['duration_seconds']}s | {v.get('platform', '')}"
        )
        lines.append(
            f"  views {p.get('views')} | ctr {p.get('ctr')}% | retention {p.get('avg_retention')}%"
        )
        lines.append(f"  thumbnail: {thumb.get('description', '')}")
        lines.append(f"  transcript: {v.get('transcript', '')}")
        lines.append("")
    lines.append("PRE-CALCULATED FACTS (use these exact values verbatim; never recalculate them):")
    lines.append(f"  average views across catalog: {benchmarks['avg_views']}")
    lines.append(f"  average CTR across catalog: {benchmarks['avg_ctr']}")
    lines.append(f"  average retention across catalog: {benchmarks['avg_retention']}")
    lines.append(f"  top quartile view threshold: {benchmarks['top_quartile_views']}")
    lines.append(f"  bottom quartile view threshold: {benchmarks['bottom_quartile_views']}")
    lines.append(f"  average duration across catalog: {avg_duration_seconds} seconds")
    return "\n".join(lines)


def run_dna_agent(
    videos: list[dict],
    benchmarks: dict,
    *,
    creator_id: str = "creator_001",
    temperature: float = 0.2,
) -> AgentResult:
    """Run the DNA agent in isolation and return the validated profile.

    `videos` must be catalog-shaped dicts (id, title, transcript, duration_seconds,
    published_at, platform, performance, thumbnail). `benchmarks` comes from
    backend.agents.benchmarks.compute_performance_benchmarks.
    """
    avg_duration = compute_avg_duration_seconds(videos)
    user_input = build_dna_input(videos, benchmarks, avg_duration)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    def _stamp_metadata(parsed: dict) -> None:
        # Metadata the agent is not asked to produce — stamped deterministically
        # (never trusted to a model echo): creator identity and timestamps.
        parsed["creator_id"] = creator_id
        parsed["created_at"] = now
        parsed["updated_at"] = now
        parsed["source_video_count"] = len(videos)

    return call_agent(
        load_prompt("dna_system"),
        user_input,
        CreatorDNAProfile,
        agent_name="dna_agent",
        input_summary=f"{len(videos)} catalog videos for {creator_id}",
        temperature=temperature,
        post_parse=_stamp_metadata,
    )
