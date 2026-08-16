-- AfterTake — Schema 8: Decision Log Entry
-- One recorded decision made by the orchestrator at any pipeline stage.
-- The full set for one run = the decision log — the demo's most important output.
-- Fully scalar. Indexed by pipeline_run_id (the query pattern for the dashboard).
CREATE TABLE IF NOT EXISTS decision_log (
  id              TEXT PRIMARY KEY,
  pipeline_run_id TEXT NOT NULL,
  creator_id      TEXT NOT NULL,
  timestamp       TEXT NOT NULL,          -- ISO timestamp
  stage           TEXT NOT NULL,          -- dna_agent | opportunity_agent | script_agent | thumbnail_agent | metadata_agent | scorer | regenerate | publish
  decision        TEXT NOT NULL,          -- plain language, 1-2 sentences
  rationale       TEXT NOT NULL DEFAULT '',  -- readable reasoning; cites the DNA profile where relevant
  input_summary   TEXT NOT NULL DEFAULT '',
  output_summary  TEXT NOT NULL DEFAULT '',
  score           REAL,                   -- numeric score if the stage produced one, else NULL
  status          TEXT NOT NULL DEFAULT 'success'  -- success | rejected | regenerated | failed
);

CREATE INDEX IF NOT EXISTS idx_decision_log_run ON decision_log(pipeline_run_id);
