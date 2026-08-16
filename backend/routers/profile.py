"""Profile endpoints (Phase 0 Step 10 API contract).

GET  /profile/{creator_id} — retrieve the stored CreatorDNAProfile, or 404.
POST /profile/build       — trigger the DNA agent to build a profile from the
                            stored catalog. The agent lands in Phase 2; this
                            endpoint is wired to it and returns 501 until then.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.db import database as db

router = APIRouter(prefix="/profile", tags=["profile"])


class BuildRequest(BaseModel):
    creator_id: str


@router.post("/build")
def build_profile(body: BuildRequest):
    # Phase 2: read the catalog for body.creator_id, call the DNA agent,
    # store the resulting CreatorDNAProfile, return it.
    raise HTTPException(
        status_code=501,
        detail="DNA agent not implemented yet (Phase 2).",
    )


@router.get("/{creator_id}")
def get_profile(creator_id: str):
    conn = db.get_connection()
    row = conn.execute(
        "SELECT * FROM creator_profiles WHERE creator_id = ?", (creator_id,)
    ).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(
            status_code=404,
            detail=f"No profile found for creator {creator_id}.",
        )
    profile = db.loads(row["profile_json"])
    # Identity fields live in columns; column values win over the JSON copy.
    profile["creator_id"] = row["creator_id"]
    profile["created_at"] = row["created_at"]
    profile["updated_at"] = row["updated_at"]
    profile["source_video_count"] = row["source_video_count"]
    return profile
