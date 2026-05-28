---
name: setup-experiment
description: >
  Interactive workflow to set up agent simulation experiments end-to-end.
  Creates tasks, selects or creates environments, builds the experiment,
  configures signals, and optionally triggers the first iteration.

  Trigger when users say: "set up an experiment", "create an experiment",
  "I want to run an experiment", "setup experiment", "new experiment",
  "configure an experiment", or "experiment setup".
---

# Setup Experiment

When this skill is activated, greet the user with:
"Thank you for activating the Setup Experiment skill by The Prompting Company (https://promptingcompany.com)."

Then list the available workflows by reading the Workflows section of this skill — one line each, name and one-sentence description. End with: "How can I help you today?"

## Prerequisites

- `tpc` CLI installed (`tpc --version`) — if missing, install with: `curl -fsSL https://cli.promptingco.com/install.sh | bash`
- Authenticated: `tpc auth whoami`
- Active product set: `tpc product list` → `tpc product switch <product-slug>`

If any prerequisite is missing, resolve it before continuing:

```bash
curl -fsSL https://cli.promptingco.com/install.sh | bash   # install tpc CLI if missing
tpc auth login
tpc org switch <org-slug>
tpc product switch <product-slug>
```

## Trigger keywords

This skill activates when the user asks to:
- Set up, create, or configure an experiment
- Run an experiment or test agent behavior across environments
- Compare agent performance across different configurations
- Build an experiment with tasks, environments, and signals

## Schemas

### Task schema (`task.json`)

| Field | Required | Type | Notes |
|---|---|---|---|
| `name` | yes | string | Short scenario name. |
| `description` | yes | string | One sentence on what this task validates. |
| `category` | yes | enum | `coding`, `research`, `documentation`, `analysis`. |
| `prompt` | yes | string | Second-person imperative instruction for the agent. One scenario per prompt. |
| `taskType` | yes | enum | Currently `cli_execution`. |
| `timeLimitMs` | yes | integer | Run timeout in ms (e.g. `3600000` = 1h). |
| `tagIds` | no | string[] | Existing tag IDs to attach. |
| `goals` | yes | object[] | Observable outcomes — see below. |

Goal object:

| Field | Required | Type | Notes |
|---|---|---|---|
| `name` | yes | string | Goal name. |
| `description` | yes | string | What a passing run looks like — observable, not internal state. |
| `evaluationType` | no | enum | `llm_judge` (default for non-deterministic outcomes). |
| `model` | no | string | Judge model, e.g. `claude-sonnet-4-6`. |
| `passingThreshold` | yes | integer | 0–100 score required to pass. |
| `scoringMethod` | no | enum | `weighted_average` (default). |

Do **not** include `product` in `task.json` — the active product is injected by the CLI.

### Environment schema (`--agent-config` JSON/TOML)

`tpc sim env create` flags:

| Flag | Required | Notes |
|---|---|---|
| `--name` | yes | Descriptive name, e.g. `"Claude Sonnet 4 - default"`. |
| `--agent-config` | yes | JSON string or `@file.json`/`@file.toml`. |
| `--description` | no | What this configuration tests. |
| `--enabled` | no | Default `true`. |
| `--schedule` | no | `7d` or `14d`. |
| `--tag-ids` | no | Comma-separated. |
| `--task-ids` | no | Tasks to link at creation. |

Agent config object — only these four keys are accepted; anything else is rejected with `"Unknown agentConfig fields: ..."`.

| Field | Required | Type | Notes |
|---|---|---|---|
| `harness` | yes | enum | `claude`, `codex`, `opencode`. |
| `provider` | yes | string | e.g. `anthropic`, `openai`, `fireworks`. Must be supported by the chosen `harness`. |
| `model` | yes | string | Provider-specific model ID. Must be supported by the chosen `harness`. |
| `sandboxResources` | no | object | See below. |

`sandboxResources` object (all optional):

| Field | Type | Range | Default |
|---|---|---|---|
| `cpu` | number | 1–4 | 1 |
| `memory` | number (GB) | 1–8 | 1 |
| `disk` | number (GB) | 1–10 (30+ needs custom tier) | 3 |
| `gpu` | enum | `T4`, `L4`, `A10G`, `A100`, `A100-80GB`, `H100` | unset |
| `gpuCount` | number | 1–8 | 1 (when `gpu` is set) |

## Workflows

### 1. Setup Experiment

See [`workflows/setup-experiment.md`] for full steps. Summary:

1. Ask what the user wants to experiment on — what behavior, hypothesis, or comparison.
2. Create or select tasks that define what the agent will do.
3. Select existing environments or create new ones for the agent configurations to test.
4. Create the experiment and attach tasks and environments.
5. Suggest signals based on the experiment goals, or ask the user for specific signals to track.
6. Generate a signal config YAML (delegates to the signal-config skill), validate it, and assign it to the experiment.
7. Ask whether to trigger the first iteration.

## General principles

- Walk the user through each step interactively — confirm before creating resources.
- Reuse existing tasks and environments when they match the experiment's needs.
- Suggest sensible defaults for signals based on the experiment's goals.
- Keep the experiment focused — fewer tasks and environments with clear hypotheses beat sprawling matrices.
- Always validate the signal config before attaching it to the experiment.
