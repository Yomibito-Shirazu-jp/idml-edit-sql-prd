from __future__ import annotations

import argparse
from db import connect


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    con = connect(args.db)
    docs = con.execute("SELECT COUNT(*) AS n FROM documents").fetchone()["n"]
    blocks = con.execute("SELECT COUNT(*) AS n FROM blocks").fetchone()["n"]
    slots = con.execute("SELECT COUNT(*) AS n FROM idml_slots").fetchone()["n"]
    files = con.execute("SELECT COUNT(*) AS n FROM idml_files").fetchone()["n"]
    rows = [
        "# QA Report",
        "",
        f"- documents: {docs}",
        f"- blocks: {blocks}",
        f"- idml_files: {files}",
        f"- idml_slots: {slots}",
        "",
        "## 判定",
        "",
        "この検証はDB整合性の最小チェックです。PDF組版検証はInDesign書き出し後に別途実施してください。",
    ]
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(rows) + "\n")
    print(f"wrote {args.out}")

if __name__ == "__main__":
    main()
