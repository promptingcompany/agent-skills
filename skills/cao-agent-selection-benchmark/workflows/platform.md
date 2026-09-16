---
name: platform
description: Phase 3–4 with the tpc CLI: scope verification, envs, tasks, three experiments, pre-flight, firing, waiting, transcript fetch, known platform behaviours
triggers: platform setup, create experiments, fire iteration, wait for runs
---

# Platform — Phase 3 and 4 with the `tpc` CLI

Every rule here was paid for. The CLI reports success in cases where nothing changed.

## Where runs execute, and how they are created

On the platform, in sandboxes, always. The operator's machine only drives the CLI and parses transcripts
afterwards. Resolve the org and product from the dashboard link the operator has open
(`python3 scripts/tpc_helpers.py resolve https://app.promptingco.com/<org>/p/<product>/simulation`),
never from memory, and confirm with `tpc auth whoami`.

Runs are created **only** through experiments: `tpc sim experiment run <experiment-id>`, one iteration
at a time, three experiments (BUILD / ADVICE / PROBE). Do not use `tpc sim run <task-id>` to "try one
quickly": an ad-hoc run does not appear on the experiments page, has no iteration number, cannot be
re-fired for k=3, and `calibrate.py` and `iterations_map.py` will not find it. The way to see one task
work is to fire iteration 1 of its family — that is what calibration is for.

## Setup sequence

```bash
tpc --version && tpc auth whoami            # note CLI vs server version drift; it has broken signal configs before
tpc org switch <org-slug>
tpc product switch <product-slug>
tpc auth whoami                             # BOTH Organization and Product lines must show the new values
```

`tpc org switch` once printed "✓ Switched" and changed nothing; a second call worked. Verify with
`whoami` before creating anything, every time. `~/.tpc/config.json` holds your auth token in plain
text; never print it.

```bash
tpc sim env create -n "Claude Code — Opus 5" --agent-config '{"harness":"claude","model":"claude-opus-5"}'
tpc sim env create -n "Codex — 5.6 Sol"      --agent-config '{"harness":"codex","model":"gpt-5.6-sol"}'
```
`agentConfig` rejects a `provider` field — harness and model only. Use the newest models the harness
accepts; check with a throwaway env if unsure.

```bash
for f in tasks/*.json; do tpc sim task create --file "$f"; done   # capture the UUID from each result into created_ids.txt
```
Task JSON: `name`, `description`, `category: "coding"`, `prompt`, `goals[]` at top level (nesting
under `taskDefinition` is rejected on create — but `tpc --format json sim task get` *returns* the
prompt under `.taskDefinition.prompt`; `preflight.py` knows this).

## Experiments — three, homogeneous

```bash
tpc sim experiment create --name "EM v1 — BUILD family" --description "..." --task-ids <build ids> --env-ids <2 envs> [--signal-config signals.yaml]
tpc sim experiment create --name "EM v1 — ADVICE family (recall + H2H)" ...
tpc sim experiment create --name "EM v1 — PROBE (labeled, never pools)" ...
```
An iteration runs the **full task × env cross product** and ignores task↔env links (one study fired
104 junk runs learning this). Lane families in separate experiments make "lanes never pool" structural.
`tpc sim experiment update <id> --task-ids ...` **replaces** the list; pass every id.

Attach task↔env links one task per call if you use `tpc sim run` directly; batch attach fails with a
bogus "invalid task IDs". Prefer experiments; `tpc sim run <task>` creates ad-hoc runs invisible on the
experiments page.

## Pre-flight (Gate 3)

`python3 scripts/preflight.py study.yaml` checks, and exits non-zero on any failure:
- platform `taskDefinition.prompt`, `name`, `goals[0].description` == local file, byte for byte, for every task;
- each experiment holds exactly its intended task set and both envs, status `draft`;
- leak gate on every non-branded prompt;
- twin integrity.
Then state the run count and cost and wait for the go.

## Firing and waiting

```bash
tpc sim experiment run <exp-id>                          # one iteration = every task × env
tpc sim experiment run status <exp-id> --iteration N     # per-iteration; default is latest only
tpc --format json sim experiment run status <exp-id> --iteration N   # has .runs[].id — the only run→iteration source
```

**Wait on run status, never iteration status.** All nine AgentMail iterations completed every run and
then sat in `generating_results` indefinitely. `scripts/wait_runs.py` polls `--iteration 1..3` for all
experiments and exits when every run is `completed`/`failed`. Poll ≤ once per 45 s; the API returned
empty bodies when three loops hammered it, and an empty body read as "0 pending" once — a false
"all done". `tpc_helpers.tpc_json` retries with backoff and raises instead of returning nothing.

Fire iteration 1 of **all** experiments together; there is no lane-specific reason to hold advice or
probe back, and it costs wall-clock. Fire iterations 2–3 only after Gate 4.

## Fetching transcripts

```bash
tpc --format json sim run list --status completed --page-size 200   # no iteration field; join via run status JSON
tpc --format json sim run logs <run-id>                             # events under .session.events
```
`calibrate.py` writes `tx/<lane>__<task>__<model>__i<n>__<runid8>.json` and retries when a body lacks
`"events"`. Check `first user message == prompt` on every run: the Opus harness sometimes captures a
*subagent's* session (first user message is an internal directive like "Email boss@example.net…"); Sol
sometimes captures an empty first message. Exclude, log, oversample if the cell matters.

## Known platform behaviours to expect

| Behaviour | What to do |
|---|---|
| `org switch` silent no-op | verify with `whoami` |
| `generating_results` hang after all runs complete | ignore for analysis; key waits on runs; flag to eng |
| empty JSON bodies under load | retry with backoff (`tpc_helpers.tpc_json`); never treat empty as zero |
| Opus subagent-capture | first-user-message check; exclude; oversample |
| Sol empty event log | refetch later; exclude if persistent |
| judge gives 100 to a run with no disk artifact | never cite judge scores |
| Codex native web search leaves no tool event | detect via `utm_source=openai` citations in prose |
| sandbox capacity errors ("no space left on device") | re-queue; not agent behaviour |
| `ugrep` aliased as `grep` chokes on `{0,220}` over UTF-8 | use Python for text scans |
