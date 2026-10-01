# Installation Guide

## Claude Code (CLI)

```bash
cp -r skills/cao-agent-selection-benchmark ~/.claude/skills/
```

Claude Code picks up skills from `~/.claude/skills/` automatically. The skill activates on the trigger
phrases listed in `SKILL.md`.

### Required companion skills

The report step uses the house brand kit and the writing pass:

```bash
cp -r skills/tpc-report-style ~/.claude/skills/      # reportlab kit at scripts/brand.py
cp -r skills/avoid-ai-writing ~/.claude/skills/
```

### Python dependencies

```bash
pip install pymupdf reportlab pyyaml
```

### Platform access

`tpc` CLI installed and authenticated (`tpc auth whoami`), and membership in the org that will hold the
runs. The skill resolves the org and product from a dashboard link
(`https://app.promptingco.com/<org>/p/<product>/simulation`); if you are not a member, the platform
owner must add you before Phase 3.

## claude.ai (Project Knowledge)

1. Open your Project in claude.ai
2. **Project Knowledge > Add content**
3. Paste `SKILL.md`, then `workflows/interview.md` and `workflows/battery.md` for Phases 0–2
4. Phases 3–6 need the `tpc` CLI and the scripts; run those from Claude Code

## Uninstalling

```bash
rm -rf ~/.claude/skills/cao-agent-selection-benchmark
```
