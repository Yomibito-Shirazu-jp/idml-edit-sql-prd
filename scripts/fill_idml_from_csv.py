from __future__ import annotations

import argparse
import csv
import html
import re
import zipfile
from pathlib import Path

TOKEN_RE = re.compile(r"\{\{([A-Za-z0-9_.:-]+)\}\}")


def read_rows(csv_path: str | Path) -> dict[str, str]:
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise SystemExit("CSV has no header row")

        fields = set(reader.fieldnames)
        id_field = "var_id" if "var_id" in fields else "block_id" if "block_id" in fields else None
        if id_field is None:
            raise SystemExit("CSV must contain either 'var_id' or 'block_id'")
        if "text" not in fields:
            raise SystemExit("CSV must contain a 'text' column")

        values: dict[str, str] = {}
        for row_number, row in enumerate(reader, start=2):
            var_id = (row.get(id_field) or "").strip()
            if not var_id:
                raise SystemExit(f"Missing {id_field} at CSV row {row_number}")
            if var_id in values:
                raise SystemExit(f"Duplicate variable id at CSV row {row_number}: {var_id}")
            values[var_id] = html.escape(row.get("text") or "", quote=False)
        return values


def main() -> None:
    ap = argparse.ArgumentParser(description="Fill {{VAR_ID}} placeholders in an IDML template from a CSV text map.")
    ap.add_argument("--template", required=True, help="Input IDML template containing {{VAR_ID}} placeholders")
    ap.add_argument("--csv", required=True, help="CSV containing var_id/text or block_id/text columns")
    ap.add_argument("--output", required=True, help="Output filled IDML path")
    ap.add_argument("--report", help="Optional Markdown fill report path")
    args = ap.parse_args()

    replacements = read_rows(args.csv)
    seen_tokens: dict[str, int] = {key: 0 for key in replacements}
    unknown_tokens: set[str] = set()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(args.template) as zin, zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.startswith("Stories/") and item.filename.endswith(".xml"):
                text = data.decode("utf-8", errors="strict")
                for match in TOKEN_RE.finditer(text):
                    token_id = match.group(1)
                    if token_id not in replacements:
                        unknown_tokens.add(token_id)
                for token_id, value in replacements.items():
                    token = "{{" + token_id + "}}"
                    count = text.count(token)
                    if count:
                        text = text.replace(token, value)
                        seen_tokens[token_id] += count
                data = text.encode("utf-8")
            zout.writestr(item, data)

    filled_unique = sum(1 for count in seen_tokens.values() if count > 0)
    total_replacements = sum(seen_tokens.values())
    missing = [token_id for token_id, count in seen_tokens.items() if count == 0]

    lines = [
        "# IDML CSV Fill Report",
        "",
        f"- template: `{args.template}`",
        f"- csv: `{args.csv}`",
        f"- output: `{args.output}`",
        f"- csv rows: {len(replacements)}",
        f"- filled unique variables: {filled_unique}",
        f"- total replacements: {total_replacements}",
        f"- missing CSV variables in template: {len(missing)}",
        f"- unknown template variables not in CSV: {len(unknown_tokens)}",
    ]

    if missing:
        lines.extend(["", "## Missing CSV variables in template", ""])
        lines.extend(f"- `{token_id}`" for token_id in missing[:200])
        if len(missing) > 200:
            lines.append(f"- ... {len(missing) - 200} more")

    if unknown_tokens:
        lines.extend(["", "## Unknown template variables not in CSV", ""])
        lines.extend(f"- `{token_id}`" for token_id in sorted(unknown_tokens)[:200])
        if len(unknown_tokens) > 200:
            lines.append(f"- ... {len(unknown_tokens) - 200} more")

    report_text = "\n".join(lines) + "\n"
    if args.report:
        report = Path(args.report)
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(report_text, encoding="utf-8")

    print(report_text)

    if missing or unknown_tokens:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
