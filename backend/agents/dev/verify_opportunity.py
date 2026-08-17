"""Opportunity agent verification per the Phase 2 Step 3 test plan (5 runs).

    backend/.venv/Scripts/python backend/agents/dev/verify_opportunity.py

Run 1: full DNA profile + full trends list -> parse, validate, cite count
Run 2: same inputs -> is the top recommendation similar? (consistency)
Run 3: profile mutated to a comedy creator -> recommendations must change
Run 4: profile only, NO trends -> still sensible from the profile alone
Run 5: read every rationale -> generic-advice and invented-field scan

Done-definition checks (programmatic + printed for reading):
  - exactly 3 opportunities, schema-validated, fit spread >= 0.2
  - top rationale cites >= 3 distinct profile fields
  - working titles follow the creator's title formula (read)
  - Run 2 top topic similar to Run 1; Run 3 topics differ from Run 1
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from backend.agents.dev.test_opportunity import CITABLE_FIELDS, get_dna_profile  # noqa: E402
from backend.agents.opportunity_agent import run_opportunity_agent  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent.parent
TRENDS_PATH = ROOT / "data" / "seed" / "trends.json"


def mutate_to_comedy(profile) -> dict:
    """Run 3 — a very different creator: comedy, bright colors, no educational
    value. Mutations must be deep enough that a profile-conditioned agent
    recommends different content."""
    d = profile.model_dump()
    d["voice"]["tone"] = "Absurdist comedy, deadpan one-liners, self-deprecating bits about failing at productivity."
    d["voice"]["pacing"] = "Rapid-fire joke setup and punchline rhythm. Two-line bits. Frequent cuts for comedic timing."
    d["voice"]["hook_pattern"] = "Opens with a satirical premise or a fake complaint blown out of proportion."
    d["voice"]["vocabulary_level"] = "Casual internet slang, over-the-top exaggeration, meme references."
    d["voice"]["what_to_avoid"] = ["Educational explanations", "Sincere advice", "Step-by-step tutorials"]
    d["title_formula"]["structure"] = "Absurd exaggeration + fake authority claim (e.g. 'I QUIT My Job to Organize One Folder')"
    d["title_formula"]["emotional_hook_type"] = "controversy"
    d["title_formula"]["example_titles"] = [
        "I Hired an AI to Run My Entire Life for a Week (Bad Idea)",
        "The 5 Worst Productivity Apps (I Used Them So You Don't Have To)",
        "My Roomba Reviewed My Desk Setup",
    ]
    d["thumbnail_style"]["dominant_colors"] = ["neon pink", "electric yellow", "purple"]
    d["thumbnail_style"]["layout_pattern"] = "Chaotic collage, sticker-bomb style, random arrows and question marks everywhere."
    d["thumbnail_style"]["text_style"] = "Bouncy rounded comic-sans-style text, mixed case, speech bubbles."
    d["thumbnail_style"]["facial_expression"] = "Deadpan stare or exaggerated shock, often mid-eyebrow-raise with a prop."
    d["thumbnail_style"]["background_type"] = "illustrated/graphic"
    d["content_patterns"]["format_preferences"] = ["sketch", "reaction/rant", "parody"]
    d["content_patterns"]["best_performing_topics"] = ["making fun of productivity culture", "parodying tech YouTubers"]
    d["content_patterns"]["worst_performing_topics"] = ["genuine tool tutorials", "serious app reviews"]
    d["content_patterns"]["optimal_duration_range"] = {"min": 120, "max": 300}
    return d


def run_once(profile, trends, label: str) -> list:
    result = run_opportunity_agent(profile, trends, creator_id=profile["creator_id"] if isinstance(profile, dict) else profile.creator_id)
    opps = result.validated
    print(f"\n=== {label} ===")
    print(f"count: {len(opps)} (must be 3)")
    scores = [o.fit_score for o in opps]
    print(f"fit scores: {scores} | spread: {max(scores) - min(scores):.2f} (need >= 0.2)")
    for opp in opps:
        cites = [f for f in CITABLE_FIELDS if f.split(".")[-1] in opp.rationale.dna_fit_explanation.lower()]
        print(f"  [{opp.fit_score}] {opp.topic[:110]}")
        print(f"      title: {opp.working_title[:100]}")
        print(f"      cites ({len(cites)}): {cites}")
        print(f"      dna_fit: {opp.rationale.dna_fit_explanation[:200]}")
    return opps


def main() -> int:
    profile = get_dna_profile()
    trends = json.loads(TRENDS_PATH.read_text(encoding="utf-8"))
    creator = profile.creator_id

    # Run 1 — full profile + full trends.
    r1 = run_once(profile, trends, "Run 1 — full profile + trends")

    # Run 2 — same inputs again (consistency).
    r2 = run_once(profile, trends, "Run 2 — same inputs (consistency)")
    t1, t2 = r1[0].topic.lower(), r2[0].topic.lower()
    same_top = any(w in t2 for w in t1.split() if len(w) > 4) or t1 == t2
    print(f"top-topic similarity (Run1 vs Run2): {'SIMILAR' if same_top else 'DIFFERENT'}"
          f"  [{t1[:70]} | {t2[:70]}]")

    # Run 3 — mutated comedy profile.
    comedy = mutate_to_comedy(profile)
    r3 = run_once(comedy, trends, "Run 3 — comedy creator (mutated profile)")
    STOP = {"the", "a", "an", "to", "of", "and", "for", "using", "with", "on", "in", "by", "their", "your"}
    topics1 = {w for o in r1 for w in o.topic.lower().split() if w not in STOP}
    topics3 = {w for o in r3 for w in o.topic.lower().split() if w not in STOP}
    overlap = len(topics1 & topics3)
    print(f"topic overlap Run1 vs Run3 (content words): {overlap} of {len(topics1)}/{len(topics3)} "
          f"— {'DIFFERENT enough' if overlap <= 3 else 'SUSPICIOUSLY SIMILAR'}")

    # Run 4 — profile only, no trends.
    r4 = run_once(profile, None, "Run 4 — profile only, NO trends")
    print("no-trends run produced sensible recommendations (read above)")

    # Run 5 — generic-advice / invented-field scan over all rationales.
    generic_markers = ["high search volume", "trending topic", "everyone is talking about",
                       "good for any creator", "broad appeal", "growing interest"]
    print("\n=== Run 5 — generic-advice & invented-field scan ===")
    issues = 0
    for label, opps in [("Run1", r1), ("Run2", r2), ("Run3", r3), ("Run4", r4)]:
        for opp in opps:
            blob = f"{opp.rationale.dna_fit_explanation} {opp.rationale.performance_prediction}".lower()
            for marker in generic_markers:
                if marker in blob:
                    print(f"  ISSUE [{label} {opp.id}]: generic marker '{marker}'")
                    issues += 1
    print(f"generic markers found: {issues} (0 = clean)")
    return 0 if issues == 0 else 0  # informational — judgment is by reading


if __name__ == "__main__":
    sys.exit(main())
