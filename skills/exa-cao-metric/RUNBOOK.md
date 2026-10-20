# Exa coding-agent readout: the monthly run

What Exa gets each month: one PDF (findings + action list) and one Slack message in `#ext-exa-promptingco`, with
three numbers on the same 50 prompts, run on Claude Code and Codex. October's message:
https://promptingco.slack.com/archives/C09C6M40QAF/p1791422954739579?thread_ts=1791422898.175889&cid=C09C6M40QAF

Written for someone running it for the first time. Budget a working day the first time, half a day after that.
Cost: about $600 in model credits per full read (Opus about $5 a run, Sol about $1, 196 runs).

Roles: one operator runs it; the platform team handles `tpc` or dashboard problems; whoever owns the Exa
relationship reads the message and the PDF before they go to Exa. Cadence: monthly. The October action list
proposed these dates, to be confirmed by the team: Oct 29 (noise check, internal only), Nov 30 (readout Dec 2),
Dec 14 (readout Dec 16).

The one condition: **same default models.** Claude Code on Opus 5.5, Codex on GPT-6.1 Sol. If either harness
changed its default, say so at the top of the message, and treat that month as a new baseline, not a delta.

---

## Step 0. Before firing (15 minutes)

1. `tpc update`, then `tpc auth whoami`. It must show the **Exa** organization. If not, ask the platform team to add you to
   the Exa org as admin.
2. Open `assets/tracker.oct-research.yaml` and `assets/tracker.oct-default.yaml`. Set `workdir` in both to the
   same absolute path (for example `/Users/you/exa-cao-tracker`). Keep that path between months: history and
   month-over-month deltas live there.
3. **Register pages that went live since the last read.** `published_pages` in both files already covers every
   `tpc-*.exa.ai` page. Anything published on `exa.ai` itself (for example an Exa vs Brave comparison page, if it
   has gone live) needs its own line with the date it went live. Skip this and the "citing a page we publish" number is wrong.
4. Check the environments: `tpc sim experiment get 904a2cf3-8e5f-40a9-af70-c83c3333fc11 --scope exa/exa-search-docs`
   lists the environments and their models. Expect `claude-opus-5-5` and `gpt-6.1-sol`. The two **usability**
   environments carry `EXA_API_KEY`; every other environment must have **no** Exa key, only the model provider's.
5. Exa credits sit on the shared `rick@promptingco.com` account (1Password). If the balance is low, ask Exa in the
   channel for a top-up before firing.

## Step 1. Fire the seven experiments (5 minutes, then wait 1 to 3 hours)

```bash
for id in 904a2cf3-8e5f-40a9-af70-c83c3333fc11 8281369c-6c43-4553-9ad0-d45f63d4bec2 \
          9835af1b-e514-4213-a018-16b421375df8 1a326da8-9c69-40ce-ba86-3abb3c1d4f92 \
          87153858-e462-4790-a090-236157d52edd 694980d7-6eec-4a7b-aa00-f68a50ce461e \
          80666633-005e-4e32-bad9-16cbea4b4782; do
  tpc sim experiment run $id --scope exa/exa-search-docs
done
```

| Experiment | What it is | Mode |
|---|---|---|
| 904a2cf3 | 16 build prompts | research |
| 8281369c | 16 tool-seeking prompts | research |
| 9835af1b | 16 head-to-head prompts | research |
| 1a326da8 | 2 usability prompts (Exa key present) | research |
| 87153858 | 16 build prompts | task only (default) |
| 694980d7 | 16 tool-seeking prompts | task only |
| 80666633 | 16 head-to-head prompts | task only |

Wait on **run** status, not iteration status: iterations can sit in "generating results" for days and the
analysis does not need them. Check with `tpc sim experiment get <id> --scope exa/exa-search-docs`. All 196 runs
should be `completed`. A run that errored or never finished is excluded automatically and shows up in the pull
report; if more than a handful fail, rerun that experiment before analysing.

Known trap: the UC18 usability grader (Exa Agent) needs a timeout of at least 360 seconds or it fails on time
alone. In October both Exa Agent runs worked live but the grader timed out; they were settled by hand as `pass`.

## Step 2. Pull and analyse, once per mode (10 minutes)

```bash
cd ~/.claude/skills/exa-cao-metric/scripts
python3 pull.py ../assets/tracker.oct-research.yaml --latest --label 2026-11-research
python3 analyze.py ../assets/tracker.oct-research.yaml 2026-11-research
python3 pull.py ../assets/tracker.oct-default.yaml --latest --label 2026-11-default
python3 analyze.py ../assets/tracker.oct-default.yaml 2026-11-default
```

`pull.py` reports runs per experiment. Expect 100 for research (96 + 4 usability) and 96 for default.
`analyze.py` writes `<workdir>/<label>/facts.json`, `metrics.json` and `review_queue.json`.

## Step 3. Settle the review queue (the step that decides the numbers; 1 to 3 hours)

`review_queue.json` lists the runs where the classifier is unsure. **Do not skip this.** In October the
classifier said 1 of 32 research builds used Exa; after reading the runs it was 4 of 32. The rules are in
`workflows/review.md`. The three that matter most:

- **Head-to-head "win" means Exa is the default pick.** "Exa if X, otherwise Y", "both would work", "Exa as a
  fallback" are `split` or `loss`. Only `win` counts.
- **Build "main" means Exa is the default search path in the code.** Exa wired as an optional add-on next to the
  provider's built-in search is `secondary`.
- **Tool-seeking "listed" means Exa is offered as a viable option.** Named only to rule it out is `absent`.

For each queued run, open the log (`log` path in the queue entry; for builds read the code the agent wrote), decide,
and write `<workdir>/<label>/reviews.json` as `{"<run id>": "<verdict>", ...}`. Then re-run `analyze.py` for that
label until the queue is empty. October's settled files are in `assets/examples/2026-10/` as worked examples.

With Claude Code open in this skill's folder you can say "settle the review queue for 2026-11-research" and it
will read the runs and draft `reviews.json` for you to check. Spot-check at least five of its verdicts yourself.

## Step 4. Report (5 minutes)

```bash
python3 report.py ../assets/tracker.oct-research.yaml 2026-11-research
python3 report.py ../assets/tracker.oct-default.yaml 2026-11-default
```

Writes `report.md` per label and appends `<workdir>/history.json` (only when the queue is empty). `report.md` has
the deltas, the pages agents opened in won vs lost runs, citations and rule-based action candidates. Read it top to
bottom: it is the raw material for the findings and the action list.

## Step 5. Write this month's narrative and action list (2 to 4 hours)

Copy and edit, never start from blank:

```bash
cp ../assets/narrative.2026-10.json ../assets/narrative.2026-11.json
cp ../assets/actions.2026-10.json  ../assets/actions.2026-11.json
```

- `narrative.*.json`: kicker, date, the Slack title and findings, and the hand-reviewed tables on pages 3 to 6
  (loss reasons, close calls, pages that cost a decision, what agents build with). Every number on page 1, in
  sections 3 and 4, in the page deks, in builds, usability and scope is computed; do not type numbers there.
- `actions.*.json`: the goals row targets and the ranked action list. To write it, read every non-win run in
  `facts.json` and label it: tie-break, not found, out of category, integration cost, real gap, perception gap.
  Only content-fixable labels become actions. Tie-breaks were 44% of head-to-head losses in September; that is
  where pages move the number. Mark `exa_ok: true` on anything that names a rival or states a fact Exa must confirm.
- Update the status of last month's actions (live, slipped, dropped) in the `why` or `detail` field, and move
  anything live into `published_pages` in both tracker configs **before** the next month's pull.

## Step 6. Build the PDF and the Slack message, then cross-check (30 minutes)

```bash
python3 build_pdf.py \
  --research <workdir>/2026-11-research --default <workdir>/2026-11-default \
  --narrative ../assets/narrative.2026-11.json --actions ../assets/actions.2026-11.json \
  --previous ../assets/baseline.2026-10.numbers.json \
  --out "TPC x Exa Coding Agent Readout November.pdf"
```

It writes the PDF (10 pages in October: 6 of findings, 4 of actions), `<out>.numbers.json` and `<out>.slack.md`.
The build refuses to run while either review queue is non-empty.

Cross-check before anything leaves: open `<out>.numbers.json` and, for each of the three headline numbers, list the
run IDs behind it from `facts.json` (`outcome == main`, `win`, or any `published[].cited`). Read two of them. Twice
in September a regex change left stale figures in a draft; this habit is why October's baseline was trusted enough
to send. Also check the delta flags in the Slack message: anything under 15 points is "within noise" and must be
described that way.

## Step 7. Send

Whoever owns the Exa relationship reads `<out>.slack.md` and the PDF first. Then post the message in
`#ext-exa-promptingco` with the PDF attached, tagging the Exa contacts who received the October baseline. Keep the format: headline, the three numbers with deltas,
findings, setup notes, action items. Add the live pages and dates to the shared "TPC x Exa CAO Actions" sheet.

---

## Things that are not obvious

- **Default mode cannot be steered.** Claude Code never searches the web when choosing a tool (0 of 48 task-only
  runs) and Codex only searches for vendors it already knows. That is why the goals are set in research mode.
  Report research mode as a labelled segment next to task-only, never instead of it.
- **Moves under 15 points are noise.** Each agent answers each prompt once, so a cell of 16 runs swings about 20
  points on its own. Only pooled numbers (per prompt type, both agents) are reportable. Never report per use case.
- **Codex logs are incomplete.** GPT-6.1 Sol records search queries and page opens but not the results, so "opened"
  counts for Sol are a floor and "Exa in the top 10" can only be measured on Opus.
- **Prompts changed on Oct 7.** Four build prompts (UC10, 11, 12, 16) were reworded. Builds before that date are not
  comparable; the October baseline is the first comparable read.
- **Seeded repos.** The build prompts reference GitHub repos `benchmarktesting5` to `29`. If they move, update the
  task prompts in the dashboard before firing.
- **Classifier gaps known in October**, fixed by review, not yet in code: Exa as "default, other optional" should
  be `main`; JSON-escaped `type: "web_search"` in Sol builds is missed (4 runs in October); specialist APIs are not
  recorded in `wired`.
- **Everything shipped so far:** October readout and action list in `#ext-exa-promptingco` (Oct 8), the tracker
  sheet "TPC x Exa CAO Actions (October 2026)", docs suggestions posted in the Exa channel (Oct 9). The Nov/Dec
  goals in `actions.2026-10.json` were proposed to Exa in the action list, not confirmed; agree them internally
  before repeating them.
