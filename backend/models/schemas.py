"""All AfterTake data shapes, defined in one place (Phase 0 Step 9 / Phase 1 Step 1).

Both the API layer and the agent layer import from here.
Never define a data shape anywhere else.

Phase 1 Step 1 hardening: every field has a type, optional fields are explicit,
and invalid data is rejected with a readable error — a fit_score of 1.5, a null
transcript, or an unrecognized stage name must fail validation.
"""
from datetime import date
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, Field, StrictInt, field_validator, model_validator

# Fields the plan calls "always an integer" get StrictInt: rejects floats (487.0),
# numeric strings ("420000"), and bools — not just fractional floats.
NonNegInt = Annotated[StrictInt, Field(ge=0)]


def _non_blank(v: str) -> str:
    """Reject empty AND whitespace-only strings — min_length alone lets "   " through."""
    if not v.strip():
        raise ValueError("must be a non-empty string")
    return v


# Fields the plan calls "non-empty" get NonBlankStr: rejects "" and "   ".
NonBlankStr = Annotated[str, Field(min_length=1), AfterValidator(_non_blank)]

# --- Allowed-value sets (Phase 0 Step 9) ------------------------------------
Platform = Literal["youtube", "tiktok", "instagram", "linkedin"]
EmotionalHook = Literal[
    "curiosity gap", "social proof", "fear of missing out",
    "personal authority", "specific transformation", "controversy",
]
BackgroundType = Literal[
    "solid color", "gradient", "blurred real location",
    "illustrated/graphic", "product or app screenshot",
]
Confidence = Literal["high", "medium", "low"]
OpportunityStatus = Literal["pending", "approved", "rejected", "in_production", "published"]
SceneType = Literal[
    "talking_head", "text_overlay", "title_card",
    "comparison_split", "list_reveal", "b_roll_description",
]
RenderStatus = Literal["pending", "rendering", "complete", "failed"]
Stage = Literal[
    "dna_agent", "opportunity_agent", "script_agent", "thumbnail_agent",
    "metadata_agent", "scorer", "regenerate", "publish",
]
LogStatus = Literal["success", "rejected", "regenerated", "failed"]
RunStatus = Literal["running", "complete", "failed", "partial"]

QUALITY_THRESHOLD_DEFAULT = 0.75
RETRY_CAP = 2


# --- Schema 1: Source Video ------------------------------------------------
class Performance(BaseModel):
    """Real performance metrics for one catalog video. Null = unknown, not zero."""
    views: NonNegInt
    likes: NonNegInt
    comments: NonNegInt
    shares: NonNegInt | None = None
    ctr: float | None = Field(default=None, ge=0.0, le=100.0, description="Click-through rate, 0.0-100.0")
    avg_retention: float | None = Field(default=None, ge=0.0, le=100.0, description="Avg % of video watched, 0.0-100.0")
    watch_time_hours: float = Field(ge=0.0)


class Thumbnail(BaseModel):
    """Thumbnail reference for one catalog video. description is how the DNA
    agent learns visual style without doing image analysis — so it must never
    be empty."""
    url: str = ""  # can be empty for seed data
    description: NonBlankStr  # the DNA agent learns visual style from this — never empty


class SourceVideo(BaseModel):
    """One past video from the creator's catalog. Raw input to the DNA agent."""
    id: str
    title: str  # always present — the DNA agent cannot function without it
    description: str = ""
    transcript: str  # always present — tone/phrasing source for the DNA agent
    duration_seconds: NonNegInt  # whole seconds, never a float
    published_at: str  # ISO date (YYYY-MM-DD) — validated below so the DNA agent can compute posting frequency
    platform: Platform = "youtube"
    performance: Performance
    thumbnail: Thumbnail  # required — description teaches visual style
    tags: list[str] = []  # can be empty, never null
    category: str = ""

    @field_validator("published_at")
    @classmethod
    def _valid_iso_date(cls, v: str) -> str:
        try:
            return date.fromisoformat(v).isoformat()
        except ValueError:
            raise ValueError("published_at must be an ISO date (YYYY-MM-DD)")


# --- Schema 2: Creator DNA Profile -----------------------------------------
class Voice(BaseModel):
    """How the creator speaks and structures language."""
    tone: str
    pacing: str
    hook_pattern: str
    vocabulary_level: str
    signature_phrases: list[str] = []
    what_to_avoid: list[str] = []  # what style drift looks like — as important as the positives


class TitleFormula(BaseModel):
    """The pattern the creator's best-performing titles follow."""
    structure: str
    avg_word_count: NonNegInt = 0
    uses_caps: bool = False
    uses_numbers: bool = False
    uses_questions: bool = False
    emotional_hook_type: EmotionalHook = "curiosity gap"
    example_titles: list[str] = Field(min_length=1, description="3-5 real titles used as references")


class ThumbnailStyle(BaseModel):
    """The recurring visual style of the creator's thumbnails."""
    dominant_colors: list[str] = Field(min_length=1)
    layout_pattern: str
    text_style: str
    facial_expression: str
    uses_props: bool = False
    background_type: BackgroundType = "solid color"
    uses_graphic_elements: bool = False


class DurationRange(BaseModel):
    """A min/max duration range (seconds)."""
    min: NonNegInt = 0
    max: NonNegInt = 0

    @model_validator(mode="after")
    def _max_not_below_min(self):
        if self.max < self.min:
            raise ValueError("optimal_duration_range.max cannot be below min")
        return self


class ContentPatterns(BaseModel):
    """Formats, topics, and cadence that correlate with the creator's performance."""
    avg_duration_seconds: NonNegInt = 0
    optimal_duration_range: DurationRange = DurationRange()
    format_preferences: list[str] = Field(min_length=1)
    posting_frequency: str = ""
    best_performing_topics: list[str] = []
    worst_performing_topics: list[str] = []


class PerformanceBenchmarks(BaseModel):
    """Calculated mathematically from the catalog — never LLM-generated.
    All five are non-null floats — they exist before the DNA agent runs."""
    avg_views: float = Field(default=0.0, ge=0.0)
    avg_ctr: float = Field(default=0.0, ge=0.0)
    avg_retention: float = Field(default=0.0, ge=0.0)
    top_quartile_views: float = Field(default=0.0, ge=0.0)
    bottom_quartile_views: float = Field(default=0.0, ge=0.0)


class CreatorDNAProfile(BaseModel):
    """The learned style + performance profile of a specific creator.
    The single most important object in the system — every generation agent
    conditions on it, every scored asset is evaluated against it."""
    creator_id: str
    created_at: str = ""  # ISO timestamp
    updated_at: str = ""  # ISO timestamp
    source_video_count: int = 0
    voice: Voice
    title_formula: TitleFormula
    thumbnail_style: ThumbnailStyle
    content_patterns: ContentPatterns
    performance_benchmarks: PerformanceBenchmarks


# --- Schema 3: Content Opportunity -----------------------------------------
class Rationale(BaseModel):
    """Why this opportunity fits the creator. dna_fit_explanation MUST cite
    specific profile attributes — if it says "fits your style" without saying
    what style and why, the prompt that produced it is wrong."""
    dna_fit_explanation: NonBlankStr
    performance_prediction: str
    trend_relevance: str
    risks: str


class ContentOpportunity(BaseModel):
    """One recommendation for what the creator should make next."""
    id: str
    creator_id: str
    created_at: str = ""  # ISO timestamp
    topic: str
    working_title: str = ""
    rationale: Rationale
    fit_score: float = Field(ge=0.0, le=1.0, description="0.8+ strong, 0.6-0.79 viable, <0.6 regenerate")
    confidence: Confidence = "medium"
    recommended_format: str = ""
    recommended_duration_seconds: NonNegInt = 0  # seconds — "6 minutes" or 360.0 is invalid
    target_hook: str = ""
    status: OpportunityStatus = "pending"


# --- Schema 4: Script -------------------------------------------------------
class Hook(BaseModel):
    """The opening 5-15 seconds of the video."""
    voiceover_text: str
    visual_description: str
    duration_seconds: NonNegInt


class Scene(BaseModel):
    """One scene of the video. scene_type maps directly to HyperFrames template types."""
    scene_number: Annotated[StrictInt, Field(ge=1)]  # order in the video, starts at 1
    scene_type: SceneType
    voiceover_text: str
    visual_description: str
    on_screen_text: str | None = None
    duration_seconds: NonNegInt


class Outro(BaseModel):
    """The closing section with the call to action."""
    voiceover_text: str
    visual_description: str
    call_to_action: str
    duration_seconds: NonNegInt


class Script(BaseModel):
    """The complete script for one video, written in the creator's learned voice.
    hook and outro are required — a script missing either is incomplete."""
    id: str
    opportunity_id: str
    creator_id: str
    hook: Hook  # required — a script with no hook is incomplete
    scenes: list[Scene] = Field(min_length=1, description="At least one scene — hook + scenes + outro are all required")
    outro: Outro  # required — a script with no outro is incomplete
    full_voiceover_text: NonBlankStr  # concatenation of hook + scenes + outro — passed to TTS
    estimated_duration_seconds: NonNegInt  # required — the rendering layer uses it
    word_count: NonNegInt = 0


# --- Schema 5: Thumbnail Variant -------------------------------------------
class ThumbnailVariant(BaseModel):
    """One generated thumbnail option. Multiple variants are generated, then the
    scorer picks one (selected=True, with selection_reason)."""
    id: str
    asset_id: str
    variant_number: int = Field(ge=1, le=3)
    svg_source: NonBlankStr  # raw SVG markup the renderer needs
    png_path: str | None = None  # null until the rendering step produces the PNG
    layout_description: str = ""
    selected: bool = False  # only one variant per set is true — enforced by the orchestrator
    selection_reason: str | None = None

    @model_validator(mode="after")
    def _selection_consistency(self):
        if self.selected and not (self.selection_reason or "").strip():
            raise ValueError("selected thumbnails must carry a non-empty selection_reason")
        if not self.selected:
            self.selection_reason = None  # only the chosen variant explains itself
        return self


# --- Schema 6: Metadata -----------------------------------------------------
class Metadata(BaseModel):
    """Publishing metadata for one piece of content — title, description, tags.
    Title is written following the creator's title_formula; title_formula_match
    explains how it maps to that formula."""
    id: str
    asset_id: str
    title: NonBlankStr
    title_formula_match: NonBlankStr  # how the title maps to the creator's formula — shown in UI, scored
    description: NonBlankStr
    tags: list[str] = Field(min_length=5, max_length=20, description="5-20 tags for YouTube")
    category: str = ""
    scheduled_publish_time: str | None = None  # ISO timestamp, null until scheduled
    platform_targets: list[str] = ["youtube"]


# --- Schema 7: Quality Score ------------------------------------------------
class QualityScore(BaseModel):
    """The scorer agent's evaluation of a generated asset against the creator's
    DNA profile. passed is COMPUTED from overall_score vs threshold_used — the
    agent never sets it arbitrarily."""
    asset_id: str
    overall_score: float = Field(ge=0.0, le=1.0, description="Weighted composite of the dimension scores")
    thumbnail_fit_score: float = Field(ge=0.0, le=1.0)
    title_fit_score: float = Field(ge=0.0, le=1.0)
    voice_fit_score: float = Field(ge=0.0, le=1.0)
    passed: bool = False  # computed: overall_score >= threshold_used
    threshold_used: float = Field(default=QUALITY_THRESHOLD_DEFAULT, ge=0.0, le=1.0)
    rejection_reason: str | None = None  # set only when passed is False
    regeneration_count: Annotated[StrictInt, Field(ge=0, le=RETRY_CAP)] = 0  # starts at 0, max 2

    @model_validator(mode="after")
    def _compute_pass_and_reason(self):
        self.passed = self.overall_score >= self.threshold_used
        if self.passed:
            self.rejection_reason = None
        elif not (self.rejection_reason or "").strip():
            raise ValueError("a failing score must carry a non-empty rejection_reason")
        return self


# --- Schema 8: Decision Log Entry -------------------------------------------
class DecisionLogEntry(BaseModel):
    """One recorded decision by the orchestrator at any pipeline stage. The full
    set for one run is the decision log — the demo's most important output.
    rationale is a readable explanation of the agent's reasoning, not a
    technical log; it must reference the creator's DNA profile where relevant."""
    id: str
    pipeline_run_id: str
    creator_id: str
    timestamp: str  # ISO timestamp
    stage: Stage
    decision: str = Field(min_length=1, description="Plain language, 1-2 sentences — the UI headline")
    rationale: str = Field(min_length=1)
    input_summary: str = ""
    output_summary: str = ""
    score: float | None = None  # null for stages that don't produce a score
    status: LogStatus = "success"


# --- Schema 9: Generated Asset ---------------------------------------------
class VideoInfo(BaseModel):
    """Render state of the asset's video. file_path/duration_seconds are null
    until rendering is complete."""
    file_path: str | None = None
    duration_seconds: int | None = None
    resolution: str = "1920x1080"
    has_captions: bool = False
    render_status: RenderStatus = "pending"


class GeneratedAsset(BaseModel):
    """The complete production package for one piece of content. The DB stores
    script_id/metadata_id refs and thumbnails/quality_score keyed by asset_id;
    this model carries the assembled full objects."""
    id: str
    opportunity_id: str
    creator_id: str
    created_at: str = ""  # ISO timestamp
    script: Script | None = None
    video: VideoInfo = VideoInfo()
    thumbnails: list[ThumbnailVariant] = []
    metadata: Metadata | None = None
    quality_score: QualityScore | None = None  # null until the scorer has run
    pipeline_run_id: str = ""


# --- Schema 10: Pipeline Run ------------------------------------------------
class PipelineRun(BaseModel):
    """One complete end-to-end execution of the pipeline — the container that
    links all other objects from one run together. Polled by the dashboard via
    /pipeline/{run_id}/status."""
    id: str
    creator_id: str
    started_at: str  # ISO timestamp
    completed_at: str | None = None  # null while the run is in progress
    status: RunStatus = "running"
    current_stage: str = ""  # updated in real time; drives the PipelineProgress UI
    opportunity_id: str | None = None  # null until the opportunity agent selects one
    asset_id: str | None = None  # null until generation completes
    stages_completed: list[str] = []  # ordered, append-only
    stages_failed: list[str] = []
    total_duration_seconds: float | None = None  # null until the run completes
    total_llm_calls: int = 0
    regeneration_count: int = 0
