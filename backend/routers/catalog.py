"""Catalog endpoints (Phase 0 Step 10 API contract).

POST /catalog/ingest — accepts a batch of Source Video objects and stores them
in the database. Storage only; no agent logic runs here.
"""
from fastapi import APIRouter
from pydantic import BaseModel

from backend.db import database as db
from backend.models.schemas import SourceVideo

router = APIRouter(prefix="/catalog", tags=["catalog"])


class IngestRequest(BaseModel):
    creator_id: str
    videos: list[SourceVideo]


class IngestResponse(BaseModel):
    creator_id: str
    videos_ingested: int
    status: str  # "success" | "error"
    message: str


@router.post("/ingest", response_model=IngestResponse)
def ingest(body: IngestRequest) -> IngestResponse:
    conn = db.get_connection()
    count = 0
    try:
        for v in body.videos:
            conn.execute(
                """INSERT OR REPLACE INTO source_videos
                   (id, creator_id, title, description, transcript,
                    duration_seconds, published_at, platform,
                    performance_json, thumbnail_json, tags_json, category)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    v.id,
                    body.creator_id,
                    v.title,
                    v.description,
                    v.transcript,
                    v.duration_seconds,
                    v.published_at,
                    v.platform,
                    db.dumps(v.performance.model_dump()),
                    db.dumps(v.thumbnail.model_dump()),
                    db.dumps(v.tags),
                    v.category,
                ),
            )
            count += 1
        conn.commit()
    except Exception as exc:  # storage failure — report per the contract, don't 500
        conn.rollback()
        return IngestResponse(
            creator_id=body.creator_id,
            videos_ingested=0,
            status="error",
            message=str(exc),
        )
    finally:
        conn.close()
    return IngestResponse(
        creator_id=body.creator_id,
        videos_ingested=count,
        status="success",
        message=f"Ingested {count} videos for creator {body.creator_id}.",
    )
