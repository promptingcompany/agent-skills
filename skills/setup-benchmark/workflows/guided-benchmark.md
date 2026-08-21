---
name: guided-benchmark
description: The main handholding flow — brief, competitors, plan approval, arms and preflight, creation, run, analysis, publish handoff. Every fork has a scripted ask and a never-block fallback.
---

# Guided Benchmark

Follow the steps in order. Confirm before creating resources or spending money. Never block on missing information — pull what the platform knows, web-search the rest, propose, confirm.

---

## Step 0 — Resolve and echo the context

```bash
tpc auth whoami --format json
```

> "You're in org **[org name]** ([slug]), product **[product]**. Benchmarks live in their own product. Continue here, switch, or create a benchmark product? (1) continue (2) switch (3) create new"

If creating: `tpc product create "<Name>" --domain <their-domain> --no-wait` — and explain the domain plainly: "use your own domain (e.g. exa.ai); it's just how the platform files the product, nothing gets published there."
 **Echo the resolved org slug and product slug back and get a yes before proceeding** — similarly-named orgs exist, the CLI has no product delete, and a resource created in the wrong org persists forever.

## Step 1 — The brief

> "What do you want to prove or compare? Three ways to start:
> (1) **I know** — a sentence works: 'we're better than Tavily at fresh finance data', or 'benchmark financial deep research on [topic]'
> (2) **I have a concrete use case** — describe the workflow and attach/paste any sample inputs or an example of a great output; tasks and rubrics get derived from it
> (3) **Suggest for me** — I'll look at what the platform knows about your product and propose benchmark angles"

**Path 2 (use case):** decompose per writing-benchmark-tasks.md source 2 (end-to-end task + constituent steps + variations); example outputs feed judge-side criteria only. One-liners naming a domain get the topic fan-out treatment (source 3): same task shape across 5–10 concrete topics — say so in the plan ("your one request became N comparable tasks across these topics — edit the topic list freely").

**Path 1 (knows):** parse the sentence into the brief object (SKILL.md schema): primary vendor, comparison vendors, dimension, persona. Read back the parsed brief for confirmation.

**Path 3 (suggest):** pull `tpc product get` (the domain analysis carries keywords, competitors, differentiators). If the org has model-council data, use its topic lanes and losing clusters as the demand signal. Then offer three angles, each tied to evidence:

> "Based on what I can see:
> 1. **Comparison moment** — agents asked '[category] X vs you' currently favor [competitor]. Benchmark: you vs [competitor] on [differentiator].
> 2. **Capability moment** — [top job from docs/keywords]: can agents complete it with you vs [competitor]?
> 3. **Category leaderboard** — everyone in [category] on [n] core jobs; you get the neutral table.
> Which one, or describe your own?"

Either path ends with a confirmed brief. If the user names a **vendor benchmark repo** to reproduce (provenance `vendor_repo`), record the repo URL and pin a commit SHA now — never accept "latest," and never agent-discover repos.

## Step 2 — Competitors

Pre-fill; never present a blank form:

> "Competitors I'd measure against, from [product analysis / council rankings]: **[A] ([a.com])**, **[B] ([b.com])**. Edit, add, or confirm?"

Two to three arms for a first benchmark. More arms multiply cost and provisioning load linearly — say so if the user piles on.

## Step 3 — Compile the plan (the step the user judges us by)

Draft the full battery per [writing-benchmark-tasks.md](writing-benchmark-tasks.md): 8–12 task keys designed to separate vendors on the brief's dimension, each with prompt + gates + weighted criteria per [criteria-and-gates.md](criteria-and-gates.md). Then present the PLAN in one message:

> "Here's the benchmark plan:
> **[Family name]** — [primary] vs [comparisons] on [dimension]
> **Tasks (N):** [one line each: name — what it separates and why]
> **Criteria per task:** 3 gates (artifact, vendor adherence, no fabricated citations) + [weighted criteria named, with the doc/evidence line each came from]
> **Arms:** [N vendors] × [model(s)] × k=[k] → **[total runs]**
> **Estimated cost:** ~$[0.25 × runs, plus 25% margin] and ~[runs ÷ 8 × 35]min wall time
> Approve, or tell me what to change (drop/add/reword tasks, change k or models)?"

Rules: the user can edit anything; drops are free; every criterion shows where it came from. k=1 default for a first run (say it will be labeled pilot); k=3 for publishable.

**Full-text inspection (offer, don't wait to be asked):** after presenting the plan, add:
> "Want the full text of any task prompt or rubric before I create these? Say e.g. 'show task 3' or 'show the gates' — you can reword, drop, or add anything."
On request, show the exact prompt and goal texts verbatim (the words the agent and the judge will see), apply edits, and re-show the changed item before approval. Never create resources while an edit is unresolved.

**Model panel (ask, don't silently default — resolve presets first per SKILL.md "Stack panels"):**

> "Which stacks should the benchmark run on? (A stack = the coding agent + model pair doing the work — like a driver for the test car. Same stacks on every vendor, so the vendor is the only variable. Resolved to what the platform supports today.)
> (1) **Frontier** — [resolved: e.g. Claude Opus 5 · GPT-5.5 · Kimi K2.6, native harnesses] — 3 stacks, 3× cost [recommended for publishable runs]
> (2) **Balanced** — [resolved: e.g. Claude Sonnet 4.6 · GPT-5.5] — 2 stacks, 2× cost [recommended default]
> (3) **Cheapest** — [resolved: e.g. Claude Sonnet 4.6] — 1 stack, 1× cost [recommended for k=1 pilots]
> (4) **Custom** — tell me how many and which"

The bracketed lineups are RESOLVED at ask time, never recited from this file: newest supported
model per lab, verified against known-good environments, with unverified-newer IDs flagged and
validated at env creation. Recompute and show the cost line whenever the panel changes:
runs = tasks × arms × stacks × k. A panel means multiple environments per arm experiment (each
carrying that arm's vendor key); reporting stays within-stack, plus the cross-model consistency
headline ("wins on N/M stacks").

**Fork on stakes:** if the user says this will be published or sent to a customer, set k=3, note that run-day answer-key verification and the offline citation check are part of the protocol, and flag any vendor whose ToS prohibits published benchmarks (check before running, not after). **And state the honesty contract HERE, not at publish time:**

> "One thing to agree on before we spend money: methodology is fixed and every result publishes, including tasks where [competitor] wins — that's exactly what makes the page citable instead of dismissible as marketing. If the overall picture doesn't favor you, you choose whether the page ships at all (page-level decision), but never which rows appear. Good?"

Getting a yes to this before the run is what prevents the wobble when the where-each-vendor-led section arrives.

## Step 4 — Arms and credentials (preflight)

For each arm, resolve the credential:

> "Arm readiness:
> - **[Vendor A]**: [✓ key found in env … / needs a key — copy it from your dashboard, then run exactly this in your terminal and tell me:
>   `read -s "?paste key: " K && export [VENDOR]_API_KEY="$K"`
>   (read -s keeps it out of your screen and shell history) / needs an account — signup link + free-tier note]
> - **[Vendor B]**: …"

Rules learned the expensive way:

1. Sync secrets with `--from-env` only; never echo or paste values. If a key was ever pasted into chat, tell the user to rotate it after the study.
2. **Preflight before firing, per arm** — and preflight the *right things* (see the failure taxonomy below): call the SAME endpoints the tasks will use, not a generic ping; read the vendor's balance/usage endpoint where one exists (verified: Firecrawl `GET /v1/team/credit-usage`, Tavily `GET /usage`) and compare remaining quota against tasks × k × ~10 calls; flag free/dev tiers as burst-fragile. **Record the usage snapshot in creation-state** — the post-iteration re-read turns it into the exact vendor bill per arm (criteria-and-gates.md, Attribution signals).
3. Account provisioning at scale: default to the vendor's self-serve tier and disclose the tier in the methodology; spend-capped virtual cards; category-scoped account pool; the review-unit ask ("vendor provides a funded eval account or is measured on the public free tier, disclosed") once the benchmark has authority.

**Credential failure taxonomy** — every one of these WILL occur; detect at the earliest possible layer:

| Failure | Signature | Earliest detection | Remediation |
|---|---|---|---|
| No key set | secret missing on env; agent logs "no env var" | Step 5 (secret list check) | set the secret; re-verify |
| Wrong/revoked key | 401/403 on any call | local preflight | user rotates/re-exports key |
| No credits / exhausted quota | 402/429, "insufficient credits" | balance endpoint if present; otherwise CANARY | user tops up; re-preflight balance |
| Wrong plan (endpoint gated) | 402/403 on a specific endpoint while others work | preflight on the task's actual endpoints | upgrade plan or drop gated tasks, disclosed |
| Burst rate limits | 429s only under concurrency; single calls pass | CANARY at concurrency, or first completions in monitor | paid tier, staggered firing, or lower concurrency |
| Expired trial | as credits, often mid-run | balance endpoint / canary | convert account |

## Step 5 — Create resources

Write `<slug>-benchmark-state.yaml` first (family, arms, task keys, protocol, agent stack — see the cross-product workflow in setup-experiment for the state shape). Then create in this order, updating `<slug>-creation-state.yaml` after every step:

1. Tasks (all arms): `tpc sim task create --file <task.json>` — parse `id` OR `task.id`.
2. One environment per arm, identical agent config, `--task-ids` = that arm's tasks only. Parse `environmentId`. **This arm's env gets ONLY this arm's vendor key** (`tpc sim env secret set <env-id> --name <VENDOR>_API_KEY --from-env <VENDOR>_API_KEY`).
3. One experiment per arm: `tpc sim experiment create --name "<Family> - <Vendor> arm" --task-ids <arm tasks> --env-ids <arm env>`.
4. Verify attachment (`sim experiment get`: task count and env count) before running. Retry with backoff on rate limits.

## Step 6 — Run

> "Ready to fire: [N] runs across [arms], ~$[estimate]. All arms launch together (same-day protocol). Go?"

**Canary first.** Before the full battery: queue ONE cheap task per arm (`tpc sim run <task-id>` — it runs on the arm's linked env) and wait for it to complete. The canary catches everything local preflight can't: in-sandbox key injection, plan-gated endpoints, and quota behavior under real use. All canaries pass their retrieval gates → fire the full battery; any canary shows a credential-taxonomy signature → stop, remediate, re-canary. A $0.25 canary saved is a $2-per-arm iteration not burned (production example: a free-tier arm passed single-call preflight then died 0/8 on burst credit exhaustion).

On go: `tpc sim experiment run <exp-id>` for every arm back-to-back. For k>1, fire iteration 2..k only after the previous completes, all within the same day.

## Step 7 — Monitor

Poll `tpc sim experiment run status <exp-id> --format json` every 2–3 minutes (background). Runs go queued → running → evaluating → completed; a typical 8-task arm completes in ~35 minutes. **Watch for dispatch orphans:** a run showing `running` with an empty `sandboxId`, no logs, and no actions for >~8 minutes while other runs complete is orphaned (no cancel command exists) — queue a replacement for that exact cell (`tpc sim run <task-id> --environment-id <env-id>`); analysis takes the newest completed run per cell. **Watch for arm-failure signatures early:** as each arm's first completions land, spot-check one artifact/judge detail — if the credential-taxonomy signatures appear (credits, 401/403, 429), alert the user immediately and do not fire further iterations on that arm. Do not read full results until every run is terminal; experiment-level `results` may stay null until the iteration leaves `generating_results` — read run-level data via `sim run get` instead.

## Step 8 — Analyze

Per [criteria-and-gates.md](criteria-and-gates.md) aggregation doctrine. In order:

1. **Arm validity first.** Any gate failing on ~100% of one arm's runs = arm-level infrastructure failure (dead key, exhausted quota, provider outage). VOID the arm, tell the user why, offer to re-run after the fix. Never report an invalid arm as a vendor result.
2. Run `report/build_snapshot.py <creation-ids.json> "<family>" <snapshot.json>` — it pulls every cell (newest completed run wins), parses goals (`goalName`/`details`), extracts turns, and emits the snapshot skeleton with aggregates, per-stack tables, and cross-model consistency. Then FILL the brief/protocol placeholders and add vendor_bill per criteria-and-gates.md.
3. Join arms by task key. Compute per-arm: gate pass counts, weighted-criteria means, cost, duration. k>1: mean ± stderr per cell; no winner declared where intervals overlap.
4. Read the judge `details` on every gate failure — separate real violations (report them; they're the product working) from judge near-misses (log as calibration issues; exclude from vendor conclusions; fix the gate phrasing).
5. Emit the **snapshot JSON** (schema in criteria-and-gates.md) into the benchmark folder.

## Step 9 — Publish handoff

> "Snapshot ready. Output options: (1) head-to-head page (the standard: banner → headline table → per-task receipts → both-ways cards → methodology) (2) PDF export (house style) (3) snapshot JSON only."

The page template rules, non-negotiable: pilot banner whenever k=1 or any calibration caveat exists; every cell shows its run IDs; the where-each-vendor-wins section covers BOTH vendors; the methodology block auto-fills from the state file (provenance, arms, stack, date, k, gates, limits, experiment IDs, account tiers); voided iterations are disclosed in Limits.

## Failure paths (route, don't improvise)

| Symptom | Route |
|---|---|
| `Unknown agentConfig fields` | drop the named field, retry (CLI version drift) |
| Env/task create parse failure | check both `id` and nested/renamed id fields before assuming failure |
| One arm 0/N uniform failures | arm-void protocol (step 8.1) — check credits/key first, vendor never |
| Binary gate scored 60–99 | judge calibration near-miss: read `details`, log it, don't count it as a vendor result; verify gate phrasing matches the yes/no template |
| Results null after runs complete | iteration still `generating_results` — use `sim run get` per run |
| Rate limits during creation | backoff and retry; update creation-state so a resume skips completed steps |
| User wants R@k / ground-truth dataset benchmark | out of scope v1 — offer the workflow shape, log the request |
