---
name: benchmark-design
description: >
  Methodology for generating a rigorous, demand-ranked usability benchmark — a
  two-arm friction delta over a task universe mined tool-agnostically from the
  whole ecosystem and proven comprehensive by source saturation. Use this when
  the deliverable is a defensible, board-level measurement of whether an
  agent-skill helps, not a quick exploratory experiment.
---

# Usability Benchmark Design

This is the high-caliber path for generating tasks. The default Path B in
[`setup-experiment.md`](setup-experiment.md) suggests tasks from a product's own
docs — fast, but it tests **the feature list, not the problem space**. This
workflow tests everything developers *actually do*, weighted by demand, and
measures whether the skill moves the needle.

Use it when the experiment is a deliverable to a customer (an ROI proof, a
roadmap input, a published benchmark), not a quick internal probe. It is more
work; do not invoke it for a 4-task smoke test.

---

## The two moves that matter

Everything below follows from two principles. Get these wrong and the benchmark
is theater.

### 1. Measure the delta, not the pass rate

Run every task **twice, frozen**: **skill-OFF** (the friction floor — what the
agent already does unaided) and **skill-ON** (skill/docs attached). The per-stage
**delta** is the result. A skill-ON pass rate of 100% is meaningless on its own —
it can't distinguish "the skill helped" from "the model already knew." A skill
that only re-wins what the agent already did has delta ≈ 0. A single-arm harness
scores it 100% and learns nothing.

→ On the platform this is two **environments**, identical harness + model,
differing only by a skill/docs attachment toggle (the same mechanism the
docs-vs-no-docs template uses). **Hold the model fixed in Phase 0**; add models
later as controlled deltas, never as a confound mixed into the first arm.

### 2. Test the problem space, not the feature list

If you enumerate tasks from the product's flags and subcommands, you only ever
test what the vendor already built — you are structurally blind to the popular
task they have no answer for. So mine the task universe **tool-agnostically**:
how does the *whole ecosystem* solve this problem class, regardless of which tool
they use? Then prove completeness by saturation (below).

---

## Step 1 — Mine the task universe (tool-agnostic)

Pull the universe from **three methodologically independent corpora**. They must
be mined separately — independence is what makes the comprehensiveness claim
hold.

| Corpus | What it is | What it gives you |
|---|---|---|
| **A · Galleries** | Competitor/ecosystem example galleries & cookbooks (e.g. for RAG: LlamaIndex, LangChain, Haystack, Unstructured) | A pre-clustered map of what developers actually build |
| **B · Hard counts** | StackOverflow tag volumes, GitHub stars + issue-reaction counts | The frequency denominator — auditable, not vibes |
| **C · Discourse** | HN points/comments, Reddit, blogs | Emergent pain points + trend direction the structured sources miss |

Mine each independently, then merge into **workflow clusters** (a cluster is one
job-to-be-done, e.g. "PDF/doc parsing → clean text", "reranking", "hybrid
retrieval"). Tag each cluster to the pipeline stage it lives in
(extract / ingest / embed / index / retrieve / rerank / cite / evaluate / ops).

## Step 2 — Prove it's comprehensive by saturation

Comprehensiveness is **measured, not declared**. The proof is **convergence**:
when all three independent corpora surface the same core clusters and the same
long tail, and fresh mining stops surfacing new clusters, the space is covered.
That convergence is the exhibit you show the customer. Report cluster frequency
with `n=` and named sources per cluster — never "felt common."

## Step 3 — Rank by demand and tier

Rank clusters by demand using the three signals from Step 1, then bucket:

| Tier | Meaning | Sampling depth |
|---|---|---|
| **CRITICAL** | Demand peak + the customer's differentiator | Full depth (3 tasks/cluster) — publishable CIs |
| **HIGH** | Strong demand across all three corpora | Order-of-rank depth (2 tasks/cluster) |
| **MEDIUM** | Real but secondary; trend-watch (rising areas) | Coverage (1 task/cluster) |
| **LOW** | Long tail — strategic-but-rare | Floor (1 task/cluster) so it still registers |

**Sample proportional to demand, floor the long tail.** Over-weight the demand
peak; keep a single task on rare-but-strategic clusters so a known product gap
still produces a data point. Flag any **strategic threat** cluster — a rising
approach that routes *around* the product entirely — and measure it as its own arm.

## Step 4 — Define "usable" as a 5-stage funnel

Score in **agent-native units** (turns, retries, hallucinated-API rate) — never
wall-clock (that's product latency) and never answer quality (that's product
quality, and it blames the vendor for a model property). Every attempt is tagged
to the **first stage it fails**:

| # | Stage | Passing question | Typical failure → fix |
|---|---|---|---|
| 1 | **Comprehension** | Right subcommand / entry point? | Picks a dev-only command or hand-rolls → fix: mapping |
| 2 | **Formation** | Valid call? | Stale model name, bad flag, `candidate-k < top-k` → fix: reference repo |
| 3 | **Execution** | Runs first try (creds pre-loaded)? | Empty/errored output → fix: verified e2e example |
| 4 | **Recovery** | Self-corrects with no human? | Loops / gives up → fix: parseable errors |
| 5 | **Efficiency** | Turns/tokens to first result | Gradient, not pass/fail → fix: one-shot pattern |

**⚠ Anti-spiral line.** Execution stops at **"ran + correctly-shaped output"**
(non-zero rows, citations present). The moment you grade whether the *answer* was
good, you've silently changed the question from *is the skill usable* to *is the
product good* — an unbounded scope that blames the vendor for the model. Keep the
line bright.

## Step 5 — Size the sample

Size backwards from confidence intervals. To separate two stages that differ by
~15 points needs **~30–40 decision events per cluster** (Wilson 95% CI). Each task
runs **both arms × k repeats** (k=2 baseline). Report per-stage rates with Wilson
95% CIs and explicit `n=`. Pass@1.

**Stage the spend.** Validate the whole pipeline — ground-truth capture + the
funnel — on the CRITICAL tier first (a few hundred runs), confirm the signal is
real, *then* widen to HIGH/MEDIUM/LOW. Do not pay for full breadth before the
funnel is proven on the demand peak.

## Step 6 — Ship each task with provenance, hide the answer key

Each task ships with four things: a **neutral prompt**, its **intent cluster**, a
**valid invocation space** (the correct call shapes, transcribed from the
vendor's current docs), and a **provenance row** (which sources, what `n=`).

**The agent never sees the bucket label, the intent cluster, or the answer key.**
Ground truth comes from the agent's **trace + emitted artifacts**, never a
self-judge. Comprehension/Formation are scored against the transcribed invocation
space; Execution/Recovery/Efficiency are deterministic counts. Stale model names
and flags rotate — re-verify the invocation surface before each engagement.

## Step 7 — The output is a demand-vs-supply map

The deliverable is not a leaderboard number. It's a map tagging every cluster:

- **served + usable** — the skill wins here (ROI proof)
- **served + unusable** — the capability exists but the agent can't drive it (ship the fix artifact: mapping, reference repo, e2e example, parseable errors)
- **popular + unserved** — high demand, no product answer (roadmap gap)

The "popular + unserved" bucket is board-level input the customer **cannot get
from their own single-arm harness**, because that harness only tests features
they already shipped.

---

## Mapping the design onto the tpc platform

| Design concept | Platform mechanism |
|---|---|
| Arms (skill-OFF vs skill-ON) | Two environments, identical `agentConfig`, differing only by the skill/docs attachment toggle |
| One model in Phase 0 | Same `model` in both environments; add models later as separate paired arms |
| 5-stage funnel + agent-native units | `signal-config.yaml` attached to the experiment (pattern / stats / llm extractors → fold → aggregate) |
| Anti-spiral goal (ran + correctly-shaped output) | A minimal per-task goal using `evaluationType: "script_judge"` (deterministic, exit-0 = pass) — **not** an `llm_judge` on answer quality |
| Comprehension/Formation vs invocation space | `script_judge` or pattern signals checking call shape against the transcribed valid-invocation space |
| Tiers (CRITICAL/HIGH/MEDIUM/LOW) | `tagIds` on each task; one tag per tier |
| k repeats | Re-run the task/experiment k times; aggregate across runs |
| Demand-vs-supply map | The friction report over per-cluster, per-stage arm deltas |

**`script_judge` note:** the deterministic-goal path requires the `script_judge`
feature flag on the organization. Scripts are LLM-security-reviewed at
registration. Confirm the flag is enabled before committing to deterministic
scoring; otherwise fall back to `llm_judge` against the invocation space and flag
the self-judge caveat in the report.

When writing the neutral prompts and the minimal goals, follow
[`writing-prompts.md`](writing-prompts.md) — especially the rules on never
leaking the bucket/answer key and on holding the anti-spiral line in goals.

---

## When NOT to use this workflow

- Quick internal probe, < ~10 tasks, no customer deliverable → use Path B's
  fast docs-based suggestion instead.
- You only need a model leaderboard on a fixed task set → use the Leaderboard
  template.
- No skill/docs artifact exists to attach → there is no skill-ON arm; either
  build the artifact first or run a model leaderboard until one exists.
