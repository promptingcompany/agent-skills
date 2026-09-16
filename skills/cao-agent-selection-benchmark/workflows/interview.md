---
name: interview
description: Intake interview — the six questions that decide the study type, reader, vendor, use-case source, rivals and where runs live
triggers: intake, what kind of study, who is the reader, which org
---

# Intake interview — Phase 0

Six questions. Ask them in two groups, in plain language, and read the answers back before moving on.
Everything else in the study is a default the operator can change later; do not turn defaults into
questions.

## Group 1 — What kind of study, and for whom

**1. Is this about one vendor, or about a whole category?**
- *One vendor* ("for AgentMail", "for Kelly's account") → vendor-tailored: unbranded lanes plus labeled
  cells that name the vendor. The report is addressed to them.
- *A category* ("what do agents pick for email", "a market map") → category study: everything
  unbranded, neutral readout, no vendor addressed.

**2. Who is the reader?** A prospect we're pitching, a paying customer, or us.
- Prospect → sales framing: the cover leads with their absence; the actions are the free consulting.
- Paying customer → baseline framing: "here is what we're seeing; these are the cells we re-read."
  Periodic by default.
- Internal → neutral, counts only.

## Group 2 — The vendor and the field (skip for a category study)

**3. Vendor name, and the one sentence that says what it does for the user.** ("An inbox per agent,
created by API.") That sentence becomes the added requirement in the twin pair.

**4. Where does the vendor list its use cases?** Fetch `<site>/sitemap.xml` and list `/use-case/`,
`/solutions/`, `/build/` URLs. Those pages become the real-job tasks and the report can say "jobs taken
from your own use-case pages". No such pages → take the jobs from docs quickstarts and say so in Method.

**5. Which rivals, and which one is the incumbent they most often lose to?** 3–6 names. The incumbent
becomes the head-to-head ("we already use X, can it do this?") and the planted objection in the probe
("my cofounder says just use our existing X"). Check the list against `tpc org list`: if a rival is a
TPC client, note it — the report's voice stays "who holds the space", never "who failed", and the
account owner sees the PDF before the client does.

## Group 3 — Where it runs

**6. Paste the dashboard link for the org and product that should hold the runs.**
`https://app.promptingco.com/<org>/p/<product>/simulation` → `python3 scripts/tpc_helpers.py resolve
<url>` gives the slugs. Runs execute in platform sandboxes, never locally, and only through
experiments. Note whose org it is: the client's own org means they can open every transcript behind
every quote — say so in the send note rather than let them discover it. No link → ask for org and
product names and confirm with `tpc org list` / `tpc product list`; not a member → stop at Phase 3
until the platform owner adds the operator.

## Defaults to state, not ask

- Models: the newest Claude and newest OpenAI the harness accepts (last known-good `claude-opus-5`,
  `gpt-5.6-sol`). Two envs, k=3.
- Battery: 15 tasks from the composition table for the study type.
- Cost and count are stated at Gate 3 from the actual task count, before anything fires.
- Time: runs finish in 1–3 hours; analysis and report take about a day.
- Someone at TPC reads the PDF and TLDR before they leave the building; the operator says who at Gate 6.

## What the operator sees at Gate 0

```
## Intake
type: vendor-tailored | reader: paying customer (Binoy, AgentMail)
vendor: AgentMail — an inbox per agent, created by API
use-case source: agentmail.to/use-case/* (15 slugs, sitemap 2026-09-16)
rivals: Resend* (incumbent), Postmark*, Mailgun, SendGrid, Gmail API, Nylas   (* = TPC client)
runs: agent-mail / agent-mail (client's org — send note says they can open every run)
defaults: claude-opus-5 + gpt-5.6-sol · k=3 · 15 tasks → cost stated at Gate 3
```

"Anything wrong here?" Proceed on a clear yes.
