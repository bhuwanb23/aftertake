"""Content endpoints (Phase 0 Step 10 API contract).

All four endpoints are agent/publisher territory:
  recommend — opportunity agent in isolation          (Phase 2)
  generate  — script + thumbnail + metadata agents    (Phase 2)
  score     — scorer agent + decision-log writes      (Phase 2)
  publish   — platform push (YouTube)                 (Phase 4)

The request/response contracts are locked here so the frontend can build
against them; the handlers return 501 until their agent lands.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.models.schemas import DecisionLogEntry, QualityScore

router = APIRouter(prefix="/content", tags=["content"])


# --- POST /content/recommend -------------------------------------------------
class RecommendRequest(BaseModel):
    creator_id: str
    topic_hint: str | None = None
    count: int = 3


@router.post("/recommend")
def recommend(body: RecommendRequest):
    # Phase 2: run the opportunity agent in isolation for body.creator_id.
    raise HTTPException(
        status_code=501,
        detail="Opportunity agent not implemented yet (Phase 2).",
    )


# --- POST /content/generate --------------------------------------------------
class GenerateRequest(BaseModel):
    opportunity_id: str


@router.post("/generate")
def generate(body: GenerateRequest):
    # Phase 2: script agent -> thumbnail agent -> metadata agent for the
    # opportunity. No scorer, no video render. Returns a partial GeneratedAsset
    # (video and quality_score null).
    raise HTTPException(
        status_code=501,
        detail="Generation agents not implemented yet (Phase 2).",
    )


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
    # Phase 2: scorer agent evaluates the asset, stores the QualityScore, writes
    # DecisionLogEntry objects (incl. reject/regenerate), and returns them.
    raise HTTPException(
        status_code=501,
        detail="Scorer agent not implemented yet (Phase 2).",
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
    # Phase 4: push the scored, passed asset to the platform (YouTube Data API)
    # or schedule it. Returns the platform post id + public URL.
    raise HTTPException(
        status_code=501,
        detail="Publisher not implemented yet (Phase 4).",
    )
