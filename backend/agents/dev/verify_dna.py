"""DNA agent verification per the Phase 2 Step 2 test plan (5 runs).

    backend/.venv/Scripts/python backend/agents/dev/verify_dna.py

Runs:
  Run 1: full catalog (8 videos)
  Run 2: full catalog again            -> compare substance to Run 1
  Run 3: only the 4 high performers    -> profile should emphasize their traits
  Run 4: only the 4 low performers     -> profile should flip (vague, abstract, long)
  Run 5: full catalog again            -> should look like Runs 1/2, not 3/4

For each run it prints the key profile fields compactly plus keyword signal
checks against the plan's done-definition, and verifies the benchmarks are
copied verbatim from the pre-calculated facts. Consistency judgment is made
by reading the printed fields across runs (the plan's own method).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from backend.agents.benchmarks import compute_performance_benchmarks  # noqa: E402
from backend.agents.dna_agent import run_dna_agent  # noqa: E402

CATALOG = Path(__file__).resolve().parent.parent.parent.parent / "data" / "seed" / "catalog.json"

HIGH_IDS = {"sv_001", "sv_002", "sv_004", "sv_007"}   # the four high performers
LOW_IDS = {"sv_003", "sv_005", "sv_006", "sv_008"}    # the bottom half of the catalog

SIGNALS = {
    "voice.first_person": ["i ", "i'm", "my ", "me "],
    "voice.specific_numbers": ["30 days", "9 am", "5 chrome", "3 hours", "30-day"],
    "voice.short_sentences": ["short", "punchy", "sentence"],
    "title.timeframe_structure": ["timeframe", "time-bound", "time bound", "for [", "for x days", "days"],
    "title.number_list": ["number", "listicle", "list"],
    "thumb.solid_color": ["solid color", "solid-color", "background"],
    "thumb.allcaps": ["all-caps", "all caps", "uppercase", "caps"],
    "thumb.creator_face": ["face", "creator"],
    "patterns.challenge_high": ["challenge", "experiment", "time-bound"],
    "patterns.comparison_high": ["comparison", "versus", "battle", "vs"],
    "patterns.tour_low": ["tour", "setup"],
    "patterns.vague_low": ["vague", "abstract", "general"],
}


def signals_present(text: str, keywords: list[str]) -> list[str]:
    t = text.lower()
    return [k for k in keywords if k in t]


def check_profile(profile, label: str, expected_benchmarks: dict) -> None:
    print(f"\n--- {label} ---")
    print(f"voice.tone:     {profile.voice.tone[:160]}")
    print(f"voice.pacing:   {profile.voice.pacing[:140]}")
    print(f"voice.hook:     {profile.voice.hook_pattern[:140]}")
    print(f"title.struct:   {profile.title_formula.structure[:140]}")
    print(f"title.examples: {profile.title_formula.example_titles}")
    print(f"thumb.bg:       {profile.thumbnail_style.background_type} | colors: {profile.thumbnail_style.dominant_colors}")
    print(f"thumb.layout:   {profile.thumbnail_style.layout_pattern[:130]}")
    print(f"thumb.text:     {profile.thumbnail_style.text_style[:130]}")
    print(f"thumb.face:     {profile.thumbnail_style.facial_expression[:130]}")
    print(f"formats:        {profile.content_patterns.format_preferences}")
    print(f"post.freq:      {profile.content_patterns.posting_frequency}")
    print(f"best topics:    {profile.content_patterns.best_performing_topics}")
    print(f"worst topics:   {profile.content_patterns.worst_performing_topics}")
    print(f"benchmarks:     {profile.performance_benchmarks.model_dump()}")

    # Verbatim-benchmark check (done-definition).
    b = profile.performance_benchmarks
    expected = expected_benchmarks
    exact = (b.avg_views == expected["avg_views"] and b.avg_ctr == expected["avg_ctr"]
             and b.avg_retention == expected["avg_retention"]
             and b.top_quartile_views == expected["top_quartile_views"]
             and b.bottom_quartile_views == expected["bottom_quartile_views"])
    print(f"benchmarks verbatim: {'YES' if exact else 'NO — MISMATCH'}")

    # Keyword signal report (informational — the plan judges substance by reading).
    blob = json.dumps(profile.model_dump(), indent=0)
    hits = []
    for sig, kws in SIGNALS.items():
        found = signals_present(blob, kws)
        hits.append(f"{sig}:{'+' if found else '-'}")
    print("signals:", " ".join(hits))


def main() -> int:
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    creator = data["creator_id"]
    videos = data["videos"]
    full_b = compute_performance_benchmarks(videos)
    high = [v for v in videos if v["id"] in HIGH_IDS]
    low = [v for v in videos if v["id"] in LOW_IDS]
    high_b = compute_performance_benchmarks(high)
    low_b = compute_performance_benchmarks(low)

    runs = [
        ("Run 1 — full catalog", videos, full_b),
        ("Run 2 — full catalog (consistency)", videos, full_b),
        ("Run 3 — 4 high performers", high, high_b),
        ("Run 4 — 4 low performers", low, low_b),
        ("Run 5 — full catalog (back to baseline)", videos, full_b),
    ]
    for label, subset, bm in runs:
        result = run_dna_agent(subset, bm, creator_id=creator)
        check_profile(result.validated, label, bm)
    print("\nAll 5 runs parsed + schema-validated. Review the printed fields for consistency per the plan.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
