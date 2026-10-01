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

1. Open `assets/tracker.exa.yaml`. Set `experiments` to the current prompt set's experiment IDs (the
   shipped IDs are the 29 Sep 2026 research-nudge experiments, a working smoke test), and set `workdir`.
2. `cd ~/.claude/skills/exa-cao-metric/scripts && python3 pull.py ../assets/tracker.exa.yaml --latest`
3. Follow `SKILL.md` from step 2 (analyze → review → report).

For another vendor, copy the config and change `target`, `rivals`, `use_cases` and `grader_goals`.
