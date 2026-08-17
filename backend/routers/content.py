"""Content endpoints (Phase 0 Step 10 API contract).

  recommend — opportunity agent in isolation          (Phase 2)
  generate  — script + thumbnail + metadata agents    (Phase 2)
  score     — scorer agent + decision-log writes      (Phase 2)
  publish   — platform push (YouTube)                 (Phase 4)

Phase 1: every handler returns a realistic STUB response (routers/stubs.py)
shaped exactly like the real response will be, so the frontend can build
against the full contract now. Phase 2+ swaps the stubs for real agents.
"""
from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

from backend.models.schemas import DecisionLogEntry, QualityScore
from backend.routers import stubs

router = APIRouter(prefix="/content", tags=["content"])

# Alternates reject/pass on each call so the frontend can build BOTH decision
# log states (rejection + regeneration + pass) against the same endpoint.
_score_calls = 0


# --- POST /content/recommend -------------------------------------------------
class RecommendRequest(BaseModel):
    creator_id: str
    topic_hint: str | None = None
    count: int = 3


@router.post("/recommend")
def recommend(body: RecommendRequest):
    # Phase 1 STUB. Phase 2: run the opportunity agent in isolation.
    opps = stubs.opportunities(body.creator_id)
    return [o.model_dump() for o in opps[: max(1, min(body.count, len(opps)))]]


# --- POST /content/generate --------------------------------------------------
class GenerateRequest(BaseModel):
    opportunity_id: str


@router.post("/generate")
def generate(body: GenerateRequest):
    # Phase 1 STUB. Phase 2: script -> thumbnail -> metadata agents in sequence.
    # Returns a partial GeneratedAsset — video pending, quality_score null.
    asset = stubs.asset(body.opportunity_id, stubs.STUB_CREATOR_ID, "", with_score=False)
    return asset.model_dump()


# --- POST /content/score -----------------------------------------------------
class ScoreRequest(BaseModel):
    asset_id: str


class ScoreResponse(BaseModel):
    asset_id: str
    quality_score: QualityScore
    passed: bool
    decision_log_entries: list[DecisionLogEntry]


@router.post("/score")
def score(body: ScoreRequest):
    # Phase 1 STUB: alternate a rejection (0.62, with reason + regenerate entry)
    # and a pass (0.81) so the UI can render both decision-log states.
    # Phase 2: real scorer agent evaluates the asset and persists the entries.
    global _score_calls
    _score_calls += 1
    ts = datetime.now(timezone.utc).isoformat()

    if _score_calls % 2 == 1:
        qs = QualityScore(
            asset_id=body.asset_id,
            overall_score=0.62,
            thumbnail_fit_score=0.45,
            title_fit_score=0.80,
            voice_fit_score=0.76,
            threshold_used=0.75,
            regeneration_count=1,
            rejection_reason=(
                "Thumbnail uses a blurred background, but this creator's profile specifies "
                "solid color backgrounds with a prominent creator face. Title and voice fit "
                "cleared the gate, but the visual check failed."
            ),
        )
        entries = [
            DecisionLogEntry(
                id=f"log_score_{_score_calls}_1",
                pipeline_run_id="",
                creator_id=stubs.STUB_CREATOR_ID,
                timestamp=ts,
                stage="scorer",
                decision="Thumbnail variant REJECTED — overall score 0.62 is below the 0.75 threshold.",
                rationale=(
                    "The thumbnail uses a blurred background, but this creator's profile specifies "
                    "solid color backgrounds with a prominent creator face. Title and voice fit "
                    "cleared the gate, but the visual check failed."
                ),
                input_summary=f"GeneratedAsset {body.asset_id} vs CreatorDNAProfile",
                output_summary="Rejection triggered regeneration",
                score=0.62,
                status="rejected",
            ),
            DecisionLogEntry(
                id=f"log_score_{_score_calls}_2",
                pipeline_run_id="",
                creator_id=stubs.STUB_CREATOR_ID,
                timestamp=ts,
                stage="regenerate",
                decision="Regenerating thumbnail set. Attempt 2 of 2.",
                rationale="Regeneration re-runs the thumbnail agent with the scorer's rejection reason appended.",
                input_summary="Scorer rejection reason",
                output_summary="New ThumbnailVariant set",
                status="regenerated",
            ),
        ]
    else:
        qs = QualityScore(
            asset_id=body.asset_id,
            overall_score=0.81,
            thumbnail_fit_score=0.88,
            title_fit_score=0.84,
            voice_fit_score=0.79,
            threshold_used=0.75,
            regeneration_count=1,
        )
        entries = [
            DecisionLogEntry(
                id=f"log_score_{_score_calls}_1",
                pipeline_run_id="",
                creator_id=stubs.STUB_CREATOR_ID,
                timestamp=ts,
                stage="scorer",
                decision="Asset passed quality gate with overall score 0.81.",
                rationale=(
                    "All dimension scores clear the threshold: thumbnail fit 0.88 (solid color "
                    "background, creator face, all-caps text), title fit 0.84 (formula match), "
                    "voice fit 0.79."
                ),
                input_summary=f"Regenerated asset {body.asset_id} vs CreatorDNAProfile",
                output_summary="QualityScore 0.81 — asset approved",
                score=0.81,
                status="success",
            ),
        ]

    return ScoreResponse(
        asset_id=body.asset_id,
        quality_score=qs,
        passed=qs.passed,
        decision_log_entries=entries,
    )


# --- POST /content/publish ---------------------------------------------------
class PublishRequest(BaseModel):
    asset_id: str
    platform: str = "youtube"  # e.g. "youtube"
    scheduled_time: str | None = None  # ISO timestamp or null


class PublishResponse(BaseModel):
    platform_post_id: str
    url: str
    status: str  # "published" | "scheduled"
    published_at: str


@router.post("/publish")
def publish(body: PublishRequest):
    # Phase 1 STUB. Phase 4: push the scored, passed asset to the platform
    # (YouTube Data API) or schedule it, then return the post id + URL.
    payload = stubs.publish_payload()
    payload["status"] = "scheduled" if body.scheduled_time else "published"
    return PublishResponse(**payload)
