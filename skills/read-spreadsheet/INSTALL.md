# Installation Guide

## Claude Code (CLI)

```bash
cp -r skills/read-spreadsheet ~/.claude/skills/
```

Or, from the skills installer:

```bash
npx skills add https://github.com/promptingcompany/agent-skills --skill read-spreadsheet -y -g --agent '*'
```

Claude Code picks up skills from `~/.claude/skills/` automatically. The skill
activates when you ask to read, inspect, or convert an `.xlsx` or `.csv`.

`tpc skills install` does **not** install this skill today. It only adds
`generative-engine-optimization`. Spreadsheet reading does not depend on `tpc`.

## claude.ai (Project Knowledge)

1. Open your Project in claude.ai
2. Go to **Project Knowledge > Add content**
3. Paste the contents of `SKILL.md`
4. Also paste `workflows/inspect-spreadsheet.md` for the convert path

For local conversion on claude.ai, the user still needs a machine with Python
3 (or to upload a csv export). The helper script is
`scripts/read_spreadsheet.py`.

## Uninstalling

```bash
rm -rf ~/.claude/skills/read-spreadsheet
```
