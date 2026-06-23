CREATE TABLE changed_files_v2_v3(
  path TEXT PRIMARY KEY,
  category TEXT,
  changed_lines INTEGER,
  same_lines INTEGER,
  v2_lines INTEGER,
  v3_lines INTEGER
);;
CREATE TABLE content_slots(
  id INTEGER PRIMARY KEY,
  idml_label TEXT,
  story_file TEXT,
  story_self TEXT,
  paragraph_index INTEGER,
  content_index_in_paragraph INTEGER,
  slot_id TEXT,
  applied_paragraph_style TEXT,
  content_text TEXT,
  content_sha256 TEXT,
  replace_scope TEXT,
  editable_candidate INTEGER
);;
CREATE TABLE conversion_findings(
  key TEXT PRIMARY KEY,
  value TEXT
);;
CREATE TABLE idml_files(
  id INTEGER PRIMARY KEY,
  label TEXT UNIQUE,
  path TEXT,
  sha256 TEXT,
  zip_entry_count INTEGER,
  story_file_count INTEGER,
  created_at TEXT
);;
CREATE TABLE internal_files(
  id INTEGER PRIMARY KEY,
  idml_label TEXT,
  path TEXT,
  category TEXT,
  bytes INTEGER,
  sha256 TEXT,
  is_story INTEGER,
  FOREIGN KEY(idml_label) REFERENCES idml_files(label)
);;
CREATE TABLE paragraph_styles(
  id INTEGER PRIMARY KEY,
  idml_label TEXT,
  style_name TEXT,
  observed_count INTEGER,
  observed_in_editable_candidate INTEGER
);;
CREATE TABLE story_compare_v2_v3(
  story_file TEXT PRIMARY KEY,
  v2_paragraphs INTEGER,
  v3_paragraphs INTEGER,
  changed_paragraphs INTEGER
);;
CREATE TABLE story_files(
  id INTEGER PRIMARY KEY,
  idml_label TEXT,
  story_file TEXT,
  story_self TEXT,
  xml_bytes INTEGER,
  xml_sha256 TEXT,
  paragraph_count INTEGER,
  content_slot_count INTEGER,
  plain_text_chars INTEGER,
  has_footnotes INTEGER,
  changed_in_v2_v3 INTEGER DEFAULT 0,
  FOREIGN KEY(idml_label) REFERENCES idml_files(label)
);;
CREATE TABLE story_paragraphs(
  id INTEGER PRIMARY KEY,
  idml_label TEXT,
  story_file TEXT,
  story_self TEXT,
  paragraph_index INTEGER,
  slot_id TEXT,
  applied_paragraph_style TEXT,
  text TEXT,
  text_sha256 TEXT,
  content_count INTEGER,
  br_count INTEGER,
  footnote_count INTEGER,
  editable_candidate INTEGER,
  FOREIGN KEY(idml_label) REFERENCES idml_files(label)
);;
CREATE TABLE touch_only_rows_v5(
  id INTEGER PRIMARY KEY,
  source_csv_row INTEGER,
  source_doc TEXT,
  source_type TEXT,
  target_story TEXT,
  block_id TEXT,
  seq INTEGER,
  docx_paragraph_index INTEGER,
  word_paragraph_style TEXT,
  inferred_role TEXT,
  idml_paragraph_style_candidate TEXT,
  permission TEXT,
  text TEXT,
  text_sha256 TEXT
);;
CREATE VIEW v_editable_idml_slots AS
SELECT idml_label, story_file, story_self, paragraph_index, slot_id, applied_paragraph_style, text, content_count, footnote_count
FROM story_paragraphs
WHERE editable_candidate=1;;
CREATE VIEW v_changed_story_slots_v3 AS
SELECT p.*
FROM story_paragraphs p
JOIN changed_files_v2_v3 c ON c.path=p.story_file
WHERE p.idml_label='generated_v3';;
CREATE VIEW v_touch_rows_needing_mapping AS
SELECT * FROM touch_only_rows_v5
WHERE target_story IS NULL OR target_story='' OR idml_paragraph_style_candidate IS NULL OR idml_paragraph_style_candidate='';;
