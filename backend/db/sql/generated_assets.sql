-- AfterTake — Schema 9: Generated Asset (Phase 1 Step 2 storage design)
-- One row per generated content package. The FULL GeneratedAsset object
-- (script, video, thumbnails, metadata, quality_score) is stored as JSON in
-- asset_json — read the whole object, write the whole object. render_status is
-- ALSO a separate column because it is queried (pending/rendering/complete/
-- failed) and querying inside JSON text is painful.
CREATE TABLE IF NOT EXISTS generated_assets (
  id              TEXT PRIMARY KEY,
  creator_id      TEXT NOT NULL,
  pipeline_run_id TEXT,
  opportunity_id  TEXT,
  render_status   TEXT NOT NULL DEFAULT 'pending',  -- pending | rendering | complete | failed
  asset_json      TEXT NOT NULL DEFAULT '{}'        -- the full GeneratedAsset object
);

CREATE INDEX IF NOT EXISTS idx_assets_run         ON generated_assets(pipeline_run_id);
CREATE INDEX IF NOT EXISTS idx_assets_opportunity ON generated_assets(opportunity_id);
