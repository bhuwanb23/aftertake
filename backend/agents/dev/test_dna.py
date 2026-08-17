"""Standalone dev script for the DNA agent (Phase 2 Step 2, Practice 1).

Loads the real seed catalog, computes the benchmarks in Python, calls the
agent against Ollama, prints the raw response, and validates against
CreatorDNAProfile. Run repeatedly while iterating on backend/prompts/dna_system.txt:

    backend/.venv/Scripts/python backend/agents/dev/test_dna.py [--runs N]

With --runs N (>1) it instead runs the Practice 6 stability harness: the same
input N times, counting every parse/validation/API failure. The agent is not
done until a stability pass shows zero failures.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from backend.agents.benchmarks import compute_performance_benchmarks
from backend.agents.core import run_stability
from backend.agents.dna_agent import build_dna_input, compute_avg_duration_seconds, run_dna_agent

CATALOG_PATH = Path(__file__).resolve().parent.parent.parent.parent / "data" / "seed" / "catalog.json"


def load_catalog(path: Path = CATALOG_PATH) -> tuple[str, list[dict]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["creator_id"], data["videos"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Dev-test the DNA agent in isolation.")
    parser.add_argument("--runs", type=int, default=1, help="Run N times (Practice 6 stability pass)")
    parser.add_argument("--catalog", default=str(CATALOG_PATH))
    args = parser.parse_args()

    creator_id, videos = load_catalog(Path(args.catalog))
    benchmarks = compute_performance_benchmarks(videos)
    avg_duration = compute_avg_duration_seconds(videos)
    print(f"catalog: {len(videos)} videos for {creator_id}")
    print(f"benchmarks: {benchmarks} | avg duration {avg_duration}s\n")

    if args.runs > 1:
        summary = run_stability(
            lambda v: run_dna_agent(v, benchmarks, creator_id=creator_id),
            [videos],
            runs_per_input=args.runs,
            name="dna_agent",
        )
        print(summary.report())
        return 0 if summary.passed else 1

    # Single run — the development loop: print everything, read the output.
    result = run_dna_agent(videos, benchmarks, creator_id=creator_id)
    print("=== RAW RESPONSE ===")
    print(result.raw)
    print("\n=== VALIDATION ===")
    profile = result.validated
    print(f"OK — CreatorDNAProfile for {profile.creator_id} "
          f"({profile.source_video_count} videos), schema-validated\n")
    print(f"voice.tone:          {profile.voice.tone}")
    print(f"voice.pacing:        {profile.voice.pacing}")
    print(f"title.structure:     {profile.title_formula.structure}")
    print(f"title.examples:      {profile.title_formula.example_titles}")
    print(f"thumb.colors:        {profile.thumbnail_style.dominant_colors}")
    print(f"thumb.background:    {profile.thumbnail_style.background_type}")
    print(f"formats:             {profile.content_patterns.format_preferences}")
    print(f"benchmarks:          {profile.performance_benchmarks.model_dump()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
