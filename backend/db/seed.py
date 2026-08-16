"""Load the seed catalog (data/seed/catalog.json) into the database.

Usage (from the repo root, backend venv's python):

    python -m backend.db.seed [--path data/seed/catalog.json]

Mirrors POST /catalog/ingest — same columns, same storage-only behavior.
Idempotent: videos are INSERT OR REPLACE, so re-running is safe.
Validates each video against SourceVideo when pydantic is installed,
otherwise falls back to structural checks.
"""
import argparse
import json
import sys
from pathlib import Path

try:
    from . import database
except ImportError:  # allow `python backend/db/seed.py` as a fallback
    from backend.db import database

try:
    from ..models.schemas import SourceVideo
    HAS_PYDANTIC = True
except Exception:  # pydantic not installed yet — fall back to structural checks
    SourceVideo = None
    HAS_PYDANTIC = False

DEFAULT_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "seed" / "catalog.json"

REQUIRED_KEYS = {"id", "title", "transcript", "duration_seconds", "published_at", "platform", "performance", "thumbnail", "tags", "category"}


def main():
    parser = argparse.ArgumentParser(description="Load the seed catalog into the AfterTake DB.")
    parser.add_argument("--path", default=str(DEFAULT_PATH), help="Path to the catalog JSON file")
    args = parser.parse_args()

    data = json.loads(Path(args.path).read_text(encoding="utf-8"))
    creator_id = data.get("creator_id")
    videos = data.get("videos", [])
    if not creator_id or not videos:
        print("ERROR: catalog file must contain creator_id and a non-empty videos list.")
        sys.exit(1)

    conn = database.get_connection()
    inserted = 0
    try:
        for v in videos:
            if HAS_PYDANTIC:
                SourceVideo.model_validate(v)  # raises on invalid shape
            else:
                missing = REQUIRED_KEYS - set(v)
                if missing:
                    print(f"ERROR: video {v.get('id')} missing keys: {sorted(missing)}")
                    sys.exit(1)
            conn.execute(
                """INSERT OR REPLACE INTO source_videos
                   (id, creator_id, title, description, transcript,
                    duration_seconds, published_at, platform,
                    performance_json, thumbnail_json, tags_json, category)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    v["id"],
                    creator_id,
                    v["title"],
                    v.get("description", ""),
                    v["transcript"],
                    v["duration_seconds"],
                    v["published_at"],
                    v["platform"],
                    database.dumps(v["performance"]),
                    database.dumps(v["thumbnail"]),
                    database.dumps(v.get("tags", [])),
                    v.get("category", ""),
                ),
            )
            inserted += 1
        conn.commit()
    finally:
        conn.close()
    print(f"Seeded {inserted} videos for creator {creator_id} (validation: {'pydantic' if HAS_PYDANTIC else 'structural'}).")


if __name__ == "__main__":
    sys.exit(main())
