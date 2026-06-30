---
name: setup-experiment
description: >
  End-to-end interactive workflow — pick a product, then either run existing
  tasks and environments (Path A) or set up new ones from docs, suggested
  tasks, credentials, and templates (Path B). Builds the experiment, attaches
  signals, and optionally triggers the first iteration. For high-stakes customer
  deliverables, the Usability Benchmark Design workflow generates a rigorous,
  demand-ranked, two-arm friction-delta benchmark instead of quick suggestions.

  Trigger when users say: "set up an experiment", "create an experiment",
  "I want to run an experiment", "run my tasks", "setup experiment",
  "new experiment", "configure an experiment", "experiment setup",
  "usability benchmark", "friction delta", "skill-off vs skill-on", or
  "does the skill help".
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
| `prompt` | yes | string | Second-person imperative instruction for the agent. One scenario per prompt. Must be self-contained — each task runs in its own isolated sandbox, so never assume shared state or context from another task. |
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
| `evaluationType` | no | enum | `llm_judge` (default), `script_judge` (deterministic, exit-0 = pass — preferred for benchmark "ran + correctly-shaped output" checks), `automatic`, `manual`. |
| `model` | no | string | Judge model for `llm_judge`, e.g. `claude-sonnet-4-6`. |
| `script` / `scriptFile` | cond. | string | Required when `evaluationType` is `script_judge`. Sh script run in the sandbox after the agent run. Needs the `script_judge` org feature flag. |
| `passingThreshold` | yes | integer | 0–100 score required to pass. |
| `scoringMethod` | no | enum | `weighted_average` (default), `binary`, `percentage`. |

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

Agent config object — set only these four keys; the API rejects unknown fields with `"Unknown agentConfig fields: ..."`.

| Field | Required | Type | Notes |
|---|---|---|---|
| `harness` | yes | enum | `claude`, `codex`, `opencode`. |
| `provider` | yes | string | e.g. `anthropic`, `openai`, `google`, `fireworks`, `custom`. Must be supported by the chosen `harness`. |
| `model` | yes | string | Provider-specific model ID. Must be supported by the chosen `harness`. |
| `sandboxResources` | no | object | See below. |

The sandbox provider is chosen automatically (the default; GPU workloads route to Modal). Don't set it.

`sandboxResources` object (all optional, numeric — not strings):

| Field | Type | Range | Default |
|---|---|---|---|
| `cpu` | number | 1–4 | 4 |
| `memory` | number (GB) | 1–8 | 4 |
| `disk` | number (GB) | 1–10 (30+ needs custom tier) | 10 |
| `gpu` | enum | `T4`, `L4`, `A10G`, `A100`, `A100-80GB`, `H100` | unset |
| `gpuCount` | number | 1–8 | 1 (when `gpu` is set) |

Optionally prepare the sandbox before the agent runs via **init commands** (bash, installs deps) and **init files** (git clone or uploaded zip). See the [Tasks](https://docs.promptingcompany.com/guides/coding-agent-optimization/tasks) doc for what these are and when to use them, and [Limits & constraints](https://docs.promptingcompany.com/guides/coding-agent-optimization/limits) for their hard limits.

## Concepts & restrictions

Definitions, use cases, and platform limits live in the Coding Agent
Optimization docs — read them rather than re-deriving anything here:

| Topic | Doc |
|---|---|
| What a task is, instructions, goals/criteria, init files & commands, secrets | [Tasks](https://docs.promptingcompany.com/guides/coding-agent-optimization/tasks) |
| Harness/model, sandbox resources, GPU, secrets CLI | [Environments](https://docs.promptingcompany.com/guides/coding-agent-optimization/environments) |
| Run lifecycle, what each run records, iterations | [Runs & iterations](https://docs.promptingcompany.com/guides/coding-agent-optimization/runs) |
| Signal extraction (also see the `signal-config` skill) | [Signals](https://docs.promptingcompany.com/guides/coding-agent-optimization/signals) |
| **Execution constraints + all hard limits** | [Limits & constraints](https://docs.promptingcompany.com/guides/coding-agent-optimization/limits) |

The constraints below come from that
[Limits](https://docs.promptingcompany.com/guides/coding-agent-optimization/limits)
page. Keep them in mind on **every** task and prompt you draft — most "the run
produced nothing" failures trace back to one of them:

- **Fresh sandbox per run, no shared state.** Each task runs isolated — nothing
  carries over. Tasks must be self-contained; deps come from init commands/files.
- **One-shot prompt.** The agent gets the prompt once and runs to exit — no
  multi-turn, no follow-up, no clarifying question.
- **No browser/GUI.** Headless Linux only — a task that needs a clickable UI
  can't be measured here.
- **Background processes are killed.** When the agent exits, the sandbox is torn
  down. A prompt that ends with "server running in the background" captures
  nothing — prompt the agent to **finish and write an artifact**, and score the
  artifact.
- **Hard caps:** run ceiling **60 min**; init zip **≤ 500 MB**; init command ≤
  10k chars, ≤ 50 commands, default 5 min each; CPU 1–4, mem 1–8 GB, disk 1–10
  GB; GPU forces Modal.
- **Secrets are environment-scoped** (`tpc sim env secret set`), revoked during
  `script_judge`; `script_judge` needs the org feature flag + passes a security
  review at registration.

## Workflows

Two workflows. Pick by stakes:

- **Setup Experiment** — interactive, fast. Pick a product, run existing tasks or suggest new ones from docs, run. Right for internal probes and quick comparisons.
- **Usability Benchmark Design** — rigorous, demand-ranked, two-arm friction delta. Right when the deliverable is a customer ROI proof, a roadmap input, or a published benchmark.

### 1. Setup Experiment

See [`workflows/setup-experiment.md`](workflows/setup-experiment.md) for full steps.

The flow branches after product selection based on what the user already has. Always pull what the platform already knows; never block on missing information — fall back to web search and sensible defaults.

**Step 1 — Pick the product.** Use the active product if one is set; otherwise list and ask. Auto-select if the org has only one.

**Step 2 — Choose your path.** Show existing tasks and environments, then route:

- **Path A — Run what I have**: returning user with existing tasks and environments. Pick from lists, attach, run.
- **Path B — Set up something new**: first-time setup or fresh experiment. Capture context, suggest tasks from docs, pick a template, run.

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

> **Caveat for high-stakes benchmarks.** Path B Step 2 suggests tasks from the product's *own* docs — that tests the feature list, not the problem space, and structurally can't surface the popular task the product has no answer for. For a customer deliverable, use Workflow 2 instead.

### 2. Usability Benchmark Design

See [`workflows/benchmark-design.md`](workflows/benchmark-design.md) for the full methodology.

Generates a rigorous benchmark instead of quick suggestions. Two principles drive it:

1. **Measure the delta, not the pass rate.** Run every task twice — **skill-OFF** (friction floor) and **skill-ON**. The per-stage delta is the result; a skill-ON pass rate alone can't tell "the skill helped" from "the model already knew."
2. **Test the problem space, not the feature list.** Mine the task universe **tool-agnostically** from the whole ecosystem (galleries + hard counts + discourse), prove it comprehensive by source **saturation**, then demand-rank and tier it.

Score "usable" as a 5-stage funnel — **Comprehension → Formation → Execution → Recovery → Efficiency** — tagging each attempt to the first stage it fails, in agent-native units (turns, retries, hallucinated-API rate). Hold the **anti-spiral line**: Execution stops at "ran + correctly-shaped output"; never grade answer quality. Ground truth is the agent's trace + artifacts, never a self-judge; the agent never sees the bucket or answer key. The output is a **demand-vs-supply map** (served+usable / served+unusable / popular+unserved), not a leaderboard number.

On the platform: arms → two environments differing only by skill/docs attachment (same model); funnel → `signal-config.yaml`; goals → deterministic `script_judge`; tiers → `tagIds`; k repeats → re-runs aggregated across runs.

## General principles

- Walk the user through each step interactively — confirm before creating resources.
- Keep every task independent — each runs in its own isolated sandbox with no shared state, so a task must never depend on another task having run first. Write each prompt to be fully self-contained.
- Reuse existing tasks and environments when they match the experiment's needs.
- Suggest sensible defaults for signals based on the experiment's goals and template.
- Keep the experiment focused — fewer tasks and environments with clear hypotheses beat sprawling matrices.
- Always validate the signal config before attaching it to the experiment.
- Never block on missing information — web-search or use sensible defaults and keep moving.
- For any "does the skill help" question, default to a **two-arm friction delta** (skill-OFF vs skill-ON, same model), never a single-arm pass rate.
- When the deliverable leaves the building (a customer, a board, a publication), generate tasks via the Usability Benchmark Design workflow — mine the problem space tool-agnostically, don't enumerate the product's feature list.
