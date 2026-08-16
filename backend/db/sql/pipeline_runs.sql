-- AfterTake — Schema 10: Pipeline Run
-- One complete end-to-end execution of the pipeline — the container that links
-- all objects from one run together. Polled by the frontend PipelineProgress
-- component via /pipeline/{run_id}/status.
CREATE TABLE IF NOT EXISTS pipeline_runs (
  id                     TEXT PRIMARY KEY,
  creator_id             TEXT NOT NULL,
  started_at             TEXT NOT NULL,          -- ISO timestamp
  completed_at           TEXT,                   -- NULL while in progress
  status                 TEXT NOT NULL DEFAULT 'running',  -- running | complete | failed | partial
  current_stage          TEXT,                   -- stage name currently executing
  opportunity_id         TEXT,                   -- NULL until opportunity agent selects one
  asset_id               TEXT,                   -- NULL until generation completes
  stages_completed_json  TEXT NOT NULL DEFAULT '[]',  -- ordered list of finished stages
  stages_failed_json     TEXT NOT NULL DEFAULT '[]',  -- stages that errored
  total_duration_seconds REAL,                   -- NULL until the run completes
  total_llm_calls        INTEGER NOT NULL DEFAULT 0,   -- Claude API calls (cost per run)
  regeneration_count     INTEGER NOT NULL DEFAULT 0    -- total reject->regenerate cycles across stages
);
