# agent-skills

Community skill packages for Claude Code and AI agents — maintained by Prompting Company.

## What are skills?

Skills are reusable instruction sets that extend what Claude can do inside Claude Code or claude.ai. Each skill lives in its own folder under `skills/` and ships with a `SKILL.md` (the agent prompt), a `README.md` (human docs), and a `metadata.json`.

## Available skills

| Skill | Description |
|---|---|
| [generative-engine-optimization](skills/generative-engine-optimization/) | Agent simulation, prompt generation, and content generation workflows |

## Installing a skill

Each skill includes an `INSTALL.md` with instructions for Claude Code CLI, claude.ai, and MCP server setup. Quick start:

```bash
# Claude Code CLI
cp -r skills/generative-engine-optimization ~/.claude/skills/
```

For MCP server configuration and claude.ai setup, see the skill's [`INSTALL.md`](skills/generative-engine-optimization/INSTALL.md).

## Contributing

1. Create a folder under `skills/<your-skill-name>/`
2. Add `SKILL.md`, `README.md`, and `metadata.json`
3. Open a PR — see `AGENTS.md` for structural guidelines
