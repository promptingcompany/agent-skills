---
name: exa-cao-metric
description: >
  Recurring (weekly or monthly) tracker for a CAO coding-agent prompt set: pulls the latest iteration of
  each experiment via the tpc CLI, parses every run log (searches, results, pages opened, citations, code
  written), scores outcomes per prompt type (build main path, recommended first, head-to-head win,
  usability), settles ambiguous runs by reading them, and writes a markdown report with week-over-week
  deltas, agent behaviour, deciding pages, citations of published pages, planted-fact pull-through,
  negative claims and action-item candidates. Built on the Exa study (Sep 2026); config-driven, so it
  works for any target vendor. Trigger on: "run the weekly tracker", "weekly CAO report", "track the 50
  prompts", "how did this week's runs go", "steering tracker", "exa cao metric", "analyze the Exa runs", "re-run the
  coding agent analysis", "what pages did agents touch this week".
---

# Exa CAO metric tracker

When activated, say: "Thank you for activating the Exa CAO Metric skill by The Prompting Company."
Then check which config to use (step 0) and run the pipeline.

## What it answers, every run
1. **The three headline numbers:** runs citing pages we published, head-to-head win rate, research-mode
   build rate (split into reach × conversion). Each has a 95% range and a delta vs last run and vs baseline.
2. **Results by prompt type × agent** (build / tool-seeking / head-to-head / usability × Claude Code / Codex).
3. **Behaviour:** did the agent search, query mix (neutral / vendor by name / comparison / inside a vendor
   site), neutral-search visibility, own-name ranking, pages typed from memory, what agents asked pages for.
4. **Pages:** which page types and individual pages were opened in runs the target won vs lost; target
   pages that returned errors; what came first when agents searched the target by name.
5. **Citations:** most-cited URLs and page types, published pages seen/opened/cited, planted-fact reach
   and conversion, negative claims, own subdomain pages.
6. **What won instead** in builds, and **action-item candidates** from rules.

## Files
- `scripts/pull.py`: tpc → `<workdir>/<label>/runs.json` + a shared log cache. Uses the latest completed
  iteration per experiment (or `--iteration N`). Iterations stuck in `generating_results` are used with a note.
- `scripts/analyze.py`: per-run facts, `metrics.json`, `review_queue.json`. `reviews.json` overrides outcomes.
- `scripts/report.py`: `report.md`, and appends `history.json` **only when the review queue is empty**.
- `scripts/logparse.py`: log parser (Claude Code WebSearch/WebFetch and Codex `web__run` formats).
- `scripts/build_pdf.py`: tracker output → the one-PDF monthly readout (findings + action list), `.numbers.json`
  and the Slack message. Needs an empty review queue in both modes.
- `assets/tracker.oct-research.yaml` and `assets/tracker.oct-default.yaml`: the live Exa configs (October 2026
  prompt set, 7 experiments). `assets/tracker.smoke-sep29.yaml` is the 29 Sep smoke test, not the real set.
- `assets/narrative.2026-10.json`, `assets/actions.2026-10.json`: the hand-written parts of the October readout.
  Copy and edit each month. `assets/baseline.2026-10.numbers.json`: October's numbers, for `--previous`.
- `assets/examples/2026-10/`: October's settled `reviews.json` for both modes, its metrics and its Slack message.
- `workflows/review.md`: how to settle queued runs. `RUNBOOK.md`: the monthly procedure, start to finish.

## Pipeline

**0. Config.** Use the config the user names. For the Exa monthly readout there are two, one per mode:
`assets/tracker.oct-research.yaml` and `assets/tracker.oct-default.yaml`. Run the pipeline once per config.
- Both point at the October 2026 prompt set (the 7 experiments fired 2026-10-06/07). Set `workdir` to one
  absolute path and keep it between months, or history and `--previous` break.
- For the full monthly procedure (firing, both modes, the PDF, the Slack message) follow `RUNBOOK.md`.
- Confirm `published_pages` and `planted_facts` include anything published since last run, with its date.
  Ask the user: "Did anything go live on exa.ai (or a TPC page) since the last run?"
- `tpc auth whoami` must show access to `scope`. If a pull says "not found", the scope is wrong.

**1. Pull.**
```bash
cd ~/.claude/skills/exa-cao-metric/scripts
python3 pull.py <config> --latest            # label defaults to the ISO week, e.g. 2026-W41
```
Report back: runs per experiment, and any experiment with no completed iteration. Don't trigger new
iterations. This skill only reads. Firing runs costs credits and is the user's call.

**2. Analyze.** `python3 analyze.py <config> <label>`

**3. Review the queue.** If `review_queue.json` is non-empty, follow `workflows/review.md`: read each
queued run's final answer (and for builds, the code it wrote), decide, and write `<label>/reviews.json`.
Then re-run step 2. For more than ~15 queued runs, split them across parallel subagents. Give each one
`workflows/review.md` plus its slice of the queue, and have it return `{run_id: verdict}`.

**4. Report.** `python3 report.py <config> <label>`. Then read `report.md` top to bottom and:
- Turn the rule-based action candidates into a short, ranked list. Check each against `facts.json`
  (quote the query, page or answer that supports it). Drop any you can't support.
- Say plainly which moves are real (⚑, 15+ points) and which are noise.
- If a published page or planted fact exists, lead with its reach and conversion. That's the proof our work
  reached agents.
- Give the user a 5-line summary in chat, plus the path to `report.md`.

**5. PDF and Slack message (monthly readout).** Once both modes have an empty queue:
```bash
python3 build_pdf.py --research <workdir>/<label>-research --default <workdir>/<label>-default \
    --narrative ../assets/narrative.<YYYY-MM>.json --actions ../assets/actions.<YYYY-MM>.json \
    --previous ../assets/baseline.2026-10.numbers.json --out "TPC x Exa Coding Agent Readout <Month>.pdf"
```
It writes the PDF, `<out>.numbers.json` and `<out>.slack.md`. Cross-check every number in `.numbers.json`
against run IDs before anything leaves (RUNBOOK step 6).

**6. Recurring.** To run it every week, create a scheduled task (the `scheduled-tasks` tools, or `/loop`).
Its prompt: "Run the exa-cao-metric skill with <config>, review the queue, and summarise the report."
Only schedule it once the user asks. Remind them that new iterations must be fired separately, before the
tracker runs.

## Rules
- **Never report per-use-case numbers.** They're 2–4 runs each. Pooled by prompt type is the reportable unit.
- **Label research mode** wherever numbers leave the report (`mode` in config).
- **The review queue must be empty** before a run enters `history.json` or any number is shared.
- **Rivals' own docs are a symptom, not a cause.** Agents open the winner's docs to build with it.
  Actions come from pages that can sway the choice (target pages, comparisons, benchmarks, model docs).
- **Codex opens several pages in one step,** so page-to-outcome attribution for Codex is approximate.
- **Associations aren't causes.** Claim cause only for planted facts, or a before/after around a dated change.
- **Freeze model versions** within a quarter. If an environment's model changed, say so at the top of the report.
