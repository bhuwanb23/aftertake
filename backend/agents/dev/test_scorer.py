"""Standalone dev script for the scorer agent (Phase 2 Step 7, Practice 1).

Loads the cached CreatorDNAProfile and the cached good-asset inputs (real
output from the thumbnail/metadata/script agents), runs the scorer, prints
the raw response and the validated QualityScore.

    backend/.venv/Scripts/python backend/agents/dev/test_scorer.py [--runs N]

With --runs N (>1) it runs the Practice 6 stability harness.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from backend.agents.core import run_stability  # noqa: E402
from backend.agents.dev.test_opportunity import get_dna_profile  # noqa: E402
from backend.agents.scorer_agent import run_scorer_agent  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent.parent
ASSET_CACHE = ROOT / "output" / "asset_inputs.json"


def get_good_asset() -> dict:
    return json.loads(ASSET_CACHE.read_text(encoding="utf-8"))


def print_score(result, label: str) -> None:
    print(f"\n=== {label} ===")
    q = result.validated
    print(f"asset={q.asset_id} | thumbnail={q.thumbnail_fit_score} title={q.title_fit_score} "
          f"voice={q.voice_fit_score} | overall={q.overall_score} (threshold {q.threshold_used}) "
          f"| passed={q.passed}")
    if q.rejection_reason:
        print(f"  REJECTION: {q.rejection_reason}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Dev-test the scorer agent in isolation.")
    parser.add_argument("--runs", type=int, default=1)
    args = parser.parse_args()

    profile = get_dna_profile()
    asset = get_good_asset()
    creator = profile.creator_id

    def run_one(inp):
        a, prof = inp
        return run_scorer_agent(
            a["thumbnail_description"], a["title"], a["title_formula_match"],
            a["full_voiceover_text"], prof, asset_id="asset_good",
        )

    if args.runs > 1:
        summary = run_stability(run_one, [(asset, profile)], runs_per_input=args.runs,
                                name="scorer")
        print(summary.report())
        return 0 if summary.passed else 1

    result = run_one((asset, profile))
    print("=== RAW RESPONSE ===")
    print(result.raw)
    print_score(result, "VALIDATION")
    return 0


if __name__ == "__main__":
    sys.exit(main())
