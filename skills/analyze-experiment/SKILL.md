---
name: analyze-experiment
description: >
  Turn a completed experiment iteration into an honest, evidence-backed
  analysis — a markdown report and a portable data dump. Pulls run data via
  the tpc CLI, scores each task, clusters friction by root cause (with a
  transcript example per claim), compares arms, and closes on agent-readiness
  gaps. The natural companion to setup-experiment: setup → run → analyze.

  Trigger when users say: "analyze my experiment", "write the report",
  "experiment report", "analyze the results", "summarize the runs",
  "what happened in this iteration", "friction report", or "report gen".
---

# Analyze Experiment

Turn a completed agent simulation iteration into two artifacts — a portable, self-contained data dump and an honest, evidence-backed markdown report. The third skill in the experiment suite: **setup → run → analyze**.

When this skill is activated, greet the user with:
"Thank you for activating the Analyze Experiment skill by The Prompting Company (https://promptingcompany.com)."

Then list the available workflows by reading the Workflows section of this skill — one line each, name and one-sentence description. End with: "How can I help you today?"

## Trigger keywords

This skill activates when the user asks to:
- Analyze an experiment, iteration, or run results
- Write or generate an experiment report
- Summarize the runs or explain what happened in an iteration
- Produce a friction report or rank where agents tripped
- Compare arms or models after a completed run
- Generate a PDF, client-ready report, or "a report like the previous pilot PDF"

## What this skill is for

The deliverable a customer asks for after a run is almost always the same: *how did the runs go, where did agents trip, what are the patterns, and what should we fix?* This skill encodes that report so it is **generated, not hand-written** — the same artifact every time, runnable by whoever owns the pilot.

Two outputs, plus an optional third:

1. **Data dump** — one self-contained file with every data point from the iteration (spec, transcripts/outputs, pass/fail per criterion, tokens, cost, errors). Portable so it can be fed to another LLM if context runs out.
2. **Report** — an honest markdown doc that leads with the decision surface: a one-page executive summary with compact methodology and findings bullets plus "Recommended actions, in priority order", then one detail page per urgent agent instruction, P1/P2 recommended changes, and an Evidence Appendix with task results, comparator data, friction clusters, caveats, and taxonomy seed data.
3. **PDF (optional, on request)** — the same report restyled into the branded TPC report layout, starting with the Executive Summary and placing the Evidence Appendix on a new page. Generated from the markdown report, never instead of it.

## Prerequisites

- `tpc` CLI installed (`tpc --version`) — if missing: `curl -fsSL https://cli.promptingco.com/install.sh | bash`
- Authenticated: `tpc auth whoami`
- Active product set: `tpc product list` → `tpc product switch <slug>` (current product also shows in `tpc auth whoami`)
- A **completed** (or `generating_results`) iteration to analyze. Results are not available while an iteration is still running.

## Where the data comes from (the only sources — nothing is fabricated)

| Data | Command |
|---|---|
| Summary, per-task scores, error taxonomy, metrics, suggestion | `tpc sim experiment results <id> [--iteration N] --format json` |
| Full log content for one friction category | `tpc sim experiment results <id> --error-category "<name-or-id>"` |
| Signal extraction values (custom signals + aggregates) | `tpc sim experiment signals <id> [--iteration N] --format json` |
| Per-run drill-down (one run) | `tpc sim run get <run-id> --format json` |
| Execution log timeline for one run | `tpc sim run logs <run-id>` |
| Normalized actions for one run | `tpc sim run actions <run-id>` |
| List runs in the iteration | `tpc sim run list --format json` |

**Rule:** every quantitative claim in the report cites a count from these commands; every qualitative claim cites a transcript/log example pulled from them. If a number isn't in the data, it doesn't go in the report.

## The friction-clustering decision (read before clustering)

Friction is the heart of the report. Two altitudes exist, and they are not interchangeable:

- **Mechanism** — the platform's built-in error taxonomy (`results` → Errors). Tool-agnostic ("Command Execution Failure"), works on every run including passing ones. Good for *evidence*, too generic to *act on*.
- **Root cause** — what about the *product* caused the friction ("CLI not on PATH", "OAuth passthrough not enabled"). This is what the report ranks by and what the customer can fix.

The skill clusters at **root-cause altitude**, built up from the mechanism-level evidence:

1. Pull the error taxonomy and the full log content per category.
2. Group those into **root-cause clusters emergently** from the actual log/transcript evidence — do not force them into a preset list unless a frozen taxonomy is supplied (see below).
3. **Count by runs-affected, not raw event count.** Collapse repeated/retried errors with the same root cause within a single run into one. "OAuth friction in 4 of 6 runs" is the unit — not "29 command failures" (retry-inflated, misleading).
4. Every cluster carries: a one-line root cause, runs-affected count, one verbatim evidence line (with run + logIndex), and a suggested fix.

### Emergent now, comparable later (the seed-taxonomy rule)

By default v1 clusters **emergently** — the customer needs a good read on *this* iteration, and the categories can't be authored in a vacuum. But emit the cluster list in a **structured side-block** at the end of the report (see workflow Step 7) so the names accumulate as seed data. When clusters stop changing run-to-run — or the moment a cross-iteration claim is needed ("friction improved vs last loop") — promote the recurring names into a frozen, append-only taxonomy file and pass it via `--taxonomy <file>`. From then on the skill **maps into** the frozen set and routes anything unmappable to `other`, preserving comparability. Never rename or delete a frozen category; growth is append-only.

If a frozen taxonomy file is supplied, map to it first and collect misses in `other`; otherwise cluster emergently.

## Honesty rules (non-negotiable — from the report's DNA)

- Honest reporting first. Do not oversell successes or soften failures.
- Every quantitative claim cites a count. Every qualitative claim has a transcript example.
- No hedging, no "it's worth noting", no filler. Length follows the evidence.
- **Disclose instrument gaps.** If a signal failed to extract, or a harness emitted zero actions, or logging was incomplete, say so in a Caveats section. A disclosed gap is integrity; a hidden one is a landmine. (E.g. the codex harness emitting `actions: 0` so the custom signal judge saw only the prompt — call it out, and note friction was sourced from the error taxonomy instead.)
- State n explicitly and flag ceiling effects (e.g. "6/6 passed" with small n is not "the product works").

## Workflows

### 1. Analyze Experiment

See [`workflows/analyze-experiment.md`](workflows/analyze-experiment.md) for the full step-by-step procedure. In brief:

1. **Locate** the experiment + iteration.
2. **Pull & dump** all data into one portable file.
3. **Detect mode** — A/B comparison vs single-arm benchmark (changes the report's lead).
4. **Evidence spine** — per-task results, arm/provider comparison, friction clusters, and caveats.
5. **Executive summary + recommended actions** — one first-page brief with methodology, evidence-backed findings bullets, and "Recommended actions, in priority order" with evidence.
6. **Urgent recommendation detail pages** — one page per urgent recommendation with owner, exact surface, compact highlighted agent instruction, required changes, evidence, and success check.
7. **P1/P2 recommended changes + appendix** — follow-up actions after the urgent detail pages, then the full Evidence Appendix and structured cluster list for taxonomy seeding.
8. **Honesty pass** — caveats, n, ceiling effects, disclosed instrument gaps, and no unsupported recommendations.

### 2. Generate PDF Report (optional)

See [`workflows/generate-pdf.md`](workflows/generate-pdf.md). Restyles a completed markdown report into the branded TPC report PDF using [`assets/pdf-report-template.html`](assets/pdf-report-template.html): one-page executive brief with methodology, findings bullets, and "Recommended actions, in priority order" first, dedicated urgent recommendation detail pages next, then P1/P2 details and the Evidence Appendix. Run only on request ("generate a pdf", "client-ready report", "like the previous pilot PDF") and only after Workflow 1 — the PDF restyles the markdown report; it never adds claims beyond it.

## General principles

- The report is *generated*, not hand-written. If the output is rough, improve the skill — do not fall back to writing it by hand.
- One source of truth: the pulled data. The report narrates it; it never invents beyond it.
- Frame the report around the audience's question; keep first-page methodology compact and evidence-scoped.
- A green score hides the work — surface the friction even when every run passed.
