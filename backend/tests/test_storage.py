"""Phase 1 Step 2 storage-layer tests — plain-python, run directly:

    backend/.venv/Scripts/python backend/tests/test_storage.py

Runs entirely against a TEMP database (never touches the dev aftertake.db).
Proves the Step 2 done-definition: the file is created automatically, every
table exists with the right columns and indexes, each table round-trips a
record via direct function calls, the documented query patterns work, and
data survives closing/reopening the DB (a server restart).
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.db import database as db  # noqa: E402

ok = fail = 0


def check(name, cond, extra=""):
    global ok, fail
    if cond:
        ok += 1
        print(f"  PASS {name} {extra}")
    else:
        fail += 1
        print(f"  FAIL {name} {extra}")


EXPECTED_TABLES = {
    "source_videos", "creator_profiles", "pipeline_runs",
    "opportunities", "generated_assets", "decision_log",
}

EXPECTED_COLUMNS = {
    "source_videos": ["id", "creator_id", "title", "description", "transcript", "duration_seconds",
                      "published_at", "platform", "performance_json", "thumbnail_json", "tags_json", "category"],
    "creator_profiles": ["creator_id", "created_at", "updated_at", "source_video_count", "profile_json"],
    "pipeline_runs": ["id", "creator_id", "started_at", "completed_at", "status", "current_stage",
                      "opportunity_id", "asset_id", "stages_completed_json", "stages_failed_json",
                      "total_duration_seconds", "total_llm_calls", "regeneration_count"],
    "opportunities": ["id", "creator_id", "pipeline_run_id", "status", "opp_json"],
    "generated_assets": ["id", "creator_id", "pipeline_run_id", "opportunity_id", "render_status", "asset_json"],
    "decision_log": ["id", "pipeline_run_id", "creator_id", "timestamp", "stage", "decision",
                     "rationale", "input_summary", "output_summary", "score", "status"],
}

EXPECTED_INDEXES = {
    "idx_source_videos_creator", "idx_runs_creator",
    "idx_opportunities_creator", "idx_opportunities_run", "idx_opportunities_status",
    "idx_assets_run", "idx_assets_opportunity",
    "idx_decision_log_run", "idx_decision_log_creator", "idx_decision_log_time",
}


def main():
    tmp = tempfile.mkdtemp(prefix="aftertake_test_")
    db_path = Path(tmp) / "test.db"

    # 1. init creates the file + all tables (the startup routine's job)
    conn = db.init_db(db_path)
    check("DB file created automatically by init", db_path.exists())
    tables = {r["name"] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
    check("all 6 plan tables exist", tables == EXPECTED_TABLES,
          f"(got {sorted(tables)})")

    # 2. right columns per table
    for table, cols in EXPECTED_COLUMNS.items():
        actual = [r["name"] for r in conn.execute(f"PRAGMA table_info({table})")]
        check(f"{table} has the right columns", actual == cols)

    # 3. right indexes per plan
    indexes = {r["name"] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'")}
    check("all plan indexes exist", EXPECTED_INDEXES <= indexes,
          f"(missing {sorted(EXPECTED_INDEXES - indexes)})")

    # 4. write/read round-trip through direct function calls (not the API)
    conn.execute(
        "INSERT INTO source_videos (id, creator_id, title, transcript, duration_seconds,"
        " published_at, platform, performance_json, thumbnail_json, tags_json, category)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        ("sv_t", "creator_001", "Test Video", "transcript here", 300, "2024-01-01",
         "youtube", db.dumps({"views": 100, "likes": 5, "comments": 2, "watch_time_hours": 1.5}),
         db.dumps({"url": "", "description": "Solid background, bold text."}),
         db.dumps(["test"]), "Tech"),
    )
    row = conn.execute("SELECT * FROM source_videos WHERE id='sv_t'").fetchone()
    check("source_videos round-trip (nested JSON intact)",
          row["title"] == "Test Video" and db.loads(row["performance_json"])["views"] == 100
          and db.loads(row["tags_json"]) == ["test"])

    profile = {"creator_id": "creator_001", "voice": {"tone": "direct"}}
    conn.execute("INSERT INTO creator_profiles (creator_id, created_at, updated_at,"
                 " source_video_count, profile_json) VALUES (?,?,?,?,?)",
                 ("creator_001", "t0", "t1", 8, db.dumps(profile)))
    row = conn.execute("SELECT * FROM creator_profiles WHERE creator_id='creator_001'").fetchone()
    check("creator_profiles round-trip (whole profile JSON)",
          db.loads(row["profile_json"])["voice"]["tone"] == "direct")

    conn.execute("INSERT INTO pipeline_runs (id, creator_id, started_at, status, current_stage,"
                 " stages_completed_json, stages_failed_json, total_llm_calls, regeneration_count)"
                 " VALUES (?,?,?,?,?,?,?,?,?)",
                 ("run_t", "creator_001", "t0", "running", "script_agent",
                  db.dumps(["dna_agent"]), db.dumps([]), 2, 0))
    row = conn.execute("SELECT * FROM pipeline_runs WHERE id='run_t'").fetchone()
    check("pipeline_runs round-trip (JSON arrays + counters)",
          db.loads(row["stages_completed_json"]) == ["dna_agent"] and row["total_llm_calls"] == 2)

    opp = {"id": "opp_t", "creator_id": "creator_001", "topic": "Testing tools",
           "fit_score": 0.87, "status": "pending"}
    conn.execute("INSERT INTO opportunities (id, creator_id, pipeline_run_id, status, opp_json)"
                 " VALUES (?,?,?,?,?)", ("opp_t", "creator_001", "run_t", "pending", db.dumps(opp)))
    row = conn.execute("SELECT * FROM opportunities WHERE id='opp_t'").fetchone()
    check("opportunities round-trip (full object JSON + status column)",
          db.loads(row["opp_json"])["fit_score"] == 0.87 and row["status"] == "pending")
    check("opportunities query by status (the reason status is a column)",
          conn.execute("SELECT COUNT(*) AS c FROM opportunities WHERE status='pending'").fetchone()["c"] == 1)

    asset = {"id": "asset_t", "creator_id": "creator_001", "script": {"id": "s1"},
             "video": {"render_status": "complete"}}
    conn.execute("INSERT INTO generated_assets (id, creator_id, pipeline_run_id, opportunity_id,"
                 " render_status, asset_json) VALUES (?,?,?,?,?,?)",
                 ("asset_t", "creator_001", "run_t", "opp_t", "complete", db.dumps(asset)))
    row = conn.execute("SELECT * FROM generated_assets WHERE id='asset_t'").fetchone()
    check("generated_assets round-trip (full asset JSON + render_status column)",
          db.loads(row["asset_json"])["script"]["id"] == "s1" and row["render_status"] == "complete")
    check("generated_assets query by render_status (the reason it's a column)",
          conn.execute("SELECT COUNT(*) AS c FROM generated_assets WHERE render_status='complete'").fetchone()["c"] == 1)

    for i, stage in enumerate(["dna_agent", "opportunity_agent"]):
        conn.execute("INSERT INTO decision_log (id, pipeline_run_id, creator_id, timestamp, stage,"
                     " decision, rationale, score, status) VALUES (?,?,?,?,?,?,?,?,?)",
                     (f"log_t{i}", "run_t", "creator_001", f"2026-01-01T00:00:0{i}+00:00", stage,
                      f"decision {i}", f"rationale {i}", 0.87 if i else None, "success"))
    rows = conn.execute("SELECT * FROM decision_log WHERE pipeline_run_id='run_t'"
                        " ORDER BY timestamp ASC").fetchall()
    check("decision_log append-only by run, ordered by timestamp (columns, not JSON)",
          [r["stage"] for r in rows] == ["dna_agent", "opportunity_agent"] and rows[0]["score"] is None)
    conn.commit()
    conn.close()

    # 5. restart persistence: fresh connection, data still there
    conn2 = db.get_connection(db_path)
    check("data survives reopen (restart)",
          conn2.execute("SELECT COUNT(*) AS c FROM source_videos WHERE id='sv_t'").fetchone()["c"] == 1
          and conn2.execute("SELECT COUNT(*) AS c FROM opportunities").fetchone()["c"] == 1
          and conn2.execute("SELECT COUNT(*) AS c FROM decision_log").fetchone()["c"] == 2)
    # init again on the existing DB must NOT drop or recreate anything (no data loss)
    db.init_db(db_path)
    check("re-init is idempotent and never drops data",
          conn2.execute("SELECT COUNT(*) AS c FROM source_videos WHERE id='sv_t'").fetchone()["c"] == 1)
    conn2.close()

    print(f"\n{ok} passed, {fail} failed")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
