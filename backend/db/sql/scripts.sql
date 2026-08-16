-- AfterTake — Schema 4: Script
-- The complete script for one video, written in the creator's learned voice.
-- Nested shapes stored as JSON: hook (object), scenes (list of objects), outro (object).
-- full_voiceover_text is the concatenation hook + scenes + outro — what TTS reads aloud.
CREATE TABLE IF NOT EXISTS scripts (
  id                         TEXT PRIMARY KEY,
  opportunity_id             TEXT NOT NULL,
  creator_id                 TEXT NOT NULL,
  hook_json                  TEXT NOT NULL DEFAULT '{}',   -- voiceover_text / visual_description / duration_seconds
  scenes_json                TEXT NOT NULL DEFAULT '[]',   -- [{scene_number, scene_type, voiceover_text, visual_description, on_screen_text, duration_seconds}]
  outro_json                 TEXT NOT NULL DEFAULT '{}',   -- voiceover_text / visual_description / call_to_action / duration_seconds
  full_voiceover_text        TEXT NOT NULL DEFAULT '',
  estimated_duration_seconds INTEGER,
  word_count                 INTEGER
);

CREATE INDEX IF NOT EXISTS idx_scripts_opportunity ON scripts(opportunity_id);
