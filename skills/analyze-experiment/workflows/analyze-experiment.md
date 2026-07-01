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

Default report order:

1. Executive Summary + Recommended actions, in priority order
2. Urgent Recommendation Detail Pages
3. P1/P2 Recommended Changes
4. Evidence Appendix

If the user names a focal product, keep the report centered on that product. Use comparator products or arms to explain what the focal product is missing, what it can copy, and what it does uniquely well; do not give every comparator equal narrative weight unless the user asks for a balanced market report.

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

## Step 4 — Build the evidence spine before writing

Build the evidence first, then write the recommendation-led report from it.

For every task x arm, capture:

- **Result** — pass/fail, score, and pass/fail per criterion/goal.
- **What the agent did** — one line from the transcript/actions.
- **Where it tripped** — the specific friction point, with a verbatim log line and its run + logIndex.

Build root-cause friction clusters from the error taxonomy plus log content:

1. Start from the mechanism-level error taxonomy (`Errors`) and its full log content.
2. Group into product root causes. Emergent by default; if a frozen taxonomy file was supplied via `--taxonomy`, map into it and route misses to `other`.
3. Count by runs-affected, deduping repeats/retries of the same root cause within a single run.
4. For each cluster, retain: root cause, frequency ("N of M runs"), affected arms/providers, one verbatim evidence line with run id + logIndex, and the likely fix lever.

Also build a compact arm/provider matrix: passed, avg score, runs-affected by friction, avg cost, avg duration, and tokens. In A/B mode this is the headline evidence; in benchmark mode it is supporting evidence.

Demote raw event counts to a parenthetical; never let a retry-inflated count headline a finding.

---

## Step 5 — Write the Executive Summary and recommended-actions brief

Do not add a cover-style page or setup detail. Keep the first page as a decision surface.

The first page is the decision surface. It must contain the Executive Summary plus a compact action list titled **"Recommended actions, in priority order"**, and it should not include the detailed agent instructions.

The Executive Summary must contain:

- **Methodology** — one compact paragraph stating experiment design, n, focal product, comparator products/arms, and evidence sources. Do not include operational setup detail.
- **Findings** — 4-6 bullet points. Each bullet must be evidence-backed with counts and/or receipt links.

The findings bullets must carry:

- Overall result and scope.
- The focal product's main friction pattern.
- Comparator lessons: what other products/arms did that improved agent experience.
- Focal product strengths worth preserving.
- The highest-leverage implication for the next rerun or product change.

The first-page recommended actions must contain:

- One line per urgent recommendation in descending priority.
- Owner or persona, exact surface, concrete change, and evidence links.
- No agent-instruction block, required-changes list, long evidence paragraph, or success-check prose.
- Use the audience-facing section title **"Recommended actions, in priority order"** instead of "P0 snapshot" or similar internal severity language.

Keep the combined methodology, findings bullets, and recommended actions tight enough to fit on the first PDF page.

---

## Step 6 — Write one P0 detail page per urgent recommendation

After the first-page brief, start the P0 details on a new page. Each urgent recommendation gets its own detail page. Every detail page must be evidence-backed and specific enough that a product, docs, engineering, marketing, or AI-agent owner knows what to change and where.

Use numbered detail sections in descending priority, not a wide table.

Each P0 detail page must include:

- **Title** — imperative, specific to the product gap.
- **Owner** — team or persona.
- **Where to change** — specific docs page, CLI command, API surface, MCP tool, template, product surface, or onboarding step.
- **Agent instruction** — a compact implementation task with context, reproduction, and exact change direction.
- **Evidence** — run/task/log receipts or counted comparator evidence.
- **Success check** — observable rerun condition or product behavior.

Agent instructions must use this compact highlighted implementation pattern:

```markdown
> **Agent instruction:** Context: <state what product/docs/API change needs to be made and why it matters for agent usability>. Reproduce: <one short sentence with the task, command, endpoint, or workflow that shows the issue>. Implement: <name the exact surface and concrete change>. Evidence: <receipt ids or appendix links>.

Required changes:

- <Specific required change or doc/API/CLI behavior.>
- <Specific required example, endpoint, state, command, or fallback.>
- <Specific edge case, error meaning, or validation path.>
```

Rules:

- Select only urgent, highest-leverage changes for P0. Prefer fixes that remove repeated blockers or close a clear comparator gap.
- Keep detailed agent instructions off the first page; the first page only gets the compact recommended-actions list.
- Force a page break before each P0 detail page in PDF-oriented markdown or HTML.
- "Where to change" must be concrete. Avoid vague surfaces like "docs" or "CLI"; name the page, command family, endpoint, MCP tool, template, env var guide, or onboarding path when the evidence supports it.
- "Agent instruction" must be highlighted as a markdown blockquote and stay compact: `Context`, `Reproduce`, `Implement`, and `Evidence` in 2-4 sentences total.
- `Context` states what needs to change and why it matters for the agent experience.
- `Reproduce` is one short sentence with the task, command, endpoint, or workflow that shows the issue. Do not include secrets or raw credentials.
- `Implement` names the exact surface and concrete change.
- Keep "Required changes" to 2-4 bullets. Each bullet must be specific enough for another coding/docs agent to execute.
- Do not split the P0 into legacy separate prose blocks; use one highlighted agent instruction plus a short required-changes list.
- Do not use vague phrases like "improve", "clarify", "lead with", "make easier", or "document X" unless the sentence also says exactly where to change it and what content/behavior to add.
- When the root cause could be either product behavior or documentation, name both possible fix surfaces and state how to decide between them.
- Every agent instruction must include required implementation content or steps detailed enough for another coding or docs agent to execute.
- The evidence column combines proof and validation. Do not introduce internal gate labels; phrase validation as an observable success check.
- Every row must cite at least one run/task/evidence cluster or a counted comparator pattern.

---

## Step 7 — Write P1/P2 Recommended Changes, then the Evidence Appendix

After the urgent recommendation detail pages, add the follow-up table or numbered list:

| Priority / owner | Where to change | Recommended change | Evidence and success check |
|---|---|---|---|
| P1 - <team/persona> | <specific surface> | <change> | <evidence plus success check> |

Then start `## Evidence Appendix`. In the PDF workflow this section starts on a new page. The appendix should contain the complete support for the recommendation tables:

- **E1. Provider scorecard and task matrix** — task x arm/provider results, criteria, and headline counts.
- **E2/E3. Comparator evidence** — what comparator products/arms did that benefited the agent, and what the focal product did uniquely well.
- **E4/E5. Strengths and friction clusters** — ranked root causes with runs-affected counts, mechanism categories, and verbatim examples.
- **E6. Caveats** — n, ceiling effects, signal failures, missing logs/actions, and what the analysis can/cannot conclude.
- **E7. Taxonomy seed** — the structured cluster block below.

**Structured cluster block (for taxonomy seeding):** emit the clusters as a machine-readable list so the names accumulate toward a frozen taxonomy:

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

This block is how emergent clustering converges to a comparable taxonomy over iterations. Review recurring slugs and promote them append-only into a frozen `--taxonomy` file when it is time.

---

## Step 8 — Honesty pass (do not skip)

Before delivering, make sure the Evidence Appendix includes a **Caveats** section:

- **n and ceiling effects** — state run counts; flag when small-n passes can't support "the product works".
- **Instrument gaps** — any signal that failed to extract, any harness that emitted zero actions, any incomplete logging. Name it and state what you used instead (e.g. "custom friction signal did not extract on the codex arm — the judge received only the prompt; friction below is sourced from the platform error taxonomy and run logs").
- **What this analysis can and cannot conclude.**

Then re-read the whole report against the honesty rules: every quantitative claim cites a count, every qualitative claim has an example, every recommendation is backed by evidence, no hedging, no filler, length follows evidence.

---

## Deliver

> "Report: `<file>`. Data dump: `<file>`.
> Headline: [one sentence — the verdict and the tension].
> Top friction: [cluster 1], [cluster 2], [cluster 3] (by runs-affected).
> Open the data dump in the CLI to drill further: `tpc sim run logs <run-id>`."

If the user wants a client-ready deliverable (or asks for "a PDF like the previous pilot report"), continue with [`generate-pdf.md`](generate-pdf.md) — it restyles this report into the branded TPC report PDF without adding any claims.
