-- AfterTake — Schema 9: Generated Asset
-- The complete production package for one piece of content. A light wrapper:
-- identity columns + the nested video object (JSON), with refs to the script
-- and metadata tables. Thumbnails and quality_score are keyed by asset_id in
-- their own tables (thumbnails.asset_id, quality_scores.asset_id).
CREATE TABLE IF NOT EXISTS generated_assets (
  id              TEXT PRIMARY KEY,
  opportunity_id  TEXT NOT NULL,
  creator_id      TEXT NOT NULL,
  created_at      TEXT NOT NULL,          -- ISO timestamp
  script_id       TEXT,                   -- -> scripts.id
  metadata_id     TEXT,                   -- -> metadata.id
  video_json      TEXT NOT NULL DEFAULT '{}',  -- file_path / duration_seconds / resolution / has_captions / render_status
  pipeline_run_id TEXT                    -- -> pipeline_runs.id
);

CREATE INDEX IF NOT EXISTS idx_assets_creator ON generated_assets(creator_id);
CREATE INDEX IF NOT EXISTS idx_assets_run ON generated_assets(pipeline_run_id);
