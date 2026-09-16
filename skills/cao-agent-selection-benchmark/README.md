# CAO Agent-Selection Benchmark

Run an agent-selection study from zero to the condensed report: when a coding agent needs a category of
tool, who gets picked, wired into code, and paid, and what changes that. Produces the house A–F PDF
(the Vercel / AgentMail format) plus a paste-ready TLDR. Built for an operator who has never done one.

## What it does

Seven phases, each ending in a stop gate the operator clears explicitly:

| Phase | Output |
|---|---|
| 0 Intake | six questions: category or vendor, reader, vendor's job, use-case pages, rivals and incumbent, dashboard link for where runs live |
| 1 Frame | DIY substitute, the shelf, the un-fakeable requirement, the buyer, rivals; the `wired` definition; `study.yaml` |
| 2 Battery | 15 tasks from a fixed composition table via `battery.yaml` → `scripts/gen_tasks.py` (leak, twin, placeholder checks) |
| 3 Platform | two envs, tasks, three homogeneous experiments; `scripts/preflight.py` byte-for-byte |
| 4 Fire | iteration 1 → capture check + hand-audit list; then k=3 |
| 5 Analyze | `wired.json`, `deepdive.txt`, `mined/`, quote sweeps, `verify_quotes.py`, `FINDINGS.md` |
| 6 Report | `build_report_template.py` → PDF; `check_report.py` send gate; `VERIFICATION.md`; TLDR |

Runs execute only in TPC platform sandboxes and only through experiments; nothing is sent to a client
from inside the skill.

## Workflows

| File | Covers |
|---|---|
| [`workflows/interview.md`](workflows/interview.md) | the intake questions and the Gate 0 read-back |
| [`workflows/battery.md`](workflows/battery.md) | framing, composition tables, `battery.yaml`, prompt rules, goal texts, worked example |
| [`workflows/platform.md`](workflows/platform.md) | `tpc` sequence, experiments, pre-flight, firing, waiting, known behaviours |
| [`workflows/analysis.md`](workflows/analysis.md) | channels, classification, lane discipline, parser-defect ledger, quote sweeps |
| [`workflows/report.md`](workflows/report.md) | A–F anatomy, voice, action measures, `check_report.py`, `VERIFICATION.md`, send checklist, TLDR |
| [`workflows/pathways.md`](workflows/pathways.md) | category study, prospect vs customer, re-read, v2 |
| [`workflows/mistakes-ledger.md`](workflows/mistakes-ledger.md) | every mistake from four studies and the rule it produced |

## Scripts and assets

`scripts/` — `gen_tasks.py`, `preflight.py`, `wait_runs.py`, `iterations_map.py`, `wired.py`,
`calibrate.py`, `deepdive.py`, `verify_quotes.py`, `check_report.py`, `build_report_template.py`,
`tpc_helpers.py`, `study.example.yaml`. `assets/` — `battery.example.yaml` (the AgentMail v3 battery),
`STUDY.template.md`.

## Requirements

`tpc` CLI authenticated and a member of the target org; Python 3 with `pymupdf`, `reportlab`, `pyyaml`;
the `tpc-report-style` skill (brand kit) and the `avoid-ai-writing` skill installed alongside.

## Install

```bash
cp -r skills/cao-agent-selection-benchmark ~/.claude/skills/
```

See [`INSTALL.md`](INSTALL.md).
