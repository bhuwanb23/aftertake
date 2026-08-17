"""Phase 1 Step 5 seed-data verification — plain-python, run directly:

    backend/.venv/Scripts/python backend/tests/test_seed.py

Proves the Step 5 done-definition against a TEMP database:
  - all 8 seed videos validate through the SourceVideo model (every field
    populated, every nested object present, types correct)
  - they store through the same insert path the seed loader / /catalog/ingest
    use, and load is idempotent
  - they are retrieved by creator_id with a single query
  - what comes back matches what went in, field by field — no dropped fields,
    no coerced types, no nulls where real values were stored
  - the five performance benchmarks are computed in Python (never the LLM) and
    match the recorded values the DNA agent will receive in Phase 2
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.agents.benchmarks import compute_performance_benchmarks  # noqa: E402
from backend.db import database as db  # noqa: E402
from backend.models.schemas import SourceVideo  # noqa: E402

ok = fail = 0


def check(name, cond, extra=""):
    global ok, fail
    if cond:
        ok += 1
        print(f"  PASS {name} {extra}")
    else:
        fail += 1
        print(f"  FAIL {name} {extra}")


CATALOG_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "seed" / "catalog.json"

INSERT_SQL = (
    "INSERT OR REPLACE INTO source_videos"
    " (id, creator_id, title, description, transcript, duration_seconds,"
    "  published_at, platform, performance_json, thumbnail_json, tags_json, category)"
    " VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"
)


def insert_video(conn, creator_id, v):
    conn.execute(
        INSERT_SQL,
        (v["id"], creator_id, v["title"], v.get("description", ""), v["transcript"],
         v["duration_seconds"], v["published_at"], v["platform"],
         db.dumps(v["performance"]), db.dumps(v["thumbnail"]), db.dumps(v.get("tags", [])),
         v.get("category", "")),
    )


def row_to_video(row):
    """Reconstruct the SourceVideo shape from a DB row — exactly what a read
    path (and later the DNA agent) does."""
    return {
        "id": row["id"], "title": row["title"], "description": row["description"],
        "transcript": row["transcript"], "duration_seconds": row["duration_seconds"],
        "published_at": row["published_at"], "platform": row["platform"],
        "performance": db.loads(row["performance_json"]),
        "thumbnail": db.loads(row["thumbnail_json"]),
        "tags": db.loads(row["tags_json"]),
        "category": row["category"],
    }


def main():
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    creator_id = data["creator_id"]
    raw_videos = data["videos"]

    check("catalog file has 8 videos", len(raw_videos) == 8)

    # 1. every video validates through the SourceVideo model, fully populated
    models = [SourceVideo.model_validate(v) for v in raw_videos]
    check("all 8 pass SourceVideo validation", len(models) == 8)
    for m in models:
        p = m.performance
        check(f"{m.id} fully populated (scalars + nested + tags)",
              all(getattr(m, f) is not None for f in
                  ["id", "title", "transcript", "duration_seconds", "published_at", "platform"])
              and m.thumbnail.description.strip()
              and p.views is not None and p.likes is not None and p.comments is not None
              and p.watch_time_hours is not None)

    # 2. store through the same insert path into a temp DB
    tmp = tempfile.mkdtemp(prefix="aftertake_seed_")
    conn = db.init_db(Path(tmp) / "test.db")
    for v in raw_videos:
        insert_video(conn, creator_id, v)
    conn.commit()

    # 3. retrieve all by creator_id with a single query
    rows = conn.execute(
        "SELECT * FROM source_videos WHERE creator_id = ? ORDER BY id", (creator_id,)
    ).fetchall()
    check("all 8 retrieved by creator_id with one query", len(rows) == 8)

    # 4. strict round-trip fidelity — field-by-field, no drops/coercions/null swaps
    expected = {m["id"]: m for m in (m.model_dump() for m in models)}
    for row in rows:
        actual = row_to_video(row)
        exp = expected[row["id"]]
        check(f"{row['id']} round-trips exactly (nested objects intact)",
              actual == exp)
        check(f"{row['id']} no phantom nulls (real values never nulled)",
              all(v is not None for k, v in actual.items()
                  if exp.get(k) is not None))

    # 5. idempotent load (INSERT OR REPLACE — no duplicates)
    for v in raw_videos:
        insert_video(conn, creator_id, v)
    conn.commit()
    n = conn.execute("SELECT COUNT(*) AS c FROM source_videos WHERE creator_id = ?",
                     (creator_id,)).fetchone()["c"]
    check("re-load is idempotent (still 8 rows)", n == 8)

    # 6. the five performance benchmarks — computed in Python, matching the
    #    recorded values that get passed into the DNA agent's prompt context
    b = compute_performance_benchmarks([m.model_dump() for m in models])
    expected_benchmarks = {
        "avg_views": 226625.0,
        "avg_ctr": 6.5,
        "avg_retention": 50.1,
        "top_quartile_views": 420000.0,
        "bottom_quartile_views": 28000.0,
    }
    for key, val in expected_benchmarks.items():
        check(f"benchmark {key} == {val}", b[key] == val, f"(got {b[key]})")
    conn.close()

    print(f"\n{ok} passed, {fail} failed")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
