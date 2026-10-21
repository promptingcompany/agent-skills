# Sim Mode

A rigor mode for agent-simulation experiments on The Prompting Company platform. It keeps grader bugs, shared-fixture leaks, sandbox failures and judge quirks out of the numbers you report.

Structured as one mode skill that routes to small single-rule principles and step-by-step playbooks: read the principles, match a playbook, copy its steps.

## Principles

| Group | Principle | Applies when |
|---|---|---|
| Instrument | The platform verdict is an intent | accepting or overturning any verdict |
| | Prove the instrument | before the first scored run, after any grader change |
| | Fixtures must not leak | seeding data, writing graders |
| | Isolate shared fixtures | tasks with side effects running in parallel |
| | Separate correctness from recorded | designing goals, computing rates |
| Triage | Infrastructure is not a result | a run failed before the agent acted |
| | Every failure has a cause | any failing correctness goal |
| | Report both numbers | triage changed a verdict |
| | Agent safety is separate | an agent did something harmful |
| Design and findings | Real jobs, not setup | writing prompts |
| | Widen before deepen | choosing configurations after a baseline |
| | Stated versus implied | a capability goes unused |
| | Counts carry denominators | any number |
| | Speak the spec | the client has a benchmark spec |

## Playbooks

| Playbook | Use it to |
|---|---|
| Design tasks | write real-job prompts, leak-proof fixtures and split goals |
| Prove the graders | test every grader on reference solutions, then validation runs |
| Run and triage | widen configurations, pull completely, rerun infrastructure, classify failures |
| Explain and audit | audit recorded verdicts, count behaviour, write findings |
| Report against the spec | map to the client's evals and publish scorecard-shaped tables |

## Scripts

- `scripts/pull-runs.ts`: complete run pull with verdicts and transcripts.
- `scripts/summarize.ts`: per-cell as-scored and adjusted pass rates, Wilson intervals, time among passes, cost. Every adjustment must carry a reason.

## Where it sits

setup-benchmark or setup-experiment designs the experiment; sim-mode proves, runs and verifies it; analyze-experiment turns verified runs into a friction report and client PDF.

## Install

```bash
cp -r skills/sim-mode ~/.claude/skills/
```

See [`INSTALL.md`](INSTALL.md).
