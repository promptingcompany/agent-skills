---
name: create-new-skill
description: >
  Creates a new skill package by reading the repository-root SPEC.md,
  scaffolding the required package files, updating the root README skills table,
  and running structural validation.

  Trigger when users say: "create a new skill", "add a skill", "scaffold a skill",
  "turn this into a skill", or "make a skill under skills/".
---

# Create New Skill

## Overview

Create a new skill package that follows the repository's canonical structural contract.

## Prerequisites

- Work from the `agent-skills` repository root, or locate it with Git.
- The repository root must contain `SPEC.md`.
- The user must provide enough intent to identify the skill's purpose. If they do not, ask one focused question.

## Required Workflow

**Follow all steps in order.**

### Step 1 - Load the structural spec

Confirm the repository root and read `SPEC.md` before creating files:

```bash
git rev-parse --show-toplevel
test -f SPEC.md
sed -n '1,260p' SPEC.md
```

If `SPEC.md` is missing, stop and report that the repository structural contract is unavailable. Do not infer a new package shape from memory.

Use `SPEC.md` as the source of truth over `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, examples, or memory when requirements differ.

### Step 2 - Define the skill contract

Extract or infer these values from the user's request:

- Skill name
- One-paragraph purpose
- Trigger keywords
- Required workflows
- External setup or prerequisites
- Expected output or validation behavior

Normalize the skill name to kebab-case. If the user did not provide a name, derive one from the main action. Ask a question only when multiple plausible names or purposes would materially change the result.

### Step 3 - Check package path

Use this path:

```text
skills/<skill-name>/
```

Before writing files, check whether it already exists:

```bash
if test -e skills/<skill-name>; then
  find skills/<skill-name> -maxdepth 2 -type f | sort
fi
```

If the path exists and the user asked for a new skill, ask whether to update the existing package or choose a new name. Do not overwrite existing skill files without explicit permission.

### Step 4 - Design the workflow set

Create the smallest workflow set that can execute the skill reliably.

Use one workflow file by default:

```text
skills/<skill-name>/workflows/<primary-workflow>.md
```

Add more workflow files only when the skill has distinct tasks with different triggers or validation loops. Every workflow file must be linked from `SKILL.md`.

### Step 5 - Scaffold required files

Create exactly the required package files unless the user asks for additional package-local support files:

```text
skills/<skill-name>/
|-- SKILL.md
|-- README.md
|-- INSTALL.md
|-- metadata.json
`-- workflows/
    `-- <workflow-name>.md
```

Use these responsibilities:

- `SKILL.md`: agent-facing trigger, purpose, required behavior, and workflow links.
- `README.md`: human-facing explanation of what the skill does and when to use it.
- `INSTALL.md`: installation, prerequisites, and verification.
- `metadata.json`: valid JSON with `version`, `organization`, and `abstract`.
- `workflows/*.md`: detailed ordered steps with frontmatter.

Keep `SKILL.md` under 500 lines. Move detailed commands, examples, and checklists into `workflows/`.

### Step 6 - Update root registration

Add the new skill to the root `README.md` skills table:

```markdown
| [<skill-name>](skills/<skill-name>/) | <short description> |
```

Keep the description concise and aligned with `metadata.json` `abstract`.

### Step 7 - Validate the package

Run structural checks before reporting completion:

```bash
python3 -m json.tool skills/<skill-name>/metadata.json >/dev/null
wc -l skills/<skill-name>/SKILL.md
find skills/<skill-name> -maxdepth 2 -type f | sort
rg -n "## Trigger keywords|workflows/" skills/<skill-name>/SKILL.md
```

Confirm:

- `SKILL.md` has `name` and `description` frontmatter.
- `SKILL.md` has `## Trigger keywords`.
- `SKILL.md` links every workflow file.
- Every workflow file has `name` and `description` frontmatter.
- The root `README.md` skills table includes the new skill.

### Step 8 - Report completion

Report:

- The created skill path.
- The workflow files created.
- The root docs updated.
- The validation commands run and whether they passed.

If validation cannot run, state the blocker and the highest-confidence manual checks completed.
