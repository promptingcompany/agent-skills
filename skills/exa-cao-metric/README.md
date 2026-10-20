# exa-cao-metric

Monthly tracker for Exa's coding-agent prompt set: how often Claude Code and Codex cite a page we publish, pick Exa
in a head-to-head, or build with Exa as the main search. Pulls runs with the `tpc` CLI, classifies them, queues the
unsure ones for a human verdict, and turns the result into the one-PDF readout (findings + action list) and the
Slack message Exa gets each month.

- **Running it this month:** `RUNBOOK.md`, start to finish, for a first-time operator.
- **How the agent uses it:** `SKILL.md`.
- **Install:** `INSTALL.md` (`tpc` CLI, `pip install pyyaml reportlab`).
- **Settling the review queue:** `workflows/review.md`.
- **Live configs:** `assets/tracker.oct-research.yaml`, `assets/tracker.oct-default.yaml` (October 2026 prompt set).
- **October baseline:** `assets/baseline.2026-10.numbers.json`, `assets/narrative.2026-10.json`,
  `assets/actions.2026-10.json`, worked examples in `assets/examples/2026-10/`.

Scripts: `pull.py` → `analyze.py` → (reviews) → `report.py` → `build_pdf.py`.
