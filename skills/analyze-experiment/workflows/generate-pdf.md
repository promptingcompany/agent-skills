---
name: generate-pdf
description: >
  Optionally render the analysis as a client-ready, branded PDF in the TPC
  report layout. Runs after (and only from) a completed markdown report.

  Trigger when users say: "generate a pdf", "pdf report", "client-ready report",
  "make it look like the pilot report", or point at a previous TPC pilot PDF and
  ask for "a report with similar structure".
---

# Generate PDF Report — Workflow

## Overview

Restyle a finished analysis into the TPC report PDF: a one-page Executive
Summary with methodology and findings bullets plus "Recommended actions, in
priority order" first, one urgent detail page per recommendation next, then
P1/P2 details and an Evidence Appendix. The output is a natural-flow HTML file
rendered with headless Chrome.

**This workflow is optional and content-second.** It consumes the markdown
report produced by `analyze-experiment.md` — it never invents content. If the
markdown report doesn't exist yet, run that workflow first. Every number in the
PDF must match the data dump; the honesty rules apply unchanged.

## Prerequisites

- A completed `<experiment>-iter<N>-report.md` and its data dump.
- Headless Chrome/Chromium:
  - macOS: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
  - Linux: `google-chrome` / `chromium` on PATH
- The template: [`../assets/pdf-report-template.html`](../assets/pdf-report-template.html)

---

## Step 1 — Map the markdown report onto the PDF structure

The PDF is the same report, re-led for a customer audience. Standard mapping:

| Markdown report section | PDF treatment |
|---|---|
| Header + methodology/findings | Report header + Executive Summary on page 1. |
| Recommended actions, in priority order | Compact first-page action list, still on page 1. |
| P0 Detail Pages | One page per P0, each with agent instruction, required changes, evidence, and success check. |
| P1/P2 Recommended Changes | Follow-up detail section after the urgent recommendation detail pages. |
| Per-task results + arm/provider comparison | Evidence Appendix, E1. |
| Comparator evidence | Evidence Appendix, E2/E3. |
| Product strengths + friction clusters | Evidence Appendix, E4/E5. |
| Caveats / instrument gaps / sources | Evidence Appendix, E6. |
| Structured cluster block | Evidence Appendix, E7. |

Writing rules that differ from the markdown report:

- **Headlines are verdicts**, not categories: "Docs attachment bought tokens, not
  compile success", never "Token analysis".
- **The first page is holistic.** It must contain compact Methodology, findings
  bullets, and "Recommended actions, in priority order" only. Do not put
  agent-instruction blocks or long evidence paragraphs on page 1.
- **Recommendation details carry the work.** Each P0 detail page must preserve
  the compact highlighted pattern from the markdown: context, one-line
  reproduction, exact surface, concrete fix, evidence links, short
  required-changes list, and success check. Do not expand a compact callout into
  long prose in the PDF. P1/P2 items must still include owner, exact surface,
  recommended change, evidence, and success check.
- **Caveats do not get cut.** The n / ceiling / instrument-gap content stays in
  the Evidence Appendix.
- If a prior report exists for this customer, add a short continuity sentence in
  the Executive Summary only when the data supports it.

## Step 2 — Fill the template

Copy `assets/pdf-report-template.html` next to the markdown report (e.g.
`<experiment>-iter<N>-report-pdf.html`) and replace every `{{PLACEHOLDER}}`.
Use the template as a natural-flow document:

- Do not add a standalone title page unless the user explicitly asks for one.
- Do not wrap content in page-sized `.page` divs or hide overflow.
- Keep the report order: one-page Executive Summary with methodology/findings +
  recommended actions in priority order, urgent recommendation detail pages,
  P1/P2 Recommended Changes, Evidence Appendix.
- Apply required page breaks before the P0 detail section, before each
  subsequent P0 detail page, and before the Evidence Appendix.
- Keep codeblock lines under roughly 95 characters when possible; long evidence
  lines may wrap, but should not obscure the run id or logIndex.
- Let the PDF page breaks happen naturally after the appendix begins. Do not
  force manual page cuts unless a table or code block becomes unreadable.

## Step 3 — Render

```bash
# macOS
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="<Customer>_<Short_Title>.pdf" \
  "file://$PWD/<experiment>-iter<N>-report-pdf.html"
```

(Linux: same flags with `google-chrome` or `chromium`.)

## Step 4 — Verify page by page (do not skip)

Read the rendered PDF and check **every page**:

1. No content overlapping, clipping, or running into the page margin.
   Fixes, in order: trim a paragraph, fold prose into a table caption, shrink
   that table's `font-size` inline, or let the table continue naturally.
2. The first page starts with the Executive Summary.
3. Page 1 contains compact methodology, findings bullets, and recommended
   actions in priority order, without urgent recommendation agent-instruction
   detail.
4. Each P0 detail starts on its own page before P1/P2 and the Evidence Appendix.
5. The Evidence Appendix begins on a new page.
6. Tables/action lists: no wrapped monospace ids that hide run identity, no orphaned header rows, and no agent instruction collapsed into vague one-line prose.
7. Spot-check 3-5 numbers against the data dump (pass counts, costs, the
   headline stat). The restyle must not have drifted from the data.

Re-render after every fix. Iterate until clean — two or three passes is normal.

## Deliver

> "PDF: `<file>` (N pages, TPC report layout). Source HTML alongside it.
> Evidence Appendix starts on page <n>; spot-checks matched the data dump."
