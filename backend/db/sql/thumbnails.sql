-- AfterTake — Schema 5: Thumbnail Variant
-- One generated thumbnail option (thumbnail agent SVG + renderer PNG).
-- Fully scalar — no nested objects. selected is a boolean (0/1); only one
-- variant per asset set should be selected. selection_reason is only set
-- on the selected variant.
CREATE TABLE IF NOT EXISTS thumbnails (
  id                 TEXT PRIMARY KEY,
  asset_id           TEXT NOT NULL,
  variant_number     INTEGER NOT NULL DEFAULT 1,  -- 1, 2, or 3
  svg_source         TEXT,                        -- raw SVG markup (cairosvg input)
  png_path           TEXT,                        -- e.g. ./output/thumbnails/thumb_001_v1.png
  layout_description TEXT,
  selected           INTEGER NOT NULL DEFAULT 0,  -- boolean 0/1
  selection_reason   TEXT
);

CREATE INDEX IF NOT EXISTS idx_thumbnails_asset ON thumbnails(asset_id);
