---
name: criteria-and-gates
description: Verbatim gate and criteria templates, the aggregation doctrine (gate-zeroing, arm-void, no-winner-in-noise), the snapshot JSON schema, and the offline checks.
---

# Criteria & Gates

The scoring layer is what makes a benchmark citable. Two species of criteria, never mixed:

- **Gates** — pass/fail prerequisites. Failing any gate zeroes the task in aggregates. Phrased as strict yes/no decisions because judges given 0–100 scales award 95s to near-misses against binary thresholds (observed in production: a gate scored 95/100 while the judge's own reasoning said the check passed).
- **Weighted leveled criteria** — quality dimensions, averaged only across gate-passing runs. Each level is a falsifiable condition, not a vibe.

## Gate templates (verbatim — fill {Vendor} and {artifact})

Every benchmark task carries these three. `evaluationType: llm_judge`, `passingThreshold: 100`, `scoringMethod: binary`.

**GATE: Artifact produced and complete**
> "Answer this as a strict yes/no decision. YES only if ALL of: the file {artifact} exists in the run outputs, is non-empty, and contains an entry for every item the task requested. Formatting, ordering, and style differences are irrelevant. If YES score exactly 100. If NO score exactly 0. No other score is valid; do not award partial credit for near-misses."

**GATE: Mandated search vendor used**
> "Answer this as a strict yes/no decision. YES only if every substantive web retrieval visible in the agent's code and logs went through {Vendor}'s search API. Directly opening a URL that {Vendor}'s results returned still counts as YES. Any use of a different search provider or search-engine scraping for new material means NO. If YES score exactly 100. If NO score exactly 0. No other score is valid."

**GATE: No fabricated citations**
> "Answer this as a strict yes/no decision. YES only if every URL cited in {artifact} also appears somewhere in the run's logs or tool outputs as actually returned or fetched. If even one cited URL never appears in the run, the answer is NO. If YES score exactly 100. If NO score exactly 0. No other score is valid."

Adapt gate 2's wording to the vendor's product type (SDK, data API). Add at most one task-specific gate when a task has a hard prerequisite (e.g. "output parses as valid CSV with all 25 ids"), using the same yes/no phrasing shape.

## Weighted criteria templates

`evaluationType: llm_judge`, `scoringMethod: weighted_average`, thresholds 60–70.

**Source dating discipline** (threshold 70)
> "Every claim in {artifact} carries a source URL and an explicit publication date for that source. Full score: all claims dated. Partial: most claims dated, a few missing dates. Fail: claims presented as fact with no source or no date."

**Recency window respected** (threshold 60; fill the window)
> "Judged only from what is written in {artifact}: {window statement, e.g. 'the cited news sources must have publication dates within the 7 days before the run; older items must be explicitly labeled historical'}. Full score: the dating in the artifact satisfies this. Partial: mostly satisfied with labeled exceptions. Fail: the artifact's own dates violate the window or the time-sensitive elements are undated."

Write task-specific criteria in the same leveled shape: name the full-score condition, the partial condition, the fail condition — all checkable from the artifact/logs. Blind the judge: criteria text never frames a vendor as "ours"/"the client" and never mentions the comparison.

## Aggregation doctrine

1. **Arm validity before any comparison.** A gate failing on ~100% of one arm's runs = infrastructure failure (dead key, quota, outage): VOID the arm, never report it as a vendor result. (Production example: an arm went 0/8 because its API credits were exhausted.)
2. **Gate-zeroing.** A task run failing any gate contributes 0 to that arm's aggregates. Report gate-failure *reasons* separately — a real fabrication is a finding about the run, not noise.
3. **Near-miss triage.** On every gate failure, read the judge's `details`. Reasoning contradicting the verdict = calibration issue: log it, exclude from vendor conclusions, fix the phrasing. Reasoning supporting the verdict = real: report it with the quote.
4. **k rules.** k=1 → output labeled "pilot, directional only," no winners declared, period. k≥3 → mean ± stderr per cell; a difference is reportable only when intervals don't overlap; ties are reported as ties.
5. **Join by task key**, per stack. Vendor comparisons are always within-stack; never average across stacks (it blends the vendor effect with the model effect). With a multi-stack panel, add the **cross-model consistency** metric: for each task and vendor, on how many of the panel's stacks does the vendor lead? "Wins on 3/3 stacks" is the strongest sentence a panel can buy; "wins on 1/3" is a model-dependent result and must be reported as such.
6. **Cost and latency come from run records**, not estimates: costUsd and duration per run, totals and medians per arm. Also extract the **effort metrics** every run already carries — tool calls/turns and tokensUsed — and report cost-per-successful-task (cost conditioned on gate-passing) alongside raw cost.
7. **Saturation rule.** When cross-arm mean-score variance is small (roughly < 3 points), the scores have hit the battery's ceiling: capability is established, and the comparison lives in the unbounded metrics (cost, duration, tool calls, tokens). The report must then lead with the efficiency/cost cuts and say so explicitly ("all arms cleared the battery; the difference is effort and price") instead of presenting near-identical scores as the story. Ceilinged scores are a finding, not a failure — but only if reported as such.
8. **Static agent-readiness audit is a separate cut, never blended into the behavior score.** A checklist row per vendor (llms.txt, MCP server, typed SDK, OpenAPI docs, CLI, agent-skills) is cheap and high-interest — report it as its own section. Blending static surface into measured behavior (as some competitors do at fixed weights) is a category error that lets documentation points mask execution failures.

## The canonical economics metric

**Total cost per completed task = (agent cost: model tokens + sandbox) + (vendor bill: API
credits/calls), ÷ successful completions.** Report both ledgers separately AND summed;
condition on success (failures inflate the effective rate, they never reduce the bill).
This is the buyer's actual question — "what does it cost to get this job done?" — and it can
invert single-ledger rankings: a pricey API that finishes in one call beats a cheap API that
forces fifteen retries. It is also the machine-labor rate for the task: benchmarks reporting
it are building the rate card. Raw per-attempt cost stays as a secondary column.

## Attribution signals (extract from run logs — access verified in production)

The structured run log (`tpc sim run logs <run-id>`) contains every tool call with full
command, output, and millisecond timestamps. Extract per run, per arm:

- **Vendor API call count** and **vendor error rate** (HTTP codes/error bodies are in the tool outputs)
- **Retrieval completeness at source** — did the vendor's API return the needed content,
  separately from whether the agent assembled it (decomposes agent-fault from API-fault)
- **Vendor bill per task** — the number a buyer actually pays (distinct from sandbox/model
  cost). Three tiers, use the best available per vendor and label the confidence:
  (1) *usage-delta bracketing* — read the vendor's usage/balance endpoint in preflight and
  again after the iteration; the delta is exact per arm-iteration (verified: Firecrawl
  `GET /v1/team/credit-usage`; Tavily `GET /usage`, which also breaks usage down by product —
  search vs extract — giving vendor-side adherence corroboration for free);
  (2) *per-call fields in logged responses* (Firecrawl `creditsUsed`; Exa `costDollars` where
  present) — per-task granularity from stored logs;
  (3) *rate-card × logged call counts* — universal fallback, labeled "estimated".
  Dedicated per-benchmark keys make deltas airtight.

  **Core principle: separate units from dollars.** Consumption units (calls, pages, bytes,
  seconds) are facts measured from logs; dollars are a pricing function applied on top. The
  report ALWAYS shows the units; the dollar column carries the assumption and a confidence
  label. Every estimate's derivation is printed in the report (a "How the vendor estimates
  are derived" block), and the vendor side is badged ESTIMATED until measured.

  **Hard pricing models:**
  - *Odd metering* (per-GB/page/minute/token): measure that unit from logged payloads and multiply.
  - *Flat subscription / seats* (no marginal cost): report TWO numbers — the plan floor
    ("this workload requires tier X") and marginal ≈ $0 within quota — plus cost-at-volume
    scenarios (e.g. 100 / 1k / 10k tasks per month), since per-task cost is volume-dependent.
    Never fake a single per-task figure for a subscription.
  - *Rate-limited free tiers*: the ceiling is the price — "free up to ~N tasks/month
    (measured calls-per-task × tier limit), then tier X."
  - *Quote-based/enterprise*: no invented number. Report measured consumption units
    prominently (the buyer's negotiation input); dollar cell reads "quote-based".
  - *Untrackable usage* (SDK-internal calls, batching): verbose SDK logging via env init;
    a counting proxy installed by init-commands (HTTP(S)_PROXY to a local tally — per-host
    connection counts without TLS interception); vendor dashboard before/after as manual
    fallback; gateway-mediated arm traffic as the deterministic endgame.
- **Time-to-first-vendor-call** and time-in-phase from event timestamps

## Offline checks (the judge cannot browse; these run post-hoc, before publishing)

- **Citation support:** fetch every cited URL; confirm it resolves and contains the claim; extract its publication date. Feeds a "claim-level source support rate" per arm.
- **Run-day currency:** compare artifact answers against the human-verified run-day answer key (the current CEO, the latest filing). This is where truth-against-the-world is scored — never in platform goals.
- Both checks append to the snapshot JSON as `offline_checks`, with the check date.

## Snapshot JSON schema (the skill's output; the publish template's input)

```json
{
  "family": "Finance Freshness V1",
  "snapshot_date": "2026-08-20",
  "iteration": 2,
  "provenance": "tpc_authored",
  "protocol": {"k": 1, "model": "claude-sonnet-4-6", "harness": "claude",
               "same_day": true, "judge": "llm_judge", "account_tiers": {"exa": "self-serve", "tavily": "self-serve"}},
  "arms": {"exa": {"experiment_id": "…", "environment_id": "…", "valid": true},
           "tavily": {"…": "…"}},
  "voided_iterations": [{"iteration": 1, "reason": "tavily arm API credits exhausted", "scope": "arm-level, not a vendor result"}],
  "tasks": [{
    "task_key": "latest_funding_lookup",
    "arms": {"exa": {"run_ids": ["…"], "passed": true, "score": 98, "cost_usd": 0.34,
                     "duration_ms": 98607,
                     "gates": {"artifact": true, "vendor_adherence": true, "no_fabrication": true},
                     "weighted": {"source_dating": 100, "recency_window": 95},
                     "judge_notes": ["…"]},
             "tavily": {"…": "…"}}
  }],
  "aggregates": {"exa": {"pass_rate": "6/8", "mean_score": 95.8, "total_cost": 2.17,
                          "median_duration_ms": 92000, "recency_mean": 95.6},
                 "tavily": {"…": "…"}},
  "calibration_issues": [{"run_id": "…", "gate": "artifact", "note": "judge scored 95 while reasoning said complete"}],
  "offline_checks": null,
  "limits": ["k=1: directional only", "…"]
}
```

Emit it into the benchmark folder on every analysis, valid or voided. It is the contract with the publish template, the input the future table UI consumes, and a row in the trace corpus.
