# Run and triage

**Widen across configurations, pull every run completely, rerun infrastructure in place, and classify every failure with evidence.**

## Step 1: Choose configurations and run counts

- Widen across harnesses and models before deepening. Pick harness/model pairs that already run cleanly elsewhere on the platform (`tpc sim env list --scope <org>/<product>` on other products shows known-good pairs) instead of guessing model strings.
- Choose each configuration for a reason the report can state: newest flagship, cheaper tier, a different vendor's harness, an open-weight model, and **the same model in a different harness** (isolates harness from model).
- Give the experiment its own environments holding only its own secrets. Import secrets from a file over stdin, never on a command line.
- Attach tasks to new environments (`tpc sim env task attach <env> <task...>`) and update the experiment's environment list (`tpc sim experiment update --env-ids` replaces the whole list; pass every ID).
- An iteration runs each task once per environment; there is no repeat count. k runs per cell means k iterations. Run them sequentially with a driver that waits for completion, resets fixtures, then triggers the next.
- State the cost estimate before triggering: environments x tasks x iterations x observed cost per run from validation.

## Step 2: Pull complete data

Use `scripts/pull-runs.ts`. Things that silently break pulls:

- `tpc sim run list` pages at 20 by default and may not show iteration runs without `--task-id`. Pull per task with `--page-size 100`.
- JSON envelopes differ by command (`runs`, `data`, `items`). Parse the key that is actually there; an empty list from guessing the wrong key looks exactly like "no runs".
- Rate limits return 429 or an empty body. Retry with backoff and count what could not be fetched as DATA UNAVAILABLE, never as a pass or a fail.
- The CLI can append an update notice after the JSON on stdout; strip it before parsing.
- Never pipe JSON through `echo` in zsh; it expands backslash escapes and corrupts strings.

## Step 3: Separate infrastructure failures and rerun them in place

A run that failed before the agent started is infrastructure. Typical `failureDetails.kind`: `sandbox_provisioning_failed` (sandbox creation timeout, snapshot still building on a harness's first use, provider at capacity).

Rerun each one inside its original iteration:

```
POST /api/v1/agent-simulation/experiments/<experiment-id>/rerun?orgSlug=<org>   {"runId": "<failed-run-id>"}
```

with the CLI bearer token. This replaces the run so the iteration total is unchanged; `tpc sim run <task>` would instead create a standalone run outside the iteration. Stagger reruns. Exclude the original failed runs from every rate and list them in the report footer.

## Step 4: Tabulate, then read every failure

Run `scripts/summarize.ts` for the per-cell table. Then, for every run with a failing correctness goal, open the transcript and classify it:

| Class | Signature | Evidence to collect | Action |
|---|---|---|---|
| Infrastructure | Failed before the agent's first event | `failureDetails` | Rerun in place, exclude |
| Grader defect | Agent's artifacts and provider state show the job done; grader message says otherwise | The artifact, the provider record, the grader line that misread it | Fix the grader, regrade from the real artifacts, push the fix, report the run as adjusted |
| Fixture contamination | Several runs fail the same check in the same time window; one side effect explains all of them | Provider record of the side effect (timestamp, object), the one transcript that caused it, start/end times of the affected runs | Count the causing run as a failure; count the others as adjusted passes, each named |
| Genuine agent failure | Transcript shows the agent's wrong choice or wrong call | The quoted line or API payload | Keep as a failure; describe it in one line |

Rules while triaging:

- **A verdict that contradicts the agent's own final message** ("both drafts created") is a lead, not proof either way. Check the provider: the agent may have used the wrong field (a `thread_id` the API silently ignores) or the grader may have misparsed the output.
- **Identical failures clustered in one window** point at a shared side effect. Query the provider for the side effect itself (for example the sent folder) and match its timestamp to run windows.
- **Find the run that caused a side effect** by searching transcripts for the call (endpoint, method) near the side effect's timestamp, then read the surrounding events and the agent's final message.
- **Regrade from real artifacts** after a grader fix: reconstruct the agent's output from the transcript, run the fixed grader against the live provider state, and confirm a fabricated input still fails.

## Step 5: Record the adjusted table

Keep the platform verdict ("as scored") and the triaged result ("adjusted") side by side per cell. Every adjusted run is listed with its class and one-line evidence in the results file. The platform still shows the original verdict; the report says so.
