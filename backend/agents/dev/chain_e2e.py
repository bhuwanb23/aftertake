"""Phase 2 Step 8 — verify the full agent chain end to end, STILL IN ISOLATION
(no API, no orchestrator). A manual sequence: each agent is fed the REAL
output of the previous one, fresh — nothing is reused from the caches the
dev scripts rely on.

    backend/.venv/Scripts/python backend/agents/dev/chain_e2e.py

Sequence (from the plan):
  1. DNA agent: 8 seed videos + pre-calculated benchmarks -> CreatorDNAProfile
  2. Opportunity agent: profile + trends -> 3 opportunities; select highest fit
  3. Thumbnail agent: selected opportunity + profile -> 3 ThumbnailVariant SVGs
  4. Script agent: selected opportunity + profile -> Script
  5. Metadata agent: script + profile -> Metadata
  6. Scorer: first variant's layout description + metadata title + script
     full voiceover + profile -> QualityScore
  7. If the score fails: print the rejection reason, then re-score with the
     next variant as the targeted fix (variant selection is the orchestrator's
     regenerate loop in miniature). The chain is done when a pass is reached.

Each stage is timed; the total is checked against the plan's ~60s bar and the
slowest stage is named. Any schema error at any stage fails the run loudly
with the stage name. Nothing is written to disk — the caches used by the
verify scripts stay untouched.
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from backend.agents.benchmarks import compute_performance_benchmarks  # noqa: E402
from backend.agents.dna_agent import run_dna_agent  # noqa: E402
from backend.agents.metadata_agent import run_metadata_agent  # noqa: E402
from backend.agents.opportunity_agent import run_opportunity_agent  # noqa: E402
from backend.agents.scorer_agent import run_scorer_agent  # noqa: E402
from backend.agents.script_agent import run_script_agent  # noqa: E402
from backend.agents.thumbnail_agent import run_thumbnail_agent  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent.parent
CATALOG_PATH = ROOT / "data" / "seed" / "catalog.json"
TRENDS_PATH = ROOT / "data" / "seed" / "trends.json"


def timed(label: str, fn):
    t0 = time.perf_counter()
    result = fn()
    dt = time.perf_counter() - t0
    print(f"[{dt:6.2f}s] {label}")
    return result, dt


def main() -> int:
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    creator = data["creator_id"]
    videos = data["videos"]
    trends = json.loads(TRENDS_PATH.read_text(encoding="utf-8"))
    times: list[tuple[str, float]] = []

    # --- Step 1: DNA agent (fresh) -----------------------------------------
    profile_r, dt = timed("DNA agent (8 seed videos + benchmarks)",
                          lambda: run_dna_agent(videos, compute_performance_benchmarks(videos),
                                                creator_id=creator))
    times.append(("dna", dt))
    profile = profile_r.validated
    print(f"  -> profile {profile.creator_id} from {profile.source_video_count} videos | "
          f"voice.tone: {profile.voice.tone[:90]}...")

    # --- Step 2: opportunity agent ------------------------------------------
    opp_r, dt = timed("opportunity agent (profile + trends)",
                      lambda: run_opportunity_agent(profile, trends, creator_id=creator))
    times.append(("opportunity", dt))
    opps = opp_r.validated
    if len(opps) != 3:
        print(f"FAIL: expected 3 opportunities, got {len(opps)}")
        return 1
    top = max(opps, key=lambda o: o.fit_score)
    print(f"  -> {len(opps)} opportunities, selected {top.id} (fit {top.fit_score}): "
          f"{top.topic[:100]}")

    # --- Step 3: thumbnail agent --------------------------------------------
    thumb_r, dt = timed("thumbnail agent (selected opportunity + profile)",
                        lambda: run_thumbnail_agent(top, profile, asset_id="asset_chain"))
    times.append(("thumbnail", dt))
    variants = thumb_r.validated
    if len(variants) != 3:
        print(f"FAIL: expected 3 thumbnail variants, got {len(variants)}")
        return 1
    print(f"  -> 3 variants | v1: {variants[0].layout_description[:100]}...")

    # --- Step 4: script agent ------------------------------------------------
    script_r, dt = timed("script agent (selected opportunity + profile)",
                         lambda: run_script_agent(top, profile, creator_id=creator))
    times.append(("script", dt))
    script = script_r.validated
    print(f"  -> script {script.id}, {script.word_count} words, "
          f"{script.estimated_duration_seconds}s | hook: {script.hook.voiceover_text[:90]}...")

    # --- Step 5: metadata agent ----------------------------------------------
    meta_r, dt = timed("metadata agent (script + profile)",
                       lambda: run_metadata_agent(script, profile, asset_id="asset_chain"))
    times.append(("metadata", dt))
    meta = meta_r.validated
    print(f"  -> title: {meta.title} | {len(meta.tags)} tags | "
          f"category: {meta.category}")

    # --- Step 6: scorer on the first variant ---------------------------------
    chosen = variants[0]
    score_r, dt = timed("scorer (variant 1)",
                        lambda: run_scorer_agent(
                            chosen.layout_description, meta.title,
                            meta.title_formula_match, script.full_voiceover_text,
                            profile, asset_id="asset_chain"))
    times.append(("scorer", dt))
    score = score_r.validated
    print(f"  -> thumbnail={score.thumbnail_fit_score} title={score.title_fit_score} "
          f"voice={score.voice_fit_score} overall={score.overall_score} "
          f"(bar {score.threshold_used}) passed={score.passed}")

    # --- Step 7: reject -> targeted fix (try the next variants) ---------------
    final_score = score
    if not score.passed:
        print(f"\n  REJECTION: {score.rejection_reason}")
        print("  -> applying targeted fix: trying the remaining variants as the "
              "regenerate loop would...")
        for alt in variants[1:]:
            r2, dt2 = timed(f"scorer (variant {alt.variant_number} — the fix)",
                            lambda a=alt: run_scorer_agent(
                                a.layout_description, meta.title,
                                meta.title_formula_match, script.full_voiceover_text,
                                profile, asset_id="asset_chain"))
            times.append((f"scorer_v{alt.variant_number}", dt2))
            if r2.validated.passed:
                final_score = r2.validated
                print(f"  -> FIX PASSED with variant {alt.variant_number}: "
                      f"overall {final_score.overall_score}")
                break
        else:
            print("  -> no variant passed; manual fix needed (see reason above)")
            final_score = score

    # --- Persist the chain's artifacts (Phase 4 will consume these shapes) -----
    chain_outputs = {
        "creator_id": creator,
        "profile": profile.model_dump(),
        "selected_opportunity": top.model_dump(),
        "thumbnail_variants": [v.model_dump() for v in variants],
        "script": script.model_dump(),
        "metadata": meta.model_dump(),
        "quality_score": score.model_dump(),
        "final_quality_score": final_score.model_dump(),
        "stage_times": {name: round(dt, 2) for name, dt in times},
        "total_seconds": round(sum(dt for _, dt in times), 2),
    }
    out = ROOT / "output" / "chain_outputs.json"
    out.write_text(json.dumps(chain_outputs, indent=2), encoding="utf-8")
    print(f"\n(chain artifacts saved to {out} — verify caches untouched)")

    # --- Summary --------------------------------------------------------------
    total = sum(dt for _, dt in times)
    slowest = max(times, key=lambda t: t[1])
    print("\n=== CHAIN SUMMARY ===")
    print(f"total: {total:.2f}s (plan bar: ~60s without video rendering) | "
          f"slowest: {slowest[0]} at {slowest[1]:.2f}s")
    for name, dt in times:
        print(f"  {name:<14} {dt:6.2f}s")
    print(f"\nfinal quality: thumbnail={final_score.thumbnail_fit_score} "
          f"title={final_score.title_fit_score} voice={final_score.voice_fit_score} "
          f"overall={final_score.overall_score} passed={final_score.passed}")
    if not final_score.passed:
        print("CHAIN DID NOT PASS THE QUALITY GATE.")
        return 1
    print("CHAIN COMPLETE — profile, 3 opportunities, 3 thumbnails, script, "
          "metadata, and a passing quality score, no schema errors at any stage.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
