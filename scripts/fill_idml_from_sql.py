from __future__ import annotations

import argparse
import html
import zipfile
from pathlib import Path
from db import connect


def main() -> None:
    ap = argparse.ArgumentParser(description="Fill {{BLOCK_ID}} placeholders in Stories/*.xml from DB blocks.text.")
    ap.add_argument("--template-idml", required=True)
    ap.add_argument("--db", required=True)
    ap.add_argument("--out-idml", required=True)
    args = ap.parse_args()

    con = connect(args.db)
    blocks = {
        row["block_id"]: html.escape(row["text"], quote=False)
        for row in con.execute("SELECT block_id, text FROM blocks WHERE editable=1")
    }
    replacements = 0
    out = Path(args.out_idml)
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.template_idml) as zin, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.startswith("Stories/") and item.filename.endswith(".xml"):
                text = data.decode("utf-8", errors="ignore")
                for block_id, value in blocks.items():
                    token = "{{" + block_id + "}}"
                    if token in text:
                        text = text.replace(token, value)
                        replacements += 1
                data = text.encode("utf-8")
            zout.writestr(item, data)
    print(f"wrote {out}; replacements={replacements}")

if __name__ == "__main__":
    main()
