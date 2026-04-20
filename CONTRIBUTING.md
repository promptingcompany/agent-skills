# Contributing to agent-skills

Thanks for contributing. This repo is a community collection of skill packages for Claude Code and AI agents.

## Getting started

1. [Fork the repo](https://github.com/promptingcompany/agent-skills/fork)
2. Clone your fork:
   ```bash
   git clone https://github.com/<your-username>/agent-skills
   cd agent-skills
   ```
3. Create a branch:
   ```bash
   git checkout -b skills/your-skill-name
   ```

## Adding a new skill

Every skill lives in its own folder under `skills/`:

```
skills/your-skill-name/
├── SKILL.md        ← agent-facing prompt (required)
├── README.md       ← human-readable docs (required)
├── INSTALL.md      ← CLI, claude.ai, MCP setup (required)
├── metadata.json   ← version, org, abstract (required)
└── workflows/      ← detailed workflow files referenced by SKILL.md
```

### SKILL.md

- Open with a one-paragraph purpose statement
- Include a `## Trigger keywords` section so the agent knows when to activate the skill
- Keep under 500 lines — move detail into `workflows/`
- Each workflow file should have YAML frontmatter (`name`, `description`, triggers)

### metadata.json

```json
{
  "version": "0.1.0",
  "organization": "Your Org",
  "abstract": "One sentence describing the skill."
}
```

## Updating an existing skill

- Open a PR with a clear title: `update: skill-name — what changed`
- Describe what workflow was added, changed, or removed and why

## Commit message conventions

| Prefix | When to use |
|---|---|
| `add:` | New skill or workflow file |
| `update:` | Changes to an existing skill or workflow |
| `fix:` | Correcting a mistake in a skill |
| `meta:` | README, metadata, or install guide only |

## Opening a pull request

- Target the `main` branch
- Title format: `[prefix]: [skill-name] — [short description]`
- PR body should include what changed, why, and a one-line trigger test

## Code of conduct

Be respectful. Contributions that are harmful, misleading, or off-topic will be closed.
