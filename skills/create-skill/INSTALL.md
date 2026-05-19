# Install Create Skill

This skill has no external runtime dependencies. It is designed to be used from an `agent-skills` checkout that contains the root `SPEC.md`.

## Claude Code

Copy the skill package into your local skills directory:

```bash
cp -r skills/create-skill ~/.claude/skills/
```

## Verification

Confirm the installed skill exists:

```bash
test -f ~/.claude/skills/create-skill/SKILL.md
```

When using the skill inside this repository, also confirm the structural spec is available:

```bash
test -f SPEC.md
```
