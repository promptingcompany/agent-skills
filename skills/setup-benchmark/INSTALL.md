# Installation Guide

## Claude Code (CLI)

```bash
cp -r skills/setup-benchmark ~/.claude/skills/
```

Claude Code picks up skills from `~/.claude/skills/` automatically. The skill activates when you use a trigger phrase (see `SKILL.md` for the full list).

### Recommended companion skills

- **setup-experiment** — shares the prompt-writing rules and state-file conventions this skill links to.
- **analyze-experiment** — deeper analysis of the underlying runs.

### Requirements

- `tpc` CLI installed and authenticated (`curl -fsSL https://cli.promptingco.com/install.sh | bash`, then `tpc auth login`)
- Python 3.9+ for the report scripts (`report/build_snapshot.py`, `report/generate_report.py`)
