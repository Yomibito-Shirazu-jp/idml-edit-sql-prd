from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS documents (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  filename TEXT NOT NULL,
  version TEXT NOT NULL,
  doc_type TEXT NOT NULL,
  sha256 TEXT NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(filename, version, doc_type, sha256)
);

CREATE TABLE IF NOT EXISTS blocks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  document_id INTEGER NOT NULL REFERENCES documents(id),
  block_id TEXT NOT NULL,
  source_order INTEGER NOT NULL,
  source_section TEXT,
  word_style TEXT,
  inferred_role TEXT,
  text TEXT NOT NULL,
  text_sha256 TEXT NOT NULL,
  editable INTEGER NOT NULL DEFAULT 1,
  permission TEXT NOT NULL DEFAULT 'TEXT_ONLY_REPLACE',
  UNIQUE(document_id, block_id)
);

CREATE TABLE IF NOT EXISTS idml_files (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  template_id TEXT NOT NULL,
  path TEXT NOT NULL,
  sha256 TEXT NOT NULL,
  size_bytes INTEGER NOT NULL,
  UNIQUE(template_id, path)
);

CREATE TABLE IF NOT EXISTS idml_slots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  template_id TEXT NOT NULL,
  slot_id TEXT NOT NULL,
  story_file TEXT NOT NULL,
  story_order INTEGER,
  content_index INTEGER,
  idml_style TEXT,
  original_text TEXT,
  original_text_sha256 TEXT,
  locked INTEGER NOT NULL DEFAULT 1,
  UNIQUE(template_id, slot_id)
);

CREATE TABLE IF NOT EXISTS block_slot_map (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  block_id TEXT NOT NULL,
  slot_id TEXT NOT NULL,
  mapping_status TEXT NOT NULL DEFAULT 'inferred',
  note TEXT,
  UNIQUE(block_id, slot_id)
);
"""

def connect(db_path: str | Path) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    return con
