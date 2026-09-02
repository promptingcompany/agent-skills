---
name: inspect-spreadsheet
description: >
  Read or convert a local .xlsx or .csv file and print it as markdown tables.
  Use when Claude's Read tool cannot open the file, or when the user asks to
  inspect a spreadsheet.

  Trigger when users say: "read this xlsx", "open this csv", "what's in this
  spreadsheet", "convert xlsx to csv", "show me the excel file", or "why can't
  Claude read xlsx".
---

# Inspect Spreadsheet

Print a local `.xlsx` or `.csv` as markdown tables. Do not use `tpc`.

## Step 1 — Resolve the file

Ask for the path if it is missing. Confirm the file exists:

```bash
ls -l -- "<path>"
```

| Extension | What to do |
|---|---|
| `.xlsx` | Skip Read. Convert with the helper, then print. |
| `.csv` / `.tsv` | Try Read first. On failure, run the helper (encoding fallbacks). |
| `.xls` (legacy) | Tell the user Read cannot parse it. Suggest saving as `.xlsx` or `.csv`. |

`tpc` is unrelated: installing the CLI does not register spreadsheet handlers,
and `tpc --format csv` only exports analytics.

## Step 2 — Run the helper

From a checkout of this repo:

```bash
python3 skills/read-spreadsheet/scripts/read_spreadsheet.py -- "<path>"
```

When the skill is installed under Claude Code:

```bash
python3 ~/.claude/skills/read-spreadsheet/scripts/read_spreadsheet.py -- "<path>"
```

Useful flags:

```bash
python3 .../read_spreadsheet.py --max-rows 50 -- "<path>"
python3 .../read_spreadsheet.py --format csv --sheet "Sheet1" -- "<path>"
```

The helper tries, in order: `pandas`, `openpyxl`, then the Python standard
library (`zipfile` + `xml` for xlsx; `csv` + encoding fallbacks for csv).
No pip install is required.

If `python3` is missing, say so. Do not invent table contents.

## Step 3 — CSV via Read (no helper needed)

For a normal `.csv`, Read it as text. If that fails (mojibake, `UnicodeDecodeError`,
or "binary" warnings), rerun the helper. It honors a UTF-8/UTF-16 BOM, then
tries `utf-8`, `cp1252`, and `latin-1`. UTF-16 without a BOM is only tried
when the file contains NUL bytes.

Do not treat a huge CSV as a failure. Preview the first `--max-rows` (default
200) and report the remaining count.

## Step 4 — Print the table

Show each sheet as:

```markdown
## SheetName

| col_a | col_b |
|---|---|
| value | value |
```

Then a one-line footer: rows shown, rows omitted, detected encoding (csv),
and which backend converted the file (`pandas`, `openpyxl`, or `stdlib`).

If the user asked to save a copy:

```bash
python3 .../read_spreadsheet.py --format csv --out /tmp/sheet.csv -- "<path>"
```

## Step 5 — Failures

| Symptom | Next action |
|---|---|
| File not found | Recheck the path. Downloads often land in `~/Downloads`. |
| `.xlsx` is actually HTML/XML (export from a web app) | Read it as text; do not run the xlsx parser. |
| Password-protected workbook | Stop. Ask the user for an unlocked copy. |
| Empty sheet | Say the sheet has no rows. List other sheet names if any. |
| Helper exits non-zero | Paste the error. Do not fall back to guessing cells. |

## Optional backends (already on the machine only)

If the helper cannot parse an `.xlsx` and one of these exists, use it, then
print the resulting csv:

```bash
xlsx2csv -- "<path>"
soffice --headless --convert-to csv --outdir /tmp -- "<path>"
```

Do not install new system packages unless the user asks.
