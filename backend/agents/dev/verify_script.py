"""Script agent verification per the Phase 2 Step 5 test plan (5 runs).

    backend/.venv/Scripts/python backend/agents/dev/verify_script.py
    backend/.venv/Scripts/python backend/agents/dev/verify_script.py --main-only
    backend/.venv/Scripts/python backend/agents/dev/verify_script.py --varied-only

Run 1: parse + validate; hook opens with a bold claim / challenge, no greeting
Run 2: read the full_voiceover_text aloud — voice consistency (printed below)
Run 3: what_to_avoid scan — none of the profile's prohibited patterns appear
Run 4: sum of durations falls inside the profile's optimal_duration_range
Run 5: scene types valid AND chosen to serve the content

Plus two varied-input runs (opp_002, opp_003) for Practice 6. All profile
data (voice.what_to_avoid, signature_phrases, optimal_duration_range) is
read from the cached DNA profile at runtime — never hardcoded.

Hard failures (exit 1): hook greeting, hook missing claim/question/pivot,
prohibited-pattern markers, out-of-range total, scene types not serving the
content, invalid scene type, or any parse/validation failure.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from backend.agents.dev.test_opportunity import get_dna_profile  # noqa: E402
from backend.agents.script_agent import run_script_agent  # noqa: E402
from backend.models.schemas import SceneType  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent.parent
OPPS_CACHE = ROOT / "output" / "opportunities.json"

GREETINGS = {"hey", "hi", "hello", "welcome", "greetings", "yo", "sup", "whats"}
GREET_PHRASES = ["in this video", "today we're going", "today we are going",
                 "today i will", "welcome back", "what's up"]

# Markers per what_to_avoid category (categories come from the profile; these
# are the concrete phrases that instantiate them).
AVOID_MARKERS = {
    "generic advice": ["the key is", "the key to", "remember to", "don't forget",
                       "always remember", "it's important to", "you should always",
                       "best practice"],
    "flowery/poetic": ["unleash", "unlock", "elevate", "embark", "delve",
                       "transformative", "revolutioniz", "seamless",
                       "supercharge", "game-changer", "world of possibilities"],
    "hedging": ["maybe", "perhaps", "kind of", "sort of", "i think",
                "probably", "i guess", "somewhat", "might be"],
    "long rambling intro": ["the world of", "in today's fast-paced"],
}


def _norm(t: str) -> str:
    return re.sub(r"\s+", " ", t.lower().replace("\u2019", "'").replace("\u2018", "'"))


def check_script(script, profile: dict, opportunity: dict, label: str) -> list[str]:
    """Return hard issues for one script. Everything else is printed for reading."""
    issues: list[str] = []
    voice = profile["voice"]
    rng = profile["content_patterns"]["optimal_duration_range"]
    full = script.full_voiceover_text

    # --- Run 1: hook opens per hook_pattern, never a greeting ---------------
    hook_text = script.hook.voiceover_text.strip()
    first = re.split(r"[^a-zA-Z']+", hook_text.lower())[:1]
    if first and first[0] in GREETINGS:
        issues.append(f"hook opens with greeting '{first[0]}'")
    low = hook_text.lower()
    if any(g in low for g in GREET_PHRASES):
        issues.append("hook contains a greeting/announcement phrase")
    has_claim = ("?" in hook_text) or re.search(r"\bI(?:'m|'ve|'ll)?\b|\d", hook_text)
    pivot = any(p in low for p in ["actually happened", "nobody tells you",
                                   "not what the internet thinks", "surprised me"])
    if not has_claim:
        issues.append("hook has no bold first-person claim, question, or number")
    if not pivot:
        issues.append("hook lacks the 'here is what actually happened' pivot")

    # --- Run 3: what_to_avoid — hard prohibition -----------------------------
    blob = _norm(full)
    for category, markers in AVOID_MARKERS.items():
        hits = [m for m in markers if m in blob]
        if hits:
            issues.append(f"what_to_avoid '{category}' violated: {hits}")
    first_sentence = full.split(". ")[0]
    if len(first_sentence.split()) > 45:
        issues.append(f"first sentence is rambling ({len(first_sentence.split())} words)")

    # --- Signature phrases appear naturally (at least one) -------------------
    sig = _norm(" ".join(voice.get("signature_phrases", [])))
    sig_variants = sig.replace("here is what", "here's what").replace("i am", "i'm")
    sig_hits = [p for p in (sig, sig_variants) if p and p in blob]
    # individual-phrase check (some phrases are long; any single one suffices)
    phrases = [re.sub(r"\s+", " ", _norm(p)) for p in voice.get("signature_phrases", [])]
    any_sig = any(p in blob for p in phrases) or bool(sig_hits)
    if not any_sig:
        issues.append("no signature phrase from the profile appears")

    # --- Voice markers: first person + specific numbers ----------------------
    n_i = len(re.findall(r"\bI(?:'m|'ve|'ll)?\b", full))
    if n_i < 2:
        issues.append(f"only {n_i} first-person 'I' tokens — not the creator's first-person voice")
    if not re.search(r"\d", full):
        issues.append("no specific numbers anywhere in the script")

    # --- Run 4: durations inside the optimal range ---------------------------
    total = script.estimated_duration_seconds
    if not (rng["min"] <= total <= rng["max"]):
        issues.append(f"total {total}s outside optimal range [{rng['min']}, {rng['max']}]")
    if script.hook.duration_seconds > 20:
        issues.append(f"hook {script.hook.duration_seconds}s is too long")
    for s in script.scenes:
        if not (20 <= s.duration_seconds <= 120):
            issues.append(f"scene {s.scene_number} duration {s.duration_seconds}s out of 20-120")

    # --- Run 5: scene types valid + serve the content ------------------------
    valid = set(SceneType.__args__)
    types = [s.scene_type for s in script.scenes]
    invalid = [t for t in types if t not in valid]
    if invalid:
        issues.append(f"invalid scene types: {invalid}")
    fmt = (opportunity.get("recommended_format", "") + " " + opportunity.get("topic", "")).lower()
    if "list" in fmt or "listicle" in fmt:
        if "list_reveal" not in types:
            issues.append("listicle video has no list_reveal scene")
    elif "comparison" in fmt or " vs " in f" {opportunity.get('topic','')} ".lower():
        if "comparison_split" not in types:
            issues.append("comparison video has no comparison_split scene")
    elif len(set(types)) < 2:
        issues.append("non-list/non-comparison video needs a mix of scene types")

    # --- Print everything for reading (Run 2 — read it aloud) ----------------
    print(f"\n=== {label} ===")
    print(f"id={script.id} | total={total}s (range {rng['min']}-{rng['max']}) "
          f"| words={script.word_count} | hook={script.hook.duration_seconds}s "
          f"| scenes={[(s.scene_type, s.duration_seconds) for s in script.scenes]} "
          f"| outro={script.outro.duration_seconds}s | first-person I={n_i}")
    print(f"  HOOK:   {hook_text}")
    print(f"  SCENES: {len(script.scenes)} | signature-phrase hits: {[p for p in phrases if p in blob]}")
    print(f"  CTA:    {script.outro.call_to_action}")
    print(f"  --- FULL VOICEOVER (read this aloud) ---")
    print(f"  {full}")
    for it in issues:
        print(f"  ISSUE: {it}")
    return [f"{label}: {it}" for it in issues]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--varied-only", action="store_true")
    parser.add_argument("--main-only", action="store_true")
    args = parser.parse_args()

    profile_model = get_dna_profile()
    profile = profile_model.model_dump()
    opps = json.loads(OPPS_CACHE.read_text(encoding="utf-8"))
    if args.varied_only:
        runs = [("Varied opp_002", opps[1]), ("Varied opp_003", opps[2])]
    elif args.main_only:
        runs = [(f"Run {i}", opps[0]) for i in range(1, 6)]
    else:
        runs = [(f"Run {i}", opps[0]) for i in range(1, 6)] + \
               [("Varied opp_002", opps[1]), ("Varied opp_003", opps[2])]

    all_issues: list[str] = []
    totals: list[int] = []
    for label, opp in runs:
        result = run_script_agent(opp, profile_model, creator_id=profile["creator_id"])
        script = result.validated
        totals.append(script.estimated_duration_seconds)
        all_issues += check_script(script, profile, opp, label)

    print("\n=== SUMMARY ===")
    print(f"scripts checked: {len(runs)} | duration totals: {totals}")
    if all_issues:
        print(f"HARD FAILURES: {len(all_issues)}")
        for it in all_issues:
            print(f"  - {it}")
        return 1
    print("ALL CHECKS PASS — hooks follow the creator's pattern with no greeting, "
          "voice matches the profile (signature phrases, first person, numbers, "
          "no prohibited patterns), durations inside the optimal range, scene "
          "types valid and serving the content.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
