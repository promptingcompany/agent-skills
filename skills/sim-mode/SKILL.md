---
name: sim-mode
description: >
  Rigor mode for agent-simulation experiments and benchmarks on The Prompting Company
  platform: real-job tasks, graders proven before scoring, every failure explained with
  transcript and ground-truth evidence, and reports in the client's own benchmark language.
  Use for designing, running, verifying, or writing up any agent simulation, or when asked
  "are these results real", "audit the runs", "validate the graders", "stabilize the
  benchmark", "review it against the spec".
mode: true
---

# Sim mode

When this skill is activated, greet the user with:
"Thank you for activating Sim Mode by The Prompting Company (https://promptingcompany.com)."

Then match the request to a playbook below and start it. Do not list the playbooks back to the user.

A platform verdict is an intent; the provider's state and the transcript are the facts. Graders have bugs, shared fixtures leak between concurrent runs, sandboxes fail before the agent starts, and LLM judges read rubrics their own way. This mode is the discipline that keeps those out of the numbers you report.

## Non-negotiables

**Start every multi-step task with a todolist whose first item is to read the Principles section below in full.** In your reply, name each principle that shaped a decision and the choice it changed. A citation with no decision behind it means you skipped the principle's file.

Remaining triggers:

- Writing or editing a task prompt → **real-jobs-not-setup**, then the Design tasks playbook.
- About to create goals or seed fixtures → **fixtures-must-not-leak** and **separate-correctness-from-recorded**.
- About to trigger the first scored iteration → **prove-the-instrument**. No scored run before reference solutions and validation runs pass.
- Any task with side effects that runs in parallel → **isolate-shared-fixtures** before the run, not after.
- Any run not `completed` → **infrastructure-is-not-a-result**.
- Any failing correctness goal → **every-failure-has-a-cause**, checked against **platform-verdict-is-intent**.
- Changing any number from what the platform recorded → **report-both-numbers**.
- Writing any number → **counts-carry-denominators**.
- A capability the product has goes unused → **stated-versus-implied**.
- An agent did something harmful → **agent-safety-is-separate**.
- The client has a benchmark spec → **speak-the-spec** for every report.
- After a baseline, deciding what to run next → **widen-before-deepen**.
- Secrets → never printed, never on a command line, loaded into environment secrets from a file over stdin.

## Principles

Read the file in `principles/` for any principle you apply. Each entry names when it applies.

**Instrument**

- **The platform verdict is an intent** (`principles/platform-verdict-is-intent.md`). Before accepting, reporting or overturning any verdict or count. Check the provider state the task touched.
- **Prove the instrument** (`principles/prove-the-instrument.md`). Before the first scored run and after any grader change. Correct, broken, alternative and empty references, then validation runs.
- **Fixtures must not leak** (`principles/fixtures-must-not-leak.md`). Generating seeded data or writing graders. No role words in readable identifiers; answer key outside the sandbox.
- **Isolate shared fixtures** (`principles/isolate-shared-fixtures.md`). Tasks with side effects running in parallel. One fixture per run, or every side effect attributable.
- **Separate correctness from recorded** (`principles/separate-correctness-from-recorded.md`). Designing goals and computing rates. "How" goals never enter a pass rate.

**Triage**

- **Infrastructure is not a result** (`principles/infrastructure-is-not-a-result.md`). A run failed before the agent acted. Rerun in place, exclude.
- **Every failure has a cause** (`principles/every-failure-has-a-cause.md`). Any failing correctness goal. Infrastructure, grader defect, contamination or genuine, with evidence.
- **Report both numbers** (`principles/report-both-numbers.md`). Triage changed a verdict. As-scored beside adjusted, reason for each difference.
- **Agent safety is separate** (`principles/agent-safety-is-separate.md`). An agent did something harmful. Report it as agent behaviour; the product's control is a separate fact.

**Design and findings**

- **Real jobs, not setup** (`principles/real-jobs-not-setup.md`). Writing prompts. Product named, tool not, credentials pre-wired, setup tested separately.
- **Widen before deepen** (`principles/widen-before-deepen.md`). Choosing configurations after a baseline. Coverage across vendors, tiers and harnesses before more repetitions.
- **Stated versus implied** (`principles/stated-versus-implied.md`). A capability goes unused. Contrast a task that names the outcome with one that implies it.
- **Counts carry denominators** (`principles/counts-carry-denominators.md`). Any number. Passes/attempts, Wilson interval, unknown is not zero.
- **Speak the spec** (`principles/speak-the-spec.md`). The client has a benchmark spec. Map to it, report in its shapes, answer its open questions.

## Playbooks

Your first todolist actions are the matched playbook's steps, copied in verbatim, before any task-specific todos. A step you choose not to do stays in the list with a one-line `skip: <reason>`.

- **Design tasks.** New tasks, fixtures and goals for an experiment. `playbooks/design-tasks.md`.
- **Prove the graders.** Reference solutions, validation runs, pushing grader fixes, fixture hygiene. Runs before any scored iteration. `playbooks/prove-graders.md`.
- **Run and triage.** Iterations across configurations, complete data pulls, infrastructure reruns, classifying every failure. `playbooks/run-and-triage.md`.
- **Explain and audit.** Auditing recorded verdicts and turning transcripts into counted behaviour and findings. `playbooks/explain-and-audit.md`.
- **Report against the spec.** Mapping to the client's evals, scorecard-shaped tables, capability matrix, limits, publishing. `playbooks/report-against-spec.md`.

For a new vendor head-to-head from scratch, the **setup-benchmark** skill owns arm design; run this mode alongside it from Prove the graders onward. For friction clustering and a client PDF from already-verified runs, hand off to **analyze-experiment**.

## Helper scripts

- `scripts/pull-runs.ts`: every run for a set of task IDs since a cutoff, with goal verdicts and transcripts, into one JSON file. Pages per task and reports what it could not fetch.
- `scripts/summarize.ts`: per task x environment cell, correctness passes/attempts (as scored and adjusted), recorded goals separately, Wilson 95% interval, median and IQR of time among passes, cost.

## Prerequisites

- `tpc` CLI authenticated as a member of the target org (`tpc auth whoami`); every scoped command takes `--scope <org-slug>/<product-slug>`.
- Read access to whatever the tasks touch, so verdicts can be checked against real state.
- `bun` for the scripts.
