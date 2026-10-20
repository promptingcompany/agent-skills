"""Build the monthly Exa readout: ONE PDF (findings + action list) and the Slack message that goes with it.

Every number on page 1, in sections 3-4, in the page deks, in the builds headline, in usability, in scope and
in the goals baseline column is computed from <research-dir>/{metrics,facts}.json and <default-dir>/{metrics,facts}.json.
Prose, hand-reviewed tables and the action list come from two JSON files (see assets/narrative.2026-10.json and
assets/actions.2026-10.json). Copy both each month and rewrite what changed.

Usage:
  python3 build_pdf.py --research <workdir>/2026-11-research --default <workdir>/2026-11-default \
      --narrative ../assets/narrative.2026-11.json --actions ../assets/actions.2026-11.json \
      --out "TPC x Exa Coding Agent Readout November.pdf" [--previous <october>.numbers.json]

Writes:  <out>                 the PDF (visibility pages, then the action list)
         <out>.numbers.json    every computed number, for the cross-check step and for next month's --previous
         <out>.slack.md        the Slack message: headline, the three numbers, findings, setup, action items

--previous adds a "vs baseline" delta to the Slack message and a BASELINE / THIS MONTH pair to the goals table.
Both tracker folders must have an empty review_queue.json, or the build stops.

Layout ported from exa-steerability/supplement/build_oct.py and build_actions_v9.py (October 2026). Fonts:
Helvetica (built in) plus a monospace face: SF Mono or Menlo on macOS, Courier elsewhere.
"""
import argparse, io, json, os, sys
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ---------------------------------------------------------------- style (unchanged from the October builders)
INK, SLATE, BLUE = HexColor('#171717'), HexColor('#455168'), HexColor('#245BFF')
BAND, HEAD, TINT, LINE = HexColor('#F5F5F5'), HexColor('#F6F6F6'), HexColor('#F2F6FF'), HexColor('#D8DDE6')
MONO = 'Courier'
for path, kw in [('/System/Library/Fonts/SFNSMono.ttf', {}), ('/System/Library/Fonts/Menlo.ttc', {'subfontIndex': 0})]:
    try:
        pdfmetrics.registerFont(TTFont('Mono', path, **kw)); MONO = 'Mono'; break
    except Exception:
        continue

W, H = letter
M = 42
FW = W - 2 * M
TOP, BOT = 88, 52
TOTAL = 0          # set after a counting pass
NARR, ACT = {}, {}
SM = '<font size="7.5" color="#455168">'


def ps(name, **k):
    base = dict(fontName='Helvetica', fontSize=9.2, leading=13, textColor=INK)
    base.update(k); return ParagraphStyle(name, **base)


S = dict(
    kicker=ps('k', fontName=MONO, fontSize=7, textColor=BLUE, leading=10, spaceAfter=9),
    title=ps('t', fontSize=27, leading=31, spaceAfter=17),
    dekb=ps('db', fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=SLATE),
    dek=ps('d', fontSize=10, leading=14, textColor=SLATE),
    num=ps('n', fontName=MONO, fontSize=7, textColor=BLUE, leading=9),
    h=ps('h', fontName='Helvetica-Bold', fontSize=13.5, leading=17),
    th=ps('th', fontName='Helvetica-Bold', fontSize=8.5, leading=11.5),
    td=ps('td', fontSize=9.2, leading=13),
    tdb=ps('tdb', fontName='Helvetica-Bold', fontSize=9.2, leading=13),
    tds=ps('tds', fontSize=8.2, leading=11.5, textColor=SLATE),
    note=ps('nt', fontSize=8.6, leading=12, textColor=SLATE),
    qmeta=ps('qm', fontName=MONO, fontSize=7, textColor=BLUE, leading=10),
    qtext=ps('qt', fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=INK),
    qsel=ps('qs', fontSize=9.2, leading=13, textColor=SLATE),
)


def frame_page(c, doc):
    c.saveState()
    c.setFillColor(INK)
    c.setFont('Times-Italic', 7.5); c.drawString(M, H - 39, 'the')
    c.setFont('Times-Roman', 10.5); c.drawString(M, H - 51.5, 'PROMPTING'); c.drawString(M, H - 62.5, 'COMPANY')
    c.setFont(MONO, 7); c.setFillColor(SLATE)
    c.drawRightString(W - M, H - 47.5, NARR['prepared_for']); c.drawRightString(W - M, H - 59.5, NARR['date'])
    c.setStrokeColor(LINE); c.setLineWidth(0.5); c.line(M, 35, W - M, 35)
    c.setFont(MONO, 6); c.setFillColor(SLATE)
    c.drawString(M, 22.5, NARR['footer']); c.drawRightString(W - M, 22.5, f'{doc.page:02d} / {TOTAL:02d}')
    c.restoreState()


def head(kicker, title, bold=None, dek=None):
    out = [Paragraph(kicker, S['kicker']), Paragraph(title, S['title'])]
    if bold: out.append(Paragraph(bold, S['dekb']))
    if dek: out.append(Paragraph(dek, S['dek']))
    out.append(Spacer(1, 13)); return out


def section(n, text):
    t = Table([[Paragraph(f'{n:02d}', S['num']), Paragraph(text, S['h'])]], colWidths=[25, FW - 25])
    t.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 0),
                           ('TOPPADDING', (0, 0), (0, 0), 2.5), ('TOPPADDING', (1, 0), (1, 0), 0),
                           ('BOTTOMPADDING', (0, 0), (-1, -1), 11)]))
    return t


def table(rows, widths, hi=None, bold_first=True, small_last=False, bold_last_row=False):
    data = []
    for i, r in enumerate(rows):
        row = []
        for j, cell in enumerate(r):
            if i == 0: st = S['th']
            elif bold_last_row and i == len(rows) - 1: st = S['tdb']
            elif bold_first and j == 0: st = S['tdb']
            elif small_last and j == len(r) - 1: st = S['tds']
            else: st = S['td']
            row.append(Paragraph(str(cell), st))
        data.append(row)
    t = Table(data, colWidths=[FW * w for w in widths], repeatRows=1)
    st = [('BACKGROUND', (0, 0), (-1, 0), HEAD), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
          ('LINEBELOW', (0, 0), (-1, -1), 0.5, LINE), ('TOPPADDING', (0, 0), (-1, -1), 6.5),
          ('BOTTOMPADDING', (0, 0), (-1, -1), 6.5), ('LEFTPADDING', (0, 0), (-1, -1), 9), ('RIGHTPADDING', (0, 0), (-1, -1), 7)]
    if hi is not None:
        st.append(('BACKGROUND', (hi, 1), (hi, -1), TINT))
    t.setStyle(TableStyle(st)); return t


def grouped(rows, widths, tight=False):
    """rows: list of (kind, cells). kind: 'head' | 'group' | 'sub'."""
    data, st = [], [('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('LINEBELOW', (0, 0), (-1, -1), 0.5, LINE),
                     ('TOPPADDING', (0, 0), (-1, -1), 6.5), ('BOTTOMPADDING', (0, 0), (-1, -1), 6.5),
                     ('LEFTPADDING', (0, 0), (-1, -1), 9), ('RIGHTPADDING', (0, 0), (-1, -1), 7)]
    for i, (kind, cells) in enumerate(rows):
        style = {'head': S['th'], 'group': S['tdb'], 'sub': S['td']}[kind]
        row = []
        for j, c in enumerate(cells):
            if kind == 'sub' and j == 0:
                row.append(Paragraph(c, ParagraphStyle('ind', parent=S['td'], fontName=MONO, fontSize=7.5, textColor=BLUE)))
            elif kind == 'sub':
                row.append(Paragraph(c, ParagraphStyle('subn', parent=S['td'], fontSize=8.6 if tight else 9.2,
                                                       leading=11.5 if tight else 13, textColor=INK if j == 1 else SLATE)))
            else:
                row.append(Paragraph(c, style))
        data.append(row)
        if kind == 'head': st.append(('BACKGROUND', (0, i), (-1, i), HEAD))
        if kind == 'group': st += [('BACKGROUND', (0, i), (-1, i), TINT), ('SPAN', (0, i), (-1, i))]
        if kind == 'sub': st.append(('LINEBELOW', (0, i), (-1, i), 0.25, HexColor('#ECEEF2')))
    if tight: st += [('TOPPADDING', (0, 0), (-1, -1), 2.6), ('BOTTOMPADDING', (0, 0), (-1, -1), 2.6)]
    t = Table(data, colWidths=[FW * w for w in widths], repeatRows=1); t.setStyle(TableStyle(st)); return t


def boxed(rows):
    t = Table([[r] for r in rows], colWidths=[FW])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), BAND), ('LINEBEFORE', (0, 0), (0, -1), 2.5, BLUE),
                           ('LEFTPADDING', (0, 0), (-1, -1), 14), ('RIGHTPADDING', (0, 0), (-1, -1), 14),
                           ('TOPPADDING', (0, 0), (-1, -1), 2), ('TOPPADDING', (0, 0), (0, 0), 11),
                           ('BOTTOMPADDING', (0, -1), (-1, -1), 14)]))
    return t


def quote(q):
    return boxed([Paragraph(q['meta'], S['qmeta']), Paragraph(f'&ldquo;{q["text"]}&rdquo;', S['qtext']),
                  Paragraph(f'Selected: {q["selected"]}', S['qsel'])])


def note(t): return Paragraph(t, S['note'])
def gap(h=18): return Spacer(1, h)
def pct(n, d): return int(100 * n / d + 0.5) if d else 0
def pc(n, d): return f'<b>{pct(n, d)}%</b> {SM}{n}/{d}</font>'
def pc_text(n, d): return f'{pct(n, d)}% ({n}/{d})'
def nice(disp): return disp.replace('OPUS', 'Opus').replace('SOL', 'Sol')


# ---------------------------------------------------------------- numbers
class Mode:
    """One tracker output folder: metrics.json + facts.json for one mode (research or default)."""

    def __init__(self, path):
        self.path = path
        qp = os.path.join(path, 'review_queue.json')
        q = json.load(open(qp)) if os.path.exists(qp) else []
        if q:
            sys.exit(f'{path}: review_queue.json still has {len(q)} runs. Settle them (workflows/review.md), re-run analyze.py, then build.')
        self.M = json.load(open(os.path.join(path, 'metrics.json')))
        self.F = [f for f in json.load(open(os.path.join(path, 'facts.json'))) if 'excluded' not in f]
        self.sel = [f for f in self.F if f['prompt_type'] != 'usability']     # the selection runs (96 in October)

    def runs(self, ptype=None, agent=None, pool=None):
        rows = self.sel if pool is None else pool
        if ptype: rows = [f for f in rows if f['prompt_type'] == ptype]
        if agent: rows = [f for f in rows if f['agent'] == agent]
        return rows

    @staticmethod
    def k(rows, pred): return sum(1 for f in rows if pred(f))

    cites_pub = staticmethod(lambda f: any(p['cited'] for p in f['published']))
    cites_exa = staticmethod(lambda f: any(c.startswith('target') for c in f['cited_cats']))
    searched = staticmethod(lambda f: f['n_queries'] > 0)          # a search call; a plain page fetch does not count
    opened_exa = staticmethod(lambda f: f['opened_target'])
    main = staticmethod(lambda f: f['outcome'] == 'main')
    uses_exa = staticmethod(lambda f: 'target' in f['wired'])
    win = staticmethod(lambda f: f['outcome'] == 'win')
    top = staticmethod(lambda f: f['outcome'] == 'top')
    named = staticmethod(lambda f: f['outcome'] in ('top', 'listed'))
    passed = staticmethod(lambda f: f['outcome'] == 'pass')

    def cell(self, pred, ptype=None, agent=None):
        rows = self.runs(ptype, agent); return self.k(rows, pred), len(rows)


def compute(R, D, agents):
    """Every number the PDF and the Slack message print, as [k, n] pairs. R = research mode, D = task only."""
    N = {}
    both = D.sel + R.sel
    chosen = sum(m.k(m.runs('tool-seeking'), m.top) + m.k(m.runs('head-to-head'), m.win) + m.k(m.runs('build'), m.main) for m in (D, R))
    N['chosen'] = (chosen, len(both)); N['lost'] = (len(both) - chosen, len(both))
    for tag, m in (('default', D), ('research', R)):
        N[f'pub_{tag}'] = m.cell(m.cites_pub); N[f'exa_{tag}'] = m.cell(m.cites_exa)
        N[f'build_{tag}'] = m.cell(m.main, 'build'); N[f'h2h_{tag}'] = m.cell(m.win, 'head-to-head')
        N[f'top_{tag}'] = m.cell(m.top, 'tool-seeking'); N[f'named_{tag}'] = m.cell(m.named, 'tool-seeking')
        for a, _ in agents:
            N[f'pub_{tag}_{a}'] = m.cell(m.cites_pub, agent=a); N[f'exa_{tag}_{a}'] = m.cell(m.cites_exa, agent=a)
            N[f'build_{tag}_{a}'] = m.cell(m.main, 'build', a); N[f'h2h_{tag}_{a}'] = m.cell(m.win, 'head-to-head', a)
            N[f'top_{tag}_{a}'] = m.cell(m.top, 'tool-seeking', a)
            N[f'searched_{tag}_{a}'] = m.cell(m.searched, agent=a); N[f'opened_{tag}_{a}'] = m.cell(m.opened_exa, agent=a)
            N[f'opened_{tag}'] = m.cell(m.opened_exa)
    N['build_both'] = (N['build_default'][0] + N['build_research'][0], N['build_default'][1] + N['build_research'][1])
    rb = R.runs('build')
    opened = [f for f in rb if R.opened_exa(f)]; not_opened = [f for f in rb if not R.opened_exa(f)]
    N['research_build_opened_used'] = (R.k(opened, R.uses_exa), len(opened))
    N['research_build_notopened_used'] = (R.k(not_opened, R.uses_exa), len(not_opened))
    us = R.runs('usability', pool=R.F)
    N['usability'] = (R.k(us, R.passed), len(us))
    N['responses'] = len(R.F) + len(D.F)
    N['use_cases'] = len({f['use_case'] for f in both if f['use_case'] != '?'})
    return {k: (list(v) if isinstance(v, tuple) else v) for k, v in N.items()}


def hdr(disp, sub): return f'{disp}<br/><font name="Helvetica">{sub}</font>'


# ---------------------------------------------------------------- the PDF
def visibility_pages(N, agents):
    a1, a2 = agents
    cols = [(a, t) for a, _ in agents for t in ('default', 'research')]
    story = []
    # page 1: scorecard
    story += head(NARR['kicker'], 'Coding agent visibility',
                  f'Coding agents chose Exa in {pct(*N["chosen"])}% of responses ({N["chosen"][0]} of {N["chosen"][1]}): {NARR["title_tail"]}')
    story += [section(1, 'The three metrics'),
              table([['METRIC', 'TASK ONLY', 'RESEARCH'],
                     ['Answers citing a page we publish', pc(*N['pub_default']), pc(*N['pub_research'])],
                     ['Builds using Exa as the main search', pc(*N['build_default']), pc(*N['build_research'])],
                     ['Head-to-head wins', pc(*N['h2h_default']), pc(*N['h2h_research'])]],
                    [0.5, 0.25, 0.25], hi=2, bold_first=False),
              Spacer(1, 9),
              note(f'For context: answers citing any Exa page, mostly Exa&rsquo;s docs: {pct(*N["exa_default"])}% task only '
                   f'({N["exa_default"][0]}/{N["exa_default"][1]}), {pct(*N["exa_research"])}% research ({N["exa_research"][0]}/{N["exa_research"][1]}).'),
              gap(16), section(2, 'By agent'),
              table([['METRIC', hdr(a1[1], 'task only'), hdr(a1[1], 'research'), hdr(a2[1], 'task only'), hdr(a2[1], 'research')],
                     ['Answers citing a page we publish'] + [pc(*N[f'pub_{t}_{a}']) for a, t in cols],
                     ['Builds using Exa'] + [pc(*N[f'build_{t}_{a}']) for a, t in cols],
                     ['Head-to-head wins'] + [pc(*N[f'h2h_{t}_{a}']) for a, t in cols]],
                    [0.32, 0.17, 0.17, 0.17, 0.17]),
              Spacer(1, 9),
              note('For context, answers citing any Exa page: ' + '; '.join(
                  f'{nice(d)} {pct(*N[f"exa_default_{a}"])}% task only ({N[f"exa_default_{a}"][0]}/{N[f"exa_default_{a}"][1]}), '
                  f'{pct(*N[f"exa_research_{a}"])}% research ({N[f"exa_research_{a}"][0]}/{N[f"exa_research_{a}"][1]})' for a, d in agents) + '.'),
              Spacer(1, 5), note(NARR['p1_definitions']), Spacer(1, 5), note(NARR['p1_noise']), PageBreak()]
    # page 2: where Exa shows up
    story += head('VISIBILITY', 'Where Exa shows up',
                  f'Asking agents to research raises how often Exa is named from {pct(*N["named_default"])}% to {pct(*N["named_research"])}%.')
    story += [section(3, 'Open tool-selection questions'),
              table([['', 'TASK ONLY', 'RESEARCH'],
                     ['Exa recommended first', pc(*N['top_default']), pc(*N['top_research'])],
                     ['Exa recommended or listed', pc(*N['named_default']), pc(*N['named_research'])]],
                    [0.5, 0.25, 0.25], hi=2),
              gap(16), section(4, 'The two agents research differently'),
              table([['', hdr(a1[1], 'task only'), hdr(a1[1], 'research'), hdr(a2[1], 'task only'), hdr(a2[1], 'research')],
                     ['Searched the web'] + [pc(*N[f'searched_{t}_{a}']) for a, t in cols],
                     ['Opened an Exa page'] + [pc(*N[f'opened_{t}_{a}']) for a, t in cols],
                     ['Recommended Exa first'] + [pc(*N[f'top_{t}_{a}']) for a, t in cols]],
                    [0.32, 0.17, 0.17, 0.17, 0.17]),
              Spacer(1, 9), note(NARR['p2_sol_note']),
              gap(16), section(5, 'How each agent finds tools'),
              table(NARR['p2_how_agents_find_tools'], [0.26, 0.37, 0.37], bold_first=True), PageBreak()]
    # page 3: why Exa loses (hand-reviewed)
    story += head('WHY EXA LOSES', 'Where Exa loses',
                  f'Exa did not win {pct(*N["lost"])}% of responses ({N["lost"][0]} of {N["lost"][1]}).', NARR['p3_sub'])
    story += [section(6, 'Reasons, largest first'),
              table(NARR['p3_reasons_rows'], [0.40, 0.15, 0.15, 0.13, 0.17], hi=4, bold_first=False, bold_last_row=True),
              Spacer(1, 9), note(NARR['p3_reasons_note']), Spacer(1, 5), note(NARR['p3_where_to_act']),
              gap(16), section(7, 'Head-to-head, by use case'), table(NARR['p3_h2h_rows'], [0.2, 0.8]),
              Spacer(1, 9), note(NARR['p3_h2h_note']), PageBreak()]
    # page 4: close calls (hand-reviewed)
    story += head('CLOSE CALLS', 'What decides a close call', NARR['p4_dek'])
    story += [section(8, 'What agents wanted'), table(NARR['p4_wanted_rows'], [0.33, 0.13, 0.10, 0.44], hi=3, bold_first=False),
              Spacer(1, 9), note(NARR['p4_losses_note']), Spacer(1, 9), quote(NARR['p4_quote']),
              gap(16), section(9, 'Exa pages that cost a decision'), table(NARR['p4_pages_rows'], [0.24, 0.76], bold_first=True), PageBreak()]
    # page 5: builds
    def frac(s): n, d = s.split('/'); return pc(int(n), int(d))
    ms = [NARR['p5_main_search_rows'][0]] + [[r[0]] + [frac(x) for x in r[1:]] for r in NARR['p5_main_search_rows'][1:]]
    sk = [NARR['p5_skill_rows'][0]] + [[r[0]] + [frac(x) for x in r[1:]] for r in NARR['p5_skill_rows'][1:]]
    by_agent = ', '.join(f'{nice(d)} {N[f"build_research_{a}"][0]}' for a, d in agents)
    story += head('BUILDS', 'What agents build with',
                  f'Exa was the main search in {pct(*N["build_both"])}% of builds ({N["build_both"][0]} of {N["build_both"][1]}).')
    story += [section(10, 'Main search in the code (task only)'), table(ms, [0.43, 0.19, 0.19, 0.19], hi=3),
              Spacer(1, 9),
              note(f'With research requested, Exa was the main search in {pct(*N["build_research"])}% ({N["build_research"][0]}/{N["build_research"][1]}): {by_agent}. '
                   f'Research builds that opened an Exa page used Exa in {N["research_build_opened_used"][0]} of {N["research_build_opened_used"][1]}; '
                   f'builds that did not open one used Exa in {N["research_build_notopened_used"][0]} of {N["research_build_notopened_used"][1]}.'),
              gap(16), section(11, 'Builds that used the provider&rsquo;s own search'), table(sk, [0.44, 0.28, 0.28], hi=1),
              Spacer(1, 9), quote(NARR['p5_quote']), Spacer(1, 9), note(NARR['p5_env_note']), PageBreak()]
    # page 6: priorities + usability + scope
    story += head('RECOMMENDATIONS', 'Priorities for Exa')
    story += [section(12, 'Action plan'), table(NARR['p6_actions_rows'], [0.07, 0.69, 0.24], bold_first=False, small_last=True),
              gap(16), section(13, 'Usability'),
              table([['', 'RESULT', ''], ['Exa integrations that worked', pc(*N['usability']), NARR['p6_usability_note']]], [0.32, 0.16, 0.52], small_last=True),
              gap(16), section(14, 'Scope'),
              note(f'<b>{N["responses"]} responses:</b> {N["use_cases"]} use cases; tool selection, head-to-head and build questions; task only and research; '
                   f'Claude Code with {nice(a1[1])} and Codex with {nice(a2[1])}; plus {N["usability"][1]} usability runs. ' + NARR['p6_method'] + NARR['p6_limits']),
              PageBreak()]
    return story


def action_pages(N, P):
    """The action list. P = previous month's numbers (or None)."""
    A = ACT['actions']
    def cell_action(r): return f'<b>{r["title"]}</b><br/>{SM}{r["detail"]}</font><br/>{SM}<i>{r["where"]}</i></font>'
    def cell_aim(r): return f'{r["aim"]}<br/>{SM}Moves: {r["moves"]}</font>'
    def cell_why(r): return f'{SM}{r["why"]}</font>'
    def cell_live(r): return f'{r["live_by"]}' + (f'<br/>{SM}Exa OK</font>' if r['exa_ok'] else '')
    key = {'pub': 'pub_research', 'h2h': 'h2h_research', 'build': 'build_research'}
    if P:
        cols = ['METRIC', 'BASELINE', 'THIS MONTH'] + ACT['goals_columns']
        rows = [[g['label'], pc(*P[key[g['metric']]]), pc(*N[key[g['metric']]])] + g['targets'] for g in ACT['goals']]
        widths = [0.34, 0.15, 0.15] + [0.36 / len(ACT['goals_columns'])] * len(ACT['goals_columns'])
    else:
        cols = ['METRIC', 'BASELINE'] + ACT['goals_columns']
        rows = [[g['label'], pc(*N[key[g['metric']]])] + g['targets'] for g in ACT['goals']]
        widths = [0.40, 0.20] + [0.40 / len(ACT['goals_columns'])] * len(ACT['goals_columns'])
    story = head(ACT['kicker'], ACT['title'], ACT['intro'])
    story += [section(15, 'Goals (research mode)'), table([cols] + rows, widths, hi=len(cols) - 1),
              Spacer(1, 8), note(ACT['goals_note']),
              gap(18), section(16, 'Top priorities'),
              table([['#', 'ACTION', 'WHAT WE&rsquo;RE TRYING TO ACHIEVE', 'LIVE BY']] +
                    [[str(r['rank']), f'<b>{r["title"]}</b><br/>{SM}<i>{r["where"]}</i></font>', cell_aim(r), cell_live(r)] for r in A if r['priority'] == 'High'],
                    [0.05, 0.52, 0.30, 0.13], bold_first=False),
              Spacer(1, 8), note(ACT['top_note']), PageBreak()]
    rows = [('head', ['#', 'ACTION, WHAT&rsquo;S IN IT, WHERE IT LIVES', 'WHAT WE&rsquo;RE TRYING TO ACHIEVE', 'WHY', 'LIVE BY'])]
    for pri in ['High', 'Medium', 'Low', 'Other']:
        items = [r for r in A if r['priority'] == pri]
        if not items: continue
        rows.append(('group', [f'{pri} priority' if pri != 'Other' else 'Other improvements (after the three metrics)', '', '', '', '']))
        rows += [('sub', [str(r['rank']), cell_action(r), cell_aim(r), cell_why(r), cell_live(r)]) for r in items]
    story += head('ALL ACTIONS', 'Ranked by priority', ACT['all_dek'])
    story += [section(17, 'Actions'), grouped(rows, [0.05, 0.42, 0.24, 0.19, 0.10], tight=True)]
    return story


def render(story, target):
    doc = BaseDocTemplate(target, pagesize=letter, leftMargin=M, rightMargin=M, topMargin=TOP, bottomMargin=BOT,
                          title=NARR['pdf_title'], author='The Prompting Company', subject=NARR['pdf_subject'], creator='The Prompting Company')
    doc.addPageTemplates([PageTemplate(id='p', frames=[Frame(M, BOT, FW, H - TOP - BOT, id='f', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=frame_page)])
    doc.build(story); return doc.page


# ---------------------------------------------------------------- the Slack message
def delta(cur, prev):
    d = pct(*cur) - pct(*prev)
    flag = '  (real move, 15+ points)' if abs(d) >= 15 else '  (within noise)'
    return f' vs baseline {pct(*prev)}%: {d:+d} points{flag}'


def slack_message(N, P):
    L = [f'*{NARR["slack_title"]}*', '',
         f'Coding agents chose Exa in {pct(*N["chosen"])}% of responses ({N["chosen"][0]} of {N["chosen"][1]}): as their first pick, as the head-to-head winner, or as the main search in a build. Full report attached.',
         '', NARR['slack_setup'], '', 'The three numbers we track each month (research mode):']
    for label, k in [('Answers citing a page we publish', 'pub_research'), ('Builds using Exa as the main search', 'build_research'),
                     ('Head-to-head wins against a named rival', 'h2h_research')]:
        L.append(f'• *{label}:* {pc_text(*N[k])}' + (delta(N[k], P[k]) if P else ''))
    L.append(f'For context, {pct(*N["exa_research"])}% of research answers cite some Exa page, mostly the docs.'
             + (f' Agents opened an Exa page in {pc_text(*N["opened_research"])} of research runs' + (delta(N['opened_research'], P['opened_research']) if P and 'opened_research' in P else '') + '.' if P else ''))
    L += ['', 'Findings:'] + [f'• {x}' for x in NARR['slack_findings']]
    L += ['', NARR['slack_next'], '', 'Notes on the setup:', f'• Models: {NARR["slack_models"]}', '',
          f'Experiments: {NARR["slack_experiments_url"]}', '', 'Action items (top priorities; the full ranked list is in the PDF):']
    for r in ACT['actions']:
        if r['priority'] == 'High':
            L.append(f'{r["rank"]}. {r["title"]}. Live by {r["live_by"]}.' + (' Needs Exa OK.' if r['exa_ok'] else ''))
    return '\n'.join(L) + '\n'


def main():
    global TOTAL, NARR, ACT
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--research', required=True, help='tracker folder for the research-mode pull')
    ap.add_argument('--default', required=True, help='tracker folder for the task-only pull')
    ap.add_argument('--narrative', required=True, help='narrative JSON (copy assets/narrative.2026-10.json and edit)')
    ap.add_argument('--actions', required=True, help='action list JSON (copy assets/actions.2026-10.json and edit)')
    ap.add_argument('--out', required=True, help='output PDF path')
    ap.add_argument('--previous', help="last month's <out>.numbers.json, for deltas")
    ap.add_argument('--agents', default='Claude Code=OPUS 5.5,Codex=GPT-6.1 SOL', help='config agent name=display label, in column order')
    a = ap.parse_args()
    NARR = json.load(open(a.narrative)); ACT = json.load(open(a.actions))
    agents = [tuple(x.split('=', 1)) for x in a.agents.split(',')]
    P = json.load(open(a.previous)) if a.previous else None
    R, D = Mode(a.research), Mode(a.default)
    N = compute(R, D, agents)
    story = lambda: visibility_pages(N, agents) + action_pages(N, P)
    TOTAL = render(story(), io.BytesIO())          # counting pass
    render(story(), a.out)
    json.dump(N, open(a.out + '.numbers.json', 'w'), indent=1)
    open(a.out + '.slack.md', 'w').write(slack_message(N, P))
    print(f'wrote {a.out} ({TOTAL} pages), {a.out}.numbers.json, {a.out}.slack.md')
    print(f'  chosen {pc_text(*N["chosen"])}  |  cites published page: default {pc_text(*N["pub_default"])}, research {pc_text(*N["pub_research"])}')
    print(f'  builds main: default {pc_text(*N["build_default"])}, research {pc_text(*N["build_research"])}  |  h2h wins: default {pc_text(*N["h2h_default"])}, research {pc_text(*N["h2h_research"])}')
    print(f'  any exa page cited: default {pc_text(*N["exa_default"])}, research {pc_text(*N["exa_research"])}  |  usability {pc_text(*N["usability"])}')


if __name__ == '__main__':
    main()
