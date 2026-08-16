-- AfterTake — Schema 3: Content Opportunity
-- One recommendation for what the creator should make next (opportunity agent output).
-- The nested rationale object (dna_fit_explanation, performance_prediction,
-- trend_relevance, risks) is stored as JSON in rationale_json.
CREATE TABLE IF NOT EXISTS opportunities (
  id                            TEXT PRIMARY KEY,
  creator_id                    TEXT NOT NULL,
  created_at                    TEXT NOT NULL,
  topic                         TEXT NOT NULL,
  working_title                 TEXT NOT NULL DEFAULT '',
  rationale_json                TEXT NOT NULL DEFAULT '{}',
  fit_score                     REAL,             -- 0.0-1.0; >=0.8 strong, 0.6-0.79 viable, <0.6 regenerate
  confidence                    TEXT,             -- high | medium | low
  recommended_format            TEXT,             -- e.g. 30-day-challenge
  recommended_duration_seconds  INTEGER,
  target_hook                   TEXT,
  status                        TEXT NOT NULL DEFAULT 'pending'  -- pending | approved | rejected | in_production | published
);

CREATE INDEX IF NOT EXISTS idx_opportunities_creator ON opportunities(creator_id);
