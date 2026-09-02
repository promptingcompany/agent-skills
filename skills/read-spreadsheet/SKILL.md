---
name: read-spreadsheet
description: >
  Use this when the user wants to read, inspect, preview, convert, or open
  .xlsx or .csv files. Also use when Claude's Read tool fails on a spreadsheet
  (binary xlsx, encoding errors, huge files), or when someone asks why xlsx/csv
  cannot be opened after installing the TPC CLI.
---

# Read Spreadsheet

Inspect `.xlsx` and `.csv` files locally and print them as tables. Claude's Read
tool does not parse binary `.xlsx`. CSV is text and usually works; if Read
fails, retry with encoding fallbacks.

When this skill is activated, convert the file immediately. Do not greet. Do
not list workflows. Do not ask how you can help.

Installing `tpc` (or `tpc skills install`) does not teach Claude how to read
spreadsheets. `tpc --format csv` is analytics export only.

Do not require `tpc` for anything in this skill.

## Trigger keywords

This skill activates when the user asks to:
- Read, open, inspect, preview, or convert an `.xlsx` or `.csv` file
- Show a spreadsheet, Excel file, workbook, or sheet as a table
- Explain why Claude cannot read xlsx/csv after installing the CLI
- Recover from a Read-tool failure on a spreadsheet

## Prerequisites

- Python 3 on PATH (`python3 --version`). No extra packages required.
- Optional: `pandas` or `openpyxl` if already installed — the helper uses them
  first, then falls back to the Python standard library.

## Workflows

### 1. Inspect Spreadsheet

See [`workflows/inspect-spreadsheet.md`](workflows/inspect-spreadsheet.md) for
the full convert path, encoding fallbacks, and output limits. Summary:

1. Resolve the file path. Do not use Read on `.xlsx` (it is a zip/binary).
2. For `.csv`, try Read first. On failure, retry encodings via the helper.
3. For `.xlsx`, convert locally and print markdown tables (one per sheet).
4. If the file is large, print a preview and say how many rows were omitted.

## General principles

- Prefer the helper script in this skill over ad-hoc one-liners.
- Print tables in the conversation. Do not silently write converted files
  unless the user asks for a saved `.csv`.
- Never invent cell values. If a sheet is empty or a dependency is missing,
  say so and show the next fallback.
- Keep output scannable: sheet name, column headers, then rows.
