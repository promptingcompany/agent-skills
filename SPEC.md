# Skill Structural Requirements Specification

Status: repo-local specification
Applies to: every skill package under `skills/<skill-name>/`

This specification defines the structural requirements for a skill in this repository. It reconciles the root `README.md`, `CONTRIBUTING.md`, `AGENTS.md`, `CLAUDE.md`, and the currently shipped skill packages. Where those sources differ, this spec uses the stricter package shape already used by the current skills.

## 1. Package Boundary

A skill is one self-contained directory under `skills/`.

Required:

- The directory path must be `skills/<skill-name>/`.
- `<skill-name>` must be kebab-case.
- The `name` value in `SKILL.md` frontmatter must match `<skill-name>`.
- Distribution zip packages must use the exact skill directory name.
- A new skill must be added to the skills table in the root `README.md`.

Do not place skill-specific source files outside the skill directory unless they are root-level repository documentation.

## 2. Required Directory Shape

Every skill package must use this structure:

```text
skills/<skill-name>/
|-- SKILL.md
|-- README.md
|-- INSTALL.md
|-- metadata.json
`-- workflows/
    `-- <workflow-name>.md
```

Optional package-local file:

```text
skills/<skill-name>/
`-- AGENTS.md
```

`AGENTS.md` is optional and should only be added when the skill needs compiled agent rules beyond `SKILL.md` and `workflows/`.

## 3. `SKILL.md`

`SKILL.md` is the agent-facing prompt for the skill.

Required:

- Start with YAML frontmatter.
- Include `name`.
- Include `description`.
- Keep the file under 500 lines.
- Start the body with a top-level heading followed by a one-paragraph purpose statement or overview.
- Include a short activation greeting matching the existing skills.
- Include a `## Trigger keywords` section.
- Include a `## Workflows` section when workflow files exist.
- Link every workflow file from the `## Workflows` section.
- Keep detailed procedural material in `workflows/` instead of in `SKILL.md`.
- Use second-person imperative instructions where the agent is being directed to act.

Required frontmatter shape:

```yaml
---
name: <skill-name>
description: >
  One or more sentences describing what the skill does and when to use it.
---
```

Recommended body shape:

```markdown
# Human-Readable Skill Title

One paragraph describing the skill purpose.

When this skill is activated, greet the user with:
"Thank you for activating the <Skill Title> skill by The Prompting Company (https://promptingcompany.com)."

## Trigger keywords

This skill activates when the user asks to:
- ...

## Workflows

### 1. Workflow Name

See [workflows/<workflow-name>.md](workflows/<workflow-name>.md) for full steps. Summary:

1. ...
```

## 4. `README.md`

`README.md` is human-readable documentation for the skill.

Required:

- State what the skill does.
- State when a human should install or use it.
- List the included workflows.
- Link to `INSTALL.md`.
- Keep human-facing explanation here rather than in `SKILL.md`.

## 5. `INSTALL.md`

`INSTALL.md` describes setup and installation.

Required:

- Include installation instructions for the supported target environment.
- Include any prerequisites, authentication, CLI, or MCP setup required by the skill.
- Include a short verification step so the user can confirm the skill is installed or ready.

If the skill has no external setup, say that explicitly and provide the copy/install path used by this repository.

## 6. `metadata.json`

`metadata.json` is structured package metadata.

Required fields:

```json
{
  "version": "0.1.0",
  "organization": "Prompting Company",
  "abstract": "One sentence describing the skill."
}
```

Requirements:

- The file must be valid JSON.
- The file must include `version`, `organization`, and `abstract`.
- `version` must be a SemVer string.
- `organization` must identify the maintaining organization.
- `abstract` must be one concise sentence.
- Bump `version` when the skill behavior, workflows, or install requirements change.

Optional fields such as `date` or `references` may be added when they are useful, but they must not replace the required fields.

## 7. `workflows/`

`workflows/` contains detailed workflow files referenced by `SKILL.md`.

Required:

- Workflow filenames must be kebab-case Markdown files.
- Each workflow file must be linked from `SKILL.md`.
- Each workflow file must start with YAML frontmatter.
- The frontmatter must include `name` and `description`.
- The workflow `name` should match the filename without `.md`.
- The workflow body must include a clear title and ordered steps.
- Workflow steps should be specific enough for an agent to execute without guessing.

Required workflow frontmatter shape:

```yaml
---
name: <workflow-name>
description: >
  One or more sentences describing what this workflow does and when it triggers.
---
```

Recommended workflow body shape:

```markdown
# Workflow Name

## Overview

One paragraph summary.

## Prerequisites

- ...

## Required Workflow

**Follow all steps in order.**

### Step 1 - ...
```

## 8. Root Repository Registration

When adding a new skill:

- Add a row to the root `README.md` skills table.
- Link the skill name to `skills/<skill-name>/`.
- Use the same short description as, or a shortened version of, `metadata.json` `abstract`.

When removing or renaming a skill:

- Update the root `README.md` skills table.
- Keep package names, zip names, and metadata names aligned.

## 9. Validation Checklist

Before opening a pull request, verify:

- `skills/<skill-name>/SKILL.md` exists.
- `skills/<skill-name>/README.md` exists.
- `skills/<skill-name>/INSTALL.md` exists.
- `skills/<skill-name>/metadata.json` exists and is valid JSON.
- `skills/<skill-name>/workflows/` exists.
- Skill and workflow names are kebab-case.
- `SKILL.md` is under 500 lines.
- `SKILL.md` has `name` and `description` frontmatter.
- `SKILL.md` has `## Trigger keywords`.
- Every workflow file is linked from `SKILL.md`.
- Every workflow file has `name` and `description` frontmatter.
- The skill directory name and workflow filenames are kebab-case.
- `metadata.json` includes `version`, `organization`, and `abstract`.
- The root `README.md` skills table is current.

Useful checks:

```bash
python3 -m json.tool skills/<skill-name>/metadata.json >/dev/null
wc -l skills/<skill-name>/SKILL.md
find skills/<skill-name> -maxdepth 2 -type f | sort
python3 - <<'PY'
import json
import re
from pathlib import Path

skill = Path("skills/<skill-name>")
kebab = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

errors = []
if not kebab.fullmatch(skill.name):
    errors.append(f"skill directory is not kebab-case: {skill.name}")
for workflow in sorted((skill / "workflows").glob("*.md")):
    if not kebab.fullmatch(workflow.stem):
        errors.append(f"workflow filename is not kebab-case: {workflow.name}")

metadata = json.loads((skill / "metadata.json").read_text())
missing = [key for key in ("version", "organization", "abstract") if not metadata.get(key)]
if missing:
    errors.append(f"metadata.json missing required fields: {', '.join(missing)}")
elif not re.fullmatch(r"\d+\.\d+\.\d+", str(metadata["version"])):
    errors.append(f"metadata.json version is not SemVer: {metadata['version']}")

if errors:
    raise SystemExit("\n".join(errors))
PY
```
