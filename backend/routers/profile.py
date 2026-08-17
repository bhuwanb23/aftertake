"""Profile endpoints (Phase 0 Step 10 API contract).

GET  /profile/{creator_id} — retrieve the stored CreatorDNAProfile, or 404.
POST /profile/build       — trigger the DNA agent to build a profile from the
                            stored catalog.

Phase 1: build returns a realistic STUB profile (routers/stubs.py) so the
frontend can build against it. GET falls back to that same stub for the seeded
demo creator (creator_001) when no profile is stored yet — per Phase 1 Step 3,
the demo creator's profile must always render. Phase 2 replaces the stub with
the real DNA agent; the storage path is the same either way.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.db import database as db
from backend.routers import stubs

router = APIRouter(prefix="/profile", tags=["profile"])


class BuildRequest(BaseModel):
    creator_id: str


@router.post("/build")
def build_profile(body: BuildRequest):
    # Phase 1 STUB: return a realistic profile and store it so GET /profile/{id}
    # works. Phase 2: read the catalog, call the DNA agent, same store path.
    profile = stubs.dna_profile(body.creator_id)
    conn = db.get_connection()
    try:
        conn.execute(
            """INSERT OR REPLACE INTO creator_profiles
               (creator_id, created_at, updated_at, source_video_count, profile_json)
               VALUES (?,?,?,?,?)""",
            (
                profile.creator_id,
                profile.created_at,
                profile.updated_at,
                profile.source_video_count,
                db.dumps(profile.model_dump()),
            ),
        )
        conn.commit()
    finally:
        conn.close()
    return profile.model_dump()


@router.get("/{creator_id}")
def get_profile(creator_id: str):
    conn = db.get_connection()
    row = conn.execute(
        "SELECT * FROM creator_profiles WHERE creator_id = ?", (creator_id,)
    ).fetchone()
    conn.close()
    if row is None:
        # Phase 1 STUB fallback: the seeded demo creator's profile always
        # renders, even before build has run. Removed when the real DNA agent
        # lands (Phase 2) — stored profiles then always win.
        if creator_id == stubs.STUB_CREATOR_ID:
            return stubs.dna_profile(creator_id).model_dump()
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
