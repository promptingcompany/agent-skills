# Installation Guide

## Claude Code (CLI)

```bash
cp -r skills/sim-mode ~/.claude/skills/
```

Claude Code picks up skills from `~/.claude/skills/` automatically. The mode activates on the triggers in `SKILL.md` ("are these results real", "audit the runs", "validate the graders", "review it against the spec").

The helper scripts need [Bun](https://bun.sh):

```bash
bun skills/sim-mode/scripts/pull-runs.ts --scope <org>/<product> --tasks <id,id> --since <ISO time> --out runs.json
bun skills/sim-mode/scripts/summarize.ts runs.json --md
```

### Works alongside

```bash
cp -r skills/setup-benchmark    ~/.claude/skills/   # design a vendor head-to-head
cp -r skills/setup-experiment   ~/.claude/skills/   # design a single-product experiment
cp -r skills/analyze-experiment ~/.claude/skills/   # friction clustering and client PDF after verification
```

## claude.ai (Project Knowledge)

1. Open your Project in claude.ai.
2. Go to **Project Knowledge > Add content**.
3. Paste `SKILL.md`, then every file in `principles/` and the playbook you need from `playbooks/`.

## Uninstalling

```bash
rm -rf ~/.claude/skills/sim-mode
```
