# CLAUDE.md

Guidelines for Claude Code when working in this repository.

## Structure

Skills live under `skills/<skill-name>/`. Each skill has:
- `SKILL.md` — the agent-facing prompt loaded into conversations
- `README.md` — human-readable docs
- `metadata.json` — structured metadata
- `workflows/` — detailed step-by-step workflow files

## When editing skills

- Keep `SKILL.md` under 500 lines; move detail into `workflows/`
- Update `metadata.json` when bumping the skill version
- Keep the root `README.md` skills table in sync when adding/removing skills

## No build step required

Skills are plain markdown. No compilation or packaging needed for development.
