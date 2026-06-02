# Installation Guide

## Claude Code (CLI)

```bash
cp -r skills/analyze-experiment ~/.claude/skills/
```

Claude Code picks up skills from `~/.claude/skills/` automatically. The skill activates on a trigger phrase (see `SKILL.md`).

### The experiment suite

This is the third skill in the experiment workflow — **setup → run → analyze**. It pairs with:

```bash
cp -r skills/setup-experiment ~/.claude/skills/   # build & run the experiment
cp -r skills/signal-config   ~/.claude/skills/   # define custom signals
```

Each is a separate install (its own folder under `~/.claude/skills/`); they are siblings in the same repo, not one bundle.

## claude.ai (Project Knowledge)

1. Open your Project in claude.ai
2. Go to **Project Knowledge > Add content**
3. Paste the contents of `SKILL.md`
4. Also paste `workflows/analyze-experiment.md` for the full procedure

## Uninstalling

```bash
rm -rf ~/.claude/skills/analyze-experiment
```
