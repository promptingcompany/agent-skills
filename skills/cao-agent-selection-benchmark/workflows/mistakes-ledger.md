---
name: mistakes-ledger
description: Merged mistakes ledger from four studies: design, platform, capture, parser, analysis, quotes, report, send
triggers: what went wrong before, checklist
---

# Mistakes ledger — four studies, one table

Read once before the first study and again whenever a result looks clean. Every row cost real time or
nearly shipped a wrong number.

| Where | Mistake | Cost | Rule now |
|---|---|---|---|
| Design | one synthetic job repeated with one sentence changed (v2 ladder) | narrow report, few competitors surfaced | real jobs from the vendor's pages + one twin pair |
| Design | no placeholder-credentials line | DIY inflated | line on every build prompt |
| Design | fictional domain in a gate | Sol `dig` → NXDOMAIN → refusal | "assume the domain is ours to edit" |
| Design | H2H asserted a capability | premise stale by run time | H2H asks |
| Design | vendor name in an unbranded prompt | lane invalid | leak gate in `gen_tasks.py` |
| Design | shelf with one anchor | menu effect not isolable | symmetric anchors or state the limit |
| Design | gate not truly un-fakeable | catch-all met "an inbox per agent" 6/6 | pre-register the DIY route; it may be the finding |
| Platform | experiment ran full cross product | 104 junk runs | one experiment per lane family |
| Platform | batch env↔task attach | stall | one task per attach |
| Platform | `org switch` silent no-op | tasks in wrong org (nearly) | `whoami` before creating |
| Platform | waited on iteration status | would never fire | wait on run status |
| Platform | polled 3 loops at once | empty API bodies; a false "all terminal" | ≤1 poll / 45 s; retry, never treat empty as zero |
| Platform | `tpc` returned no JSON under load | script crash | `tpc_json` retries with backoff |
| Capture | Opus subagent session captured | 2/36 runs invalid | first-user-message check |
| Parser | Codex `apply_patch` unparsed | 37/120 runs read as zero code | `channels()` handles it; never remove |
| Parser | bare vendor words | phantom wires (stdlib class, schema name, own CLI, README) | anchor CODE regexes to product surfaces |
| Parser | one regex set for code and prose | recall 6/6 read as 2/6 | `VENDOR` vs `PROSE_VENDOR` |
| Parser | comments scanned | 3 phantom vendors | strip whole-line comments |
| Parser | diff-in-heredoc unsplit | README counted as wired | split unified diffs |
| Parser | research from tool events only | Codex search invisible | citation markers |
| Analysis | trusted analyst counts | "13/13/13 files" that were 6 | hand grep is truth |
| Analysis | pooled probe cells into rates | inflated pick rate | branded lanes labeled, never pooled |
| Analysis | counted first-party wiring as origination | inverted a finding | first-party scored separately |
| Analysis | counted retained incumbent as a win | flattered the client | retained ≠ selected |
| Analysis | summed per-experiment counts | +75 runs (shared ids) | de-dup by run id |
| Quotes | analyst-supplied quote not in corpus; stitched fragments | fabrication nearly published | contiguous match, from source |
| Quotes | writer swapped dash/quote/period while tightening | 5 verified quotes failed | verify after every edit |
| Report | numbers written one parser state earlier | 6 stale figures | recompute after any regex change |
| Report | reused template text from another study | foreign numbers in client drafts | re-derive every figure per study |
| Report | text-only verification of PDF | "196 sealed runs" on a cover | contact sheet, every page |
| Report | heading at page foot | found by eye | stranded-heading rule in `check_report.py` |
| Report | `.q` CSS renamed by a "no-op" replace | quotes rendered 16px | never write a replace you think is a no-op |
| Send | client-facing number never reconciled with internal | 2/25 vs 78 pieces | one number set, three documents |
| Voice | thesis titles, em-dash flourishes | "turgid LLM goobedidook" | factual titles; `avoid-ai-writing` |
