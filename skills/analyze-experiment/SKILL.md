---
name: analyze-experiment
description: >
  Turn a completed experiment iteration into an honest, evidence-backed
  analysis — a portable data dump, a markdown report, and a branded client-ready
  PDF. Pulls run data via the tpc CLI, scores each task, clusters friction by
  root cause (with a transcript example per claim), compares arms, and closes on
  agent-readiness gaps. Optionally produces a deeper no-fluff evidence report
  with prioritized actions and agent instructions. The natural companion to
  setup-experiment: setup → run → analyze.

  Trigger when users say: "analyze my experiment", "write the report",
  "experiment report", "analyze the results", "summarize the runs",
  "what happened in this iteration", "friction report", "report gen",
  "evidence-backed report", "no-fluff report", or "deep report".
---

# Analyze Experiment

Turn a completed agent simulation iteration into three artifacts — a portable, self-contained data dump, an honest, evidence-backed markdown report, and a branded client-ready PDF. The third skill in the experiment suite: **setup → run → analyze**.

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
- Produce a deeper evidence-backed, no-fluff report with prioritized actions
- Generate a PDF, client-ready report, or "a report like the previous pilot PDF"

## What this skill is for

The deliverable a customer asks for after a run is almost always the same: *how did the runs go, where did agents trip, what are the patterns, and what should we fix?* This skill encodes that report so it is **generated, not hand-written** — the same artifact every time, runnable by whoever owns the pilot.

Outputs:

1. **Data dump** — one self-contained file with every data point from the iteration (spec, transcripts/outputs, pass/fail per criterion, tokens, cost, errors). Portable so it can be fed to another LLM if context runs out. **Always produced** — it is the internal source of truth for every other artifact.
2. **Report** — an honest analysis: per-task results, friction clusters grouped by root cause, model/arm differences, and a short closing on agent-readiness gaps. Delivered in the format(s) the user picks (see "Before analyzing" below):
   - **`md`** — the markdown report. Always generated internally as the source of truth; delivered as a file when selected.
   - **`pdf`** — the markdown report restyled into the branded TPC pilot-report layout (cover, executive summary, numbered findings, appendices) for customer delivery. Rendered from the branded HTML; always derived from the markdown report, never instead of it.
   - **`html`** — the branded, self-contained HTML report (the filled pilot-report template the PDF renders from), delivered standalone.

## Before analyzing — ask two questions first

Do **not** start the analyze workflow until you have asked the user, up front, both of these (present as checkboxes / multi-select where the surface supports it):

1. **Which output format(s) do you want?** — `md`, `pdf`, `html`. Multiple allowed; at least one required. The data dump is produced regardless.
2. **Do you want a setup analysis?** — yes/no. If yes, produce it as described below.

Produce only the report formats the user selected. The markdown report is still generated internally when `pdf` or `html` is chosen (both derive from it), but only deliver the file formats that were picked.

## Setup analysis (optional — chat-only, never in an artifact)

When the user asks for a setup analysis, deliver it **in the chat only**. It must **not** appear in the PDF, the markdown report, or the HTML — those artifacts stay client-facing and evidence-only. The setup analysis is an internal read for the team running the pilot.

It has exactly three parts:

1. **Verdict with a lean** — "Ready for Rerun" or "Revise Setup", plus how far it leans each way as a percentage split (e.g. "30% Ready for Rerun / 70% Revise Setup"). The two numbers sum to 100.
2. **Short summary** — a few sentences on *why* the verdict landed where it did, grounded in the run data and instrument gaps (not vibes).
3. **Improvement list — two separate lists**, both scoped to *our* side, never the user's:
   - **Setup changes** — things we can change in the experiment setup or by checking the documentation: task prompts, goals, inits, environments, signal extraction. These are the levers the team owns and can adjust before the next run.
   - **Platform fixes** — things the *developer* should adjust in the product itself to meet the fix (a product gap the iteration exposed, not something reconfigurable via setup).

   Do not include recommendations aimed at the end user; every item is a setup change we make or a product fix the developer makes.

Base the verdict on the same evidence the report uses: did the instruments capture what they needed to (signals extracted, actions logged, arms comparable, n adequate), or did gaps/design issues undermine the read? Lean toward **Revise Setup** when instrument gaps or design flaws mean a rerun would repeat the same blind spots; lean toward **Ready for Rerun** when the setup held and the results are trustworthy enough to iterate on directly.

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

See [`workflows/analyze-experiment.md`](workflows/analyze-experiment.md) for the full step-by-step procedure. Produces the data dump plus the report in the format(s) the user picked, and optionally a chat-only setup analysis. In brief:

0. **Ask the two pre-flight questions** — output format(s) and whether to run a setup analysis (see "Before analyzing" above). Do not proceed until answered.
1. **Locate** the experiment + iteration.
2. **Pull & dump** all data into one portable file.
3. **Detect mode** — A/B comparison vs single-arm benchmark (changes the report's lead).
4. **Per-task results** — pass/fail per criterion, what the agent did, where it tripped.
5. **Friction clusters** — root-cause grouped, runs-affected, evidence + fix each.
6. **Arm/model comparison** — where the arms diverge, with counts.
7. **Closing + structured cluster block** — agent-readiness gaps and the levers that address them; emit the structured cluster list for taxonomy seeding.
8. **Honesty pass** — caveats, n, ceiling effects, disclosed instrument gaps.
9. **Render the selected formats** — if `pdf` or `html` was picked, restyle the markdown report into the branded TPC pilot-report layout, following [`workflows/generate-pdf.md`](workflows/generate-pdf.md).
10. **Setup analysis (if requested)** — deliver the chat-only verdict, summary, and improvement list. Never write it into any artifact.

When `pdf` or `html` is selected, the branded artifact is produced from the markdown report (see [`workflows/generate-pdf.md`](workflows/generate-pdf.md)): the branded TPC pilot-report layout (cover page, executive summary, "HOW WE MEASURED" box, stat cards, per-finding pages with pull quotes, appendices) using [`assets/pdf-report-template.html`](assets/pdf-report-template.html) — the `html` deliverable is that filled template, and `pdf` renders it with headless Chrome, verified page by page. It restyles the markdown report; it never adds claims beyond it.

### 2. Deep Evidence Report

See [`workflows/deep-evidence-report.md`](workflows/deep-evidence-report.md) when the user asks for a deeper, evidence-backed, no-fluff report with prioritized actions, exact owner/surface recommendations, and compact agent instructions. This workflow changes the markdown report structure only; it does not modify or replace the existing PDF generator.

## General principles

- The report is *generated*, not hand-written. If the output is rough, improve the skill — do not fall back to writing it by hand.
- One source of truth: the pulled data. The report narrates it; it never invents beyond it.
- Lead with the question the audience is asking, not with the methodology.
- A green score hides the work — surface the friction even when every run passed.
