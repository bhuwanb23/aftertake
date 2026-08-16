-- AfterTake — Schema 6: Metadata
-- Publishing metadata for one piece of content (metadata agent output).
-- tags and platform_targets are lists -> JSON columns.
-- scheduled_publish_time is nullable (null until scheduled).
CREATE TABLE IF NOT EXISTS metadata (
  id                     TEXT PRIMARY KEY,
  asset_id               TEXT NOT NULL,
  title                  TEXT NOT NULL,
  title_formula_match    TEXT,                -- how the title maps to the creator's title_formula
  description            TEXT NOT NULL DEFAULT '',
  tags_json              TEXT NOT NULL DEFAULT '[]',        -- 10-15 tags for YouTube
  category               TEXT,                -- e.g. Science & Technology
  scheduled_publish_time TEXT,                -- ISO timestamp or NULL
  platform_targets_json  TEXT NOT NULL DEFAULT '[]'         -- e.g. ["youtube"]
);

CREATE INDEX IF NOT EXISTS idx_metadata_asset ON metadata(asset_id);
