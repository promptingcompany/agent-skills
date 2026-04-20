# agent-skills

Community skill packages for Claude Code and AI agents — maintained by Prompting Company.

## What are skills?

Skills are reusable instruction sets that extend what Claude can do inside Claude Code or claude.ai. Each skill lives in its own folder under `skills/` and ships with a `SKILL.md` (the agent prompt), a `README.md` (human docs), and a `metadata.json`.

## Available skills

| Skill | Description |
|---|---|
| [generative-engine-optimization](skills/generative-engine-optimization/) | Agent simulation, prompt generation, and content generation workflows |

## Installing a skill

**Claude Code (CLI)**
```bash
# Copy the skill to your global skills directory
cp -r skills/generative-engine-optimization ~/.claude/skills/
```

**claude.ai**
Paste the contents of `SKILL.md` into your project knowledge or directly into a conversation.

## Contributing

1. Create a folder under `skills/<your-skill-name>/`
2. Add `SKILL.md`, `README.md`, and `metadata.json`
3. Open a PR — see `AGENTS.md` for structural guidelines
