from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path
from docx import Document
from db import connect

BODY_START_RE = re.compile(r"^プロローグ[\s　]")
CHAPTER_RE = re.compile(r"^(プロローグ|エピローグ|第[０-９0-9一二三四五六七八九十]+章|＜座談会[０-９0-9]+＞)")
SECTION_RE = re.compile(r"^[０-９0-9]+[．.]\s*")

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def infer_role(text: str, style: str) -> str:
    stripped = text.strip()
    if not stripped:
        return "blank"
    if CHAPTER_RE.match(stripped):
        return "chapter_or_roundtable_title"
    if SECTION_RE.match(stripped):
        return "section_title"
    if len(stripped) <= 32 and "。" not in stripped and "、" not in stripped:
        return "subhead_candidate"
    return "body"

def iter_paragraphs(docx_path: Path, body_only: bool):
    doc = Document(str(docx_path))
    started = not body_only
    body_start_seen = 0
    for idx, p in enumerate(doc.paragraphs):
        text = p.text.replace("\u00a0", " ").strip()
        if not text:
            continue
        if body_only:
            if BODY_START_RE.match(text):
                body_start_seen += 1
                if body_start_seen >= 2:
                    started = True
            if not started:
                continue
        style = p.style.name if p.style is not None else ""
        yield idx, style, text

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--docx", required=True)
    ap.add_argument("--doc-type", required=True, choices=["main", "roundtable"])
    ap.add_argument("--version", required=True)
    ap.add_argument("--db", required=True)
    ap.add_argument("--body-only", action="store_true", default=True)
    args = ap.parse_args()

    docx_path = Path(args.docx)
    digest = sha256_bytes(docx_path.read_bytes())
    con = connect(args.db)
    cur = con.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO documents(filename, version, doc_type, sha256) VALUES (?, ?, ?, ?)",
        (docx_path.name, args.version, args.doc_type, digest),
    )
    cur.execute(
        "SELECT id FROM documents WHERE filename=? AND version=? AND doc_type=? AND sha256=?",
        (docx_path.name, args.version, args.doc_type, digest),
    )
    document_id = cur.fetchone()["id"]

    count = 0
    for order, (docx_idx, style, text) in enumerate(iter_paragraphs(docx_path, args.body_only), start=1):
        prefix = "M" if args.doc_type == "main" else "T"
        block_id = f"{prefix}_{order:06d}"
        role = infer_role(text, style)
        permission = "TEXT_ONLY_REPLACE"
        cur.execute(
            """
            INSERT OR REPLACE INTO blocks(
              document_id, block_id, source_order, source_section, word_style,
              inferred_role, text, text_sha256, editable, permission
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (document_id, block_id, docx_idx, None, style, role, text, sha256_text(text), 1, permission),
        )
        count += 1
    con.commit()
    print(f"imported {count} blocks from {docx_path}")

if __name__ == "__main__":
    main()
