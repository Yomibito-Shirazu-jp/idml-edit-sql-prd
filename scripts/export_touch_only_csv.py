from __future__ import annotations

import argparse
import csv
from db import connect

FIELDS = [
    "block_id", "source_order", "word_style", "inferred_role", "permission", "text_sha256", "text"
]

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    con = connect(args.db)
    rows = con.execute(
        "SELECT block_id, source_order, word_style, inferred_role, permission, text_sha256, text FROM blocks WHERE editable=1 ORDER BY id"
    ).fetchall()
    with open(args.out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in FIELDS})
    print(f"exported {len(rows)} editable rows to {args.out}")

if __name__ == "__main__":
    main()
