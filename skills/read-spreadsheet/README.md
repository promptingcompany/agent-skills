# Read Spreadsheet

Use this when you need Claude to inspect a local `.xlsx` or `.csv`. Claude's
Read tool does not parse binary Excel workbooks. This skill converts them to
markdown tables (or csv) with a local Python helper — no `tpc` required.

Installing the TPC CLI does not teach Claude how to open spreadsheets.

## Workflows

| Workflow | Triggers |
|---|---|
| Inspect spreadsheet | "read this xlsx", "open this csv", "what's in this spreadsheet", "convert xlsx to csv" |

## Convert locally

```bash
python3 skills/read-spreadsheet/scripts/read_spreadsheet.py -- path/to/file.xlsx
python3 skills/read-spreadsheet/scripts/read_spreadsheet.py --max-rows 50 -- path/to/file.csv
```

The helper prefers `pandas` or `openpyxl` if they are already installed, then
falls back to the Python standard library.

## Install

```bash
cp -r skills/read-spreadsheet ~/.claude/skills/
```

See [`INSTALL.md`](INSTALL.md) for claude.ai setup.

`tpc skills install` currently adds only `generative-engine-optimization`.
Shipping this skill with the CLI is a follow-up in `promptingcompany/ctrl0`
(`apps/cli/cmd/skills.go`).
