---
name: pathways
description: What changes for a category study, prospect vs customer, a periodic re-read, or a v2 with seeded repos; what to do when the operator lacks access
triggers: category study, re-read, v2, baseline read
---

# Pathways — what changes when the study is not the default

The default pathway (vendor-tailored, paying customer or prospect) is what SKILL.md walks through.
These are the four variants and exactly what differs.

## 1. Category study (no vendor addressed)

- **Intake**: questions 3–5 (vendor, use-case pages, incumbent) do not apply. Ask instead for the 4–8 vendors that should be
  detectable, so `vendor_code` / `vendor_prose` cover the field. Reader is internal or public.
- **Battery**: the category table (2 sentinels, 5 outcome-framed real jobs, 2 shelf anchors, twin
  pair, 2 gates, control, 1 neutral advice). No probe, no H2H, no recall.
- **Experiments**: BUILD and ADVICE only.
- **Analysis**: same parser; the ledger section of `deepdive.py` (§2) is per vendor — run it with each
  vendor key or read the grid.
- **Report**: A becomes "who agents recommend" with a WINNER column and no vendor-result column; B is
  "who holds each job"; C is the twin; D quotes are about the *moments*, not a product; E four claims
  about the category; F actions are for whoever commissions the read (often "what a vendor would have to
  do to appear"). Neutral about every vendor. The kit's public category benchmark is the reference.
- **Reuse**: a category corpus is the base for later tailored reports — add only the labeled cells
  (probe, H2H, recall, a vendor-specific gate) for each vendor. Same run ids, new experiments.

## 2. Prospect vs paying customer (both tailored)

| | Prospect | Paying customer |
|---|---|---|
| kicker | `AGENT SELECTION STUDY · <VENDOR> · <MONTH>` | `… · BASELINE` |
| cover lead | the absence: "wired in 0 of N builds" | the same numbers, framed as a baseline to move |
| dek closer | "Full report and raw transcripts available." | "Each action names the cell it should move; we re-run that cell after the change." |
| F last row | the standing re-measure loop as an offer | the re-read cadence as a commitment |
| TLDR | the meeting-getter; one striking fact; offer a transcript walkthrough | what we're seeing / what to do / we re-run after each change |
| send | account exec sends; the walkthrough is the meeting | the account owner sends into the shared channel with the org-visibility line |

## 3. Re-read of an existing study (periodic)

Nothing new is designed. The point is a clean delta.

1. Reuse `study.yaml`, `battery.yaml`, the task ids and the three experiment ids from the baseline
   `STUDY.md`. **Do not edit any prompt.** A changed prompt is a new task and breaks comparability.
2. If the vendor shipped something the baseline's actions asked for, record what and when in
   `STUDY.md` before firing — that is the hypothesis being tested.
3. Fire iterations N+1…N+3 on the same experiments (`tpc sim experiment run <id>` three times, spaced
   by the wait). `iterations_map.py` picks them up as new iteration numbers; pass `--iterations <total>`.
4. `calibrate.py` again — the hand-audit list can surface new false positives when models change
   what they write. Fix the config; re-derive both baseline and re-read from the same parser so the
   comparison is like for like.
5. Report: same A–F shape. Every table gets a "then → now" cell ("L5: 0/6 → 2/6"). Movement in a
   6-run cell is one or two runs; the method paragraph says direction is read across two consecutive
   reads. If a cell moved, quote the run that moved it. If nothing moved, say so in the Score line.
6. Baselines drift on their own (Vercel's preview control moved 0/5 → 3/14 in a month with no change
   from the vendor). Always re-fire the control and sentinel too; if *they* moved, say so before
   claiming any action worked.

## 4. v2 after a first read landed

The first read's deliberate omissions become the additions:

- **Seeded-repo trigger cells** (the moment DIY breaks in a real repo — 7/8 conversion in the search
  study): build a public GitHub repo per trigger with a README whose every claimed failure exists as a
  real code path (Opus audits premises and refuses otherwise); grep the repo for every rival and for
  AI/agent mentions before pushing; wire a per-repo env trio with `--init-files`; one experiment per
  repo. Get explicit approval before anything is pushed public.
- **Consider-vendor probe on a seeded repo** with the incumbent planted as the objection; **leave-vendor probe** only
  if the vendor is an incumbent somewhere.
- **A second gate** on a different job shape, so the money cell is not one prompt.
- **Symmetric shelf** (the same job on the rival's home ecosystem and a neutral stack).
- **Content arms** (the Vercel four-arm ladder): control / control re-run / vendor-only content /
  level-shelf content. This is how an action gets marked *proven* in F.

Budget: +20–60 runs on top of the baseline corpus; report folds into the same A–F shape with C
carrying the ladder.

## 5. If the operator lacks something

| Missing | Do |
|---|---|
| `tpc` access or the org | stop at Phase 3; ask the platform owner to add the operator to the org; nothing else in Phase 3 can proceed |
| the vendor has no use-case pages | take the five jobs from docs quickstarts and the pricing page's plan names; say so in Method |
| a budget nod | do not fire; a pre-flight in `draft` costs nothing and is a fine stopping point |
| a reviewer | do not send; the skill never sends |
| PyMuPDF / reportlab / pyyaml | `pip install pymupdf reportlab pyyaml` |
