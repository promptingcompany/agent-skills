---
name: generate-pdf
description: >
  Optionally render the analysis as a client-ready, branded PDF in the TPC
  pilot-report layout. Runs after (and only from) a completed markdown report.

  Trigger when users say: "generate a pdf", "pdf report", "client-ready report",
  "make it look like the pilot report", or point at a previous TPC pilot PDF and
  ask for "a report with similar structure".
---

# Generate PDF Report — Workflow

## Overview

Restyle a finished analysis into the TPC pilot-report PDF: cover page, executive
summary, numbered sections with serif headings, stat cards, evidence tables,
callouts, pull quotes, and appendices. The output is a hand-paginated HTML file
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

| Markdown report section | PDF page(s) |
|---|---|
| Header + verdict | Cover (title, italic research question, abstract) + Executive summary |
| Experiment design, judge, n/ceiling caveats | 1 · Methodology (with the "HOW WE MEASURED" box) |
| Per-task results + arm comparison | 2 · Results (stat cards + tables) |
| The failure analysis / friction clusters | 3..k · Finding A, B, C — one page per finding, strongest first |
| Agent-readiness gaps | N · Agent-readiness gaps & CAO levers |
| Closing | N · Conclusion & next steps (with closing pull quote) |
| Run-level detail | Appendix A — run inventory table |
| Structured cluster block | Appendix B — cluster seed YAML in a codeblock |
| Caveats / instrument gaps / sources | Appendix C — method & environment notes |

Writing rules that differ from the markdown report:

- **Headlines are verdicts**, not categories: "Docs attachment bought tokens, not
  compile success", never "Token analysis".
- **One pull quote per finding at most** — the single italic sentence that
  carries it.
- **Caveats don't get cut.** The n / ceiling / instrument-gap content moves into
  "A note on sample and claims" (Methodology) and Appendix C, but it all ships.
- If a prior pilot PDF exists for this customer, open with the continuity beat
  (what that report recommended → what this iteration shows) when the data
  actually supports it.

## Step 2 — Fill the template

Copy `assets/pdf-report-template.html` next to the markdown report (e.g.
`<experiment>-iter<N>-report-pdf.html`) and replace every `{{PLACEHOLDER}}`,
duplicating/deleting skeleton pages as needed. Layout constraints the template
enforces — respect them:

- Each `.page` div is one fixed letter page; **there is no auto-flow**. Budget
  content per page; a 20-row table fits one page at `font-size: 8.2pt`.
- Cover has no footer. Every other page: the `.footer` div, numbered
  sequentially from **2**. Number footers as the *last* step, after page count
  is final.
- Keep codeblock lines under ~95 characters (shorten YAML `root_cause` lines
  rather than letting them wrap mid-word).
- Dense pages that routinely overflow: friction-events table, appendices.
  Split appendices onto separate pages rather than stacking two on one.

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

1. No content overlapping or running past the footer rule (the common failure).
   Fixes, in order: trim a paragraph, fold prose into a table caption, shrink
   that table's `font-size` inline, split the page in two.
2. Footers present on all pages except the cover; numbers sequential; the
   running title matches the report.
3. Tables: no wrapped monospace ids, no orphaned header rows.
4. Spot-check 3–5 numbers against the data dump (pass counts, costs, the
   headline stat). The restyle must not have drifted from the data.

Re-render after every fix. Iterate until clean — two or three passes is normal.

## Deliver

> "PDF: `<file>` (N pages, TPC pilot-report layout). Source HTML alongside it —
> edit and re-render with the same Chrome command."
