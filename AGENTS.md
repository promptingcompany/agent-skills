# AGENTS.md — AI Agent Guidelines

This file guides AI agents working inside this repository.

## Repository layout

```
skills/
  <skill-name>/
    SKILL.md        ← agent-facing prompt (keep under 500 lines)
    README.md       ← human-readable documentation
    AGENTS.md       ← compiled rules/instructions for agents (optional)
    metadata.json   ← version, org, date, abstract, references
    workflows/      ← detailed workflow files referenced by SKILL.md
```

## SKILL.md guidelines

- Open with a one-paragraph purpose statement
- List trigger keywords that activate the skill
- Keep the file under 500 lines — put detailed reference material in `workflows/`
- Use second-person imperative ("Check the…", "Ask the user…")

## Naming conventions

- Directory names: `kebab-case`
- Workflow files: `kebab-case.md`
- Zip packages (for distribution): match the directory name exactly

## Adding a new skill

1. Create `skills/<name>/`
2. Write `SKILL.md`, `README.md`, `metadata.json`
3. Add detailed steps to `workflows/` files and reference them from `SKILL.md`
4. Update the skills table in the root `README.md`
