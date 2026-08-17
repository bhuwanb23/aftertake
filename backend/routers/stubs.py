"""Phase 1 STUB data — realistic fake responses for the agent endpoints.

These are NOT agent output. They exist so the frontend can build and test the
full UI against data that looks exactly like the real pipeline output (Phase 1
Step 3: "a frontend built against a stub that looks like real data will work
correctly when the real data arrives").

Every object here is constructed through the real Pydantic models, so it is
guaranteed to satisfy the same validation the real agents' output must pass.
All of this is replaced by real agent logic in Phase 2+; nothing here should
be treated as production code.
"""
from datetime import datetime, timedelta, timezone

from backend.models.schemas import (
    ContentOpportunity,
    CreatorDNAProfile,
    DecisionLogEntry,
    GeneratedAsset,
    Hook,
    Metadata,
    Outro,
    PerformanceBenchmarks,
    PipelineRun,
    QualityScore,
    Rationale,
    Scene,
    Script,
    ContentPatterns,
    ThumbnailStyle,
    ThumbnailVariant,
    TitleFormula,
    VideoInfo,
    Voice,
)

STUB_CREATOR_ID = "creator_001"
STUB_RUN_ID = "run_stub_001"
STUB_OPPORTUNITY_ID = "opp_stub_001"
STUB_ASSET_ID = "asset_stub_001"

RUN_STAGES = [
    "dna_agent",
    "opportunity_agent",
    "script_agent",
    "thumbnail_agent",
    "metadata_agent",
    "scorer",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# --- Stub DNA profile -------------------------------------------------------
def dna_profile(creator_id: str, source_video_count: int = 8) -> CreatorDNAProfile:
    """A complete, realistic CreatorDNAProfile for the seed productivity creator.

    performance_benchmarks are the REAL values computed from the seed catalog
    (backend/agents/benchmarks.py) — the plan's rule: LLMs don't do arithmetic.
    """
    ts = _now()
    return CreatorDNAProfile(
        creator_id=creator_id,
        created_at=ts,
        updated_at=ts,
        source_video_count=source_video_count,
        voice=Voice(
            tone="Conversational and direct. Never formal or academic. "
                 "Speaks like explaining something to a friend, not presenting to an audience.",
            pacing="Short punchy sentences. Rarely more than 15 words per beat. "
                   "Uses pauses deliberately. Speeds up when excited, slows down for emphasis.",
            hook_pattern="Always opens with either a provocative question directed at the viewer "
                         "or a bold personal claim within the first 8 seconds. Never starts with "
                         "'Hey guys' or a greeting.",
            vocabulary_level="Everyday language. Avoids jargon entirely. Occasionally self-deprecating. "
                             "Uses specific numbers whenever possible rather than vague qualifiers.",
            signature_phrases=[
                "Here's the thing",
                "So I actually tested this",
                "which surprised me",
                "I am not guessing",
            ],
            what_to_avoid=[
                "Corporate language",
                "Passive voice",
                "Inspirational quotes",
                "Vague calls to action like 'let me know in the comments'",
            ],
        ),
        title_formula=TitleFormula(
            structure="I [did specific thing] for [specific timeframe] — here's what [actually] happened",
            avg_word_count=9,
            uses_caps=True,
            uses_numbers=True,
            uses_questions=False,
            emotional_hook_type="curiosity gap",
            example_titles=[
                "I Used Notion for 30 Days — Here's What Actually Happened",
                "5 Chrome Extensions That Saved Me 3 Hours a Week",
                "7 Things Productive People Do Before 9 AM",
                "Obsidian vs Notion — Which One Actually Wins?",
            ],
        ),
        thumbnail_style=ThumbnailStyle(
            dominant_colors=["red", "white", "black", "orange"],
            layout_pattern="Creator face occupies the left half of the frame. Bold stacked text "
                           "on the right. Solid color background. Subject always looking directly "
                           "into camera or at the text.",
            text_style="2 to 4 words maximum. All caps. Very thick font weight. White text with "
                       "thick black outline for readability on any background.",
            facial_expression="Surprised or excited. Eyebrows raised. Mouth slightly open. "
                              "Never neutral or smiling politely. Always a strong emotion.",
            uses_props=True,
            background_type="solid color",
            uses_graphic_elements=False,
        ),
        content_patterns=ContentPatterns(
            avg_duration_seconds=472,
            optimal_duration_range={"min": 324, "max": 487},
            format_preferences=["30-day-challenge", "listicle", "head-to-head-comparison", "tool-review"],
            posting_frequency="2 to 3 times per week, most commonly Tuesday and Friday",
            best_performing_topics=["productivity apps", "30-day challenges", "tool comparisons", "morning routines"],
            worst_performing_topics=["setup tours", "vague habit advice", "gear reviews without challenge format"],
        ),
        performance_benchmarks=PerformanceBenchmarks(
            avg_views=226625.0,
            avg_ctr=6.5,
            avg_retention=50.1,
            top_quartile_views=420000.0,
            bottom_quartile_views=28000.0,
        ),
    )


# --- Stub opportunities -----------------------------------------------------
def opportunities(creator_id: str) -> list[ContentOpportunity]:
    """Three ranked recommendations, fit scores 0.87 / 0.71 / 0.58 — including
    one weak enough that the scorer would regenerate it."""
    ts = _now()
    return [
        ContentOpportunity(
            id=STUB_OPPORTUNITY_ID,
            creator_id=creator_id,
            created_at=ts,
            topic="Testing 5 AI writing tools side by side for a month and measuring actual output quality",
            working_title="I Tested 5 AI Writing Tools for 30 Days — Here's the Honest Ranking",
            rationale=Rationale(
                dna_fit_explanation=(
                    "This maps directly to your highest-performing format (30-day challenge) and your "
                    "best-performing topic category (productivity app comparisons). The title follows "
                    "your established formula of 'I tested X for Y days.' The definitive ranking element "
                    "satisfies your audience's expectation for answers, aligning with your curiosity-gap "
                    "hook type and your use of specific numbers."
                ),
                performance_prediction=(
                    "Your top 3 videos by CTR are all app comparisons with a 30-day structure. This topic "
                    "combines both. Your 30-day challenge videos average 420k views vs 71k for non-challenge "
                    "formats, so this sits above your top-quartile threshold of 420k if the execution holds."
                ),
                trend_relevance=(
                    "AI writing tools are the most searched productivity topic in this niche over the last "
                    "60 days. Three major new releases landed in the last 30 days, giving a natural news hook."
                ),
                risks=(
                    "If the creator cannot access all 5 tools, the comparison loses specificity. Tool "
                    "comparison videos also have a shorter shelf life than general productivity advice videos."
                ),
            ),
            fit_score=0.87,
            confidence="high",
            recommended_format="30-day-challenge",
            recommended_duration_seconds=360,
            target_hook=(
                "Open with the total monthly cost of all 5 tools and ask 'is any of it actually worth it?' "
                "— creates immediate stakes and curiosity."
            ),
            status="pending",
        ),
        ContentOpportunity(
            id="opp_stub_002",
            creator_id=creator_id,
            created_at=ts,
            topic="7 Notion templates that measurably save time, tested for two weeks each",
            working_title="7 Notion Templates That ACTUALLY Saved Me Time",
            rationale=Rationale(
                dna_fit_explanation=(
                    "Listicle is your second-strongest format (7 Things Productive People Do Before 9 AM is "
                    "your top video at 510k views), and Notion is your proven best-performing topic. The "
                    "number-led title with caps on 'ACTUALLY' matches your title formula's caps + numbers."
                ),
                performance_prediction=(
                    "Listicles with a specific number average 445k views in your catalog vs 226k overall. "
                    "The specific claim ('saved me time') mirrors your highest-CTR framing of measurable outcomes."
                ),
                trend_relevance=(
                    "Notion template searches spike every January and at back-to-school season; template "
                    "marketplaces are actively promoting this category right now."
                ),
                risks=(
                    "Template videos risk feeling like a static slideshow. Needs the measured-time framing "
                    "to hold, otherwise it drifts toward your worst-performing 'vague habit advice' category."
                ),
            ),
            fit_score=0.71,
            confidence="medium",
            recommended_format="listicle",
            recommended_duration_seconds=330,
            target_hook="Open with the number of hours the best template saved in the first week.",
            status="pending",
        ),
        ContentOpportunity(
            id="opp_stub_003",
            creator_id=creator_id,
            created_at=ts,
            topic="Why I stopped using a separate productivity stack and consolidated into one app",
            working_title="I Deleted 9 Productivity Apps (And It Backfired)",
            rationale=Rationale(
                dna_fit_explanation=(
                    "The consolidation framing is a tool-review, which is a known format, but the premise "
                    "is vague — no specific timeframe or measured outcome. It risks your weakest format "
                    "('setup tour'-adjacent) and does not follow your number-led title formula."
                ),
                performance_prediction=(
                    "Vague consolidation stories have no direct precedent in your catalog; your weakest "
                    "performers (28k and 19k views) are all unframed 'here is how I do things' videos."
                ),
                trend_relevance=(
                    "App consolidation is a recurring topic in the niche but not currently spiking; no "
                    "strong news hook behind it right now."
                ),
                risks=(
                    "Without a challenge framing or measurement, this lands in your lowest-performing "
                    "category and has no clear thumbnail story — no number, no bold claim, no solid-color "
                    "visual anchor."
                ),
            ),
            fit_score=0.58,
            confidence="low",
            recommended_format="tool-review",
            recommended_duration_seconds=300,
            target_hook="None strong enough — regenerate or reframe with a specific, measured premise.",
            status="pending",
        ),
    ]


# --- Stub generated asset ---------------------------------------------------
def script(opportunity_id: str, creator_id: str) -> Script:
    hook = Hook(
        voiceover_text=(
            "Five AI writing tools. Five hundred and forty dollars a month combined. "
            "I used every single one for a full thirty days — and the ranking I ended up "
            "with genuinely surprised me."
        ),
        visual_description="Solid orange background. Creator face left half of frame, surprised "
                           "expression. Bold white text top right: '30 DAYS'.",
        duration_seconds=15,
    )
    scenes = [
        Scene(
            scene_number=1,
            scene_type="list_reveal",
            voiceover_text=(
                "So here is the honest ranking, from the tool that wasted my time to the one that "
                "actually earned its price tag."
            ),
            visual_description="Five app icons revealed one by one in a grid, each with a rank badge.",
            on_screen_text="5 TOOLS — 30 DAYS",
            duration_seconds=100,
        ),
        Scene(
            scene_number=2,
            scene_type="comparison_split",
            voiceover_text=(
                "Tool number two and tool number four output nearly identical quality — but one of "
                "them costs four times as much. That gap is why you cannot trust a demo video."
            ),
            visual_description="Split screen: two tools side by side with identical sample outputs and "
                               "contrasting price tags.",
            on_screen_text="SAME OUTPUT — 4x THE PRICE",
            duration_seconds=110,
        ),
        Scene(
            scene_number=3,
            scene_type="text_overlay",
            voiceover_text=(
                "The winner was not the most expensive tool. It was the one I kept coming back to "
                "after the test ended. And that, more than any spec sheet, is what actually matters."
            ),
            visual_description="Solid red background. Winner's logo centered with 'THE WINNER' in "
                               "thick white caps above it.",
            on_screen_text="THE WINNER",
            duration_seconds=100,
        ),
    ]
    outro = Outro(
        voiceover_text=(
            "If you want the full dataset with all of my test prompts, subscribe — I am posting the "
            "60-day follow-up next month to see if the winner holds up."
        ),
        visual_description="Creator face center frame, direct look into camera, black background.",
        call_to_action="Subscribe for the 60-day follow-up",
        duration_seconds=35,
    )
    full_text = " ".join(
        [hook.voiceover_text]
        + [s.voiceover_text for s in scenes]
        + [outro.voiceover_text]
    )
    return Script(
        id="script_stub_001",
        opportunity_id=opportunity_id,
        creator_id=creator_id,
        hook=hook,
        scenes=scenes,
        outro=outro,
        full_voiceover_text=full_text,
        estimated_duration_seconds=360,
        word_count=len(full_text.split()),
    )


def thumbnails(asset_id: str) -> list[ThumbnailVariant]:
    svg = {
        "red": (
            '<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720">'
            '<rect width="1280" height="720" fill="#C1272D"/>'
            '<text x="60" y="420" font-family="Arial,sans-serif" font-size="120" font-weight="bold" fill="#FFFFFF">HONEST RANKING</text>'
            '<text x="60" y="560" font-family="Arial,sans-serif" font-size="64" font-weight="bold" fill="#FFFFFF">5 TOOLS TESTED</text>'
            "</svg>"
        ),
        "blue": (
            '<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720">'
            '<rect width="1280" height="720" fill="#0B2545"/>'
            '<circle cx="880" cy="220" r="120" fill="#3A86FF"/>'
            '<circle cx="1120" cy="220" r="120" fill="#3A86FF"/>'
            '<circle cx="880" cy="500" r="120" fill="#3A86FF"/>'
            '<circle cx="1120" cy="500" r="120" fill="#3A86FF"/>'
            '<text x="80" y="400" font-family="Arial,sans-serif" font-size="110" font-weight="bold" fill="#FFFFFF">5 TOOLS</text>'
            "</svg>"
        ),
        "black": (
            '<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720">'
            '<rect width="1280" height="720" fill="#111111"/>'
            '<text x="560" y="400" font-family="Arial,sans-serif" font-size="160" font-weight="bold" fill="#FFFFFF">VS</text>'
            '<text x="200" y="600" font-family="Arial,sans-serif" font-size="56" font-weight="bold" fill="#FFB703">WHO WINS?</text>'
            "</svg>"
        ),
    }
    variants = [
        ThumbnailVariant(
            id="thumb_stub_001",
            asset_id=asset_id,
            variant_number=1,
            svg_source=svg["red"],
            png_path=None,
            layout_description=(
                "Solid red background. Bold white all-caps text 'HONEST RANKING' top-left with "
                "'5 TOOLS TESTED' below it. Creator face occupies the left half of the frame, "
                "surprised expression, looking directly at the camera."
            ),
            selected=True,
            selection_reason=(
                "Closest match to the creator's layout_pattern ('creator face left, bold text right') "
                "and dominant_colors (red, white, black). Thick all-caps text follows the learned "
                "text_style of 2-4 words. Solid color background matches background_type exactly."
            ),
        ),
        ThumbnailVariant(
            id="thumb_stub_002",
            asset_id=asset_id,
            variant_number=2,
            svg_source=svg["blue"],
            png_path=None,
            layout_description=(
                "Dark blue solid background. Five app icons in a clean grid on the right half. "
                "Bold white '5 TOOLS' text on the left. Creator face absent."
            ),
            selected=False,
        ),
        ThumbnailVariant(
            id="thumb_stub_003",
            asset_id=asset_id,
            variant_number=3,
            svg_source=svg["black"],
            png_path=None,
            layout_description=(
                "Black solid background. Huge white 'VS' centered with amber 'WHO WINS?' below. "
                "Battle-style layout with creator face between the two contenders."
            ),
            selected=False,
        ),
    ]
    return variants


def metadata(asset_id: str) -> Metadata:
    return Metadata(
        id="metadata_stub_001",
        asset_id=asset_id,
        title="I Tested 5 AI Writing Tools for 30 Days — Here's the Honest Ranking",
        title_formula_match=(
            "Follows the 'I [did specific thing] for [specific timeframe] — here's what [actually] "
            "happened' structure. Contains a specific number (5), a specific timeframe (30 days), "
            "and definitive framing ('Honest Ranking'). Curiosity-gap hook type, matching the "
            "creator's strongest-performing titles."
        ),
        description=(
            "I used 5 AI writing tools every single day for a full month and ranked them on output "
            "quality, consistency, and price. Here is the honest ranking — including the tool I "
            "expected to win and the one that actually did.\n\n"
            "0:00 The test setup and the cost\n"
            "1:45 The honest ranking\n"
            "6:00 The winner and why\n\n"
            "Full dataset with test prompts on the 60-day follow-up. Subscribe so you do not miss it."
        ),
        tags=[
            "ai writing tools",
            "30 day challenge",
            "ai tools comparison",
            "writing tools",
            "chatgpt alternatives",
            "productivity tools",
            "ai for writers",
            "tool review",
            "honest review",
            "content creation",
            "ai software",
            "work smarter",
        ],
        category="Science & Technology",
        scheduled_publish_time=None,
        platform_targets=["youtube"],
    )


def _final_quality_score(asset_id: str) -> QualityScore:
    return QualityScore(
        asset_id=asset_id,
        overall_score=0.81,
        thumbnail_fit_score=0.88,
        title_fit_score=0.84,
        voice_fit_score=0.79,
        threshold_used=0.75,
        regeneration_count=1,
    )


def asset(opportunity_id: str, creator_id: str, pipeline_run_id: str, with_score: bool) -> GeneratedAsset:
    """The assembled production package. with_score=False for /content/generate
    (scorer has not run); True for the pipeline run stub (final pass, 0.81)."""
    return GeneratedAsset(
        id=STUB_ASSET_ID,
        opportunity_id=opportunity_id,
        creator_id=creator_id,
        created_at=_now(),
        script=script(opportunity_id, creator_id),
        video=VideoInfo(render_status="pending", resolution="1920x1080"),
        thumbnails=thumbnails(STUB_ASSET_ID),
        metadata=metadata(STUB_ASSET_ID),
        quality_score=_final_quality_score(STUB_ASSET_ID) if with_score else None,
        pipeline_run_id=pipeline_run_id,
    )


# --- Stub decision log ------------------------------------------------------
def decision_log_entries(run_id: str, creator_id: str) -> list[DecisionLogEntry]:
    """The full 8-entry decision log for the stub run — including the live
    reject -> regenerate -> pass cycle that is the demo's wow moment."""
    t0 = datetime.now(timezone.utc).replace(microsecond=0)
    ts = [t0]
    for _ in range(7):
        ts.append(ts[-1] + timedelta(seconds=27))

    def e(n, stage, decision, rationale, status, score=None, inp="", out=""):
        return DecisionLogEntry(
            id=f"log_stub_{n:02d}",
            pipeline_run_id=run_id,
            creator_id=creator_id,
            timestamp=ts[n - 1].isoformat(),
            stage=stage,
            decision=decision,
            rationale=rationale,
            input_summary=inp,
            output_summary=out,
            score=score,
            status=status,
        )

    return [
        e(
            1, "dna_agent",
            "Built CreatorDNAProfile from 8 catalog videos for creator_001.",
            "Learned the creator's voice (conversational, number-driven), title formula "
            "('I tested X for Y days'), thumbnail style (solid color, creator face, all-caps text), "
            "and computed performance benchmarks from real catalog data.",
            "success",
            inp="8 SourceVideo objects for creator_001",
            out="CreatorDNAProfile with 5 sub-profiles + computed benchmarks",
        ),
        e(
            2, "opportunity_agent",
            "Generated 3 opportunities; selected opp_stub_001 with fit score 0.87.",
            "Fit score 0.87 exceeds the 0.8 threshold for a strong recommendation. The rationale "
            "cites the creator's two best-performing formats (30-day challenge and app comparison) "
            "and maps to their top-performing topic category.",
            "success",
            score=0.87,
            inp="CreatorDNAProfile + 14 static trends",
            out="ContentOpportunity opp_stub_001 passed to script agent",
        ),
        e(
            3, "script_agent",
            "Wrote a 360-second script in the creator's learned voice: hook + 3 scenes + outro.",
            "Hook opens with a bold personal claim and a specific number within the first 8 seconds; "
            "pacing follows the short-sentence style in the voice profile.",
            "success",
            inp="ContentOpportunity opp_stub_001 + CreatorDNAProfile",
            out="Script script_stub_001 with full voiceover text",
        ),
        e(
            4, "thumbnail_agent",
            "Generated 3 thumbnail variants following the learned thumbnail_style.",
            "All variants use solid color backgrounds and bold all-caps text per the profile; "
            "variant 1 mirrors the layout_pattern of creator face left + stacked text right.",
            "success",
            inp="Script + CreatorDNAProfile.thumbnail_style",
            out="3 ThumbnailVariant objects with SVG source",
        ),
        e(
            5, "metadata_agent",
            "Wrote title, description, and 12 tags following the learned title_formula.",
            "Title follows the 'I tested X for Y days' structure with a specific number (5) and "
            "definitive framing; description includes timestamps and a follow-up hook.",
            "success",
            inp="Script + CreatorDNAProfile.title_formula",
            out="Metadata metadata_stub_001",
        ),
        e(
            6, "scorer",
            "Thumbnail variant 2 REJECTED — overall score 0.62 is below the 0.75 threshold.",
            "Variant 2 has no creator face and uses a grid layout, which contradicts the learned "
            "thumbnail_style (creator face prominent, left half of frame). The title and voice fit "
            "were strong, but the visual gate failed.",
            "rejected",
            score=0.62,
            inp="GeneratedAsset asset_stub_001 vs CreatorDNAProfile",
            out="Rejection triggered regeneration (attempt 1 of 2)",
        ),
        e(
            7, "regenerate",
            "Regenerating thumbnail set. Attempt 2 of 2.",
            "Regeneration re-ran the thumbnail agent with the scorer's rejection reason appended "
            "to the prompt, so the new set enforces the learned layout_pattern and dominant colors.",
            "regenerated",
            inp="Scorer rejection reason",
            out="New ThumbnailVariant set",
        ),
        e(
            8, "scorer",
            "Asset passed quality gate with overall score 0.81.",
            "All dimension scores now clear the threshold: thumbnail fit 0.88 (solid red background, "
            "creator face, all-caps text), title fit 0.84 (formula match), voice fit 0.79. The "
            "regenerated variant 1 was selected.",
            "success",
            score=0.81,
            inp="Regenerated asset vs CreatorDNAProfile",
            out="QualityScore 0.81 — asset approved",
        ),
    ]


# --- Stub pipeline run ------------------------------------------------------
def run_payload(creator_id: str) -> dict:
    """The full /pipeline/run stub response: PipelineRun with the selected
    opportunity, the generated asset, and the complete decision log embedded."""
    now = _now()
    run = PipelineRun(
        id=STUB_RUN_ID,
        creator_id=creator_id,
        started_at=now,
        completed_at=now,
        status="complete",
        current_stage="",
        opportunity_id=STUB_OPPORTUNITY_ID,
        asset_id=STUB_ASSET_ID,
        stages_completed=list(RUN_STAGES),
        stages_failed=[],
        total_duration_seconds=214.5,
        total_llm_calls=9,
        regeneration_count=1,
    )
    return {
        **run.model_dump(),
        "opportunity": opportunities(creator_id)[0].model_dump(),
        "asset": asset(STUB_OPPORTUNITY_ID, creator_id, STUB_RUN_ID, with_score=True).model_dump(),
        "decision_log": [e.model_dump() for e in decision_log_entries(STUB_RUN_ID, creator_id)],
    }


def publish_payload() -> dict:
    return {
        "platform_post_id": "yt_stub_001",
        "url": "https://www.youtube.com/watch?v=aftertake-demo-001",
        "status": "scheduled",
        "published_at": _now(),
    }
