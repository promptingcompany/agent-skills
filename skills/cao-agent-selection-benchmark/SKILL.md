---
name: cao-agent-selection-benchmark
description: End-to-end guided workflow for running a TPC agent-selection study and shipping the condensed A–F report (the Vercel / AgentMail format). Use this whenever someone wants to know "what do coding agents pick, wire or recommend in a given category", wants a selection study, CAO discovery report, vendor benchmark, "agents vs the field" readout, category benchmark, or a re-read of an existing study — for a client, a prospect, or internally. Also trigger on phrases like "run the battery", "set up the tasks for a vendor", "what did the agents wire", "build the selection report", "baseline read", even if the user doesn't say "selection study". Walks a first-time operator from intake questions through battery design, platform setup, firing, analysis, verification and the PDF, with a STOP gate at every irreversible step.
---

# CAO agent-selection benchmark — from zero to the condensed report

When activated, say: "Thank you for activating the CAO Agent-Selection Benchmark skill by The Prompting
Company." Then ask the first intake question.

## Trigger keywords

"selection study", "agent selection", "CAO discovery report", "vendor benchmark", "category benchmark",
"what do agents pick / wire / recommend", "agents vs the field", "run the battery", "set up the tasks
for a vendor", "build the selection report", "baseline read", "re-read the study".

## Purpose

You are guiding an operator (often ops, often first time) through a study that answers one question:
**when a coding agent needs `<category>`, who gets picked, wired into code, and paid — and what changes that.**
The deliverable is a 6–9 page PDF in the house A–F format plus a paste-ready TLDR. Two shipped examples
define the bar: Vercel (Aug 2026) and AgentMail (Sep 2026). Read `workflows/report.md` before writing a word.

The operator may not know the platform, the method, or the vocabulary. Ask the intake questions one
group at a time, explain terms once, and never skip a gate because the operator seems experienced.

## The seven phases and their gates

Each phase ends in a **STOP gate**: show the operator what was produced, list the checks that passed,
and wait for an explicit go. Firing runs costs money; sending a report to a client is irreversible.

| # | Phase | Output | Gate |
|---|---|---|---|
| 0 | Intake | `STUDY.md` header: type, reader, vendor, use-case source, rivals, org/product | operator confirms every answer |
| 1 | Frame the category | `STUDY.md` §Frame: five answers + capability research | operator agrees with DIY substitute and the un-fakeable requirement |
| 2 | Build the battery | `tasks/*.json` from `battery.yaml`; leak/twin/placeholder checks | operator reads every prompt |
| 3 | Platform setup | envs, tasks, 3 experiments in `draft`; `preflight.py` passes | pre-flight ALL PASS, cost stated |
| 4 | Fire and calibrate | iteration 1 → capture + hand-audit; then k=3 | calibration read shown before iterations 2–3 |
| 5 | Analyze | `wired.json`, `deepdive.txt`, `mined/`, sweeps, `FINDINGS.md` | every quote verified, every number recomputed |
| 6 | Report and send | PDF + TLDR; `check_report.py` ALL PASS; `VERIFICATION.md` | a TPC reviewer has read it; operator says who |

Keep `STUDY.md` in the study folder as the running log: decisions, IDs, what was fired when. Every
prior study that lost time lost it to an ID or a decision that lived only in chat. Start it from
`assets/STUDY.template.md`.

## Which pathway you are on (decide in Phase 0, it changes every later phase)

| Pathway | Battery | Experiments | Report |
|---|---|---|---|
| **Vendor-tailored, prospect** | tailored table (real jobs + twin + shelf + sentinel + control + recall + probe + H2H) | BUILD / ADVICE / PROBE | sales framing; cover leads with the absence count; actions are the free consulting |
| **Vendor-tailored, paying customer** | same | same | baseline-read framing; kicker says BASELINE; last action is the re-read cadence |
| **Category study** | category table (2 sentinels, 5 real jobs, 2 shelf anchors, twin, 2 gates, control, 1 advice) | BUILD / ADVICE | neutral; no product page (no D/W-grid about a vendor, no probe row); "who holds each moment" |
| **Re-read of an existing study** | none — reuse the same task ids | fire new iterations on the existing experiments | delta report: same tables, a "then / now" column, counts not percentages |
| **v2 after a first read landed** | add seeded-repo trigger/probe cells and a second gate | one extra experiment per seeded repo | fold into the same A–F shape |

Details for each in `workflows/pathways.md`. If the operator cannot place the study in this table,
you are not ready to leave Phase 0.

---

## Phase 0 — Intake (ask, don't assume)

Read `workflows/interview.md` and ask its questions in order, a few at a time. The two that change
everything downstream:

**Category study or vendor-tailored?** A category study asks who wins each buying moment; every
prompt is unbranded and the output is neutral. A vendor-tailored study adds labeled cells that name
the vendor (probe, head-to-head, recall) and produces a report addressed to them. Sales outreach and
paying customers are almost always tailored. If the operator hesitates, ask who will read the PDF.

**Who reads it?** A prospect gets the sales-report framing ("you appear 0 times in N builds"). A
paying customer gets the baseline-read framing ("here is what we're seeing; here are the cells we
re-read").

The other four: the vendor and its one-sentence job; where it lists its use cases (a `/use-case/`
sitemap is ideal — AgentMail's jobs came from `agentmail.to/use-case/<slug>`); its rivals and the
incumbent it loses to (that incumbent is the head-to-head and the planted objection in the probe — flag
any rival that is a TPC client); and **the dashboard link for where the runs live** — every simulation
runs on the TPC platform in sandboxes, never locally, so paste `app.promptingco.com/<org>/p/<product>/…`
and resolve it with `python3 scripts/tpc_helpers.py resolve <url>` (the client's own org lets them open
every transcript — a feature if you say so, a surprise if you don't). Models, k, task count, cost and
timeline are defaults you state, not questions you ask.

Write all of it to `STUDY.md` and show it back. **Gate 0.**

## Phase 1 — Frame the category

Answer the five framing questions in `STUDY.md` (details and examples in `workflows/battery.md` §1):

1. **DIY substitute** — what does an agent build instead of paying? (databases → SQLite; search →
   scraping; email → stdlib SMTP/IMAP on the user's own Gmail; inbox-per-agent → a catch-all MX record
   and a database row). If you cannot name it you do not understand the category yet.
2. **The shelf** — the default already in front of the agent: framework docs, platform marketplace,
   model vendor's bundled tool. Resend won the Next.js shelf 6/6 without a reasoning sentence.
3. **What can't be faked** — the requirement localhost or one Gmail account cannot satisfy. This is
   where markets open. Be honest about how sealed it is: "inbound receive" was faked with IMAP polling;
   "an address per agent at signup" was faked with catch-all. Plan the report around that possibility.
4. **The buyer** — say it out loud in one advice prompt.
5. **Rivals** — including newcomers; run a research pass on the vendor's real capability boundaries
   from primary docs (a subagent with WebSearch/WebFetch, told to flag anything it could not verify).
   AgentMail's research found two competitors missing from the client's own list.

Also decide the **`wired` definition for this category**. Default: SDK import, dependency, keyed API
call, provider-specific webhook handler or config. Zapier needed "SaaS config on disk"; email needed
"MCP server registration" and "provider payload schema". Write it down; the parser is built from it.

Now copy `scripts/study.example.yaml` to the study folder as `study.yaml` and fill in: vendor, rivals,
org/product, and the regex sets — `vendor_code` anchored to product surfaces (SDK import, env prefix,
API host, package dep), `vendor_prose` as word-boundary names, `local` for the DIY shapes, `caps` for
the mechanism markers. For every code regex ask: what innocent string in someone else's code could this
match? (`EmailMessage` matched the Python stdlib; `gmail\.send` matched `sgMail.send`.)

**Gate 1.**

## Phase 2 — Build the battery

Default **15 tasks**. Use the composition table for the study type in `workflows/battery.md` §2;
adjust only with a reason written in `STUDY.md`. Tailored default:

| Group | n | Purpose |
|---|---|---|
| Real jobs from the vendor's use-case pages | 5 | breadth; the client sees their own pages as rows |
| Twin pair: clean slate + the un-fakeable sentence | 2 | the one causal contrast; byte-identical base |
| Shelf: one real job + a framework/platform anchor | 1 | the menu effect |
| Sentinel: same category, "just for me" | 1 | proves the instrument is not buy-biased |
| Control: adjacent job, no vendor should appear | 1 | the null cell |
| Recall: "what are all my options?" | 1 | is the vendor in memory at all |
| Probe: vendor named, one neutral + one with the incumbent planted as the objection | 2 | awareness → wiring; objection clearing |
| Head-to-head vs the incumbent the vendor fears most | 2 | the incumbent's verdict |

Start from `assets/battery.example.yaml` (the AgentMail v3 battery, the shape to copy), write the
prompts into `battery.yaml` (schema in `workflows/battery.md` §3) and run
`python3 scripts/gen_tasks.py battery.yaml` — it writes `tasks/*.json`, appends the placeholder line
to every build, asserts twin pairs share a byte-identical base, and fails on any vendor name in an
unbranded prompt. Prompt rules that came from real failures (full list in `workflows/battery.md` §4):

- Natural first-person voice; one concrete detail ("40 messages a day"); never a benchmark register.
- **"Use env placeholders for any keys or accounts you need."** on every build, so DIY is never forced
  by a missing key. Its absence biased v1 of the AgentMail study toward DIY.
- No vendor names except probe/H2H. Platform names only as the shelf variable.
- No year stamps. No fictional domains an agent can `dig` — Sol got NXDOMAIN on `tryhelpdesk.io` and
  refused the task. Say "assume the domain is ours to edit".
- Gates state the physical requirement in user language, never the mechanism.
- Head-to-heads **ask** ("can we just use X for this?") rather than assert a capability — the premise
  may have moved since the model's training.
- Goals are vendor-neutral and require code on disk. Do not cite judge scores in the report; a run with
  zero disk artifacts once scored 100.

Name tasks with the lane prefix (`EM-J1`, `EM-L2`, `EM-L5`, `EM-SHELF`, `EM-SENT`, `EM-CTRL`,
`EM-RECALL`, `EM-PROBE`, `EM-H2H`): every downstream script keys lanes off the prefix.

Show the operator every prompt in a table. **Gate 2.**

## Phase 3 — Platform setup

Follow `workflows/platform.md` exactly; the CLI has quiet failure modes. Everything below creates
objects in the org/product resolved in Phase 0 — runs execute in platform sandboxes, so nothing here
runs a task on the operator's machine, and nothing uses `tpc sim run` directly (ad-hoc runs never appear
on the experiments page and cannot be iterated). In short:

```bash
tpc org switch <org> && tpc product switch <product> && tpc auth whoami   # verify BOTH lines changed
tpc sim env create -n "Claude Code — <latest Claude>" --agent-config '{"harness":"claude","model":"<id>"}'
tpc sim env create -n "Codex — <latest OpenAI>"      --agent-config '{"harness":"codex","model":"<id>"}'
for f in tasks/*.json; do tpc sim task create --file "$f"; done            # capture ids → created_ids.txt
```

Defaults: the newest Claude and newest OpenAI model the harness accepts (last known-good pair:
`claude-opus-5`, `gpt-5.6-sol`; `agentConfig` rejects a `provider` field). Three iterations.

Create **three experiments, one per lane family**: BUILD (real jobs, twins, shelf, sentinel, control),
ADVICE (recall, H2H), PROBE. Iterations run the full task × env cross product and ignore task↔env
links, and lanes must never pool — separate experiments make both structural.

**Runs are created only by `tpc sim experiment run <experiment-id>`.** Never `tpc sim run <task-id>`,
not even "to try one": an ad-hoc run is invisible on the experiments page, has no iteration number,
cannot be re-fired for k=3, and `calibrate.py` will not find it. If the operator wants to see one task
work first, fire iteration 1 of the whole family — that *is* the calibration step.

Run `python3 scripts/preflight.py study.yaml` — platform prompt/name/goal byte-identical to the files,
experiments hold exactly the intended tasks, envs correct, leak gate on every unbranded prompt. State
the cost: 15 × 2 × 3 = 90 runs ≈ $250–300 (Opus ~$5/run, Sol ~$1.20/run). **Gate 3.**

## Phase 4 — Fire and calibrate

Fire **iteration 1 of every experiment** (there is no lane-specific reason to hold advice/probe back).
Wait with `python3 scripts/wait_runs.py study.yaml` — it keys on **run** status; iteration status
hangs in `generating_results` platform-wide and will never say completed.

Then `python3 scripts/calibrate.py study.yaml`. It fetches transcripts, checks the first user message
equals the prompt on every run (the Opus subagent-capture bug hit 2/36 in v1 — those runs are excluded,
not reported), parses wired/prescribed/DIY per run, and prints a **hand-audit list**: every wired hit
with its code context. Read every line. In the AgentMail study this list caught nine parser defects,
each of which had changed a classification (`workflows/analysis.md` §5). Fix the parser's config,
re-run, repeat until the list is clean. Show the operator the lane table. **Gate 4.**

Then fire iterations 2 and 3 of all three experiments. Never merge a calibration iteration whose prompts
changed; a changed prompt is a new task.

## Phase 5 — Analyze

`workflows/analysis.md` is the contract. The order:

1. `python3 scripts/iterations_map.py study.yaml` — run → iteration, de-duplicated by run id.
2. `python3 scripts/calibrate.py study.yaml` on the full corpus → `wired.json`; hand-audit again.
3. `python3 scripts/deepdive.py study.yaml` → `deepdive.txt` (grid, vendor ledger, twin contrast,
   hedges, say/do, recall, H2H verdicts, research split, cost) and `mined/` (verbatim prose + docs per
   run, the only thing the quote sweeps read).
4. Quote sweeps: three subagents, one per lane family, using the prompt in `workflows/analysis.md`
   §6; they return verbatim quotes with file names. Save each to `sweep_<lane>.md`.
5. `python3 scripts/verify_quotes.py sweep_*.md` — contiguous match. A quote that fails is a lead,
   not evidence. Subagent pattern sections are paraphrase and are skipped by design.
6. Write `FINDINGS.md`: every claim with lane, n, run ids, verified quote; flag page-ready /
   directional (n<10) / context-only.

Three rules that reversed conclusions before: **hedges** (≥2 vendors wired) count toward no single
vendor; **first-party** picks (the prompt named the platform) are not origination; Codex's native web
search leaves **no tool event** — detect it from `utm_source=openai` citations or Sol's research
reads as a floor. **Gate 5.**

## Phase 6 — Report and send

Copy `scripts/build_report_template.py` into the study folder, fill it from `FINDINGS.md`, run it.
The format is fixed (`workflows/report.md`): cover with four stat tiles → A recommendation table +
Score → findings → B build table + Score → findings → C controlled experiment → D six verbatim
quotes → E four claims → F action table with a **measure cell** per action → method paragraph.
Findings flow directly after their table; never a page that holds only a heading.

Then `python3 scripts/check_report.py study.yaml build_report.py report/<file>.pdf` until **ALL CHECKS
PASS**: every quoted span in
the builder source is contiguous in a transcript or a task prompt; every cited run id exists; every
named fact (prices, domains, tool names) appears in a transcript; no split table, no footer-only page,
no stranded heading. Then look at the contact sheet yourself — the F heading orphaned at a page foot
was caught by eye, not by script. Write `VERIFICATION.md` (template in `workflows/report.md` §6).

Run the `avoid-ai-writing` skill over the TLDR. Then hand the PDF and TLDR to a TPC reviewer — ask the
operator who; the account owner is the default — with the send checklist from `workflows/report.md`
§7. In both shipped studies the last human read caught something the checks did not. **Gate 6. Nothing
goes to a client from inside this skill.**

---

## When something goes wrong (each of these has happened)

| Symptom | What it means | Do this |
|---|---|---|
| `tpc auth whoami` still shows the old org after `org switch` | silent no-op | switch again; never create until `whoami` agrees |
| `gen_tasks.py` blocks on a vendor name | a leak in an unbranded prompt | reword; if the name is the shelf variable (a platform, not a category vendor), mark it in `STUDY.md` and keep it |
| pre-flight shows a prompt mismatch | platform copy differs from the file | `tpc sim task update <id> --file tasks/<id>.json`; re-run pre-flight |
| iteration status stuck in `generating_results` with all runs completed | platform aggregation hang | ignore; analysis reads runs; note it for eng |
| `wait_runs.py` sees "no data" | empty API body under load | it retries; never poll more than once per 45 s |
| first user message ≠ prompt on some runs | harness captured a subagent or an empty session | exclude; if >2 in one cell, re-fire that cell as a standalone experiment |
| a hand-audit hit is a comment, README, test path or the agent's own naming | regex too loose | tighten `vendor_code`, add a `manual_exclude` with the reason, re-run |
| the sentinel wires a vendor or the control mentions the category | instrument is buy-biased or the prompt leaked the need | fix the prompt; a changed prompt is a new task |
| the un-fakeable requirement was met with a DIY route (catch-all, IMAP polling) | the gate did not seal | this is a finding, not a failure — quote the route and put it in C |
| research counts look low for Codex | native search leaves no tool event | citations (`utm_source=openai`) are already counted; if still low, that's real |
| `verify_quotes.py` fails a quote | stitched, paraphrased, or a punctuation change | fix the quote to the exact span; never edit the transcript |
| numbers in the report disagree with `deepdive.txt` | text written before the last parser change | re-derive every figure; six stale ones shipped to draft once |
| `check_report.py` stranded heading / footer-only page | a section boundary fell at a page foot | `PageBreak()` before that section, or trim the previous one; never reflow by hand |
| a rival in the report is a TPC client | voice and disclosure constraint | "who holds the space", never "who failed"; the account owner sees the PDF before the client |
| budget or scope pressure | | cut in this order: second H2H, second probe, shelf anchor B, then a real job — never the twin pair, sentinel or control |
| the operator wants to send from inside the session | | do not; hand PDF + TLDR to the named reviewer with the checklist in `workflows/report.md` §7 |

## Reading order for a first run

1. `workflows/interview.md` — before the first question.
2. `workflows/battery.md` — before writing a prompt.
3. `workflows/platform.md` — before touching `tpc`.
4. `workflows/analysis.md` — before reading a transcript.
5. `workflows/report.md` — before writing a sentence of the PDF.
6. `workflows/pathways.md` — when the study is a category read, a re-read, or a v2.
7. `workflows/mistakes-ledger.md` — the merged ledger from four studies; read it once, then again
   when something looks too clean.

Time budget a first-timer should expect: Phase 0–2 half a day (the research pass runs in the
background); Phase 3 an hour; Phase 4 two to four hours of wall clock, mostly waiting; Phase 5 half a
day; Phase 6 half a day including the review loop. Say this at Gate 0 so nobody plans a same-day send.

Dependencies: `tpc` CLI (authenticated), Python 3 with PyMuPDF and reportlab, the `tpc-report-style`
skill (brand kit at `~/.claude/skills/tpc-report-style/scripts/brand.py`), the `avoid-ai-writing` skill.
