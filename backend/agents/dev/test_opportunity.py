"""Standalone dev script for the opportunity agent (Phase 2 Step 3, Practice 1).

Loads the CreatorDNAProfile (generating it once via the DNA agent, cached in
output/dna_profile.json), runs the opportunity agent with the real trends
list, prints the raw response and each opportunity's key fields.

    backend/.venv/Scripts/python backend/agents/dev/test_opportunity.py [--runs N]
    backend/.venv/Scripts/python backend/agents/dev/test_opportunity.py --no-trends

With --runs N (>1) it runs the Practice 6 stability harness. --no-trends
exercises the profile-only path (test plan Run 4).
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from backend.agents.benchmarks import compute_performance_benchmarks  # noqa: E402
from backend.agents.core import run_stability  # noqa: E402
from backend.agents.dna_agent import run_dna_agent  # noqa: E402
from backend.agents.opportunity_agent import build_opportunity_input, run_opportunity_agent  # noqa: E402
from backend.models.schemas import CreatorDNAProfile  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent.parent
CATALOG_PATH = ROOT / "data" / "seed" / "catalog.json"
TRENDS_PATH = ROOT / "data" / "seed" / "trends.json"
PROFILE_CACHE = ROOT / "output" / "dna_profile.json"

# Profile field names the rationale must cite (used for the citation count).
CITABLE_FIELDS = [
    "content_patterns.format_preferences", "content_patterns.best_performing_topics",
    "content_patterns.worst_performing_topics", "content_patterns.optimal_duration_range",
    "content_patterns.avg_duration_seconds", "content_patterns.posting_frequency",
    "title_formula.structure", "title_formula.emotional_hook_type", "title_formula.example_titles",
    "thumbnail_style.dominant_colors", "thumbnail_style.background_type", "thumbnail_style.layout_pattern",
    "voice.hook_pattern", "voice.tone", "voice.pacing", "performance_benchmarks",
]


def get_dna_profile(force: bool = False) -> CreatorDNAProfile:
    """Load the cached DNA profile, generating it once if needed."""
    if not force and PROFILE_CACHE.exists():
        return CreatorDNAProfile.model_validate(json.loads(PROFILE_CACHE.read_text(encoding="utf-8")))
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    creator, videos = data["creator_id"], data["videos"]
    result = run_dna_agent(videos, compute_performance_benchmarks(videos), creator_id=creator)
    PROFILE_CACHE.parent.mkdir(parents=True, exist_ok=True)
    PROFILE_CACHE.write_text(
        json.dumps(result.validated.model_dump(), indent=2), encoding="utf-8"
    )
    print(f"(DNA profile generated and cached to {PROFILE_CACHE})")
    return result.validated


def count_citations(text: str) -> list[str]:
    """Distinct profile fields cited. Matches the bare field name at word
    boundaries, with or without the dotted parent path — so "your
    content_patterns.format_preferences" and "your best_performing_topics"
    both count as citing that field."""
    t = text.lower()
    return [f for f in CITABLE_FIELDS if f.split(".")[-1] in t]


def print_opportunities(result, label: str) -> None:
    print(f"\n=== {label} ===")
    opps = result.validated
    print(f"count: {len(opps)} (must be exactly 3)")
    for opp in opps:
        cites = count_citations(opp.rationale.dna_fit_explanation)
        print(f"--- {opp.id} fit={opp.fit_score} conf={opp.confidence} fmt={opp.recommended_format} dur={opp.recommended_duration_seconds}s")
        print(f"  topic:          {opp.topic}")
        print(f"  working_title:  {opp.working_title}")
        print(f"  dna_fit:        {opp.rationale.dna_fit_explanation[:220]}")
        print(f"  perf_pred:      {opp.rationale.performance_prediction[:160]}")
        print(f"  trend:          {opp.rationale.trend_relevance[:140]}")
        print(f"  risks:          {opp.rationale.risks[:140]}")
        print(f"  hook:           {opp.target_hook[:140]}")
        print(f"  citations ({len(cites)}): {cites}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Dev-test the opportunity agent in isolation.")
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--no-trends", action="store_true", help="Run with profile only (test plan Run 4)")
    parser.add_argument("--force-profile", action="store_true", help="Regenerate the cached DNA profile")
    args = parser.parse_args()

    profile = get_dna_profile(force=args.force_profile)
    trends = None if args.no_trends else json.loads(TRENDS_PATH.read_text(encoding="utf-8"))
    creator = profile.creator_id

    def run_one(p):
        return run_opportunity_agent(p, trends, creator_id=creator)

    if args.runs > 1:
        summary = run_stability(run_one, [profile], runs_per_input=args.runs, name="opportunity_agent")
        print(summary.report())
        return 0 if summary.passed else 1

    result = run_one(profile)
    print("=== RAW RESPONSE ===")
    print(result.raw)
    print_opportunities(result, "VALIDATION")
    return 0


if __name__ == "__main__":
    sys.exit(main())
