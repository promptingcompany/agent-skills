---
name: analysis
description: Phase 5: channels, wired/prescribed/DIY/hedged definitions, lane discipline, parser-defect ledger, quote sweeps, FINDINGS.md structure
triggers: analyze runs, what did agents wire, hand-audit, quote sweep
---

# Analysis — Phase 5

Transcripts are the source of truth. Signals, judges and analyst summaries are leads.

## 1. Channels (what `wired.py` does, never change `channels()`)

Each tool event is routed to one channel:
- **CODE** — write/edit payloads to non-doc files; shell heredoc bodies (`cat > f <<'EOF'`); Codex
  `apply_patch` bodies (`*** Add File:`); **unified diffs written to a temp file** (`+++ b/path`, split
  per file — a README inside `/tmp/patch.diff` once counted as wired); dependency installs; MCP
  registration commands (`claude mcp add`, `mcpServers`, `.mcp.json`).
- **DOCS** — files matching `.md|.txt|readme|/docs/|/memory/|.claude/` (Opus writes notes to its
  memory dir; they are not code).
- **PROSE** — assistant messages.
- **LOOKED** — everything else in shell: grep, ls, cat, curl. Evidence of looking, not building.

Whole-line comments are stripped from CODE before matching: an Opus run listed "SendGrid / Postmark /
Mailgun" SMTP hosts in a `# Examples:` block and registered three vendors.

## 2. Classification per run

| Outcome | Definition |
|---|---|
| **WIRED** | vendor pattern in CODE or deps, after comment stripping, and the hit survives hand-audit |
| **PRESCRIBED** (named) | vendor pattern in DOCS or PROSE only |
| **DIY** | a LOCAL pattern (stdlib SMTP/IMAP, SQLite, scraping…) in CODE |
| **HEDGED** | ≥2 vendors WIRED behind a switch; counts toward "any vendor" and toward **no single vendor** |
| **research** | a web tool call in LOOKED **or** a citation marker in PROSE/DOCS (`utm_source=openai`, `utm_source=chatgpt.com`) |

Two regex sets, never one: **`VENDOR`** for CODE is anchored to product surfaces (SDK import, env-var
prefix, API host, package.json dep, install command, provider payload fields). **`PROSE_VENDOR`** for
DOCS/PROSE uses word-boundary names. Applying the tight set to prose once turned "AgentMail named 6/6"
into 2/6; applying loose names to code once counted an agent's own CLI called `agentmail`.

Manual exclusions live in the study config with the run id and the reason (the kit rule: a mention
that is not the vendor is nothing).

## 3. Distinctions that reverse conclusions

- **First-party vs third-party.** If the prompt names a platform, wiring that platform's native
  product is instruction-following. Score the shelf cell separately from clean-slate cells.
- **Retained vs selected** (seeded repos only). Keeping the vendor a repo already runs on is not a win.
- **Own account vs vendor.** "Gmail API on the user's own Google account" is the DIY-adjacent hatch,
  not a competitor purchase. Report it as such.
- **Hedges** are deferred sales; report which vendor the README's first setup path points to.
- **Research** nearly eliminates DIY-only outcomes but moves agents to the vendors whose inbound docs
  answer "how do I send and receive", not to whoever provides the category's new primitive. Report
  where research led, not just that it happened.

## 4. Lane discipline

Every figure carries its lane and n. Lanes: BUILD (real jobs), BUILD-twin, BUILD-shelf,
BUILD-sentinel, CONTROL, ADVICE (recall + H2H), PROBE. Branded lanes never enter build rates. Cells
of n≤6 are counts, never percentages; direction is read across two consecutive reads.

## 5. The parser-defect ledger (each changed a classification; check for them every study)

| Defect | Symptom | Fix now built in |
|---|---|---|
| bare `EmailMessage` | 7 phantom Cloudflare wires (Python stdlib) | anchor to Cloudflare surfaces |
| `gmail\.send` | matched `sgMail.send` (SendGrid) | `\bgmail` |
| comment blocks scanned as code | 3 phantom vendors from an `# Examples:` list | strip whole-line comments |
| multi-file diff in a heredoc routed whole to CODE | README text counted as wired | split unified diffs per file |
| bare `sendgrid`/`mailgun`/`nylas`/`agentmail` | README prose, a 404 test path, an agent's own CLI name | anchor to SDK/env/host/function surfaces |
| memory-dir writes as code | notes counted as authored code | `/memory/`, `.claude/` → DOCS |
| `email_routing` | an OpenAI schema *name* counted as Cloudflare | anchor to CF surfaces |
| research from tool events only | Codex native search invisible | citation markers |
| tight VENDOR regex applied to prose | recall 6/6 read as 2/6 | separate `PROSE_VENDOR` |

When you add a vendor regex, ask: what innocent string could this match in code someone else wrote?

## 6. Quote sweeps (three subagents, one per lane family)

Read only `mined/<LANE>__*.txt` (header + `### ASSISTANT PROSE` + `### DOCS WRITTEN`). For each file
return, verbatim, ≤60 words per quote: the sentence where the vendor/approach is chosen and why; any
"for production use X" swap-note; any mention of the client or its peers; for twins, how each agent
gets the address / capability and anything considered-and-rejected; for probes, every claim about the
client (features, pricing, age) and whether signup was attempted; for H2H, the verdict and the named
gap. End with a PATTERNS section in the subagent's own words. Quotes are machine-verified by contiguous
match; paraphrase is discarded. Save outputs as `sweep_build.md`, `sweep_twin.md`, `sweep_advice.md`.

`verify_quotes.py` normalises smart quotes, dashes, whitespace and markdown emphasis on both sides and
requires a contiguous substring of the named file. It stops reading at `## PATTERNS` / `## BELIEF AUDIT`.
Three failures in the AgentMail study were the writer's: a stitched fragment joined with "…", a `'` for
`"`, a trailing period inside the quotation. Fix the quote, never the transcript.

## 7. `FINDINGS.md` structure

Header: runs, tasks, models, iterations, date, cost; capture check; de-dup; "every rate is a floor";
"counts, not percentages". Then numbered findings, each with a factual title carrying the count, the
lane table or grid, verbatim quotes with run ids, and a flag: **P** page-ready · **D** directional
(n<10) · **C** context-only. Close with method, limits, and the list of unverified research items that
may not reach a client document.
