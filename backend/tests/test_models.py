"""Phase 1 Step 1 model validation tests — plain-python, run directly:

    backend/.venv/Scripts/python backend/tests/test_models.py

For every model: a valid instance must construct, and each invalid mutation
must be rejected with a ValidationError. Covers Source Video, Creator DNA
Profile, Content Opportunity, Script, Thumbnail Variant, Metadata, and
Quality Score (remaining models added with the rest of Step 1).
"""
import sys
from copy import deepcopy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from pydantic import ValidationError  # noqa: E402

from backend.models.schemas import (  # noqa: E402
    ContentOpportunity,
    CreatorDNAProfile,
    Metadata,
    QualityScore,
    Script,
    SourceVideo,
    ThumbnailVariant,
)

ok = fail = 0


def check(name, cond):
    global ok, fail
    if cond:
        ok += 1
        print(f"  PASS {name}")
    else:
        fail += 1
        print(f"  FAIL {name}")


def rejects(mut, label, cls, valid):
    v = deepcopy(valid)
    mut(v)
    try:
        cls(**v)
        check(label, False)
    except ValidationError:
        check(label, True)


# --- Fixtures ---------------------------------------------------------------
VALID_VIDEO = {
    "id": "sv_001",
    "title": "I Used Notion for 30 Days",
    "description": "",
    "transcript": "So I gave Notion an honest 30 days.",
    "duration_seconds": 487,
    "published_at": "2024-01-15",
    "platform": "youtube",
    "performance": {"views": 420000, "likes": 18400, "comments": 1240, "shares": 300,
                    "ctr": 9.2, "avg_retention": 58.0, "watch_time_hours": 68.0},
    "thumbnail": {"url": "", "description": "Orange background. Creator surprised. Text '30 DAYS'."},
    "tags": ["notion", "productivity"],
    "category": "Science & Technology",
}

VALID_PROFILE = {
    "creator_id": "creator_001",
    "source_video_count": 8,
    "voice": {"tone": "t", "pacing": "p", "hook_pattern": "h", "vocabulary_level": "v",
              "signature_phrases": ["Here's the thing"], "what_to_avoid": ["Corporate language"]},
    "title_formula": {"structure": "I [did X] for [Y] — here's what happened", "avg_word_count": 9,
                      "uses_caps": True, "uses_numbers": True, "uses_questions": False,
                      "emotional_hook_type": "curiosity gap",
                      "example_titles": ["I Used Notion for 30 Days"]},
    "thumbnail_style": {"dominant_colors": ["red", "white"], "layout_pattern": "l", "text_style": "t",
                        "facial_expression": "f", "uses_props": True, "background_type": "solid color",
                        "uses_graphic_elements": False},
    "content_patterns": {"avg_duration_seconds": 472, "optimal_duration_range": {"min": 324, "max": 487},
                         "format_preferences": ["30-day-challenge"], "posting_frequency": "2-3/week",
                         "best_performing_topics": ["productivity apps"],
                         "worst_performing_topics": ["setup tours"]},
    "performance_benchmarks": {"avg_views": 226625.0, "avg_ctr": 6.5, "avg_retention": 50.1,
                               "top_quartile_views": 420000.0, "bottom_quartile_views": 28000.0},
}

VALID_OPP = {
    "id": "opp_001", "creator_id": "creator_001",
    "topic": "Testing 5 AI writing tools for a month",
    "working_title": "I Tested 5 AI Writing Tools for 30 Days", "created_at": "",
    "rationale": {"dna_fit_explanation": "Maps to your top format (30-day challenge).",
                  "performance_prediction": "Top CTR videos are comparisons.",
                  "trend_relevance": "AI tools trending.", "risks": "Access to all 5 tools."},
    "fit_score": 0.87, "confidence": "high", "recommended_format": "30-day-challenge",
    "recommended_duration_seconds": 360, "target_hook": "Open with total cost.", "status": "pending",
}

VALID_SCRIPT = {
    "id": "sc_001", "opportunity_id": "opp_001", "creator_id": "creator_001",
    "hook": {"voiceover_text": "Five tools. One month.", "visual_description": "Orange bg, creator face.",
             "duration_seconds": 15},
    "scenes": [{"scene_number": 1, "scene_type": "list_reveal", "voiceover_text": "Here is the ranking.",
                "visual_description": "Grid of icons.", "on_screen_text": "5 TOOLS", "duration_seconds": 100}],
    "outro": {"voiceover_text": "Subscribe.", "visual_description": "Black bg.",
              "call_to_action": "Subscribe for the 60-day follow-up", "duration_seconds": 35},
    "full_voiceover_text": "Five tools. One month. Here is the ranking. Subscribe.",
    "estimated_duration_seconds": 150, "word_count": 8,
}

VALID_THUMB = {"id": "t1", "asset_id": "a1", "variant_number": 1, "svg_source": "<svg/>",
               "png_path": None, "layout_description": "Red bg, bold text.", "selected": False}

VALID_META = {"id": "m1", "asset_id": "a1", "title": "I Tested 5 AI Writing Tools for 30 Days",
              "title_formula_match": "Follows the 'I tested X for Y days' structure.",
              "description": "Full description with timestamps.",
              "tags": ["ai tools", "writing", "test", "ranking", "productivity"],
              "category": "Tech", "scheduled_publish_time": None, "platform_targets": ["youtube"]}


def valid_qs(**over):
    base = {"asset_id": "a1", "overall_score": 0.81, "thumbnail_fit_score": 0.88,
            "title_fit_score": 0.84, "voice_fit_score": 0.79}
    base.update(over)
    return base


# --- Source Video ------------------------------------------------------------
check("SV valid constructs", SourceVideo(**VALID_VIDEO).id == "sv_001")
check("SV null ctr stays null (unknown != zero)",
      SourceVideo(**{**VALID_VIDEO, "performance": {**VALID_VIDEO["performance"], "ctr": None}}).performance.ctr is None)
check("SV empty tags allowed", SourceVideo(**{**VALID_VIDEO, "tags": []}).tags == [])
check("SV empty thumbnail url allowed (seed data)", SourceVideo(**VALID_VIDEO).thumbnail.url == "")
for mut, label in [
    (lambda v: v.pop("id"), "SV missing id rejected"),
    (lambda v: v.pop("title"), "SV missing title rejected"),
    (lambda v: v.pop("transcript"), "SV missing transcript rejected"),
    (lambda v: v.__setitem__("duration_seconds", 60.5), "SV float duration rejected"),
    (lambda v: v.__setitem__("duration_seconds", 487.0), "SV integral-float duration rejected"),
    (lambda v: v.__setitem__("duration_seconds", -10), "SV negative duration rejected"),
    (lambda v: v.__setitem__("published_at", "March 15, 2024"), "SV freeform date rejected"),
    (lambda v: v.__setitem__("published_at", "2024-13-45"), "SV impossible date rejected"),
    (lambda v: v.__setitem__("platform", "twitch"), "SV unknown platform rejected"),
    (lambda v: v["thumbnail"].__setitem__("description", ""), "SV empty thumbnail description rejected"),
    (lambda v: v["thumbnail"].__setitem__("description", "   "), "SV whitespace-only description rejected"),
    (lambda v: v["performance"].__setitem__("views", "420000"), "SV string views rejected"),
    (lambda v: v["performance"].__setitem__("views", 420000.0), "SV float views rejected"),
    (lambda v: v["performance"].__setitem__("views", -5), "SV negative views rejected"),
    (lambda v: v["performance"].__setitem__("ctr", 150.0), "SV ctr > 100 rejected"),
    (lambda v: v.__setitem__("tags", None), "SV null tags rejected"),
]:
    rejects(mut, label, SourceVideo, VALID_VIDEO)

# --- Creator DNA Profile -----------------------------------------------------
check("DNA valid profile constructs", CreatorDNAProfile(**VALID_PROFILE).creator_id == "creator_001")
for mut, label in [
    (lambda p: p.pop("voice"), "DNA missing voice rejected"),
    (lambda p: p.pop("title_formula"), "DNA missing title_formula rejected"),
    (lambda p: p.pop("thumbnail_style"), "DNA missing thumbnail_style rejected"),
    (lambda p: p.pop("content_patterns"), "DNA missing content_patterns rejected"),
    (lambda p: p.pop("performance_benchmarks"), "DNA missing benchmarks rejected"),
    (lambda p: p["title_formula"].__setitem__("example_titles", []), "DNA empty example_titles rejected"),
    (lambda p: p["thumbnail_style"].__setitem__("dominant_colors", []), "DNA empty dominant_colors rejected"),
    (lambda p: p["content_patterns"].__setitem__("format_preferences", []), "DNA empty format_preferences rejected"),
    (lambda p: p["content_patterns"].__setitem__("optimal_duration_range", {"min": 500, "max": 300}),
     "DNA duration range max<min rejected"),
    (lambda p: p["performance_benchmarks"].__setitem__("avg_views", None), "DNA null benchmark rejected"),
    (lambda p: p["performance_benchmarks"].__setitem__("avg_views", -1.0), "DNA negative benchmark rejected"),
    (lambda p: p["title_formula"].__setitem__("emotional_hook_type", "clickbait"), "DNA unknown hook type rejected"),
    (lambda p: p["thumbnail_style"].__setitem__("background_type", "checkerboard"), "DNA unknown background rejected"),
    (lambda p: p["voice"].__setitem__("tone", None), "DNA null voice field rejected"),
    (lambda p: p["title_formula"].__setitem__("avg_word_count", "9"), "DNA string word count rejected"),
]:
    rejects(mut, label, CreatorDNAProfile, VALID_PROFILE)

# --- Content Opportunity -----------------------------------------------------
check("OPP valid constructs", ContentOpportunity(**VALID_OPP).fit_score == 0.87)
for mut, label in [
    (lambda v: v.__setitem__("fit_score", 1.5), "OPP fit_score > 1 rejected"),
    (lambda v: v.__setitem__("fit_score", -0.1), "OPP fit_score < 0 rejected"),
    (lambda v: v.__setitem__("confidence", "maybe"), "OPP unknown confidence rejected"),
    (lambda v: v.__setitem__("status", "draft"), "OPP unknown status rejected"),
    (lambda v: v.__setitem__("rationale", "flat string, not nested"), "OPP flat-string rationale rejected"),
    (lambda v: v["rationale"].__setitem__("dna_fit_explanation", ""), "OPP empty dna_fit_explanation rejected"),
    (lambda v: v["rationale"].__setitem__("dna_fit_explanation", "   "), "OPP whitespace dna_fit_explanation rejected"),
    (lambda v: v.__setitem__("recommended_duration_seconds", "6 minutes"), "OPP '6 minutes' duration rejected"),
    (lambda v: v.__setitem__("recommended_duration_seconds", 360.0), "OPP float duration rejected"),
    (lambda v: v.__setitem__("recommended_duration_seconds", -10), "OPP negative duration rejected"),
]:
    rejects(mut, label, ContentOpportunity, VALID_OPP)

# --- Script ------------------------------------------------------------------
check("SCRIPT valid constructs", Script(**VALID_SCRIPT).hook.duration_seconds == 15)
check("SCRIPT null on_screen_text allowed",
      Script(**{**VALID_SCRIPT, "scenes": [s | {"on_screen_text": None} for s in VALID_SCRIPT["scenes"]]})
      .scenes[0].on_screen_text is None)
for mut, label in [
    (lambda v: v.pop("hook"), "SCRIPT missing hook rejected"),
    (lambda v: v.pop("outro"), "SCRIPT missing outro rejected"),
    (lambda v: v.__setitem__("scenes", []), "SCRIPT empty scenes rejected"),
    (lambda v: v.__setitem__("full_voiceover_text", ""), "SCRIPT empty voiceover rejected"),
    (lambda v: v.pop("estimated_duration_seconds"), "SCRIPT missing estimated duration rejected"),
    (lambda v: v["scenes"][0].__setitem__("scene_type", "stock_footage"), "SCRIPT unknown scene_type rejected"),
    (lambda v: v["scenes"][0].__setitem__("duration_seconds", 100.0), "SCRIPT float scene duration rejected"),
    (lambda v: v["scenes"][0].__setitem__("scene_number", 0), "SCRIPT scene_number 0 rejected"),
]:
    rejects(mut, label, Script, VALID_SCRIPT)

# --- Thumbnail Variant -------------------------------------------------------
check("THUMB valid (png_path null pre-render)", ThumbnailVariant(**VALID_THUMB).png_path is None)
check("THUMB selected with reason ok",
      ThumbnailVariant(**{**VALID_THUMB, "selected": True, "selection_reason": "Matches dominant colors."}).selected)
check("THUMB unselected reason normalized to None",
      ThumbnailVariant(**{**VALID_THUMB, "selection_reason": "leftover"}).selection_reason is None)
for mut, label in [
    (lambda v: v.__setitem__("svg_source", ""), "THUMB empty svg_source rejected"),
    (lambda v: (v.__setitem__("selected", True), v.__setitem__("selection_reason", None)),
     "THUMB selected without reason rejected"),
    (lambda v: (v.__setitem__("selected", True), v.__setitem__("selection_reason", "  ")),
     "THUMB selected whitespace reason rejected"),
    (lambda v: v.__setitem__("variant_number", 0), "THUMB variant 0 rejected"),
    (lambda v: v.__setitem__("variant_number", 4), "THUMB variant 4 rejected"),
]:
    rejects(mut, label, ThumbnailVariant, VALID_THUMB)

# --- Metadata ----------------------------------------------------------------
check("METADATA valid constructs", Metadata(**VALID_META).tags[0] == "ai tools")
check("METADATA null scheduled time allowed", Metadata(**VALID_META).scheduled_publish_time is None)
for mut, label in [
    (lambda v: v.__setitem__("title", ""), "METADATA empty title rejected"),
    (lambda v: v.__setitem__("title", "   "), "METADATA whitespace title rejected"),
    (lambda v: v.__setitem__("title_formula_match", ""), "METADATA empty formula match rejected"),
    (lambda v: v.__setitem__("description", ""), "METADATA empty description rejected"),
    (lambda v: v.__setitem__("tags", ["a", "b", "c", "d"]), "METADATA 4 tags rejected (min 5)"),
    (lambda v: v.__setitem__("tags", list(range(21))), "METADATA 21 tags rejected (max 20)"),
]:
    rejects(mut, label, Metadata, VALID_META)

# --- Quality Score -----------------------------------------------------------
q = QualityScore(**valid_qs())
check("QS valid constructs", q.passed is True)  # computed, not set
check("QS passed computed from threshold",
      QualityScore(**valid_qs(overall_score=0.74, rejection_reason="below threshold")).passed is False)
check("QS reject needs reason",
      QualityScore(**valid_qs(overall_score=0.62, rejection_reason="Blurred background mismatch.")).rejection_reason)
check("QS pass clears rejection_reason",
      QualityScore(**valid_qs(overall_score=0.81, rejection_reason="stale")).rejection_reason is None)
check("QS agent-set passed overridden",
      QualityScore(**valid_qs(overall_score=0.62, passed=True, rejection_reason="r")).passed is False)
check("QS threshold default 0.75", QualityScore(**valid_qs()).threshold_used == 0.75)
for mut, label in [
    (lambda v: v.__setitem__("overall_score", 1.5), "QS score > 1 rejected"),
    (lambda v: v.__setitem__("overall_score", -0.1), "QS score < 0 rejected"),
    (lambda v: (v.__setitem__("overall_score", 0.62), v.__setitem__("rejection_reason", None)),
     "QS fail without reason rejected"),
    (lambda v: v.__setitem__("regeneration_count", 3), "QS regen count 3 rejected (max 2)"),
    (lambda v: v.__setitem__("regeneration_count", -1), "QS regen count -1 rejected"),
    (lambda v: v.__setitem__("regeneration_count", "1"), "QS string regen count rejected"),
    (lambda v: (v.__setitem__("overall_score", 0.5), v.__setitem__("rejection_reason", "  ")),
     "QS whitespace rejection reason rejected"),
]:
    rejects(mut, label, QualityScore, valid_qs())

print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
