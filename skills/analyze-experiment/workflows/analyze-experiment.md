---
name: analyze-experiment
description: Full step-by-step procedure to turn a completed experiment iteration into a portable data dump and an honest, evidence-backed markdown report. Trigger when users say "analyze my experiment", "write the report", "experiment report", "analyze the results", or "report gen".
---

# Analyze Experiment — Workflow

## Overview

Produce two artifacts from one completed iteration:

- **`<experiment>-iter<N>-data.json|md`** — portable, self-contained data dump.
- **`<experiment>-iter<N>-report.md`** — the honest analysis report.

Pull everything from the `tpc` CLI. Fabricate nothing. Lead with the audience's question. Surface friction even when runs pass.

## Prerequisites

- `tpc --version` and `tpc auth whoami` succeed.
- Active product set (`tpc product current`).
- Target iteration is `completed` or `generating_results`.

---

## Step 1 — Locate the experiment and iteration

```
tpc sim experiment list
```

Ask which experiment if not given. Then confirm the iteration (default: latest):

```
tpc sim experiment get <experiment-id> --format json
```

Confirm with the user:

> "Analyzing **[experiment name]**, iteration **[N]** — [X] tasks × [Y] arms = [X·Y] runs. Right one?"

---

## Step 2 — Pull everything and write the data dump

Pull the full picture as JSON:

```
tpc sim experiment results <experiment-id> --iteration <N> --format json
tpc sim experiment signals <experiment-id> --iteration <N> --format json
tpc sim run list --format json
```

For each run that matters (every run, or at minimum every failed/high-friction run), pull the drill-down:

```
tpc sim run get <run-id> --format json
tpc sim run logs <run-id>
```

For each error category in the results, pull full log content:

```
tpc sim experiment results <experiment-id> --error-category "<category>"
```

Assemble one **self-contained** file containing, per run: task spec, environment/arm, pass/fail per criterion, score, tokens, cost, duration, the error entries (category + summary + logIndex + logContent), and a transcript/output excerpt. This is the portable artifact — it must stand alone if handed to another LLM.

> "Data dump written to `<file>`. Drafting the report now."

---

## Step 3 — Detect the mode (it changes the report's lead)

- **A/B comparison** — two arms differ on one dimension (model, harness, docs on/off, skill version). **Lead with the delta**: which arm did better, by how much, and where they diverge.
- **Benchmark** — a single arm (or a model lineup) run across a task list to map where friction is. **Lead with the friction profile**: the ranked root-cause clusters across the suite.

Same data model, different primary axis. Pick the lead accordingly; the rest of the sections are shared.

---

## Step 4 — Per-task results

For every task × arm, a row:

- **Result** — pass/fail, score, and pass/fail **per criterion/goal** (not just overall).
- **What the agent did** — one line, from the transcript/actions.
- **Where it tripped** — the specific friction point, with a verbatim log line and its run + logIndex.

Render as a compact table the audience can scan. Counts only — no adjectives without a number behind them.

---

## Step 5 — Friction clusters (the core of the report)

This is where the value is. Build root-cause clusters from the error taxonomy + log content pulled in Step 2.

1. **Start from the mechanism-level error taxonomy** (the `Errors` block) and its full log content.
2. **Group into root-cause clusters** — what about the product caused each. Emergent by default; if a frozen taxonomy file was supplied via `--taxonomy`, map into it and route misses to `other`.
3. **Count by runs-affected**, deduping repeats/retries of the same root cause within a single run. Rank clusters by runs-affected (then by severity).
4. For each cluster, write a numbered finding:
   - **Root cause** — one line, actionable ("Databricks CLI not on PATH after bootstrap").
   - **Frequency** — "N of M runs" (+ which arms).
   - **Evidence** — one verbatim log/transcript line with run id + logIndex.
   - **Fix** — the lever that would remove it (docs, llms.txt, MCP surface, harness/template change, task-design fix).

Demote raw event counts to a parenthetical; never let a retry-inflated count headline a finding.

---

## Step 6 — Arm / model comparison

A short matrix: arms × {passed, avg score, friction events (runs-affected), avg cost, avg duration, tokens}. Then 2–4 sentences on **where the arms diverge** and what that implies — each sentence backed by a count or an example. In A/B mode this is the headline; in benchmark mode it's supporting.

---

## Step 7 — Closing + structured cluster block

**Closing (prose):** a short section on what the results suggest about agent-readiness gaps — the recurring root causes that the product's levers (docs, llms.txt, MCP, CLAUDE.md, templates, error messages) would address. Tie each gap to the cluster(s) that evidence it. No roadmap padding; only what the data supports.

**Structured cluster block (for taxonomy seeding):** at the very end, emit the clusters as a machine-readable list so the names accumulate toward a frozen taxonomy:

```yaml
# friction-clusters — iteration <N>  (seed data; not yet frozen)
clusters:
  - id: <slug>            # emergent slug
    root_cause: <one line>
    runs_affected: <int>
    arms: [<arm>, ...]
    evidence: { run: <run-id>, logIndex: <int> }
    mechanism_categories: [<error-taxonomy names that fed this>]
  - ...
unmapped_other: <int>     # events that fit no cluster
```

This block is how emergent clustering converges to a comparable taxonomy over iterations — review recurring slugs and promote them append-only into a frozen `--taxonomy` file when it's time.

---

## Step 8 — Honesty pass (do not skip)

Before delivering, add a **Caveats** section:

- **n and ceiling effects** — state run counts; flag when small-n passes can't support "the product works".
- **Instrument gaps** — any signal that failed to extract, any harness that emitted zero actions, any incomplete logging. Name it and state what you used instead (e.g. "custom friction signal did not extract on the codex arm — the judge received only the prompt; friction below is sourced from the platform error taxonomy and run logs").
- **What this analysis can and cannot conclude.**

Then re-read the whole report against the honesty rules: every quantitative claim cites a count, every qualitative claim has an example, no hedging, no filler, length follows evidence.

---

## Deliver

> "Report: `<file>`. Data dump: `<file>`.
> Headline: [one sentence — the verdict and the tension].
> Top friction: [cluster 1], [cluster 2], [cluster 3] (by runs-affected).
> Open the data dump in the CLI to drill further: `tpc sim run logs <run-id>`."

If the user wants a client-ready deliverable (or asks for "a PDF like the previous pilot report"), continue with [`generate-pdf.md`](generate-pdf.md) — it restyles this report into the branded TPC pilot-report PDF without adding any claims.
