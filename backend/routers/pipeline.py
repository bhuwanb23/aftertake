"""Pipeline endpoints (Phase 0 Step 10 API contract).

POST /pipeline/run         — the single end-to-end endpoint; runs all stages
                             synchronously (the live demo call). The orchestrator
                             lands in Phase 2 — stub returns 501 until then.
GET  /pipeline/{run_id}/status — run status for the PipelineProgress UI (polls
                             every 2s); progress % computed from stages done.
GET  /pipeline/{run_id}/log — the full decision log for one run, oldest first.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.db import database as db

router = APIRouter(prefix="/pipeline", tags=["pipeline"])

# The generation stages in pipeline order. Used to compute progress_percentage.
# regenerate/publish are lifecycle events, not run stages, so they're excluded.
STAGES = [
    "dna_agent",
    "opportunity_agent",
    "script_agent",
    "thumbnail_agent",
    "metadata_agent",
    "scorer",
]


class RunRequest(BaseModel):
    creator_id: str
    topic_hint: str | None = None  # loose nudge for the opportunity agent, or ignored


@router.post("/run")
def run_pipeline(body: RunRequest):
    # Phase 2: the orchestrator runs every stage in order and returns the full
    # PipelineRun with embedded opportunity, GeneratedAsset, and decision log.
    raise HTTPException(
        status_code=501,
        detail="Orchestrator not implemented yet (Phase 2).",
    )


@router.get("/{run_id}/status")
def get_status(run_id: str):
    conn = db.get_connection()
    row = conn.execute(
        "SELECT * FROM pipeline_runs WHERE id = ?", (run_id,)
    ).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(
            status_code=404, detail=f"No pipeline run found with id {run_id}."
        )
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
