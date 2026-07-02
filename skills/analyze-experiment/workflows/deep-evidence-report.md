---
name: deep-evidence-report
description: >
  Optional no-fluff analysis workflow for a completed experiment iteration.
  Produces a recommendation-led markdown report with compact methodology,
  prioritized evidence-backed actions, agent instructions, and a separate
  evidence appendix. Use when users ask for a deeper report, stronger action
  items, exact evidence links, or a primary-product-focused comparison.
---

# Deep Evidence Report

Use this workflow when the user wants a deeper, evidence-backed report rather
than the default compact experiment analysis. It is a markdown-report workflow,
not a PDF-template workflow. Do not change the existing PDF generator or
`assets/pdf-report-template.html` to satisfy this workflow unless the user
explicitly asks to redesign PDF generation.

## Output shape

Produce the same portable data dump as [`analyze-experiment.md`](analyze-experiment.md),
then write a markdown report in this order:

1. Executive Summary + **Recommended actions, in priority order**
2. Urgent recommendation detail pages
3. P1/P2 Recommended Changes
4. Evidence Appendix

If the user names a focal product, keep the report centered on that product.
Use comparator products or arms to explain what the focal product is missing,
what it can copy, and what it does uniquely well. Do not give every comparator
equal narrative weight unless the user asks for a balanced market report.

## Step 1 — Build the evidence spine first

Pull the same data as the base workflow:

```bash
tpc sim experiment results <experiment-id> --iteration <N> --format json
tpc sim experiment signals <experiment-id> --iteration <N> --format json
tpc sim run list --format json
tpc sim run get <run-id> --format json
tpc sim run logs <run-id>
tpc sim experiment results <experiment-id> --error-category "<category>"
```

Before writing recommendations, create a working evidence spine:

- Task x arm/provider results: pass/fail, score, per-goal pass/fail.
- Arm/provider matrix: passed runs, average score, cost, duration, tokens, and
  runs affected by friction.
- Root-cause friction clusters: count by runs affected, dedupe repeated retries
  within one run, keep one transcript/log receipt per cluster.
- Comparator evidence: what another product/arm did that benefited agent
  experience, and what the focal product did uniquely well.
- Caveats: n, ceiling effects, signal failures, missing logs/actions, and what
  the analysis can/cannot conclude.

Demote raw event counts to a parenthetical; never let a retry-inflated count
headline a finding.

## Step 2 — First page: decision surface

Do not add a cover-style page or setup detail. The first page must contain:

- **Methodology** — one compact paragraph stating design, n, focal product,
  comparator products/arms, and evidence sources.
- **Findings** — 4-6 bullets with counts and/or receipt links.
- **Recommended actions, in priority order** — a compact action list.

The findings bullets should cover:

- Overall result and scope.
- The focal product's main friction pattern.
- Comparator lessons: what other products/arms did that improved agent
  experience.
- Focal product strengths worth preserving.
- Highest-leverage implication for the next rerun or product change.

The first-page action list must include owner/persona, exact surface, concrete
change, and evidence links. Keep detailed agent instructions off the first page.

## Step 3 — Urgent recommendation detail pages

After the first-page brief, write one detail section per urgent recommendation.
Use numbered sections in descending priority, not a wide table.

Each urgent detail section must include:

- **Title** — imperative and specific to the product gap.
- **Owner** — team or persona.
- **Where to change** — specific docs page, CLI command, API surface, MCP tool,
  template, product surface, or onboarding step.
- **Agent instruction** — compact implementation task.
- **Evidence** — run/task/log receipts or counted comparator evidence.
- **Success check** — observable rerun condition or product behavior.

Use this agent-instruction pattern:

```markdown
> **Agent instruction:** Context: <what product/docs/API change needs to be made and why it matters for agent usability>. Reproduce: <one short sentence with the task, command, endpoint, or workflow that shows the issue>. Implement: <exact surface and concrete change>. Evidence: <receipt ids or appendix links>.

Required changes:

- <Specific required change or doc/API/CLI behavior.>
- <Specific required example, endpoint, state, command, or fallback.>
- <Specific edge case, error meaning, or validation path.>
```

Rules:

- Select only urgent, highest-leverage changes for this section.
- Keep agent instructions compact: `Context`, `Reproduce`, `Implement`, and
  `Evidence` in 2-4 sentences total.
- Avoid vague phrases like "improve", "clarify", "lead with", "make easier",
  or "document X" unless the sentence also says where to change it and what to
  add.
- If the root cause could be product behavior or documentation, name both
  possible fix surfaces and state how to decide between them.
- Every recommendation must cite at least one run/task/evidence cluster or a
  counted comparator pattern.

## Step 4 — P1/P2 recommended changes

After urgent details, add a follow-up table or numbered list:

| Priority / owner | Where to change | Recommended change | Evidence and success check |
|---|---|---|---|
| P1 - <team/persona> | <specific surface> | <change> | <evidence plus success check> |

Keep P1/P2 items specific and evidence-backed. Do not add roadmap filler.

## Step 5 — Evidence Appendix

Start the appendix as its own section:

```markdown
## Evidence Appendix
```

Include:

- **E1. Provider scorecard and task matrix** — task x arm/provider results,
  criteria, and headline counts.
- **E2/E3. Comparator evidence** — what comparators did that benefited the
  agent, and what the focal product did uniquely well.
- **E4/E5. Strengths and friction clusters** — ranked root causes with
  runs-affected counts, mechanism categories, and verbatim examples.
- **E6. Caveats** — n, ceiling effects, signal failures, missing logs/actions,
  and what the analysis can/cannot conclude.
- **E7. Taxonomy seed** — the structured cluster block below.

Emit clusters as machine-readable seed data:

```yaml
# friction-clusters — iteration <N>  (seed data; not yet frozen)
clusters:
  - id: <slug>
    root_cause: <one line>
    runs_affected: <int>
    arms: [<arm>, ...]
    evidence: { run: <run-id>, logIndex: <int> }
    mechanism_categories: [<error-taxonomy names that fed this>]
  - ...
unmapped_other: <int>
```

## Step 6 — Honesty pass

Before delivering, re-read the report against these checks:

- Every quantitative claim cites a count.
- Every qualitative claim has a transcript/log example.
- Every recommendation is evidence-backed.
- Caveats are explicit, especially small n and signal/logging gaps.
- The first page is a decision surface, not a methodology dump.
- The PDF generator was not modified as part of this workflow.
