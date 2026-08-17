"""Pipeline endpoints (Phase 0 Step 10 API contract).

POST /pipeline/run         — the single end-to-end endpoint; runs all stages
                             synchronously (the live demo call).
GET  /pipeline/{run_id}/status — run status for the PipelineProgress UI (polls
                             every 2s); progress % computed from stages done.
GET  /pipeline/{run_id}/log — the full decision log for one run, oldest first.

Phase 1: /run returns a realistic STUB run (routers/stubs.py) AND persists the
run + decision-log rows so the real GET /status and GET /log endpoints serve
it. Phase 2: the orchestrator replaces the stub with real stage execution;
the persistence path is the same.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.db import database as db
from backend.routers import stubs

router = APIRouter(prefix="/pipeline", tags=["pipeline"])

# The generation stages in pipeline order. Used to compute progress_percentage.
# regenerate/publish are lifecycle events, not run stages, so they're excluded.
STAGES = stubs.RUN_STAGES


class RunRequest(BaseModel):
    creator_id: str
    topic_hint: str | None = None  # loose nudge for the opportunity agent, or ignored


@router.post("/run")
def run_pipeline(body: RunRequest):
    # Phase 1 STUB: return the full fake run and persist it so the status/log
    # endpoints work for the frontend. Phase 2: orchestrator runs real stages.
    payload = stubs.run_payload(body.creator_id)
    entries = payload["decision_log"]
    conn = db.get_connection()
    try:
        conn.execute(
            """INSERT OR REPLACE INTO pipeline_runs
               (id, creator_id, started_at, completed_at, status, current_stage,
                opportunity_id, asset_id, stages_completed_json, stages_failed_json,
                total_duration_seconds, total_llm_calls, regeneration_count)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                payload["id"],
                payload["creator_id"],
                payload["started_at"],
                payload["completed_at"],
                payload["status"],
                payload["current_stage"],
                payload["opportunity_id"],
                payload["asset_id"],
                db.dumps(payload["stages_completed"]),
                db.dumps(payload["stages_failed"]),
                payload["total_duration_seconds"],
                payload["total_llm_calls"],
                payload["regeneration_count"],
            ),
        )
        for e in entries:
            conn.execute(
                """INSERT OR REPLACE INTO decision_log
                   (id, pipeline_run_id, creator_id, timestamp, stage, decision,
                    rationale, input_summary, output_summary, score, status)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    e["id"], e["pipeline_run_id"], e["creator_id"], e["timestamp"],
                    e["stage"], e["decision"], e["rationale"], e["input_summary"],
                    e["output_summary"], e["score"], e["status"],
                ),
            )
        conn.commit()
    finally:
        conn.close()
    return payload


# Phase 1 STUB: a hardcoded demo run that always reports an in-progress state,
# so the frontend PipelineProgress component can be built against the
# "running" state (the real stub run completes instantly).
DEMO_RUN_ID = "run_demo"


@router.get("/{run_id}/status")
def get_status(run_id: str):
    if run_id == DEMO_RUN_ID:
        return {
            "run_id": run_id,
            "status": "running",
            "current_stage": "script_agent",
            "stages_completed": ["dna_agent", "opportunity_agent"],
            "stages_failed": [],
            "progress_percentage": 40,
        }
    conn = db.get_connection()
    row = conn.execute(
        "SELECT * FROM pipeline_runs WHERE id = ?", (run_id,)
    ).fetchone()
    conn.close()
    if row is None:
        # Phase 1 STUB fallback (per plan): any unknown run ID reports complete
        # at 100% so a poll never shows a broken state. Phase 4: 404 for
        # genuinely unknown runs.
        return {
            "run_id": run_id,
            "status": "complete",
            "current_stage": "",
            "stages_completed": list(STAGES),
            "stages_failed": [],
            "progress_percentage": 100,
        }
    completed = db.loads(row["stages_completed_json"])
    failed = db.loads(row["stages_failed_json"])
    progress = round(len(completed) / len(STAGES) * 100) if STAGES else 0
    return {
        "run_id": row["id"],
        "status": row["status"],
        "current_stage": row["current_stage"] or "",
        "stages_completed": completed,
        "stages_failed": failed,
        "progress_percentage": progress,
    }


@router.get("/{run_id}/log")
def get_log(run_id: str):
    conn = db.get_connection()
    run = conn.execute(
        "SELECT id FROM pipeline_runs WHERE id = ?", (run_id,)
    ).fetchone()
    if run is None:
        conn.close()
        raise HTTPException(
            status_code=404, detail=f"No pipeline run found with id {run_id}."
        )
    rows = conn.execute(
        "SELECT * FROM decision_log WHERE pipeline_run_id = ? ORDER BY timestamp ASC, id ASC",
        (run_id,),
    ).fetchall()
    conn.close()
    return {"run_id": run_id, "entries": [dict(r) for r in rows]}
