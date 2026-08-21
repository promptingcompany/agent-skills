---
name: writing-benchmark-tasks
description: Task-generation tactics for head-to-head benchmarks — dimension-first design, the vendor mandate preamble, trap tasks, category playbooks, cross-arm equivalence.
---

# Writing Benchmark Tasks

All of setup-experiment's [writing-prompts.md](../../setup-experiment/workflows/writing-prompts.md) rules apply (intent not implementation, self-contained, one ask, junior-dev voice, never leak the answer key). This file adds what benchmarks need on top.

## Task-generation sources (pick by what the user gives you; combine freely)

1. **Dimension-led (default, top-down):** from the brief's dimension + persona, via the
   category playbooks below — core jobs + stress tests + traps. Use when the user names a
   dimension ("we're better at fresh finance data").
2. **Use-case-led (bottom-up, Optima-style):** the user describes ONE concrete workflow,
   optionally with example inputs (sample files, a docs link, a model answer). Decompose it
   into: (a) the whole job end-to-end as one task, (b) its constituent capability steps as
   separate tasks, (c) input variations. Example files become task inputs (in-prompt content
   or init files); a provided "great output" example becomes judge-side criteria material —
   never shown to the agent. Ask for it explicitly: "have a sample input or an example of a
   great output? Tasks and rubrics get derived from it."
3. **Topic fan-out (the one-liner amplifier):** when the request is one job shape on a domain
   ("financial deep research on X"), instantiate the SAME task template across 5–10 concrete
   topics in that domain (each topic = one task, identical criteria and artifact schema).
   This turns a one-liner into a battery with real sample size while keeping cross-arm and
   cross-task comparability. Pick topics with verifiable, dateable answers; reserve 1–2
   fan-out slots for traps (a stale-answer topic, a fictional-entity topic).
4. **Demand-led:** council clusters / prompt data where the org has them (the suggest path).
5. **Repo-led:** a pinned vendor benchmark repo (provenance `vendor_repo`).

Whatever the source, every generated task still passes the design question and checklist below.

## The one design question

**Would the two vendors plausibly differ on this task, on the brief's dimension?** A task both vendors ace teaches nothing; a task both fail teaches nothing; a task that differs for reasons unrelated to the dimension pollutes the story. Design each task by naming, in one line, *why* the vendors should separate on it — that line goes in the plan the user approves. If you cannot write that line, cut the task.

## Structure of every benchmark task prompt

```
[VENDOR MANDATE PREAMBLE] + [the job, junior-professional voice] + [SOURCING SUFFIX]
```

**Vendor mandate preamble** (branded arm — fill the vendor):

> "Use {Vendor}'s search API for all web lookups in this task — an API key for it is available in the environment; inspect the available environment variables to find it. Do not use any other search provider."

Adapt "search API" to the vendor's product type (data API, email API, …). Never hint the exact env-var name, endpoint, or SDK call — discovering the path is part of the measurement.

**Sourcing suffix** (any research-flavored task):

> "For every claim in the file include the source URL and that source's publication date. If something can't be verified from your search results, write that in the file instead of guessing."

**Artifact requirement:** every task ends in a named file (`funding.md`, `resolved.csv`). Sandboxes tear down at agent exit; only artifacts are scoreable. Structured artifacts (fixed columns, required fields) push scoring up the deterministic ladder — prefer them.

## Tactics

**Dimension-first windows.** Give every time-sensitive task an explicit recency window matched to how fast its truth moves: 48h (news), 7d (market moves), 90d (regulatory), most-recent-event (rate decisions, filings). The window goes in the weighted criterion, not the prompt.

**Trap tasks (include 1–3 per battery).**
- *Stale-answer traps:* ask about something whose answer changed recently (an executive who changed, a product that repriced). The judge-side key records both the stale and the current answer; surfacing the stale one as current fails. This is the single most discriminating freshness instrument.
- *Fabrication bait:* tasks whose plausible answer is easy to construct without retrieving (an SEC EDGAR URL, a GitHub repo path). The no-fabricated-citations gate catches agents that pattern-generate instead of retrieve — a real failure we caught in production (an agent constructed a plausible sec.gov URL that never appeared in its logs).
- *Honest-empty traps:* a question whose correct answer may be "nothing found" (no regulatory action in the window). Criteria reward the honest empty + the queries run, over padding with stale items.

**Judge-side answer keys.** Expected answers live ONLY in goal descriptions (the agent never sees goals). The judge cannot browse, so keys must be verifiable from the artifact ("cites the July 28–29 FOMC decision") — and keys for a publishable run are verified by a human on run day, because truth moves. Anything requiring the live web to verify goes to the offline checker, not a goal.

**Cross-arm equivalence.** Arms differ by exactly two strings: the vendor name in the preamble and (if unavoidable) vendor-specific docs links. Everything else — job, artifact name, criteria, thresholds — identical, or the comparison is unfair and the benchmark unpublishable. Generate arms from one template, never by hand-editing copies.

**Battery composition (8–12 keys).** Roughly: 4–6 core jobs of the persona (the bread and butter), 2–3 dimension stress tests (tightest windows), 1–3 traps. Avoid tasks that need a browser, an account signup on the vendor's site mid-run, or > 30 minutes.

**Difficulty ladder (anti-ceiling rule).** Tier the battery easy/medium/hard and tag tiers in task descriptions. If every capable vendor is expected to clear a task, it establishes capability but won't discriminate — that's what the hard tier is for: multi-step chains, adversarial targets, scale (many pages/records), recovery-under-pressure. A battery whose scores all land at ~100 has measured the floor, not the frontier; the unbounded metrics (cost, time, calls, tokens) then carry the comparison (see the saturation rule in criteria-and-gates.md), but the next battery version should raise the hard tier. Production example: an 8-task extraction battery scored 96–100 on all three arms — capability parity — while cost spread 1.4× and speed 1.6×; the report's story was efficiency, and battery v2 needed harder tasks.

## Category playbooks

- **Search/retrieval APIs:** research jobs with dated citations; windows do the discriminating; traps = stale-answer + fabrication bait. (The validated playbook — Finance Freshness V1.)
- **Devtool SDKs/APIs:** integration jobs — first successful call, pagination sweep, webhook verification, error recovery after a 429/4xx. Discriminators: hallucinated-endpoint rate, retries, time-to-first-success. Gates unchanged; "vendor adherence" becomes "used the mandated SDK/API."
- **Data/enrichment APIs:** entity-resolution jobs with structured output schemas; traps = fictional entities (correct answer: not_found; any concrete fact = fabrication fail).
- **Anything requiring the vendor's web signup mid-run:** out of scope for a benchmark task — provision credentials in the environment instead; signup UX is a usability study (setup-experiment), not a vendor benchmark.

## Pre-create checklist (per task, both arms)

- [ ] One line stating why vendors should differ on it, tied to the brief's dimension
- [ ] Mandate preamble + sourcing suffix present; no env-var/endpoint leaks
- [ ] Ends in a named artifact; structured where possible
- [ ] Window matched to how fast this truth moves
- [ ] Identical across arms except the vendor strings
- [ ] Goals attached from [criteria-and-gates.md](criteria-and-gates.md) templates, keys judge-side only
