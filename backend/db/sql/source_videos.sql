-- AfterTake — Schema 1: Source Video
-- One past video from the creator's catalog. Raw input to the DNA agent.
-- Nested shapes (performance, thumbnail, tags) are stored as JSON text columns.
CREATE TABLE IF NOT EXISTS source_videos (
  id               TEXT PRIMARY KEY,
  creator_id       TEXT NOT NULL,
  title            TEXT NOT NULL,
  description      TEXT NOT NULL DEFAULT '',
  transcript       TEXT NOT NULL DEFAULT '',
  duration_seconds INTEGER,
  published_at     TEXT,                -- ISO date (YYYY-MM-DD)
  platform         TEXT NOT NULL DEFAULT 'youtube',
  performance_json TEXT NOT NULL DEFAULT '{}',   -- views/likes/comments/shares/ctr/avg_retention/watch_time_hours
  thumbnail_json   TEXT NOT NULL DEFAULT '{}',   -- url + description
  tags_json        TEXT NOT NULL DEFAULT '[]',   -- list of strings
  category         TEXT
);

-- The DNA agent loads ALL videos for one creator — this is that query.
CREATE INDEX IF NOT EXISTS idx_source_videos_creator ON source_videos(creator_id);
