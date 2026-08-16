"""All AfterTake data shapes, defined in one place (Phase 0 Step 9).

Both the API layer and the agent layer import from here.
Never define a data shape anywhere else.
"""
from pydantic import BaseModel, Field


# --- Schema 1: Source Video ------------------------------------------------
class Performance(BaseModel):
    """Real performance metrics for one catalog video. Null = unknown, not zero."""
    views: int
    likes: int
    comments: int
    shares: int | None = None
    ctr: float | None = Field(default=None, description="Click-through rate, 0.0-100.0")
    avg_retention: float | None = Field(default=None, description="Avg % of video watched, 0.0-100.0")
    watch_time_hours: float


class Thumbnail(BaseModel):
    """Thumbnail reference for one catalog video. description is how the DNA
    agent learns visual style without doing image analysis."""
    url: str = ""
    description: str = ""


class SourceVideo(BaseModel):
    """One past video from the creator's catalog. Raw input to the DNA agent."""
    id: str
    title: str
    description: str = ""
    transcript: str = ""
    duration_seconds: int
    published_at: str  # ISO date (YYYY-MM-DD)
    platform: str = "youtube"  # youtube | tiktok | instagram | linkedin
    performance: Performance
    thumbnail: Thumbnail = Thumbnail()
    tags: list[str] = []
    category: str = ""


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
    avg_word_count: int = 0
    uses_caps: bool = False
    uses_numbers: bool = False
    uses_questions: bool = False
    emotional_hook_type: str = "curiosity gap"  # curiosity gap | social proof | fomo | personal authority | specific transformation | controversy
    example_titles: list[str] = []


class ThumbnailStyle(BaseModel):
    """The recurring visual style of the creator's thumbnails."""
    dominant_colors: list[str] = []
    layout_pattern: str
    text_style: str
    facial_expression: str
    uses_props: bool = False
    background_type: str = "solid color"  # solid color | gradient | blurred real location | illustrated/graphic | product or app screenshot
    uses_graphic_elements: bool = False


class DurationRange(BaseModel):
    """A min/max duration range (seconds)."""
    min: int = 0
    max: int = 0


class ContentPatterns(BaseModel):
    """Formats, topics, and cadence that correlate with the creator's performance."""
    avg_duration_seconds: int = 0
    optimal_duration_range: DurationRange = DurationRange()
    format_preferences: list[str] = []
    posting_frequency: str = ""
    best_performing_topics: list[str] = []
    worst_performing_topics: list[str] = []


class PerformanceBenchmarks(BaseModel):
    """Calculated mathematically from the catalog — never LLM-generated."""
    avg_views: float = 0.0
    avg_ctr: float = 0.0
    avg_retention: float = 0.0
    top_quartile_views: float = 0.0
    bottom_quartile_views: float = 0.0


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
    dna_fit_explanation: str
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
    confidence: str = "medium"  # high | medium | low
    recommended_format: str = ""
    recommended_duration_seconds: int = 0
    target_hook: str = ""
    status: str = "pending"  # pending | approved | rejected | in_production | published


# --- Schema 4: Script -------------------------------------------------------
class Hook(BaseModel):
    """The opening 5-15 seconds of the video."""
    voiceover_text: str
    visual_description: str
    duration_seconds: int


class Scene(BaseModel):
    """One scene of the video. scene_type maps directly to HyperFrames template types."""
    scene_number: int
    scene_type: str  # talking_head | text_overlay | title_card | comparison_split | list_reveal | b_roll_description
    voiceover_text: str
    visual_description: str
    on_screen_text: str | None = None
    duration_seconds: int


class Outro(BaseModel):
    """The closing section with the call to action."""
    voiceover_text: str
    visual_description: str
    call_to_action: str
    duration_seconds: int


class Script(BaseModel):
    """The complete script for one video, written in the creator's learned voice."""
    id: str
    opportunity_id: str
    creator_id: str
    hook: Hook
    scenes: list[Scene] = []
    outro: Outro
    full_voiceover_text: str = ""  # concatenation of hook + scenes + outro — passed to TTS
    estimated_duration_seconds: int = 0
    word_count: int = 0


# --- Schema 5: Thumbnail Variant -------------------------------------------
class ThumbnailVariant(BaseModel):
    """One generated thumbnail option. Multiple variants are generated, then the
    scorer picks one (selected=True, with selection_reason)."""
    id: str
    asset_id: str
    variant_number: int  # 1, 2, or 3
    svg_source: str = ""  # raw SVG markup — cairosvg converts this to PNG
    png_path: str = ""  # e.g. ./output/thumbnails/thumb_001_v1.png
    layout_description: str = ""
    selected: bool = False
    selection_reason: str | None = None


# --- Schema 6: Metadata -----------------------------------------------------
class Metadata(BaseModel):
    """Publishing metadata for one piece of content — title, description, tags.
    Title is written following the creator's title_formula; title_formula_match
    explains how it maps to that formula."""
    id: str
    asset_id: str
    title: str
    title_formula_match: str = ""
    description: str = ""
    tags: list[str] = []  # 10-15 tags for YouTube
    category: str = ""
    scheduled_publish_time: str | None = None  # ISO timestamp, null until scheduled
    platform_targets: list[str] = ["youtube"]


# --- Schema 7: Quality Score ------------------------------------------------
class QualityScore(BaseModel):
    """The scorer agent's evaluation of a generated asset against the creator's
    DNA profile. Rule: passed == (overall_score >= threshold_used)."""
    asset_id: str
    overall_score: float = Field(ge=0.0, le=1.0, description="Weighted composite of the dimension scores")
    thumbnail_fit_score: float = Field(ge=0.0, le=1.0)
    title_fit_score: float = Field(ge=0.0, le=1.0)
    voice_fit_score: float = Field(ge=0.0, le=1.0)
    passed: bool = False
    threshold_used: float = Field(default=0.75, ge=0.0, le=1.0)
    rejection_reason: str | None = None  # set only when passed is False
    regeneration_count: int = Field(default=0, ge=0, le=2, description="Max 2 — the retry cap")


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
    stage: str  # dna_agent | opportunity_agent | script_agent | thumbnail_agent | metadata_agent | scorer | regenerate | publish
    decision: str  # plain language, 1-2 sentences
    rationale: str = ""
    input_summary: str = ""
    output_summary: str = ""
    score: float | None = None  # null for stages that don't produce a score
    status: str = "success"  # success | rejected | regenerated | failed


# --- Schema 9: Generated Asset ---------------------------------------------
class VideoInfo(BaseModel):
    """Render state of the asset's video. file_path/duration_seconds are null
    until rendering is complete."""
    file_path: str | None = None
    duration_seconds: int | None = None
    resolution: str = "1920x1080"
    has_captions: bool = False
    render_status: str = "pending"  # pending | rendering | complete | failed


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
    status: str = "running"  # running | complete | failed | partial
    current_stage: str = ""  # updated in real time; drives the PipelineProgress UI
    opportunity_id: str | None = None  # null until the opportunity agent selects one
    asset_id: str | None = None  # null until generation completes
    stages_completed: list[str] = []  # ordered
    stages_failed: list[str] = []
    total_duration_seconds: float | None = None  # null until the run completes
    total_llm_calls: int = 0
    regeneration_count: int = 0
