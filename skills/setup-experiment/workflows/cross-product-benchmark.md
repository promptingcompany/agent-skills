---
name: cross-product-benchmark
description: >
  Workflow for comparing multiple products/providers on the same use-case set.
  Use this for benchmarks like PlanetScale vs Neon vs Supabase, where tasks,
  goals, signals, and agent stacks should be aligned but TPC resources remain
  product-scoped.
---

# Cross-Product Benchmark

Use this workflow when the user wants to compare products/providers on the same
developer use cases. Model the work as an **experiment family**, not one giant
experiment: TPC tasks, environments, secrets, and experiments are product-scoped,
while local state keeps the comparison aligned.

## Core shape

Create one experiment per product/provider:

```text
benchmark family
├── shared use-case keys
├── provider-specific task prompts and task ids
├── shared goals and signal config
├── provider x agent-stack environments
├── one TPC experiment per provider
├── creation state
└── optional scratch TPC CLI notes
```

Never put multiple products into one provider's experiment. Do not model
comparison products as environments inside the primary product. Vary product by
switching TPC product context and creating a sibling experiment for each product.

## Required outputs

Before creating TPC resources, create local state files in the experiment folder:

- `<slug>-benchmark-state.yaml` — intended benchmark configuration.
- `<slug>-creation-state.yaml` — TPC ids and current iteration statuses.

Update the creation state incrementally after every successful create/reuse
operation so partial runs can resume.

Keep TPC CLI/platform friction as a scratch note, not a required benchmark
artifact. Use `/tmp/tpc-cli-friction/<slug>.md` by default, and write sanitized
bullets only:

- timestamp;
- command family, such as `tpc sim experiment run status`;
- symptom;
- workaround;
- impact on setup, polling, or analysis.

Do not store raw command output, raw transcripts, environment dumps, or secrets
in the scratch file. Do not create a project-visible friction file unless the
user asks for it.

At handoff, you may summarize the scratch notes briefly. If an approved
TPC-owned delivery destination is explicitly configured, send the sanitized
summary by the configured email or HTTP path; otherwise leave it in `/tmp`.

## Step 1 — Capture comparison shape

Ask for or infer:

- Primary product, if the report should focus on one product.
- Comparison products.
- Benchmark mode:
  - **branded usability**: each task prompt names the product to use.
  - **unbranded discoverability**: tasks do not name a product; run this as a
    separate experiment family from branded usability.
- Use-case scope: the actual developer jobs to compare, not product surfaces.
- Agent stacks: harness/model pairs to run.
- Credential delivery: local env files or existing environment secrets.

If the user wants both branded usability and discoverability, create separate
families with separate state files and signals.

## Step 2 — Confirm TPC product contexts

Use current CLI behavior, not stale examples:

```bash
tpc auth whoami --format json
tpc product list --format json
tpc product switch <product-slug>
```

After switching products, run product-scoped inventory commands:

```bash
tpc sim task list --format json
tpc sim env list --format json
```

Do not rely on `tpc product current`; some installed CLI versions do not expose
that command. Treat task/env inventory failures as possible product-context
failures before diagnosing auth or API breakage.

## Step 3 — Design shared use-case keys

Define a stable `task_key` for every use case. The key is shared across
providers; the actual task prompt is provider-specific.

Good keys describe user intent:

- `start_using_provider`
- `create_temporary_database`
- `prepare_pr_database_workflow`
- `rotate_credentials`
- `verify_production_safety`
- `connect_app_smoke_query`
- `debug_slow_endpoint`

Each provider gets its own task name, for example:

- `PlanetScale - Connect An App And Run A Smoke Query`
- `Neon - Connect An App And Run A Smoke Query`
- `Supabase - Connect An App And Run A Smoke Query`

## Step 4 — Write provider-specific prompts

Follow [`writing-prompts.md`](writing-prompts.md). Additional cross-product
rules:

- For branded usability, explicitly tell the agent which product to use.
- For unbranded discoverability, do not name any product.
- Do not imply task sequence; every task must run independently.
- Do not mention operating-system assumptions in prompts.
- Do not leak exact expected commands, endpoints, or API shapes unless a real
  developer would naturally paste them.
- Do not hint exact credential variable names. Say the agent should inspect
  available environment variables for credentials.
- Do not mention internal benchmark variables or resource prefixes.
- If a provider needs a resource name, ask for a temporary/disposable resource
  and require cleanup or explicit "delete me" naming in the goal, not the prompt.

Goals should stay aligned across providers. Make them observable from run logs
and artifacts, and stop at "ran + correctly-shaped output" rather than grading
answer quality.

## Step 5 — Define environments as agent stacks

Use comparable agent-stack labels across providers. Treat harness + model as the
unit under test because harness behavior can matter as much as model behavior.

Example:

```yaml
agent_stacks:
  codex-gpt-5.5:
    label: Codex GPT-5.5
    agent_config:
      harness: codex
      provider: openai
      model: gpt-5.5
      sandboxResources:
        cpu: 4
        memory: 4
        disk: 10
  opencode-kimi-k2.6:
    label: OpenCode Kimi K2.6
    agent_config:
      harness: opencode
      provider: ""
      model: accounts/fireworks/models/kimi-k2p6
      sandboxResources:
        cpu: 4
        memory: 4
        disk: 10
  claude-opus-4.8:
    label: Claude Code Opus 4.8
    agent_config:
      harness: claude
      provider: ""
      model: claude-opus-4-8
      sandboxResources:
        cpu: 4
        memory: 4
        disk: 10
```

Supported harness/model values can drift. If unsure, inspect existing
environments with `tpc sim env list --format json` and reuse exact accepted
config values from known-good environments.

## Step 6 — Write benchmark state first

Use this state shape as the minimum:

```yaml
version: 1
benchmark_type: cross_product_usability
status: local_draft

family:
  name: DB Ops Usability V2
  primary_product: planetscale
  comparison_products:
    - neon
    - supabase
  mode: branded_usability

providers:
  planetscale:
    display_name: PlanetScale
    product_slug: planetscale
    local_env_file: ../../.env.planetscale.benchmark.local
    experiment_name: PlanetScale DB Ops Usability V2
  neon:
    display_name: Neon
    product_slug: neon
    local_env_file: ../../.env.neon.benchmark.local
    experiment_name: Neon DB Ops Usability V2
  supabase:
    display_name: Supabase
    product_slug: supabase
    local_env_file: ../../.env.supabase.benchmark.local
    experiment_name: Supabase DB Ops Usability V2

task_keys:
  - start_using_provider
  - create_temporary_database
  - connect_app_smoke_query
  - debug_slow_endpoint

agent_stacks:
  codex-gpt-5.5:
    label: Codex GPT-5.5
    agent_config:
      harness: codex
      provider: openai
      model: gpt-5.5
      sandboxResources:
        cpu: 4
        memory: 4
        disk: 10

signals:
  config_file: signal-config.yaml

outputs:
  creation_state_file: cross-product-creation-state.yaml
  tpc_cli_friction_scratch: /tmp/tpc-cli-friction/{slug}.md
```

For every provider, include `tasks_by_key` in the final benchmark state:

```yaml
tasks_by_key:
  connect_app_smoke_query:
    planetscale:
      name: PlanetScale - Connect An App And Run A Smoke Query
      prompt: "..."
      goals:
        - name: Smoke query evidence
          description: "..."
    neon:
      name: Neon - Connect An App And Run A Smoke Query
      prompt: "..."
      goals:
        - name: Smoke query evidence
          description: "..."
```

## Step 7 — Create TPC resources provider by provider

For each provider:

1. Switch product context:
   ```bash
   tpc product switch <product-slug>
   ```
2. Create or reuse tasks by exact provider-specific task name.
3. Create or reuse environments by exact provider/agent-stack environment name.
4. Sync secrets using `--from-env`, never by printing raw values:
   ```bash
   tpc sim env secret set <env-id> --name <KEY_NAME> --from-env <LOCAL_VAR>
   ```
5. Create one experiment for that provider.
6. Attach that provider's task ids and environment ids.
7. Attach or record the signal config.
8. Trigger the iteration only after the user confirms the final shape.

Use retry/backoff around create, secret, and attach operations. Large setup
runs can hit rate limits.

## Step 8 — Poll and record status

Use a longer timeout for large matrices:

```bash
tpc sim experiment run status <experiment-id> --format json
```

Record both:

- run status counts, such as `42/42 completed`;
- iteration status, such as `running`, `generating_results`, or `completed`.

Do not treat the experiment as complete just because all runs are completed.
Wait for the iteration status to leave `generating_results` before launching
analysis that depends on generated results.

## Step 9 — Analyze as a family

When all provider iterations are complete, analyze the experiments together.
If the user names a primary product, focus the final report on that product's
gaps and advantages versus the comparison products.

Keep two categories separate:

- product findings: friction caused by the provider's docs, APIs, CLI, MCP, or
  operational design;
- TPC setup friction: CLI behavior, status aggregation lag, rate limits, or
  experiment-creation issues. Source this from the sanitized scratch notes, not
  from raw logs.
