"""Standalone dev script for the metadata agent (Phase 2 Step 6, Practice 1).

Loads the cached CreatorDNAProfile and the cached scripts (scr_001 for the
top opportunity), runs the metadata agent, prints the raw response and the
validated metadata (title, formula match, description, tags).

    backend/.venv/Scripts/python backend/agents/dev/test_metadata.py [--runs N]

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
from backend.agents.metadata_agent import run_metadata_agent  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent.parent
SCRIPTS_CACHE = ROOT / "output" / "scripts.json"


def get_script(index: int = 0) -> dict:
    return json.loads(SCRIPTS_CACHE.read_text(encoding="utf-8"))[index]


def print_metadata(result, label: str) -> None:
    print(f"\n=== {label} ===")
    m = result.validated
    print(f"id={m.id} asset={m.asset_id} category={m.category} platforms={m.platform_targets}")
    print(f"--- TITLE ---")
    print(f"  {m.title}")
    print(f"--- TITLE FORMULA MATCH ---")
    print(f"  {m.title_formula_match}")
    print(f"--- DESCRIPTION ---")
    print(f"  {m.description}")
    print(f"--- TAGS ({len(m.tags)}) ---")
    print(f"  {', '.join(m.tags)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Dev-test the metadata agent in isolation.")
    parser.add_argument("--runs", type=int, default=1)
    args = parser.parse_args()

    profile = get_dna_profile()
    script = get_script(0)
    creator = profile.creator_id

    def run_one(inp):
        scr, prof = inp
        return run_metadata_agent(scr, prof, asset_id=f"asset_{creator}")

    if args.runs > 1:
        summary = run_stability(run_one, [(script, profile)], runs_per_input=args.runs,
                                name="metadata_agent")
        print(summary.report())
        return 0 if summary.passed else 1

    result = run_one((script, profile))
    print("=== RAW RESPONSE ===")
    print(result.raw)
    print_metadata(result, "VALIDATION")
    return 0


if __name__ == "__main__":
    sys.exit(main())
