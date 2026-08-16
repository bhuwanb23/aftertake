-- AfterTake — Schema 7: Quality Score
-- The scorer agent's evaluation of a generated asset against the creator's DNA.
-- Fully scalar. passed == (overall_score >= threshold_used); threshold defaults
-- to 0.75. regeneration_count caps at 2 (the orchestrator retry cap).
CREATE TABLE IF NOT EXISTS quality_scores (
  asset_id            TEXT PRIMARY KEY,
  overall_score       REAL,              -- 0.0-1.0, weighted composite
  thumbnail_fit_score REAL,              -- 0.0-1.0
  title_fit_score     REAL,              -- 0.0-1.0
  voice_fit_score     REAL,              -- 0.0-1.0
  passed              INTEGER NOT NULL DEFAULT 0,   -- boolean 0/1
  threshold_used      REAL NOT NULL DEFAULT 0.75,
  rejection_reason    TEXT,              -- set only when passed is 0
  regeneration_count  INTEGER NOT NULL DEFAULT 0    -- 0-2 (retry cap)
);
