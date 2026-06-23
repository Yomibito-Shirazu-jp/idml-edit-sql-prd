from __future__ import annotations

import argparse
import hashlib
import re
import zipfile
from pathlib import Path
from lxml import etree
from db import connect

CONTENT_RE = re.compile(rb"<Content(?:\s[^>]*)?>(.*?)</Content>", re.DOTALL)

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def strip_xml_text(raw: bytes) -> str:
    try:
        node = etree.fromstring(b"<root>" + raw + b"</root>")
        return "".join(node.itertext()).strip()
    except Exception:
        return raw.decode("utf-8", errors="ignore").strip()

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--idml", required=True)
    ap.add_argument("--template-id", required=True)
    ap.add_argument("--db", required=True)
    args = ap.parse_args()

    idml_path = Path(args.idml)
    con = connect(args.db)
    cur = con.cursor()
    files = 0
    slots = 0
    with zipfile.ZipFile(idml_path) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            data = zf.read(info.filename)
            cur.execute(
                "INSERT OR REPLACE INTO idml_files(template_id, path, sha256, size_bytes) VALUES (?, ?, ?, ?)",
                (args.template_id, info.filename, sha256_bytes(data), len(data)),
            )
            files += 1
            if info.filename.startswith("Stories/") and info.filename.endswith(".xml"):
                for idx, match in enumerate(CONTENT_RE.finditer(data), start=1):
                    text = strip_xml_text(match.group(1))
                    if not text:
                        continue
                    slot_id = f"SLOT_{slots + 1:06d}"
                    cur.execute(
                        """
                        INSERT OR REPLACE INTO idml_slots(
                          template_id, slot_id, story_file, story_order, content_index,
                          idml_style, original_text, original_text_sha256, locked
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (args.template_id, slot_id, info.filename, None, idx, None, text, sha256_text(text), 1),
                    )
                    slots += 1
    con.commit()
    print(f"indexed {files} idml files and {slots} content slots from {idml_path}")

if __name__ == "__main__":
    main()
