# Setup Benchmark

Guided workflow to produce a head-to-head vendor benchmark on the TPC agent-simulation platform: same tasks, same agent stack, one arm per vendor, every number traceable to a run.

Sibling of [setup-experiment](../setup-experiment/) — reuses its prompt-writing rules and state-file conventions. Where setup-experiment answers "how do agents behave on my product," setup-benchmark answers "which vendor wins this job, provably."

## Workflows

| Workflow | Triggers |
|---|---|
| Guided Benchmark | "set up a benchmark", "benchmark X vs Y", "head to head", "versus page", "compare vendors", "prove we're better at" |
| Writing Benchmark Tasks | referenced from Guided Benchmark step 3 |
| Criteria & Gates | referenced from Guided Benchmark steps 3 and 8 |

## What it produces

1. A benchmark family: one TPC product hosting sibling experiments (one per vendor arm), tasks aligned by shared task keys, each arm's environment holding only its own vendor's API key.
2. A dated, immutable snapshot per run: scores, gates, costs, durations, run IDs.
3. A snapshot JSON that the publish template consumes: head-to-head page (banner → headline table → per-task receipts → both-ways cards → methodology block).

## Doctrine (non-negotiable)

- Gates before averages: fabrication, vendor adherence, and execution are yes/no gates; failing one zeroes the task.
- No number without a receipt; no winner inside the error margin; k=1 output is labeled pilot automatically.
- The competitor-wins section is mandatory on anything published.
- Arm-level failures (dead key, exhausted quota) void the arm — they are never reported as a vendor result.
