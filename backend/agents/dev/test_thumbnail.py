"""Standalone dev script for the thumbnail agent (Phase 2 Step 4, Practice 1).

Loads the cached CreatorDNAProfile and the cached top ContentOpportunity
(generating each once if needed), runs the thumbnail agent, prints the raw
response and each validated variant, then RENDERS every SVG to
output/thumbnails/dev_*.png and reports the result — an SVG that does not
render is a prompt failure, not a Phase 3 problem.

    backend/.venv/Scripts/python backend/agents/dev/test_thumbnail.py [--runs N]
    backend/.venv/Scripts/python backend/agents/dev/test_thumbnail.py --regenerate

With --runs N (>1) it runs the Practice 6 stability harness. --regenerate
recreates the cached profile/opportunities instead of reusing them.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from backend.agents.dev.svgutil import png_dimensions, render_svg  # noqa: E402
from backend.agents.dev.test_opportunity import get_dna_profile  # noqa: E402
from backend.agents.core import run_stability  # noqa: E402
from backend.agents.opportunity_agent import run_opportunity_agent  # noqa: E402
from backend.agents.thumbnail_agent import run_thumbnail_agent  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent.parent
TRENDS_PATH = ROOT / "data" / "seed" / "trends.json"
OPPS_CACHE = ROOT / "output" / "opportunities.json"
THUMBS_DIR = ROOT / "output" / "thumbnails"


def get_top_opportunity(force: bool = False) -> dict:
    """Load the cached opportunity set (top one), generating it once if needed."""
    if not force and OPPS_CACHE.exists():
        return json.loads(OPPS_CACHE.read_text(encoding="utf-8"))[0]
    profile = get_dna_profile()
    trends = json.loads(TRENDS_PATH.read_text(encoding="utf-8"))
    result = run_opportunity_agent(profile, trends, creator_id=profile.creator_id)
    opps = [o.model_dump() for o in result.validated]
    OPPS_CACHE.parent.mkdir(parents=True, exist_ok=True)
    OPPS_CACHE.write_text(json.dumps(opps, indent=2), encoding="utf-8")
    print(f"(opportunities generated and cached to {OPPS_CACHE})")
    return opps[0]


def print_variants(result, label: str, render: bool = True) -> None:
    print(f"\n=== {label} ===")
    variants = result.validated
    print(f"count: {len(variants)} (must be exactly 3)")
    for v in variants:
        print(f"--- {v.id} variant {v.variant_number} selected={v.selected} png_path={v.png_path}")
        print(f"  layout_description: {v.layout_description}")
        svg = v.svg_source
        print(f"  svg: {len(svg)} chars, starts <svg: {svg.lstrip().startswith('<svg')}, "
              f"ends </svg>: {svg.rstrip().endswith('</svg>')}")
        if render:
            try:
                png = render_svg(svg)
                w, h = png_dimensions(png)
                path = THUMBS_DIR / f"dev_{v.id}.png"
                path.write_bytes(png)
                print(f"  RENDER OK: {w}x{h}, {len(png)} bytes -> {path}")
            except Exception as exc:  # noqa: BLE001 — render failure is the finding
                print(f"  RENDER FAILED: {type(exc).__name__}: {str(exc)[:200]}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Dev-test the thumbnail agent in isolation.")
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--regenerate", action="store_true", help="Regenerate cached profile/opportunities")
    args = parser.parse_args()

    profile = get_dna_profile(force=args.regenerate)
    opportunity = get_top_opportunity(force=args.regenerate)
    creator = profile.creator_id

    def run_one(inp):
        opp, prof = inp
        return run_thumbnail_agent(opp, prof, asset_id=f"asset_{creator}")

    if args.runs > 1:
        summary = run_stability(run_one, [(opportunity, profile)], runs_per_input=args.runs,
                                name="thumbnail_agent")
        print(summary.report())
        return 0 if summary.passed else 1

    result = run_one((opportunity, profile))
    print("=== RAW RESPONSE ===")
    print(result.raw)
    print_variants(result, "VALIDATION")
    return 0


if __name__ == "__main__":
    sys.exit(main())
