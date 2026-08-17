"""Standalone dev script for the script agent (Phase 2 Step 5, Practice 1).

Loads the cached CreatorDNAProfile and the cached top ContentOpportunity,
runs the script agent, prints the raw response and the validated script with
its computed facts (duration total vs optimal range, word count).

    backend/.venv/Scripts/python backend/agents/dev/test_script.py [--runs N]

With --runs N (>1) it runs the Practice 6 stability harness.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

# Windows consoles default to cp1252 — model text can contain unicode (arrows,
# em dashes) that would crash print().
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from backend.agents.core import run_stability  # noqa: E402
from backend.agents.dev.test_opportunity import get_dna_profile  # noqa: E402
from backend.agents.script_agent import run_script_agent  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent.parent
OPPS_CACHE = ROOT / "output" / "opportunities.json"


def get_top_opportunity() -> dict:
    return json.loads(OPPS_CACHE.read_text(encoding="utf-8"))[0]


def print_script(result, label: str) -> None:
    print(f"\n=== {label} ===")
    s = result.validated
    print(f"id={s.id} opp={s.opportunity_id} creator={s.creator_id} "
          f"est_duration={s.estimated_duration_seconds}s words={s.word_count}")
    print(f"--- HOOK ({s.hook.duration_seconds}s) ---")
    print(f"  vo:  {s.hook.voiceover_text}")
    print(f"  vis: {s.hook.visual_description}")
    for scene in s.scenes:
        print(f"--- SCENE {scene.scene_number} [{scene.scene_type}] ({scene.duration_seconds}s) ---")
        print(f"  vo:  {scene.voiceover_text}")
        print(f"  vis: {scene.visual_description}")
        if scene.on_screen_text:
            print(f"  ost: {scene.on_screen_text}")
    print(f"--- OUTRO ({s.outro.duration_seconds}s) ---")
    print(f"  vo:  {s.outro.voiceover_text}")
    print(f"  cta: {s.outro.call_to_action}")
    print(f"--- FULL VOICEOVER ({s.word_count} words) ---")
    print(s.full_voiceover_text)


def main() -> int:
    parser = argparse.ArgumentParser(description="Dev-test the script agent in isolation.")
    parser.add_argument("--runs", type=int, default=1)
    args = parser.parse_args()

    profile = get_dna_profile()
    opportunity = get_top_opportunity()
    creator = profile.creator_id

    def run_one(inp):
        opp, prof = inp
        return run_script_agent(opp, prof, creator_id=creator)

    if args.runs > 1:
        summary = run_stability(run_one, [(opportunity, profile)], runs_per_input=args.runs,
                                name="script_agent")
        print(summary.report())
        return 0 if summary.passed else 1

    result = run_one((opportunity, profile))
    print("=== RAW RESPONSE ===")
    print(result.raw)
    print_script(result, "VALIDATION")
    return 0


if __name__ == "__main__":
    sys.exit(main())
