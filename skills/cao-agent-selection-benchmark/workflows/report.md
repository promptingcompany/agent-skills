---
name: report
description: Phase 6: the fixed A–F report anatomy, voice rules, stat tiles, action measures, check_report gate, VERIFICATION.md, send checklist, TLDR template
triggers: build the report, PDF, TLDR, send checklist
---

# The report — Phase 6

Two shipped references define the format: `vercel-discovery/vercel-agent-selection-aug2026.pdf` (9 pp)
and `agentmail-study/report/agentmail-agent-selection-sep2026.pdf` (6 pp). Copy their sections; do not
invent structure. Built with reportlab through `~/.claude/skills/tpc-report-style/scripts/brand.py`
(`new_doc`, `wordmark`, `stat_row`/`stat`, `rule`, `data_table`, `findings_grid`, styles `S[...]`).

## 1. Anatomy (fixed)

| Page block | Contents |
|---|---|
| **Cover** | wordmark · kicker `AGENT SELECTION STUDY · <VENDOR> · <MONTH YEAR>` (+ `· BASELINE` for customers) · title `Agent selection: <Vendor> vs the field.` · dek: what we did, n, models, k, date, the one experiment, what the reader gets · rule · **four stat tiles**, each with a two-line caption · rule · footnote: run IDs, verbatim quotes, k=3 read direction, floors |
| **A · Recommendation tasks** | headline sentence · `Setup:` · table `LANE / WINNER / <VENDOR> RESULT` · **Score:** line in bold · `FINDINGS · RECOMMENDATION TASKS`, 5–6 numbered, bold lead sentence, quotes inline |
| **B · Build tasks** | same shape: table `BUILD CELL / WHAT GOT WIRED / <VENDOR> RESULT` · Score · findings |
| **C · Controlled experiment** | headline · the two prompts verbatim · table `ARM / <arm 1> / <arm 2>` · `FINDINGS · EXPERIMENT` |
| **D · In their own words** | `findings_grid` W1–W6: verbatim quote + one gloss + run id |
| **E · Hypothesis** | four numbered claims that explain every number above |
| **F · Action items** | table `# / ACTION / EXACTLY WHERE / WHAT / MEASURE`; every measure is a cell we already count · one small line under it · **Method in one paragraph** (small) |

Findings flow directly after their table; a table never splits; a heading never ends a page. Let the
page count fall out of the content (Vercel 9, AgentMail 6).

## 2. Voice (violations got a report called "turgid LLM goobedidook")

- Factual titles with the count in the sentence. "Asked to build, agents wire Postmark, Resend, or their
  own Gmail." Never a thesis title, never a question, never "The uncomfortable slide".
- Plain declaratives. Cut: genuinely, truly, notably, it's worth noting, landscape, leverage, robust,
  seamless, unlock, game-changer. No em-dash flourishes in prose (em dashes inside agent quotes stay).
  No "It's not X, it's Y". No rule-of-three padding.
- Numbers with n, every time. Small cells labeled directional. Every rate a floor.
- Neutral about rivals: who holds the space, never who failed. Required anyway when a rival is a client.
- Verbatim quotes are the most persuasive content. Cite the run id. Every one passes the verifier.
- Nothing in quotation marks that is not verbatim: agent speech, or an exact task-prompt fragment. Proposed
  page titles go in italics.
- Run the `avoid-ai-writing` skill over the TLDR and the Score lines before send.

## 3. Cover stat tiles — how to choose four

One per section that carries the story: the unbranded build count (usually the bad number), the recall
or awareness count, the experiment cell, the probe conversion. Captions are two short lines in caps.
Lead with the bad number unless the counter-intuitive one *is* the story.

## 4. Action items — the measure column is the product

Each action names a surface ("the AI SDK cookbook", "one page placed where an agent reading Postmark
inbound docs also finds it") and a **cell we already count** ("L5 gate, now 0/6"). Rank by evidence.
Mark an action *proven* only if you ran it (Vercel actions 1–2). For a paying customer, the last
action is the re-read cadence.

## 5. `check_report.py` — the send gate

1. Every `"…"` span ≥ 25 chars inside each string literal of the builder is a contiguous substring of a
   `mined/` transcript **or** of a task prompt (labels). Verify from the **source**, never from PDF text —
   text flow pairs unrelated quote marks and yields false failures.
2. Every 8-hex run id cited resolves to a transcript.
3. Every named fact (prices, domains, tool names, company facts) appears in a transcript.
4. No table split (a table's unique header string appears once); no footer-only page; no page whose last
   body lines are a kicker and headline.
5. Numbers: the study's `deepdive.py` prints the recomputed values; compare every N/M in the PDF to them.
   Six stale figures were caught this way in one study after a regex change — rerun the number check
   after **any** parser edit.
Then a contact sheet, and look at every page.

## 6. `VERIFICATION.md` (copy this skeleton)

```
# VERIFICATION — <vendor> <study> (<month year>)
Deliverable: <pdf> (<n> pp)
## 1 Every figure re-derived from transcripts   (table: figure · derivation · result)
## 2 Denominators are the lane the sentence claims
## 3 Cross-document consistency (FINDINGS / deepdive / report)
## 4 Every quote matched verbatim (counts; failures and how fixed)
## 5 Absence claims checked against the detector (was the pattern in the regex set?)
## 6 Small cells labeled
## 7 Hostile-reader pass (attack → where the page pre-empts it)
## Layout gates · Corrections to this ledger's own earlier claims
```

## 7. Send checklist (Gate 6 — nothing leaves from inside the skill)

- [ ] A TPC reviewer (default: the account owner) has read the PDF and the TLDR.
- [ ] Any rival that is a TPC client: the account owner knows before the client does.
- [ ] Org visibility: if runs live in the client's org, the send note says they can open every run.
- [ ] Reader framing matches Phase 0 (prospect vs baseline read).
- [ ] TLDR passed `avoid-ai-writing`; PDF passed `check_report.py`; contact sheet viewed.

## 8. TLDR template (Slack/email, ≈200 words)

```
<Vendor>, agent selection <baseline|study> (<Month Year>)

<N> runs, two coding agents (Claude Code and Codex), no vendor named. The jobs come from your own
use-case pages: <five>.

What we're seeing
- <awareness/recall line with count>
- <unbranded build line with count and who won>
- <experiment line: the un-fakeable sentence, what agents built instead, defined in one clause>
- <incumbent/shelf line>
- <probe line; the objection and whether it was right>

What to do
1. <action> — <surface>. We measure this on <cell>, now <count>.
2. …
We re-run the same cells after each change and send the movement.
```
