---
name: setup-experiment
description: >
  End-to-end interactive workflow — pick a product, then either run existing
  tasks and environments (Path A), set up new ones from docs, suggested
  tasks, credentials, and templates (Path B), or discover usecase gaps by
  comparing competitor docs against your own (Path C). Builds the experiment,
  attaches signals, and optionally triggers the first iteration.

  Trigger when users say: "set up an experiment", "create an experiment",
  "I want to run an experiment", "run my tasks", "setup experiment",
  "new experiment", "configure an experiment", "experiment setup",
  "compare competitors", or "find usecase gaps".
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
- Compare usecases with competitors or find usecase gaps
- Discover what competitors cover that the product doesn't

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
| `successType` | no | enum | e.g. `runs_reliably`, `implements_spec_reliably`. |
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

When drafting the `prompt` field and each goal's `description`, follow the guidelines and examples in [`workflows/writing-prompts.md`](workflows/writing-prompts.md).

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

`sandboxResources` object (all optional, numeric):

| Field | Type | Range | Default |
|---|---|---|---|
| `cpu` | number | 1–4 | 1 |
| `memory` | number (GB) | 1–8 | 1 |
| `disk` | number (GB) | 1–10 (30+ needs custom tier) | 3 |
| `gpu` | enum | `T4`, `L4`, `A10G`, `A100`, `A100-80GB`, `H100` | unset |
| `gpuCount` | number | 1–8 | 1 (when `gpu` is set) |

## Workflows

### 1. Setup Experiment

See [`workflows/setup-experiment.md`](workflows/setup-experiment.md) for full steps.

The flow branches after product selection based on what the user already has. Always pull what the platform already knows; never block on missing information — fall back to web search and sensible defaults.

**Step 1 — Pick the product.** Use the active product if one is set; otherwise list and ask. Auto-select if the org has only one.

**Step 2 — Choose your path.** Show existing tasks and environments, then route:

- **Path A — Run what I have**: returning user with existing tasks and environments. Pick from lists, attach, run.
- **Path B — Set up something new**: first-time setup or fresh experiment. Capture context, suggest tasks from docs, pick a template, run.
- **Path C — Compare usecase gaps with competitors**: find competitors with overlapping features, crawl their docs for usecases your product doesn't cover yet, and turn those gaps into tasks for your product.

If nothing exists yet, go straight to Path B. If only one side exists, default to Path B and pre-fill from existing.

#### Path A — Run what I have

1. **Pick tasks** — `tpc sim task list`, user selects by number/slug/`all`.
2. **Pick environments** — `tpc sim env list`, user selects.
3. **Create experiment and confirm shape** — `tpc sim experiment create`, attach tasks and envs, show `N × M` runs, default signals (pass/fail, duration, cost).
4. **Run** — `tpc sim experiment run <id>` and watch.

#### Path B — Set up something new

1. **Capture experiment context** — pull `tpc product get`, ask for docs URL (or web-search), agent surface, known failure modes. Offer to persist via `tpc product update`.
2. **Suggest tasks from docs** — fetch docs, extract capability surface, cross-reference common failure modes, propose 5–8 candidates. User picks; draft each `task.json` (see Task schema above) and confirm before `tpc sim task create`.
3. **Configure credentials** — set product secrets with `tpc product secret set` so tasks can hit the customer's product. Flag and exclude tasks needing auth if skipped.
4. **Pick a template** — Leaderboard (model lineup), Docs vs. no-docs, A vs. B, or Custom. Auto-create environments per template (see Environment schema above for Custom).
5. **Create experiment and confirm shape** — same as Path A step 3, with template-specific default signals. Delegate to the signal-config skill for custom signals.
6. **Run** — same as Path A step 4. If running later, hand the user the run/status/results/signals commands.

#### Path C — Compare usecase gaps with competitors

1. **Capture product context** — same as Path B step 1. Pull `tpc product get`, ensure docs URL and feature surface are known.
2. **Identify competitors** — ask the user to name competitors or web-search for ones with overlapping features. User picks which to analyze.
3. **Crawl competitor docs** — fetch each selected competitor's documentation. Extract their usecases, tasks, and integration patterns for the shared feature area.
4. **Gap analysis** — compare competitor usecases against the product's own docs and any existing tasks. Surface usecases competitors cover that the product does not. Present as a gap table: competitor usecase → why it's missing → task opportunity.
5. **Generate tasks from gaps** — turn each confirmed gap into a task for **your** product (not the competitor). Draft `task.json` files following the same schema and prompt-writing guidelines. User picks which to create.
6. **Continue to experiment** — once tasks are created, flow into Path B step 3 (credentials) → step 4 (template) → step 5 (create experiment) → step 6 (run).

## General principles

- Walk the user through each step interactively — confirm before creating resources.
- Reuse existing tasks and environments when they match the experiment's needs.
- Suggest sensible defaults for signals based on the experiment's goals and template.
- Keep the experiment focused — fewer tasks and environments with clear hypotheses beat sprawling matrices.
- Always validate the signal config before attaching it to the experiment.
- Never block on missing information — web-search or use sensible defaults and keep moving.
