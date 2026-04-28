# AGENTS.md - AI Agent Guidelines

This file guides AI agents working inside this repository.

## Repository layout

Always place skills under `skills/<skill-name>/`. Do not create top-level skill folders.

```text
skills/
  <skill-name>/
    SKILL.md        - agent-facing prompt, keep under 500 lines
    README.md       - human-readable documentation
    INSTALL.md      - installation notes for Claude Code, claude.ai, and agent runtimes
    AGENTS.md       - compiled rules/instructions for agents (optional)
    metadata.json   - version, organization, and abstract
    workflows/      - detailed workflow files referenced by SKILL.md
```

## SKILL.md guidelines

- Open with YAML frontmatter containing `name` and `description`.
- Open the body with a one-paragraph purpose statement.
- Include a short activation greeting matching the existing skills.
- List trigger keywords that activate the skill.
- Keep detailed procedures in `workflows/` and link to them from `SKILL.md`.
- Use second-person imperative instructions.
- Keep `SKILL.md` concise and under 500 lines.

## Naming conventions

- Directory names: `kebab-case`
- Workflow files: `kebab-case.md`
- Skill names in frontmatter: match the directory name
- Zip packages for distribution: match the directory name exactly

## Adding a new skill

1. Create `skills/<name>/`.
2. Write `SKILL.md`, `README.md`, `INSTALL.md`, and `metadata.json`.
3. Add detailed steps to `workflows/` files and reference them from `SKILL.md`.
4. Update the skills table in the root `README.md`.
5. Validate the file layout against this guide before opening a PR.
