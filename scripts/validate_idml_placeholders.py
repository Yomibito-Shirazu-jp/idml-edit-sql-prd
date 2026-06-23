from __future__ import annotations

import argparse
import csv
import re
import zipfile
from pathlib import Path

TOKEN_RE = re.compile(r"\{\{([A-Za-z0-9_.:-]+)\}\}")


def count_csv_rows(csv_path: str | Path) -> int:
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise SystemExit("CSV has no header row")
        id_field = "var_id" if "var_id" in reader.fieldnames else "block_id" if "block_id" in reader.fieldnames else None
        if id_field is None:
            raise SystemExit("CSV must contain either 'var_id' or 'block_id'")
        return sum(1 for row in reader if (row.get(id_field) or "").strip())


def scan_idml(idml_path: str | Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    with zipfile.ZipFile(idml_path) as zf:
        for name in zf.namelist():
            if not (name.startswith("Stories/") and name.endswith(".xml")):
                continue
            text = zf.read(name).decode("utf-8", errors="strict")
            for match in TOKEN_RE.finditer(text):
                token_id = match.group(1)
                counts[token_id] = counts.get(token_id, 0) + 1
    return counts


def main() -> None:
    ap = argparse.ArgumentParser(description="Validate remaining {{VAR_ID}} placeholders in generated IDML.")
    ap.add_argument("--idml", required=True)
    ap.add_argument("--csv", help="Optional CSV used for fill; row count is reported as expected filled variable count")
    ap.add_argument("--expected-filled", type=int, help="Expected CSV variable count")
    ap.add_argument("--expected-remaining", type=int, default=0)
    ap.add_argument("--out", help="Optional Markdown report path")
    args = ap.parse_args()

    remaining = scan_idml(args.idml)
    remaining_total = sum(remaining.values())
    csv_rows = count_csv_rows(args.csv) if args.csv else None

    lines = [
        "# Placeholder Validation",
        "",
        f"- idml: `{args.idml}`",
        f"- remaining unique placeholders: {len(remaining)}",
        f"- remaining total placeholders: {remaining_total}",
    ]

    if csv_rows is not None:
        lines.append(f"- csv variable rows: {csv_rows}")
    if args.expected_filled is not None:
        lines.append(f"- expected filled variables: {args.expected_filled}")
    lines.append(f"- expected remaining placeholders: {args.expected_remaining}")

    ok = True
    if remaining_total != args.expected_remaining:
        ok = False
        lines.extend(["", "## Remaining placeholders", ""])
        for token_id, count in sorted(remaining.items())[:200]:
            lines.append(f"- `{{{{{token_id}}}}}`: {count}")
        if len(remaining) > 200:
            lines.append(f"- ... {len(remaining) - 200} more")

    if args.expected_filled is not None and csv_rows is not None and csv_rows != args.expected_filled:
        ok = False
        lines.extend([
            "",
            "## CSV row count mismatch",
            "",
            f"- expected: {args.expected_filled}",
            f"- actual: {csv_rows}",
        ])

    lines.extend(["", "## Result", "", "PASS" if ok else "FAIL"])
    report_text = "\n".join(lines) + "\n"

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report_text, encoding="utf-8")

    print(report_text)
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
