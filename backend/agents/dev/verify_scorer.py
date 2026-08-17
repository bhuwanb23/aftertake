"""Scorer agent verification per the Phase 2 Step 7 test plan.

    backend/.venv/Scripts/python backend/agents/dev/verify_scorer.py

The scorer must be tested with deliberate BAD input — not just the happy
path. The plan's test matrix:

  PASS x5        real output from the other agents (cached asset_inputs.json)
                 -> pass, overall >= 0.75
  REJECT A       thumbnail violates the profile (blurred bg, no face, mixed
                 case) -> fail, reason cites thumbnail_style fields
  REJECT B       title violates the formula (vague, no number/timeframe/
                 first-person) -> fail, reason cites title_formula.structure
  REJECT C       borderline: thumbnail AND title each partially wrong -> fail
                 overall, reason identifies the dragging dimension(s)
  FIX-AND-RESUBMIT: A's thumbnail fixed per the critique + good title/voice
                 -> pass, thumbnail_fit_score >= 0.75

Every rejection reason must name a profile field AND the specific mismatch —
generic reasons are failures. All 9 runs are scorer calls; nothing else is
regenerated. Exit 1 on any hard failure.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from backend.agents.core import AgentOutputError  # noqa: E402
from backend.agents.dev.test_opportunity import get_dna_profile  # noqa: E402
from backend.agents.scorer_agent import run_scorer_agent  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent.parent
ASSET_CACHE = ROOT / "output" / "asset_inputs.json"


def check_specific(reason: str, fields: list[str], descriptors: list[str]) -> list[str]:
    """A specific rejection reason names a profile field AND the offending
    content. Return issues (empty = specific enough)."""
    r = reason.lower()
    issues = []
    if not any(f in r for f in fields):
        issues.append(f"reason cites no profile field from {fields}")
    if not any(d in r for d in descriptors):
        issues.append(f"reason names no specific mismatch from {descriptors}")
    return issues


def main() -> int:
    profile = get_dna_profile()
    asset = json.loads(ASSET_CACHE.read_text(encoding="utf-8"))
    good = {k: v for k, v in asset.items()}
    all_issues: list[str] = []

    # --- PASS x5 -------------------------------------------------------------
    for i in range(1, 6):
        try:
            r = run_scorer_agent(good["thumbnail_description"], good["title"],
                                 good["title_formula_match"], good["full_voiceover_text"],
                                 profile, asset_id="asset_good")
            q = r.validated
        except AgentOutputError as exc:
            all_issues.append(f"pass run {i}: scorer output failed ({str(exc)[:120]})")
            continue
        print(f"\n=== PASS run {i} === thumbnail={q.thumbnail_fit_score} "
              f"title={q.title_fit_score} voice={q.voice_fit_score} "
              f"overall={q.overall_score} passed={q.passed}")
        if not q.passed or q.overall_score < 0.75:
            all_issues.append(f"pass run {i}: scored {q.overall_score} — expected pass")

    # --- REJECT A: thumbnail violation --------------------------------------
    bad_thumb = ("Blurred desk background photo. No creator face visible. "
                 "Small text in mixed case reading 'why i switched to this "
                 "new productivity tool for my team'.")
    try:
        r = run_scorer_agent(bad_thumb, good["title"], good["title_formula_match"],
                             good["full_voiceover_text"], profile, asset_id="asset_a")
        q = r.validated
    except AgentOutputError as exc:
        all_issues.append(f"REJECT A failed to produce a score: {str(exc)[:120]}")
        q = None
    if q is not None:
        print(f"\n=== REJECT A (bad thumbnail) === thumbnail={q.thumbnail_fit_score} "
              f"title={q.title_fit_score} voice={q.voice_fit_score} "
              f"overall={q.overall_score} passed={q.passed}")
        print(f"  REASON: {q.rejection_reason}")
        if q.passed:
            all_issues.append("REJECT A: scorer PASSED a blurred/no-face/mixed-case thumbnail")
        else:
            all_issues += [f"REJECT A: {it}" for it in check_specific(
                q.rejection_reason or "", ["thumbnail_style", "background_type", "text_style"],
                ["blurr", "mixed case", "no face", "no creator face"])]

    # --- REJECT B: title violation ------------------------------------------
    bad_title = "My thoughts on productivity tools"
    bad_match = "The title is about productivity tools which is a popular topic."
    try:
        r = run_scorer_agent(good["thumbnail_description"], bad_title, bad_match,
                             good["full_voiceover_text"], profile, asset_id="asset_b")
        q = r.validated
    except AgentOutputError as exc:
        all_issues.append(f"REJECT B failed to produce a score: {str(exc)[:120]}")
        q = None
    if q is not None:
        print(f"\n=== REJECT B (bad title) === thumbnail={q.thumbnail_fit_score} "
              f"title={q.title_fit_score} voice={q.voice_fit_score} "
              f"overall={q.overall_score} passed={q.passed}")
        print(f"  REASON: {q.rejection_reason}")
        if q.passed:
            all_issues.append("REJECT B: scorer PASSED a vague formula-less title")
        else:
            all_issues += [f"REJECT B: {it}" for it in check_specific(
                q.rejection_reason or "", ["title_formula", "formula", "structure"],
                ["number", "timeframe", "first-person", "vague"])]

    # --- REJECT C: borderline (both partially wrong) -------------------------
    partial_thumb = ("Solid orange background. FACE placeholder centered. "
                     "Text in mixed case reads 'the honest ranking of five "
                     "tools for your workflow'.")
    partial_title = "I Compared Productivity Tools for 30 Days"  # number+timeframe+first-person, but NO caps word, NO qualifier
    try:
        r = run_scorer_agent(partial_thumb, partial_title, good["title_formula_match"],
                             good["full_voiceover_text"], profile, asset_id="asset_c")
        q = r.validated
    except AgentOutputError as exc:
        all_issues.append(f"REJECT C failed to produce a score: {str(exc)[:120]}")
        q = None
    if q is not None:
        print(f"\n=== REJECT C (borderline) === thumbnail={q.thumbnail_fit_score} "
              f"title={q.title_fit_score} voice={q.voice_fit_score} "
              f"overall={q.overall_score} passed={q.passed}")
        print(f"  REASON: {q.rejection_reason}")
        if q.passed:
            all_issues.append("REJECT C: borderline asset passed — scorer not calibrated")
        elif q.overall_score > 0.74:
            all_issues.append(f"REJECT C: overall {q.overall_score} too close to the bar — "
                              "the borderline test should sit clearly below 0.75")
        else:
            # The reason must identify WHICH dimension dragged it down.
            all_issues += [f"REJECT C: {it}" for it in check_specific(
                q.rejection_reason or "", ["title_formula", "thumbnail_style", "text_style", "structure"],
                ["mixed case", "caps", "number", "qualifier", "words"])]

    # --- FIX-AND-RESUBMIT: A's thumbnail fixed -------------------------------
    fixed_thumb = ("Solid red background. Creator face placeholder on the "
                   "left half, positioned for a surprised high-energy "
                   "expression. Bold white all-caps text '30 DAYS' on the "
                   "right.")
    try:
        r = run_scorer_agent(fixed_thumb, good["title"], good["title_formula_match"],
                             good["full_voiceover_text"], profile, asset_id="asset_d")
        q = r.validated
    except AgentOutputError as exc:
        all_issues.append(f"FIX run failed to produce a score: {str(exc)[:120]}")
        q = None
    if q is not None:
        print(f"\n=== FIX-AND-RESUBMIT (A fixed) === thumbnail={q.thumbnail_fit_score} "
              f"title={q.title_fit_score} voice={q.voice_fit_score} "
              f"overall={q.overall_score} passed={q.passed}")
        if q.thumbnail_fit_score < 0.75:
            all_issues.append(f"FIX run: thumbnail_fit {q.thumbnail_fit_score} — the fixed "
                              "thumbnail should pass the dimension")
        if not q.passed:
            all_issues.append(f"FIX run: overall {q.overall_score} — expected full pass after the fix")

    print("\n=== SUMMARY ===")
    if all_issues:
        print(f"HARD FAILURES: {len(all_issues)}")
        for it in all_issues:
            print(f"  - {it}")
        return 1
    print("ALL CHECKS PASS — 5/5 good assets pass (>=0.75), all three deliberate "
          "rejections fail with specific field-citing reasons, and the fixed "
          "asset passes the previously failing dimension.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
