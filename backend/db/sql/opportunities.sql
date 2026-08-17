-- AfterTake — Schema 3: Content Opportunity (Phase 1 Step 2 storage design)
-- One row per recommended opportunity. The opportunity agent generates several
-- per run (e.g. three) and the orchestrator selects one via the status column.
-- The FULL ContentOpportunity object is stored as JSON in opp_json; status is
-- ALSO a separate column because it is queried (pending/approved/rejected/...)
-- and querying inside JSON text is painful.
CREATE TABLE IF NOT EXISTS opportunities (
  id              TEXT PRIMARY KEY,
  creator_id      TEXT NOT NULL,
  pipeline_run_id TEXT,               -- the run that generated this opportunity
  status          TEXT NOT NULL DEFAULT 'pending',  -- pending | approved | rejected | in_production | published
  opp_json        TEXT NOT NULL DEFAULT '{}'        -- the full ContentOpportunity object
);

CREATE INDEX IF NOT EXISTS idx_opportunities_creator ON opportunities(creator_id);
CREATE INDEX IF NOT EXISTS idx_opportunities_run     ON opportunities(pipeline_run_id);
CREATE INDEX IF NOT EXISTS idx_opportunities_status  ON opportunities(status);
