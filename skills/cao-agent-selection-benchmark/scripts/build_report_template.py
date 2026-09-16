#!/usr/bin/env python3
# Condensed selection-study report — TEMPLATE. Copy into the study folder as build_report.py, replace every
# <<...>> with content from FINDINGS.md, delete rows you do not have, never invent classes or sections.
# Section-for-section copy of vercel-agent-selection-aug2026 and agentmail-agent-selection-sep2026.
# Findings flow after their table; a heading never ends a page (PageBreak before F is deliberate).
import sys, os
sys.path.insert(0, os.path.expanduser('~/.claude/skills/tpc-report-style/scripts'))
from brand import *

VENDOR = "<<Vendor>>"; MONTH = "<<Month Year>>"; KIND = "BASELINE"   # KIND: BASELINE for customers, STUDY for prospects
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'report', f'{VENDOR.lower()}-agent-selection-{MONTH.lower().replace(" ","")}.pdf')
os.makedirs(os.path.dirname(OUT), exist_ok=True)
doc, story = new_doc(OUT, footer_left=f'THE PROMPTING COMPANY · AGENT SELECTION · {VENDOR.upper()} · {MONTH.upper()}')
A = '#2563EB'
def P(t, s='body'): story.append(Paragraph(t, S[s]))
def sp(h): story.append(Spacer(1, h))
def T(rows, widths): story.append(data_table(rows, widths))
def cell(t, h=False): return Paragraph(t, S['tcellh' if h else 'tcell'])

# ---------------- COVER ----------------
story.append(wordmark()); sp(14)
story.append(Paragraph(f'AGENT SELECTION STUDY · {VENDOR.upper()} · {MONTH.upper()} · {KIND}', S['kicker'])); sp(6)
story.append(Paragraph(f'Agent selection:<br/><font color="{A}">{VENDOR}</font> vs the field.', S['title']))
P('<<Coding agents got real <category> jobs from your use-case pages, no vendor named. We recorded what they recommend and '
  'what they wire into the repo. N runs, two models (Claude Code with X, Codex with Y), k=3 per cell, DATE. One controlled '
  'experiment: the same prompt with and without the sentence that describes your product, <the sentence>. Each action below '
  'names the cell it should move; we re-run that cell after the change.>>', 'dek')
story.extend(rule())
story.append(stat_row([
    stat('<<0/54>>', '<<UNBRANDED BUILDS WIRING<br/>VENDOR. NAMED IN 0 TOO>>'),
    stat('<<6/6>>',  '<<RECALL RUNS NAMING VENDOR<br/>UNPROMPTED, 4 FROM MEMORY>>'),
    stat('<<0/6>>',  '<<GATE RUNS WIRING IT.<br/>ALL 6 BUILT <DIY ROUTE>>>'),
    stat('<<2/6>>',  '<<PROBE RUNS WIRING IT ONCE<br/>THE USER NAMED IT>>'),
]))
story.extend(rule())
P('Every number carries a run ID. Quotes are verbatim, checked against transcripts. k=3 per model: read direction, not '
  'decimals. Every rate is a floor: one-shot sandboxes, placeholder credentials, no sign-ups.', 'small')
story.append(PageBreak())

# ---------------- A: RECOMMENDATION TASKS ----------------
story.append(Paragraph('A · RECOMMENDATION TASKS', S['kicker']))
story.append(Paragraph('<<Asked for options, agents name you. Asked to decide, they keep the incumbent.>>', S['h1']))
P('Setup: <<an unbranded recall prompt, a head-to-head where the user already runs <incumbent>, a probe where a colleague '
  'suggests <vendor> and a cofounder objects. 6 runs per lane, two models.>>')
T([
    [cell('LANE', True), cell('WINNER', True), cell(f'{VENDOR.upper()} RESULT', True)],
    [cell('Recall: "<<exact prompt fragment>>"'), cell('<<winner, counts>>'), cell('<<named n/6 (memory/search split); category; recommended for which case>>')],
    [cell('Head-to-head: "<<exact prompt fragment>>"'), cell('<<incumbent, n/6 stay>>'), cell('<<named n/6; how discounted>>')],
    [cell('Probe: "<<exact prompt fragment>>"'), cell('<<objection vendor, n/6>>'), cell('<<wired n/6 (which runs); rejected n/6 on what; cost objection?>>')],
], [W*0.30, W*0.33, W*0.37])
sp(4)
P('<b>Score: <<one sentence with the counts>>.</b> <<two sentences of reading>>')
sp(8)
story.append(Paragraph('FINDINGS · RECOMMENDATION TASKS', S['kicker']))
P('<b>1. <<Factual lead sentence.>></b> <<evidence with verbatim quote>>')
P('<b>2. <<…>></b> <<…>>')
P('<b>3. <<…>></b> <<…>>')
P('<b>4. <<…>></b> <<…>>')
P('<b>5. <<…>></b> <<…>>')
P('<b>6. <<…>></b> <<…>>')
story.append(PageBreak())

# ---------------- B: BUILD TASKS ----------------
story.append(Paragraph('B · BUILD TASKS', S['kicker']))
story.append(Paragraph('<<Asked to build, agents wire A, B, or their own C.>>', S['h1']))
P('Setup: <<real jobs from your use-case pages, a shelf cell, a sentinel, a control. No vendor named.>> Wired means in files: '
  'SDK imports, dependencies, keyed API calls, provider webhook handlers.')
T([
    [cell('BUILD CELL', True), cell('WHAT GOT WIRED', True), cell(f'{VENDOR.upper()} RESULT', True)],
    [cell('<<Job: "exact prompt fragment", 6 runs>>'), cell('<<per model counts>>'), cell('<<0 / n>>')],
    [cell('<<…>>'), cell('<<…>>'), cell('<<…>>')],
    [cell('Shelf: <<job + "exact anchor fragment">>, 6 runs'), cell('<<incumbent 6/6, no reason given>>'), cell('<<0. Same job unanchored: n/6>>')],
    [cell('Sentinel: <<job>>, "<<Just for me>>", 6 runs'), cell('<<DIY 6/6>>'), cell('0, correctly')],
    [cell('Control: <<job>>, 6 runs'), cell('<<no vendor, no category term>>'), cell('0, correctly')],
], [W*0.34, W*0.34, W*0.32])
sp(4)
P('<b>Score: <<0 of N unbranded build runs wired VENDOR; 0 named it.>></b> <<totals over real-job runs; the one job that buys>>')
sp(8)
story.append(Paragraph('FINDINGS · BUILD TASKS', S['kicker']))
P('<b>1. <<The transport follows the language pick.>></b> <<quotes>>')
P('<b>2. <<Model A goes DIY and says why; Model B buys and does not.>></b> <<counts>>')
P('<b>3. <<What is the hard part; what is a commodity.>></b> <<quotes>>')
P('<b>4. <<Research buys; memory builds.>></b> <<searched: n wired / m DIY; not: …; where research led>>')
P('<b>5. <<Hedges.>></b> <<count, model, quote, where the README points>>')
P('<b>6. <<The shelf decides first.>></b> <<anchored vs unanchored counts, quote>>')
story.append(PageBreak())

# ---------------- C: CONTROLLED EXPERIMENT ----------------
story.append(Paragraph('C · CONTROLLED EXPERIMENT', S['kicker']))
story.append(Paragraph('<<One sentence added, one variable changed: the <gate>.>>', S['h1']))
P('Two prompts, byte-identical: "<<base prompt verbatim>>" <<Gate id>> adds: "<<appended sentence verbatim>>" That sentence is '
  'your product. Both models, k=3; <<every run searched first>>.')
T([
    [cell('ARM', True), cell('<<L2 · CLEAN SLATE (6 runs)>>', True), cell('<<L5 · GATE (6 runs)>>', True)],
    [cell('<<Model A>> wired'), cell('<<…>>'), cell('<<…>>')],
    [cell('<<Model B>> wired'), cell('<<…>>'), cell('<<…>>')],
    [cell(f'{VENDOR} or <<peer>> named'), cell('<<0 of 6>>'), cell('<<0 of 6>>')],
    [cell('<<How the requirement was met>>'), cell('<<…>>'), cell('<<the DIY route, n/6>>')],
], [W*0.26, W*0.34, W*0.40])
sp(4)
story.append(Paragraph('FINDINGS · EXPERIMENT', S['kicker']))
P('<b>1. <<The gate did / did not seal.>></b> <<quote>>')
P('<b>2. <<What agents picture when they hear the requirement.>></b> <<quote>>')
P('<b>3. <<Whether the category was named, and how.>></b> <<quotes>>')
P('<b>4. <<How the vendor\'s primitive was framed.>></b> <<quote>>')
P('<b>5. <<What research did.>></b> <<…>>')
story.append(PageBreak())

# ---------------- D: IN THEIR OWN WORDS ----------------
story.append(Paragraph('D · IN THEIR OWN WORDS', S['kicker']))
story.append(Paragraph('Verbatim, grep-verified, run IDs on request.', S['h1']))
story.append(findings_grid([
    ('W1', '"<<verbatim>>"', '<<one-sentence gloss>>. Run <<8-hex>>.'),
    ('W2', '"<<verbatim>>"', '<<gloss>>. Run <<8-hex>>.'),
    ('W3', '"<<verbatim>>"', '<<gloss>>. Run <<8-hex>>.'),
    ('W4', '"<<verbatim>>"', '<<gloss>>. Run <<8-hex>>.'),
    ('W5', '"<<verbatim>>"', '<<gloss>>. Run <<8-hex>>.'),
    ('W6', '"<<verbatim>>"', '<<gloss>>. Run <<8-hex>>.'),
]))
sp(14)

# ---------------- E: HYPOTHESIS ----------------
story.append(Paragraph('E · HYPOTHESIS', S['kicker']))
story.append(Paragraph('Four claims that explain every number above.', S['h1']))
P('<b>1.</b> <<Selection happens without evaluation; what decides it.>>')
P('<b>2.</b> <<What agents know about the vendor, and where the gap actually is.>>')
P('<b>3.</b> <<Who the real competitor is.>>')
P('<b>4.</b> <<What content can and cannot do; where the leverage is.>>')
story.append(PageBreak())

# ---------------- F: ACTION ITEMS ----------------
story.append(Paragraph('F · ACTION ITEMS', S['kicker']))
story.append(Paragraph('<<Five>> actions, with the exact surfaces and the measurement.', S['h1']))
T([
    [cell('#', True), cell('ACTION', True), cell('EXACTLY WHERE / WHAT', True), cell('MEASURE', True)],
    [cell('1'), cell('<<action>>'), cell('<<surface, in the agents\' vocabulary>>'), cell('<<cell, now n/6>>')],
    [cell('2'), cell('<<…>>'), cell('<<…>>'), cell('<<…>>')],
    [cell('3'), cell('<<…>>'), cell('<<…>>'), cell('<<…>>')],
    [cell('4'), cell('<<…>>'), cell('<<…>>'), cell('<<…>>')],
    [cell('5'), cell('Re-read the same cells after each change'), cell('Same tasks, two models, k=3, fired after each action ships. Movement in a 6-run cell is one or two runs; direction is read across two consecutive reads'), cell('The standing scoreboard: <<cells>>')],
], [W*0.03, W*0.17, W*0.57, W*0.23])
sp(4)
P('Every number in the right-hand column is one we already produce. <<Action 1 targets the cell this study was designed to open; it is the first re-read.>>', 'small')
sp(6)
P('<b>Method in one paragraph.</b> <<N runs, DATE, two models, k=3 per cell, three homogeneous experiments (build n, advice n, '
  'probe n). Cells: … Only the probe and head-to-head name a vendor; they are labeled lanes outside the build counts. Every build '
  'prompt allows placeholder credentials, so a missing key never forces DIY. Judges grade working code on disk, never the vendor. '
  'Wired means the vendor is in code the agent authored (write tools, shell heredocs, Codex apply_patch, dependency installs); '
  'comments and READMEs count as named; every hit was inspected in context. First user message equals the task prompt in N of N '
  'runs. Quotes are checked by contiguous match against source files. Limits: two models; one prompt per cell; no seeded-repo cell; '
  'placeholder credentials remove the sign-up moment. Cost $X. Transcripts, run IDs and all experiments available on request.>>', 'small')

doc.build(story); print('OK', OUT)
