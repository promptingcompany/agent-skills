# Installation Guide

## Claude Code (CLI)

```bash
cp -r skills/exa-cao-metric ~/.claude/skills/
```

Claude Code picks up skills from `~/.claude/skills/` automatically. Trigger with "run the weekly tracker"
or "exa cao metric".

## Python dependencies

```bash
pip install pyyaml
```

## Platform access

- `tpc` CLI installed and authenticated: `tpc auth whoami`
- Membership in the org that holds the runs. The Exa config uses scope `exa/exa-search-docs`.

## First run

Follow `RUNBOOK.md`. In short: set `workdir` in `assets/tracker.oct-research.yaml` and
`assets/tracker.oct-default.yaml` to one absolute path, fire the seven experiments, then pull → analyze → review →
report for each config, then `build_pdf.py` for the PDF and the Slack message.

`build_pdf.py` also needs `pip install reportlab`. `assets/tracker.smoke-sep29.yaml` points at the 29 Sep 2026
smoke-test experiments and is only for trying the scripts.

For another vendor, copy a config and change `target`, `rivals`, `use_cases` and `grader_goals`.
