---
name: setup-experiment
description: End-to-end interactive workflow — pick a product, run existing tasks and environments (Path A), set up new ones (Path B), or discover usecase gaps by comparing competitor docs (Path C), then trigger the first iteration. Trigger when users say "set up an experiment", "create an experiment", "I want to run an experiment", "run my tasks", "new experiment", "configure an experiment", "compare competitors", or "find usecase gaps".
---

# Setup Experiment

## Overview

Three paths after product selection, depending on what the user already has:

- **Path A — Run what I have**: returning user with existing tasks and environments. Pick from lists, attach, run.
- **Path B — Set up something new**: first-time setup or fresh experiment. Capture context, suggest tasks from docs, pick a template, run.
- **Path C — Compare usecase gaps with competitors**: find competitors with overlapping features, crawl their docs for usecases your product doesn't cover, turn gaps into tasks for your product.

Pull what the platform already knows. Never block on missing information — fall back to web search and sensible defaults.

## Prerequisites

- `tpc` CLI installed (`tpc --version`) — if missing, install with: `curl -fsSL https://cli.promptingco.com/install.sh | bash`
- Authenticated: `tpc auth whoami`
- Active org set: `tpc org list` → `tpc org switch <org-slug>`

If any prerequisite is missing, resolve it before continuing:

```bash
curl -fsSL https://cli.promptingco.com/install.sh | bash   # install tpc CLI if missing
tpc auth login
tpc org switch <org-slug>
```

## Required Workflow

**Follow steps in order. Do not skip steps or create resources without user confirmation.**

---

### Step 1 — Pick the product

Check the active product:

```
tpc product current
```

If none is set, list and ask:

```
tpc product list
```

> "Which product are you experimenting on? (pick number or slug)"

Then: `tpc product switch <slug>`

If a product is already active, confirm:

> "Active product: [name]. Continue with this one or switch?"

If the org has only one product, auto-select it silently.

---

### Step 2 — Choose your path

Show inventory and route:

```
tpc sim task list
tpc sim env list
```

> "I see [N] tasks and [M] environments for [product].
> What do you want to do?
> (1) **Run what I have** — pick from existing, skip setup
> (2) **Set up something new** — guided flow with task suggestions and templates
> (3) **Compare usecase gaps with competitors** — find what competitors cover that you don't, turn gaps into tasks"

If nothing exists yet, skip the question and go straight to **Path B**.

If only one side exists (e.g. tasks but no environments), default to **Path B** and pre-fill from existing where possible.

---

## Path A — Run what I have

For returning users who already have tasks and environments.

### Step A1 — Pick tasks

```
tpc sim task list
```

Show as a numbered list. Ask:

> "Which tasks should this experiment include? (numbers, slugs, or 'all')"

### Step A2 — Pick environments

```
tpc sim env list
```

> "Which environments? (numbers, slugs, or 'all')"

### Step A3 — Create experiment and confirm shape

```
tpc sim experiment create --name "<name>" --description "<short hypothesis>"
```

Attach selected tasks and environments:

```
tpc sim experiment task add <experiment-id> <task-id>
tpc sim experiment env add <experiment-id> <env-id>
```

Show the summary:

> "Here's your experiment:
> - Tasks: [N]
> - Environments: [M]
> - Total runs per iteration: [N × M]
> - Signals: default (pass/fail, duration, cost) — edit?"

Wait for explicit confirmation. If the user wants custom signals, delegate to the signal-config skill.

### Step A4 — Run

```
tpc sim experiment run <experiment-id>
tpc sim experiment run status <experiment-id> --watch
```

---

## Path B — Set up something new

For first-time setup or a fresh experiment.

### Step B1 — Capture experiment context

Pull what the platform already has, ask only for the rest. Never block on missing info.

```
tpc product get
```

Show what we have, pre-populated:

> "Here's what I have on [product]:
> - Name: [name]
> - About: [one-liner]
>
> Edit either? (y/N)
>
> I still need:
> - **Docs URL** — paste it, or say 'don't have one' and I'll find it
> - **Agent surface** — CLI, SDK, MCP server, library, web app
> - **Known failure modes** — optional, anything you've seen agents get wrong"

**If the user doesn't have a docs URL:**

1. Web-search for `<product name> docs` or `<product name> developer documentation`.
2. Propose the top candidate:
   > "Found: [URL]. Use this? (Y/n)"
3. If rejected, ask the user to point you in the right direction or paste content directly.

After capture, offer to persist:

> "Save these to the product profile so we don't ask next time? (Y/n)"

If yes:

```
tpc product update --docs-url <url> --surface <surface> --failure-modes "<notes>"
```

### Step B2 — Suggest tasks from docs

> "Want me to read your docs and propose tasks, or do you have specific scenarios in mind?"

If propose:

1. Fetch docs from the location captured in Step B1.
2. Extract the product's capability surface — top primitives, common API calls, the "getting started" path.
3. Cross-reference against known agent failure modes (deprecated SDK installs, missing required fields, framework version confusion, MCP vs. CLI ambiguity, auth pattern errors).
4. Propose 5–8 candidates. For each: name, what it tests, why an agent is likely to fail, suggested success check.
5. If the product already has existing tasks, include them in the picker alongside the new suggestions so the user can mix.

Example output:

> Based on your docs, here are tasks I'd run:
>
> 1. **Getting Started** — agent installs the SDK and ships a hello-world. Likely failure: installing a deprecated package version.
> 2. **Send first message** — agent uses the SDK to send one message end-to-end. Likely failure: missing required fields.
> 3. **Set up webhook** — agent registers a delivery-event webhook. Likely failure: wrong auth header format.
> 4. **Batch send** — agent sends to more than 10 recipients. Likely failure: hits rate limit, doesn't retry.
> 5. **Configure custom domain** — agent adds and verifies a sending domain. Likely failure: skips DNS verification.
>
> Which should I turn into tasks? (e.g. "1, 3, 5" or "all")

For each selected task, draft a `task.json`. When writing the `prompt` field and each goal's `description`, follow the rules and examples in [`writing-prompts.md`](writing-prompts.md).

**Task schema** (`task.json`):

| Field | Required | Notes |
|---|---|---|
| `name` | yes | Short scenario name. |
| `description` | yes | One sentence on what this validates. |
| `category` | yes | `coding`, `research`, `documentation`, `analysis`. |
| `prompt` | yes | Second-person imperative; one scenario only. |
| `taskType` | yes | `cli_execution`. |
| `timeLimitMs` | yes | Run timeout in ms (e.g. `3600000`). |
| `successType` | no | e.g. `runs_reliably`, `implements_spec_reliably`. |
| `tagIds` | no | Existing tag IDs. |
| `goals[]` | yes | Goal objects: `name`, `description`, `passingThreshold` (0–100), and optional `evaluationType` (`llm_judge`), `model` (e.g. `claude-sonnet-4-6`), `scoringMethod` (`weighted_average`). |

Do **not** include `product` — the active product is injected by the CLI.

```json
{
  "name": "<short scenario name>",
  "description": "<what this task validates>",
  "category": "<coding | research | documentation | analysis>",
  "prompt": "<specific, actionable instruction>",
  "taskType": "cli_execution",
  "timeLimitMs": 3600000,
  "successType": "runs_reliably",
  "goals": [
    {
      "name": "<goal name>",
      "description": "<what a passing run looks like>",
      "evaluationType": "llm_judge",
      "model": "claude-sonnet-4-6",
      "passingThreshold": 70,
      "scoringMethod": "weighted_average"
    }
  ]
}
```

Confirm before creating:

```
tpc sim task create --file task.json
```

Note each returned task ID.

### Step B3 — Configure credentials

Most tasks need to hit the customer's product. Set up credentials before creating the experiment.

> "Tasks will need to hit [product]. How should agents authenticate?
> - Paste an API key / token (I'll store it as a secret on the product profile)
> - Skip — only run tasks that don't need auth
> - Already configured"

If paste:

```
tpc product secret set <product-slug> <key-name> <value>
```

Confirm:

```
tpc product secret list <product-slug>
```

If skip, flag tasks that require auth and exclude them from the run.

### Step B4 — Pick an experiment template

> "What shape are you running?
> (1) **Leaderboard** — run tasks across leading models, get a ranked report
> (2) **Docs vs. no-docs** — same model, with and without docs in context
> (3) **A vs. B** — paired comparison on one dimension (model, harness, etc.)
> (4) **Custom** — pick your own environments"

**Leaderboard** (default for first runs and baseline reports):

- Default lineup: `frontier-coding` — Claude Opus 4.7 and Codex 5.5.
- Ask if the user wants a different lineup; otherwise proceed with the default.
- Auto-create one environment per model in the lineup, all else equal.
- Success framing defaults to `runs_reliably`.

**Docs vs. no-docs**:

- Auto-create `<product>-with-docs` and `<product>-no-docs`, identical except for docs in context.
- Same model across both (default: Claude Opus 4.7).
- Success framing defaults to `implements_spec_reliably`.

**A vs. B**:

- Ask the one dimension that varies. Create two environments.

**Custom**:

- Fall through to manual environment creation. For each environment, collect name, description, and agent config.

**Environment schema** (`tpc sim env create` flags):

| Flag | Required | Notes |
|---|---|---|
| `--name` | yes | Descriptive name. |
| `--agent-config` | yes | JSON string or `@file.json`/`@file.toml`. |
| `--description` | no | What this configuration tests. |
| `--enabled` | no | Default `true`. |
| `--schedule` | no | `7d` or `14d`. |
| `--tag-ids` | no | Comma-separated tag IDs. |
| `--task-ids` | no | Tasks to link at creation. |

**Agent config object** — only these four keys are accepted; any other key is rejected by the API with `"Unknown agentConfig fields: ..."`.

| Field | Required | Notes |
|---|---|---|
| `harness` | yes | `claude`, `codex`, `opencode`. |
| `provider` | yes | e.g. `anthropic`, `openai`, `fireworks`. Must be supported by the chosen `harness`. |
| `model` | yes | Provider-specific model ID. Must be supported by the chosen `harness`. |
| `sandboxResources` | no | Object (see below). |

`sandboxResources` (all optional, numeric — not strings):

| Field | Type | Range | Default |
|---|---|---|---|
| `cpu` | number | 1–4 | 1 |
| `memory` | number (GB) | 1–8 | 1 |
| `disk` | number (GB) | 1–10 (30+ needs custom tier) | 3 |
| `gpu` | enum | `T4`, `L4`, `A10G`, `A100`, `A100-80GB`, `H100` | unset |
| `gpuCount` | number | 1–8 | 1 (when `gpu` is set) |

```json
{
  "harness": "claude",
  "provider": "anthropic",
  "model": "claude-opus-4-7",
  "sandboxResources": {
    "cpu": 2,
    "memory": 4,
    "disk": 10
  }
}
```

Create with:

```
tpc sim env create --name "<name>" --agent-config '<json>' --description "<description>"
```

### Step B5 — Create experiment and confirm shape

```
tpc sim experiment create --name "<experiment name>" --description "<hypothesis or goal>"
```

Attach tasks and environments:

```
tpc sim experiment task add <experiment-id> <task-id>
tpc sim experiment env add <experiment-id> <env-id>
```

Show the summary:

> "Here's your experiment:
> - Tasks: [N]
> - Environments: [M] ([template name])
> - Total runs per iteration: [N × M]
> - Signals: default (pass/fail, duration, cost) — edit?"

Default signals by template:

| Template         | Default signals                                                          |
| ---------------- | ------------------------------------------------------------------------ |
| Leaderboard      | `status` (pass/fail), `duration` (stats), `cost` (stats), `token_total`  |
| Docs vs. no-docs | Goal pass rate, fabricated API/function detection, `steps` (stats)       |
| A vs. B          | Goal pass rate, `duration` (stats), `cost` (stats)                       |

If the user wants custom signals, delegate to the signal-config skill. Otherwise apply defaults:

```
tpc sim experiment update <experiment-id> --signal-config <default-template>.yaml
```

Wait for explicit confirmation.

### Step B6 — Run

```
tpc sim experiment run <experiment-id>
tpc sim experiment run status <experiment-id> --watch
```

If the user wants to run later, give them the commands:

> "When you're ready:
>
> ```
> tpc sim experiment run <experiment-id>
> tpc sim experiment run status <experiment-id> --watch
> tpc sim experiment results <experiment-id>
> tpc sim experiment signals <experiment-id>
> ```"

---

## Path C — Compare usecase gaps with competitors

For users who want to discover missing usecases by analyzing what competitors already cover. Tasks are always created for **your** product — competitors are only used as inspiration.

### Step C1 — Capture product context

Same as Path B Step B1. Pull what the platform has, fill in what's missing.

```
tpc product get
```

Ensure you have:
- **Docs URL** — needed to know what usecases the product already covers
- **Feature surface** — the capabilities/features the product offers (e.g. "agentic monitoring tools", "email API", "payment processing")

If docs URL is missing, web-search for it. If feature surface is vague, extract it from the docs.

> "To find competitor gaps I need to know your product's feature area.
> Here's what I see: [features from docs].
> Anything to add or correct?"

### Step C2 — Identify competitors

Ask the user first:

> "Do you have specific competitors in mind, or should I search for ones with overlapping features?"

**If the user names competitors:**

Take their list as-is. For each, web-search for the docs URL if not provided.

**If the user wants a search:**

Web-search for competitors that share features with the product. Use queries like:
- `<feature area> tools`
- `<feature area> alternatives`
- `<product name> competitors`
- `<product name> vs`

Present a ranked list:

> "I found these competitors with overlapping features:
>
> 1. **Competitor A** — [one-liner on what they do, docs URL]
> 2. **Competitor B** — [one-liner, docs URL]
> 3. **Competitor C** — [one-liner, docs URL]
>
> Which ones should I analyze? (numbers or 'all')"

Aim for 3–5 candidates.

### Step C3 — Crawl competitor docs

For each selected competitor:

1. Fetch their documentation (getting started, guides, tutorials, API reference, use-case pages).
2. Extract every distinct **usecase** or **integration pattern** they document. A usecase is a concrete thing a user can accomplish — not a feature bullet point.

Organize findings per competitor:

> **Competitor A** usecases found:
> - Implement multi-domain monitoring
> - Set up alerting across microservices
> - Create custom dashboards with real-time metrics
> - Configure log aggregation from multiple sources
> - ...

### Step C4 — Gap analysis

Compare competitor usecases against:
1. The product's own documentation (from Step C1)
2. Any existing tasks on the platform (`tpc sim task list`)

For each competitor usecase, classify it:
- **Covered** — your product docs or existing tasks already address this
- **Gap** — your product likely supports this capability but has no documented usecase or task for it
- **Out of scope** — your product doesn't offer this capability (skip these)

Present the gaps as a table:

> "Here are usecases competitors cover that you don't have tasks for:
>
> | # | Usecase | Source | Why it's a gap | Task opportunity |
> |---|---|---|---|---|
> | 1 | Multi-domain monitoring setup | Competitor A | Your docs show single-domain only, but the API supports multiple | Task: set up monitoring across two domains |
> | 2 | Alerting across microservices | Competitor A, B | No tutorial covering distributed alerting | Task: configure alerts spanning 3 services |
> | 3 | Log aggregation from K8s | Competitor C | Your docs cover VM only, not containers | Task: pipe K8s pod logs into the platform |
>
> Which gaps should I turn into tasks? (numbers or 'all')"

Focus on **gaps**, not out-of-scope items. Only surface usecases that the product can realistically support.

### Step C5 — Generate tasks from gaps

For each selected gap, draft a `task.json` for **your product** (not the competitor). The competitor usecase is inspiration — the task prompt must reference your product's API, docs, and capabilities.

Follow the same rules as Path B Step B2:
- Use the task schema from the main skill definition
- Follow [`writing-prompts.md`](writing-prompts.md) for prompt and goal writing
- Frame prompts as a user asking for help with your product, not the competitor's

Example — if the gap is "multi-domain monitoring" inspired by Competitor A:

```json
{
  "name": "multi-domain-monitoring",
  "description": "Agent sets up monitoring across two separate domains in a single account.",
  "category": "coding",
  "prompt": "I have two domains — api.example.com and web.example.com — and I want to monitor both from my [product] account. Set up monitoring for both so I can see their status on one dashboard.",
  "taskType": "cli_execution",
  "timeLimitMs": 3600000,
  "successType": "runs_reliably",
  "goals": [
    {
      "name": "both-domains-monitored",
      "description": "The agent's run produces configuration or API calls that register both domains for monitoring, and a status check confirms both are active.",
      "evaluationType": "llm_judge",
      "model": "claude-sonnet-4-6",
      "passingThreshold": 70,
      "scoringMethod": "weighted_average"
    }
  ]
}
```

Show each drafted task and confirm before creating:

```
tpc sim task create --file task.json
```

Note each returned task ID.

### Step C6 — Continue to experiment

Once gap-derived tasks are created, merge into the standard experiment flow:

1. **Configure credentials** — same as Path B Step B3.
2. **Pick a template** — same as Path B Step B4. Leaderboard is a good default here to see how different models handle the newly discovered usecases.
3. **Create experiment and confirm shape** — same as Path B Step B5.
4. **Run** — same as Path B Step B6.
