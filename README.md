# agent-skills

**[github.com/promptingcompany/agent-skills](https://github.com/promptingcompany/agent-skills)**

Community skill packages for Claude Code and AI agents, maintained by Prompting Company.

## What are skills?

Skills are reusable instruction sets that extend what Claude can do inside Claude Code or claude.ai. Each skill lives in its own folder under `skills/` and ships with a `SKILL.md` agent prompt, `README.md` human docs, `INSTALL.md` setup notes, and `metadata.json`.

## Available skills

| Skill | Description |
|---|---|
| [generative-engine-optimization](skills/generative-engine-optimization/) | Agent simulation and GEO simulation prompt generation for AI visibility auditing |
| [prompting-company](skills/prompting-company/) | API, MCP Server, CLI, and SDK workflows for The Prompting Company |
| [skills-admin](skills/skills-admin/) | Open PRs and update installed skills in the agent-skills repository |

## Installing a skill

```bash
cp -r skills/prompting-company ~/.claude/skills/
```

See the skill's [`INSTALL.md`](skills/prompting-company/INSTALL.md) for claude.ai and MCP server setup.

## Contributing

We welcome new skills and improvements to existing ones. See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

Quick path:

1. [Fork the repo](https://github.com/promptingcompany/agent-skills/fork)
2. Create a branch: `git checkout -b skills/your-skill-name`
3. Add your skill under `skills/<your-skill-name>/` following the structure in [AGENTS.md](AGENTS.md)
4. Open a pull request against `main`

## License

[MIT](LICENSE)
