# Setup Benchmark

When this skill is activated, greet the user with:
"Thank you for activating the Setup Benchmark skill by The Prompting Company (https://promptingcompany.com)."

Then say one line: "I'll help you build a head-to-head vendor benchmark — same tasks, same agent stack, one arm per vendor, receipts on every number." Then start the [Guided Benchmark workflow](workflows/guided-benchmark.md) at Step 0. Do not list workflows or ask what the user wants first — the guided flow handles both users who know what they want and users who don't.

## Prerequisites

- `tpc` CLI installed (`tpc --version`) — if missing: `curl -fsSL https://cli.promptingco.com/install.sh | bash`
- Authenticated: `tpc auth whoami`
- Active org set: `tpc org list` → `tpc org switch <org-slug>`

## Trigger keywords

Set up / create / run a benchmark · "X vs Y" · head-to-head · versus page · compare vendors/providers/competitors · "prove we're better at" · "which vendor should agents pick" · vendor leaderboard.

If the user wants to compare *models* on one product (not vendors), or measure their own product's usability, stop and route to the setup-experiment skill instead. If the user wants a ground-truth dataset benchmark (R@k / MRR over query sets with known answers, no agent in the loop), say that shape is not yet supported and offer the workflow-shape alternative: agents attempting real jobs through each vendor.

## Core concepts

- **Benchmark family** — one TPC product hosts the whole comparison. One **sibling experiment per vendor arm**. Never put two vendors in one experiment: experiments run the full task × environment cross-product, so mixed arms create runs where a task meets the wrong vendor's environment — guaranteed-failure runs at real cost. The platform has no arm primitive; sibling experiments joined by shared task keys are the workaround.
- **Arm** — environment + task set for one vendor. The arm's environment holds ONLY that vendor's API key: vendor adherence enforced structurally, not just judged. Identical agent stack (harness, model, sandbox resources) across arms, always.
- **Task key** — a stable slug (`latest_funding_lookup`) shared across arms; each arm gets its own branded task (`Exa - Latest Funding Lookup`). The key is how analysis joins arms into one table.
- **Gates vs weighted criteria** — three gates on every task (artifact produced, mandated vendor used, no fabricated citations), phrased as strict yes/no decisions; failing any gate fails the task and zeroes it in aggregates. Weighted leveled criteria carry quality (source dating, recency). Full templates: [criteria-and-gates.md](workflows/criteria-and-gates.md).
- **Snapshot** — one iteration's complete, dated, immutable result set. The comparison table is a view over it. Snapshots are never edited; a new run is a new snapshot.
- **k** — runs per task per arm. k=1 = directional pilot (output auto-labeled as such). k=3 same-day = minimum for a publishable claim, with error bars and no winner declared inside the noise.

## Schemas

### Benchmark brief (the skill's input object; a human writes it today, model council can emit it later)

```yaml
brief:
  primary_vendor: exa              # whose story is this benchmark for (may be none = neutral)
  comparison_vendors: [tavily]
  dimension: finance-research data freshness   # what the tasks are designed to separate
  persona: finance analyst                     # whose jobs the tasks mimic
  provenance: tpc_authored         # tpc_authored | vendor_repo (repo URL + commit SHA, pinned)
  target_metric: null              # optional: the council cluster/metric this should move
  k: 1                             # 1 = pilot, 3 = publishable
  model_panel: pilot               # pilot | frontier | open_source | custom (see Stack panels)
```

### Task schema

Same as setup-experiment's `task.json` (name, description, category, prompt, taskType `cli_execution`, timeLimitMs, goals[]) with benchmark rules layered on:

- `prompt` opens with the **vendor mandate preamble** and ends with the **sourcing suffix** — templates in [writing-benchmark-tasks.md](workflows/writing-benchmark-tasks.md).
- `goals` = 3 gates (binary, threshold 100, yes/no phrasing) + 1–2 weighted leveled criteria (threshold 60–70, weighted_average). Verbatim templates in [criteria-and-gates.md](workflows/criteria-and-gates.md).
- Do NOT include `product` — the CLI injects the active product.

### Stack panels (model selection is a user choice — presets by user intuition, resolved at runtime)

The unit is a harness+model **stack**, never a bare model — harness behavior matters as much
as the model. Offer four presets; NEVER present a hardcoded lineup as "frontier" without
resolving it first (see resolution procedure below):

| Preset | Meaning (slots, not fixed IDs) | Recommend when |
|---|---|---|
| `frontier` | The latest top model per major lab the platform supports, each on its native harness (e.g. latest Claude Opus on claude, latest GPT on codex, leading OSS flagship on opencode) | Publishable runs — strongest, most citable panel |
| `balanced` | Strong mid-tier stacks: high quality at moderate cost (e.g. latest Claude Sonnet-class + one comparable peer) | Most runs — the sensible default when unsure |
| `cheapest` | One minimum-viable capable stack | k=1 pilots and battery shakeouts — you're testing the tasks, not publishing |
| `custom` | User names count + harness/model pairs | Anything else |

**Resolution procedure (run before presenting the presets, so the names shown are current):**

1. Scan for known-good, currently-accepted IDs: `tpc sim env list --format json` across this and
   recent products — models in working environments are proven supported.
2. Check for a newer generation than the scan shows (e.g. an Opus 5 released after the envs were
   made): consult current model knowledge / a quick web check of the labs' latest IDs.
3. A candidate ID newer than any known-good env is *unverified*: say so in the ask ("Opus 5 —
   verifying platform support"), and validate it by creating the environment — creation errors
   are the validation; fall back to the newest known-good ID of that lab and tell the user.
4. Present each preset with its resolved, named stacks and the cost multiplier.

Dated fallback lineup (update whenever drift is observed; last verified 2026-08-21):
frontier ≈ claude/claude-opus-5 (verify) · codex/gpt-5.5 (known-good) · opencode/kimi-k2p6
(known-good); balanced ≈ claude/claude-sonnet-4-6 (known-good) + codex/gpt-5.5;
cheapest ≈ claude/claude-sonnet-4-6.

Cost scales linearly: runs = tasks × arms × stacks × k — show the multiplication live when the
user changes panels. Implementation: a panel = multiple environments per arm experiment (same
vendor key on each env of that arm); the task × env cross-product within the arm is the panel.
Reporting: vendor comparisons stay within-stack; the headline metric a panel buys is
**cross-model consistency** ("vendor X wins this task on 3/3 stacks").

### Agent config (environment)

```json
{"harness": "claude", "model": "claude-sonnet-4-6", "sandboxResources": {"cpu": 2, "memory": 4, "disk": 10}}
```

**Version drift warning:** field acceptance varies by CLI version — e.g. CLI 0.1.43 rejects a `provider` key that older docs list as required. On any `Unknown agentConfig fields` error, drop the named field and retry. When unsure of accepted model IDs, copy the exact `agentConfig` from a known-good environment (`tpc sim env list --format json` in any product).

### Response-shape gotchas (parse defensively, all verified on CLI 0.1.43)

- `sim env create --format json` → id field is `environmentId`, not `id`
- `sim task create --format json` → sometimes `{id: …}`, sometimes `{task: {id: …}}` — check both
- `sim run get` goal entries → name field is `goalName`; judge reasoning is in `details`
- experiment results (`sim experiment results`) may return null `summary` until iteration status leaves `generating_results` — read run-level data via `sim run get` instead of waiting

## Platform constraints that shape benchmarks

- **The LLM judge cannot browse.** Every goal must be checkable from run artifacts and logs alone (dates printed in the artifact, API calls visible in the transcript). Truth-against-the-live-world checks (run-day answer keys) happen in the offline analysis layer, never in platform goals.
- Fresh sandbox per run, one-shot prompt, no browser, 60-min ceiling, artifacts must be written to files — all setup-experiment constraints apply. Prompt agents to finish and write an artifact; score the artifact.
- Secrets are environment-scoped (`tpc sim env secret set <env-id> --name KEY --from-env VAR`) — never echo values.
- `script_judge` needs an org feature flag; default to `llm_judge` with the yes/no gate phrasing.

## Workflows

- **[Guided Benchmark](workflows/guided-benchmark.md)** — the main flow: brief → competitors → plan approval → arms & preflight → create → run → analyze → publish handoff. Start here for a NEW benchmark.
- **Report on an existing benchmark** — when the user asks to analyze, report on, or publish a benchmark that already ran ("build the report", "show me the results", "make the versus page"), skip setup entirely: load the family's state files and snapshot (or rebuild the snapshot from run data per Guided Benchmark Step 8), then run `report/generate_report.py <snapshot.json> <out.html>` — the standard report generator (hero cards, leaderboard, per-task heatmap, criteria cut, cost/speed, receipts, methodology, auto-summary; a stack cut appears automatically for multi-stack panels). Same input, same report, every time. This is the analyze-experiment analog for benchmarks; it may graduate into its own skill (`benchmark-report`) once report-only invocations are common — the snapshot JSON is the interface either way, so the split costs nothing later.
- **[Writing Benchmark Tasks](workflows/writing-benchmark-tasks.md)** — task-generation tactics: dimension-first design, trap tasks, category playbooks, the mandate preamble.
- **[Criteria & Gates](workflows/criteria-and-gates.md)** — verbatim gate/criteria templates, aggregation doctrine, snapshot JSON schema, offline checks.

## General principles

- **Handhold.** Assume the user may not know what to benchmark. Pull what the platform knows (product analysis, competitors, council data) before asking anything. Numbered choices at every fork. Never block — web-search or default, then confirm.
- **Echo the resolved org + product and get confirmation before creating anything.** Similarly-named orgs exist; the CLI has no product delete; mistakes persist.
- **Confirm before money.** The plan (tasks + criteria + arms + models + k + cost estimate) is approved explicitly before any resource is created, and the run is confirmed explicitly with its cost shown.
- **Tasks and rubrics are the user's to inspect and edit.** The plan shows one-line summaries, but the FULL task prompts and FULL goal texts (gates and weighted criteria, verbatim) are always available on request and offered before creation ("want the full text of any task or rubric before I create these?"). Support a per-task edit loop: show → user rewords/drops/adds → re-show → approve. Nothing is created until the user has had the chance to read the exact words the agent and the judge will see.
- **Preflight every arm** before firing: key present, key works (one cheap authenticated call), quota covers tasks × k. A dead arm discovered mid-run wastes the whole iteration.
- **Same day, same stack.** All arms' iterations fire within the same day on identical agent configs. The model is not the variable; the vendor is.
- **Honest instrument.** Arm-level failures void the arm (never reported as vendor results). k=1 outputs carry a pilot label automatically. No winner inside the error margin. The competitor-wins section ships on everything published.
- **State files first.** Write `<slug>-benchmark-state.yaml` before creating resources and update `<slug>-creation-state.yaml` after every create, so partial runs resume. Record CLI friction as sanitized bullets in `/tmp/tpc-cli-friction/<slug>.md`, never in the user's project unless asked.
- **Every engagement leaves a snapshot JSON** (schema in criteria-and-gates.md) — it is the interface to the publish template and the trace corpus.
- **Report cuts registry** (generator: report/generate_report.py): hero cards · leaderboard · score bars · per-task heatmap · h2h wins · criteria cut · cost+speed · efficiency cut (tool calls, turns, tokens) · **total cost per completed task** (agent cost + vendor bill, conditioned on success — the canonical economics headline) · agent-readiness checklist (static, separate) · receipts · methodology · auto-summary · [k>1] consistency/flake · [multi-stack] cross-model consistency. Saturation rule: near-identical scores across arms → lead with efficiency/cost cuts and say capability is at ceiling.
