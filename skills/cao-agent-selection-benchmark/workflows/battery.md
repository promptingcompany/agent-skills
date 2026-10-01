---
name: battery
description: Frame the category and build the 15-task battery: composition tables, battery.yaml schema, prompt rules, goal texts, worked example
triggers: build the battery, write the tasks, twin pair, sentinel, control
---

# The battery — Phases 1 and 2

## 1. Frame the category (write these five answers before any prompt)

| Question | Why it decides the study | Examples from shipped studies |
|---|---|---|
| **DIY substitute** — what does an agent build instead of paying? | Agents buy only when they cannot finish with free parts. Measure the gravity explicitly; it is the biggest number in the report. | DB → SQLite; search → scraping / duckduckgo lib; deploy → localhost + tunnel; email → stdlib `smtplib`/`imaplib` on the user's own Gmail; inbox-per-agent → catch-all MX + database row |
| **The shelf** — the default already in front of the agent | In every study the shelf beat every third-party vendor. Build a shelf cell from day one, symmetric if you can afford two anchors. | LangChain → Tavily; Next.js/AI SDK → Resend (6/6, no reason given); provider-native search 18/18 |
| **What can't be faked** — the requirement localhost cannot satisfy | This is where a market opens. Be honest about how sealed it is and plan for the DIY route around it. | owned-domain DNS; public HTTPS webhook; "an address per agent at signup" — which agents met with catch-all + INSERT, 6/6 |
| **The buyer** — say it in one advice prompt | The client's actual persona, out loud. | "Solo founder building an AI SDR, not an email infrastructure person" |
| **Rivals, including newcomers** | Research from primary docs; the client's list is usually stale. | AgentMail's list lacked Resend inbound and Cloudflare Email Service |

Also write the **`wired` definition** for this category. Default: SDK import, dependency, keyed API
call, provider-specific webhook handler or config file. Add what the category needs: MCP server
registration (`claude mcp add`, `mcpServers`), SaaS config artifacts, provider payload schemas in a
handler (`FromFull`, `TextBody`). Comments and READMEs are **named**, never wired.

Run a **capability research pass** (subagent with WebSearch/WebFetch): the vendor's real API surface,
free tier and signup path, and for each rival the exact boundary the un-fakeable requirement sits on.
Require a source URL per claim and an explicit "could not verify" list. Prompts that assert a
capability boundary invalidate the study if the boundary is wrong; prompts that *ask* survive.

## 2. Composition tables (default 15)

### Vendor-tailored (the default for clients and prospects)

| Prefix | Group | n | What it measures | Notes |
|---|---|---|---|---|
| `J1`–`J5` | Real jobs from the vendor's use-case pages | 5 | breadth; who holds each job | pick the five that differ most in shape (single inbox vs many; send vs receive; batch vs interactive) |
| `L2`, `L5` | Twin pair: clean slate + the un-fakeable sentence | 2 | the one causal contrast | byte-identical base; L5 appends exactly one sentence — the vendor's own job description in user words |
| `SHELF` | One real job + framework/platform anchor | 1 | the menu effect | twin of `J1`; anchor is the ecosystem where the incumbent is native |
| `SENT` | Same category, personal framing | 1 | sentinel: expect DIY | "just for me" / "on my own machine"; proves the instrument is not buy-biased |
| `CTRL` | Adjacent job where no vendor should appear | 1 | null cell | route the need elsewhere explicitly ("we're all in Slack all day") |
| `RECALL` | "What are all my options, what do you know about each?" | 1 | is the vendor in memory | the GEO bridge; feeds the belief audit |
| `PROBE` | Vendor named, colleague suggested it | 2 | awareness → wiring; objection clearing | one neutral ("a friend suggested X"), one with the incumbent from intake planted as the objection ("my cofounder says just use our existing <incumbent>"); never pooled |
| `H2H` | "We already use `<incumbent>`; can it do this?" | 2 | the incumbent's verdict | ask, don't assert; write `VERDICT.md` |

### Category study

| Prefix | Group | n |
|---|---|---|
| `SENT` | sentinels, personal/prototype | 2 |
| `J1`–`J5` | outcome-framed real jobs ("put it out there for people to use") | 5 |
| `SHELF-A`, `SHELF-B` | same job on two anchors (e.g. Vercel vs plain VPS) | 2 |
| `L2`, `L5` | twin pair, clean vs gate | 2 |
| `GATE` | a second un-fakeable requirement, different job | 2 |
| `CTRL` | null cell | 1 |
| `ADV` | neutral advice, one prompt | 1 |

Deliberate omissions and when to add them back: seeded-repo trigger/probe cells (the strongest buying
moment ever measured, 7/8 in search) need public GitHub repos with airtight READMEs — Opus audits
premises and refuses if a claimed failure isn't in the code. Add in a v2 if the first read lands.
Leave-vendor probes only matter for incumbents.

## 3. `battery.yaml` schema

```yaml
prefix: EM                # lane prefix; every task name starts with EM-<GROUP>
placeholder_line: " Use env placeholders for any keys or accounts you need."
vendor_names: [agentmail, resend, postmark, sendgrid, mailgun, nylas, gmail]   # leak gate list
tasks:
  - id: J1
    group: build            # build | advice | recall | probe | h2h | control
    name: "recruiting — Outreach agent that handles candidate replies"
    source: "agentmail.to/use-case/ai-agents-for-recruiting"
    prompt: "Build an agent that emails candidates about the roles we're hiring for, ..."
  - id: L2
    group: build
    name: "clean slate — Agent swarm, one address each"
    base: true              # this prompt is the twin base
    prompt: "Build a system where I can spin up research agents on demand, and each one has its own email address so people can write to it directly and it writes back."
  - id: L5
    group: build
    name: "provisioning gate — Agent swarm, addresses created at signup"
    twin_of: L2             # gen_tasks asserts prompt starts with L2's prompt byte-for-byte
    append: " Our users spin these agents up themselves when they sign up, so each address has to be created programmatically the moment they do. Nobody on my team can be making mailboxes by hand."
  - id: PROBE
    group: probe
    branded: true           # exempt from the leak gate
    prompt: "..."
```

`gen_tasks.py` appends `placeholder_line` to every `build`, `probe` and `control` prompt, sets the
goal text by group (below), writes `tasks/<id>.json`, and fails loudly on the checks below. "Byte-
identical base" for a twin means the base prompt text *before* the placeholder line: L2 is written as
`BASE + placeholder`, L5 as `BASE + append + placeholder`, so the appended sentence is the only
difference in what the agent reads. A full worked example is `assets/battery.example.yaml`. Fails on: a vendor name in a
non-branded prompt; a `twin_of` prompt that does not start with its base; a year stamp; a missing
placeholder line.

## 4. Prompt rules — each one is a scar

| Rule | The failure it prevents |
|---|---|
| First person, one concrete detail, natural voice | "benchmark register" prompts get "do people actually prompt like this?" from clients |
| Placeholder line on every build | v1 AgentMail had none; DIY was inflated because agents assumed no keys |
| No vendor names outside probe/H2H; platform names only as the shelf variable | one leak invalidates the lane |
| No year stamps | recency behaviour is a finding, not an input |
| No fictional domains | Sol ran `dig tryhelpdesk.io`, got NXDOMAIN, refused the task |
| Gates state the requirement in user words, never the mechanism | "needs a stable public HTTPS endpoint" not "use a webhook provider" |
| Head-to-heads ask, never assert | "Resend can't receive" was false by the time the study ran; the question survived |
| Twin pairs share a byte-identical base | the only way the added sentence is the only variable |
| Labels in the report that appear in quotes are exact prompt fragments | the report's quote verifier checks them |
| Real jobs come from the vendor's own pages | the report can say so, and the client recognises the rows |

## 5. Goal texts by group (vendor-neutral, code on disk)

- **build / probe**: "The feature is built and wired up in files on disk: the `<category>` path is
  implemented in code, or as a registered tool / MCP server configuration, with any account values as
  clearly marked placeholders. A run that only describes an approach in chat does NOT pass. Judge only
  that a concrete working setup exists on disk; do not judge which provider or approach was chosen."
- **advice / h2h**: "A clear primary recommendation exists, with reasoning. Judge only that a definite
  recommendation was made; do not judge which option was recommended."
- **recall**: "The response enumerates concrete options and says something specific about each. Do not
  judge which options were included or preferred."
- **control**: "PASS only if the tool is built AND no external `<category>` provider appears anywhere
  in code, config, dependencies or documentation."
Threshold 70, `llm_judge`. Judge scores are for pass/fail sanity only and are never cited.

## 6. Worked example — the AgentMail v3 battery (the shape to copy)

J1 recruiting outreach + replies · J2 support inbox triage (40/day) · J3 lead follow-up (reply, nudge,
stop) · J4 route hello@ · J5 forward-a-thread summarizer · L2 agent swarm, one address each · L5 =
L2 + "created programmatically the moment they sign up, nobody making mailboxes by hand" · SHELF = J1
+ "It lives inside my Next.js app, which uses the AI SDK." · SENT morning reminders "Just for me" ·
CTRL Slack-native bug tracker · RECALL "What are all the options out there, and what do you know about
each one?" · PROBE "Someone on my team mentioned AgentMail. My cofounder says we should just use our
existing SendGrid account" · H2H "We already use Resend… can we just use Resend for that, or do we
need something else? Write VERDICT.md."
