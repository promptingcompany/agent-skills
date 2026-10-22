# Prove the graders

**Prove every grader against reference solutions on live fixtures, then validate on the platform, before any scored iteration.**

Run this before any scored iteration. The goal is an instrument you can defend: every goal has been shown to pass what should pass and fail what should fail, on the same fixtures the agents will see.

## Step 1: Inventory the goals

List every goal on every task with its evaluation type and what it reads:

| Task | Goal | Type | Reads | Correctness or recorded |
|---|---|---|---|---|

- **Correctness** goals decide pass/fail. **Recorded** goals describe how the agent worked (route used, where a rule is enforced) and never enter a pass rate. Put "(recorded, not correctness)" in the goal name so the platform UI and every export carry it.
- Prefer `script_judge` for anything checkable against state (files, provider objects, HTTP responses). `script_judge` needs the org feature flag; if creation returns "The Script Judge goal type is not enabled for your organization", ask the org admin to enable it rather than downgrading to an LLM judge.
- Reserve `llm_judge` for judgement that has no state to check, and write its rubric so a reasonable alternative cannot be misread (see Step 4).

## Step 2: Make fixtures that cannot leak the answer

- Identifiers the agent can read (message IDs, MIME boundaries, filenames, record keys) must not encode the role of the object. Hash them: an ID like `target@...` or a boundary `b-decoy-1` hands the agent the answer.
- Grep the generated fixtures for role words before seeding.
- Keep the answer key out of the sandbox. Graders may embed the minimum needed to grade (a hash, an expected total), never the mapping of which object is which.
- Seed by the route the real world uses (real email delivery, real API calls) when the benchmark spec requires it, and verify the seeded state against the provider afterwards: counts, attachment hashes, whether original fields (dates, headers) survived. Record anything the seeding path rewrites (for example a sending service replacing `Message-ID`): answer keys must use what arrives, not what was sent.
- Add a fixture check as a task init command that fails the run (as infrastructure) if the seeded state is incomplete.

## Step 3: Write reference solutions and run every grader against them

For each task, write at least three solutions and run each grader goal locally against the live fixtures:

| Reference | Expected |
|---|---|
| Correct | every correctness goal passes |
| Broken (the realistic mistake: wrong object, missing file, full-privilege credential) | the matching goal fails with a clear message |
| Plausible alternative (a different but valid approach, e.g. app-level instead of provider-enforced isolation) | correctness passes; the recorded goal classifies it correctly |
| Empty (agent did nothing) | every goal fails; no vacuous pass |

Fix every mismatch. The empty case catches graders that pass because nothing violated a negative check.

Keep every script grader inside the platform's script time limit (120 seconds today, and not documented). A grader
that waits for an asynchronous effect, such as an email arriving, must poll within that budget; a timeout scores as a
failure, not as unknown.

Do not depend on field names the prompt did not fix. Agents write `inbox_address`, `inboxId` or a nested
`steps.create.email` for the same value; find values by content (an address pattern, a token pattern) and verify them
against ground truth.

An LLM judge for "did it only through X" must also fail when the operation never happened. Otherwise a run that gave
up immediately passes the compliance goal.

Make graders tolerant of output shape and strict about substance: accept any JSON shape that contains the IDs, never a single expected key. A grader that only reads `[...]` or `{"drafts": [...]}` will fail an agent that wrote `{"draft_ids": [...]}` and did the job.

Clean up everything the reference solutions created (keys, drafts, objects) with the fixture-reset script before moving on.

## Step 4: Validation runs

1. Create the tasks and attach init commands. Init command `cwd` must start with the sandbox home path including the trailing slash (for example `/home/agent-user/`); the API rejects it otherwise with a generic "Invalid init commands payload".
2. Queue one standalone run per task per environment (`tpc sim run <task-id> --scope ...`). Standalone runs sit outside experiment iterations and do not count.
3. When they finish, pull every run with goal verdicts and read each verdict against its transcript. For each failure ask: did the agent fail, or did the grader misread what it did? Check the agent's saved artifacts and the provider state, not just the grader message.
4. Check that the tool under test was actually available in every environment. The platform writes some harness
   configs after task setup runs, which can silently drop what setup added; an agent reporting "the tools are not
   available" is an instrument failure, not an agent result.
5. Read LLM-judge verdicts critically. If the judge failed something a reasonable reader would pass (a date filter counted as "not searching"), tighten the rubric so the boundary is explicit.

## Step 5: Push fixes and re-verify on the platform

- Update tasks from a task-only JSON (`tpc sim task update <id> --file task.json`). Script goals go through an LLM security review on every create or update; "the security review could not complete" is transient, retry with backoff (it can take several attempts).
- After each update, read the task back and confirm the new grader text is live and the init commands survived.
- Generate task specs from one builder script per experiment so every provider or arm gets the same fix.

## Step 6: Fixture hygiene between iterations

- Write a reset script that deletes only objects created after the experiment start (a `--since` cutoff), and logs each deletion by name and creation time. Never delete pre-existing objects: a reset that removes "everything" will eventually remove something a human made.
- Run it between iterations, not during them.
- Decide now whether concurrent runs can share a fixture. If a task has side effects (sending, deleting, creating credentials), give each run its own fixture or make every side effect attributable to one run; otherwise one agent's action fails every run open at the same moment.
