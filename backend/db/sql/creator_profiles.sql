-- AfterTake — Schema 2: Creator DNA Profile
-- The learned style + performance profile of a specific creator.
-- The most important object in the system: every generation agent conditions
-- on it, every scored asset is evaluated against it.
-- All nested objects (voice, title_formula, thumbnail_style, content_patterns,
-- performance_benchmarks) are stored as one JSON document in profile_json.
CREATE TABLE IF NOT EXISTS creator_profiles (
  creator_id         TEXT PRIMARY KEY,
  created_at         TEXT NOT NULL,
  updated_at         TEXT NOT NULL,
  source_video_count INTEGER NOT NULL DEFAULT 0,
  profile_json       TEXT NOT NULL DEFAULT '{}'
);
