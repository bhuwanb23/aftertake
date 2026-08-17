"""Phase 1 Step 6 API-contract test — plain-python, run directly:

    backend/.venv/Scripts/python backend/tests/test_api.py

Hits every endpoint through FastAPI's TestClient (an in-process REST client)
against a TEMP database, proving the Step 6 item: "every endpoint returns a
sensible response from a REST client", including the pipeline/run response with
its full decision log (rejection + regeneration entries visible).
"""
import os
import sys
import tempfile
from pathlib import Path

# Point the app at a temp DB BEFORE importing it (connections are per-request,
# so the env var just needs to be set before the first call).
_tmp = tempfile.mkdtemp(prefix="aftertake_api_")
os.environ["DATABASE_PATH"] = str(Path(_tmp) / "api_test.db")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi.testclient import TestClient  # noqa: E402

from backend.main import app  # noqa: E402

ok = fail = 0


def check(name, cond, extra=""):
    global ok, fail
    if cond:
        ok += 1
        print(f"  PASS {name} {extra}")
    else:
        fail += 1
        print(f"  FAIL {name} {extra}")


VALID_VIDEO = {
    "id": "sv_001", "title": "I Used Notion for 30 Days",
    "description": "", "transcript": "So I gave Notion an honest 30 days.",
    "duration_seconds": 487, "published_at": "2024-01-15", "platform": "youtube",
    "performance": {"views": 420000, "likes": 18400, "comments": 1240, "watch_time_hours": 68.0},
    "thumbnail": {"url": "", "description": "Orange background. Creator surprised. Text '30 DAYS'."},
    "tags": ["notion", "productivity"], "category": "Science & Technology",
}


def main():
    with TestClient(app) as c:  # context manager runs the lifespan (init_db)
        # health
        check("GET /health", c.get("/health").status_code == 200)

        # catalog
        r = c.post("/catalog/ingest", json={"creator_id": "creator_001", "videos": [VALID_VIDEO]})
        j = r.json()
        check("POST /catalog/ingest", r.status_code == 200 and j["status"] == "success" and j["videos_ingested"] == 1)

        # profile
        r = c.post("/profile/build", json={"creator_id": "creator_001"}); j = r.json()
        check("POST /profile/build", r.status_code == 200 and j["creator_id"] == "creator_001"
              and all(k in j for k in ["voice", "title_formula", "thumbnail_style",
                                       "content_patterns", "performance_benchmarks"]))
        check("GET /profile/creator_001", c.get("/profile/creator_001").status_code == 200)
        check("GET /profile/nope -> 404", c.get("/profile/nope").status_code == 404)

        # recommend
        r = c.post("/content/recommend", json={"creator_id": "creator_001", "count": 3}); j = r.json()
        check("POST /content/recommend (3 ranked)", len(j) == 3
              and [round(o["fit_score"], 2) for o in j] == [0.87, 0.71, 0.58])

        # generate
        r = c.post("/content/generate", json={"opportunity_id": "opp_stub_001"}); j = r.json()
        check("POST /content/generate (script + 3 thumbs + metadata, video pending)",
              j["script"] and len(j["thumbnails"]) == 3 and j["metadata"]["tags"]
              and j["video"]["render_status"] == "pending" and j["quality_score"] is None)

        # score — reject then pass
        j1 = c.post("/content/score", json={"asset_id": "a1"}).json()
        j2 = c.post("/content/score", json={"asset_id": "a1"}).json()
        check("POST /content/score reject (0.62 + reason + entries)",
              j1["passed"] is False and j1["quality_score"]["overall_score"] == 0.62
              and j1["quality_score"]["rejection_reason"] and len(j1["decision_log_entries"]) == 2)
        check("POST /content/score pass (0.81)", j2["passed"] is True
              and j2["quality_score"]["overall_score"] == 0.81)

        # pipeline run — the full fake response with the decision log
        r = c.post("/pipeline/run", json={"creator_id": "creator_001"}); j = r.json()
        log = j["decision_log"]
        statuses = [e["status"] for e in log]
        check("POST /pipeline/run (complete, opportunity + asset embedded)",
              j["status"] == "complete" and j["opportunity"]["fit_score"] == 0.87
              and j["asset"]["quality_score"]["overall_score"] == 0.81)
        check("decision log: 8 entries with rejection + regeneration + pass visible",
              len(log) == 8 and "rejected" in statuses and "regenerated" in statuses
              and "success" in statuses
              and log[5]["stage"] == "scorer" and log[5]["score"] == 0.62
              and log[6]["stage"] == "regenerate" and log[7]["stage"] == "scorer" and log[7]["score"] == 0.81)

        # status — demo running state, unknown complete/100, real run
        s = c.get("/pipeline/run_demo/status").json()
        check("GET status run_demo (running/40)", s["status"] == "running" and s["progress_percentage"] == 40)
        s = c.get("/pipeline/unknown/status").json()
        check("GET status unknown (complete/100)", s["status"] == "complete" and s["progress_percentage"] == 100)
        s = c.get("/pipeline/run_stub_001/status").json()
        check("GET status real run (complete/100)", s["status"] == "complete" and len(s["stages_completed"]) == 6)

        # log
        r = c.get("/pipeline/run_stub_001/log"); j = r.json()
        check("GET pipeline log (8 entries, oldest first)", len(j["entries"]) == 8
              and j["entries"][0]["stage"] == "dna_agent")

        # publish
        p = c.post("/content/publish", json={"asset_id": "a1", "platform": "youtube"}).json()
        check("POST /content/publish", p["platform_post_id"] and p["url"].startswith("https://www.youtube.com/")
              and p["status"] in ("published", "scheduled"))

        # output
        r = c.get("/output/thumbnail/whatever.png")
        check("GET output thumbnail (placeholder PNG)", r.status_code == 200
              and r.headers["content-type"].startswith("image/png")
              and r.content[:8] == b"\x89PNG\r\n\x1a\n")
        r = c.get("/output/video/missing.mp4")
        check("GET output video -> 404", r.status_code == 404)

        # errors
        r = c.post("/catalog/ingest", json={"creator_id": "c", "videos": [{"id": "x"}]})
        check("malformed body -> 422 readable", r.status_code == 422 and r.json()["status"] == "error")
        r = c.get("/nope")
        check("unknown route -> 404 consistent shape", r.status_code == 404 and r.json()["status"] == "error")

    print(f"\n{ok} passed, {fail} failed")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
