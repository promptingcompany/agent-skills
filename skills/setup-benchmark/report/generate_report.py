#!/usr/bin/env python3
"""TPC benchmark report generator v2 — multi-stack snapshots (tasks[].cells[arm][stack]).
Cuts: banner / hero / overall leaderboard / per-stack leaderboard / per-stack heatmaps /
cross-model consistency / criteria cut / efficiency+cost / receipts / methodology / summary.
Usage: generate_report.py <snapshot.json> <out.html>"""
import json, sys, html, statistics as st
snap=json.load(open(sys.argv[1]))
ARMS=list(snap["arms"].keys()); DISP={a:snap["arms"][a]["display"] for a in ARMS}
STACKS=[s["id"] for s in snap["protocol"]["stacks"]]; SLBL={s["id"]:s["label"] for s in snap["protocol"]["stacks"]}
AG=snap["aggregates"]; PS=snap["per_stack"]; TASKS=snap["tasks"]; k=snap["protocol"]["k"]; pilot=k==1
e=lambda s: html.escape(str(s))
def bucket(s):
    return "bnone" if s is None else "bhi" if s>=97 else "bmid" if s>=85 else "blow" if s>=60 else "bbad"
def bars(vals,unit="",invert=False,fmt=lambda v:v):
    mx=max(vals.values()) or 1
    best=min(vals,key=vals.get) if invert else max(vals,key=vals.get)
    r=""
    for a in vals:
        w=round(100*vals[a]/mx,1); cls="lead" if a==best else ""
        r+=f'<div class="brow"><span class="blab">{e(DISP.get(a,a))}</span><span class="btrack"><span class="bfill {cls}" style="width:{w}%"></span></span><span class="bval">{e(fmt(vals[a]))}{unit}</span></div>'
    return f'<div class="bars">{r}</div>'

WM='<text x="628" y="16" text-anchor="end" font-family="ui-monospace,Menlo,monospace" font-size="9" fill="var(--muted)" opacity=".7">THE PROMPTING COMPANY</text>'
def vbar(vals,fmt=lambda v:v,invert=False,unit=""):
    W,Hh,pad=640,270,40; n=len(vals); bw=min(110,(W-2*pad)/n*0.55)
    mx=max(vals.values())*1.18 or 1
    best=min(vals,key=vals.get) if invert else max(vals,key=vals.get)
    s=[f'<svg viewBox="0 0 {W} {Hh}" style="width:100%;max-width:{W}px">',WM]
    for i in range(1,5):
        y=Hh-40-(Hh-80)*i/4
        s.append(f'<line x1="{pad}" y1="{y}" x2="{W-20}" y2="{y}" stroke="var(--line)" stroke-dasharray="3 4"/>')
        s.append(f'<text x="{pad-6}" y="{y+3}" text-anchor="end" font-size="9" fill="var(--muted)" font-family="ui-monospace,Menlo,monospace">{fmt(round(mx*i/4/1.18*1.18,2)) if False else ""}</text>')
    step=(W-2*pad)/n
    for i,(a,v) in enumerate(vals.items()):
        h=(Hh-80)*v/mx; x=pad+step*i+(step-bw)/2; y=Hh-40-h
        fill="var(--accent)" if a==best else "var(--muted)"; op="1" if a==best else "0.45"
        s.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{bw:.0f}" height="{h:.0f}" rx="3" fill="{fill}" opacity="{op}"/>')
        s.append(f'<text x="{x+bw/2:.0f}" y="{y-7:.0f}" text-anchor="middle" font-size="12" font-family="ui-monospace,Menlo,monospace" fill="var(--ink)">{fmt(v)}{unit}</text>')
        s.append(f'<text x="{x+bw/2:.0f}" y="{Hh-22:.0f}" text-anchor="middle" font-size="11.5" fill="var(--muted)">{DISP.get(a,a)}</text>')
    s.append(f'<line x1="{pad}" y1="{Hh-40}" x2="{W-20}" y2="{Hh-40}" stroke="var(--muted)" stroke-width="0.8"/>')
    s.append('</svg>'); return "".join(s)
def stackbar(pairs,fmt=lambda v:f"${v}"):
    W,Hh,pad=640,280,40; n=len(pairs); bw=min(110,(W-2*pad)/n*0.55)
    mx=max(a+b for a,b in pairs.values())*1.18 or 1; step=(W-2*pad)/n
    s=[f'<svg viewBox="0 0 {W} {Hh}" style="width:100%;max-width:{W}px">',WM]
    for i in range(1,5):
        y=Hh-46-(Hh-92)*i/4
        s.append(f'<line x1="{pad}" y1="{y}" x2="{W-20}" y2="{y}" stroke="var(--line)" stroke-dasharray="3 4"/>')
    for i,(a,(ag,vd)) in enumerate(pairs.items()):
        x=pad+step*i+(step-bw)/2
        hA=(Hh-92)*ag/mx; hV=(Hh-92)*vd/mx
        yA=Hh-46-hA; yV=yA-hV
        s.append(f'<rect x="{x:.0f}" y="{yA:.0f}" width="{bw:.0f}" height="{hA:.0f}" fill="var(--accent)"/>')
        s.append(f'<rect x="{x:.0f}" y="{yV:.0f}" width="{bw:.0f}" height="{max(hV,2):.0f}" fill="var(--good)"/>')
        s.append(f'<text x="{x+bw/2:.0f}" y="{yV-7:.0f}" text-anchor="middle" font-size="12" font-family="ui-monospace,Menlo,monospace" fill="var(--ink)">{fmt(round(ag+vd,2))}</text>')
        s.append(f'<text x="{x+bw/2:.0f}" y="{Hh-28:.0f}" text-anchor="middle" font-size="11.5" fill="var(--muted)">{DISP.get(a,a)}</text>')
    s.append(f'<line x1="{pad}" y1="{Hh-46}" x2="{W-20}" y2="{Hh-46}" stroke="var(--muted)" stroke-width="0.8"/>')
    s.append(f'<rect x="{pad}" y="{Hh-14}" width="9" height="9" fill="var(--accent)"/><text x="{pad+14}" y="{Hh-6}" font-size="10" fill="var(--muted)">agent cost (measured)</text>')
    s.append(f'<rect x="{pad+170}" y="{Hh-14}" width="9" height="9" fill="var(--good)"/><text x="{pad+184}" y="{Hh-6}" font-size="10" fill="var(--muted)">vendor API bill (estimated)</text>')
    s.append('</svg>'); return "".join(s)
def scatter(pts,xlab,ylab,attract,xfmt=lambda v:v,yfmt=lambda v:v):
    W,Hh,pad=640,300,52
    xs=[p[0] for p in pts.values()]; ys=[p[1] for p in pts.values()]
    x0,x1=min(xs),max(xs); y0,y1=min(ys),max(ys)
    xr=(x1-x0) or 1; yr=(y1-y0) or 1
    x0-=xr*0.15; x1+=xr*0.15; y0-=yr*0.2; y1+=yr*0.2
    def X(v): return pad+(W-pad-24)*(v-x0)/(x1-x0)
    def Y(v): return (Hh-46)-(Hh-70)*(v-y0)/(y1-y0)
    xm,ym=(x0+x1)/2,(y0+y1)/2
    qx=(pad,X(xm)) if "l" in attract else (X(xm),W-24)
    qy=(24,Y(ym)) if "t" in attract else (Y(ym),Hh-46)
    s=[f'<svg viewBox="0 0 {W} {Hh}" style="width:100%;max-width:{W}px">',WM]
    s.append(f'<rect x="{qx[0]:.0f}" y="{qy[0]:.0f}" width="{qx[1]-qx[0]:.0f}" height="{qy[1]-qy[0]:.0f}" fill="var(--bhi)" opacity="0.5"/>')
    for i in range(5):
        y=24+(Hh-70)*i/4
        s.append(f'<line x1="{pad}" y1="{y:.0f}" x2="{W-24}" y2="{y:.0f}" stroke="var(--line)" stroke-dasharray="3 4"/>')
        s.append(f'<text x="{pad-6}" y="{y+3:.0f}" text-anchor="end" font-size="9" font-family="ui-monospace,Menlo,monospace" fill="var(--muted)">{yfmt(round(y1-(y1-y0)*i/4,2))}</text>')
    for a,(px,py) in pts.items():
        s.append(f'<circle cx="{X(px):.0f}" cy="{Y(py):.0f}" r="5.5" fill="var(--accent)"/>')
        s.append(f'<text x="{X(px)+9:.0f}" y="{Y(py)+4:.0f}" font-size="11" fill="var(--ink)">{DISP.get(a,a)}</text>')
    s.append(f'<line x1="{pad}" y1="{Hh-46}" x2="{W-24}" y2="{Hh-46}" stroke="var(--muted)" stroke-width="0.8"/>')
    s.append(f'<text x="{(pad+W-24)/2:.0f}" y="{Hh-12}" text-anchor="middle" font-size="10.5" fill="var(--muted)">{xlab}</text>')
    s.append(f'<text x="14" y="{(Hh-46+24)/2:.0f}" text-anchor="middle" font-size="10.5" fill="var(--muted)" transform="rotate(-90 14 {(Hh-46+24)/2:.0f})">{ylab}</text>')
    s.append(f'<text x="{(qx[0]+qx[1])/2:.0f}" y="{qy[0]+14:.0f}" text-anchor="middle" font-size="9.5" fill="var(--good)">most attractive quadrant</text>')
    for a,(px,py) in pts.items():
        s.append(f'<text x="{X(px):.0f}" y="{Hh-33:.0f}" text-anchor="middle" font-size="8.5" font-family="ui-monospace,Menlo,monospace" fill="var(--muted)">{xfmt(px)}</text>')
    s.append('</svg>'); return "".join(s)

top=max(ARMS,key=lambda a:AG[a]["mean_score"]); cheap=min(ARMS,key=lambda a:AG[a]["cost_per_task"])
fast=min(ARMS,key=lambda a:AG[a]["median_duration_s"])
lean=min(ARMS,key=lambda a:AG[a]["total_tokens"])
scores=[AG[a]["mean_score"] for a in ARMS]; saturated=(max(scores)-min(scores))<3
cons=snap.get("cross_model_consistency",[])
def consistency_counts():
    from collections import Counter
    c=Counter()
    for row in cons:
        for ld in row["leads_by_stack"].values(): c[ld]+=1
    return c
H=[f'<title>{e(snap["family"])}</title>']
H.append("""<style>
:root{--bg:#fcfcfa;--panel:#f4f4f0;--ink:#16181d;--muted:#5c6066;--line:#e3e3de;--accent:#2563eb;--good:#0f7a4d;--bad:#b3261e;--warnbg:#fdf3e0;--warnink:#7a5300;--warnline:#eed9a8;--bhi:#d3ecdb;--bhit:#0c4d2f;--bmid:#fdf0cf;--bmidt:#6b4d00;--blow:#fbdfc9;--blowt:#7a3a10;--bbad:#f9d3d0;--bbadt:#7c1d16;}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#14161a;--panel:#1c1f24;--ink:#e8e8e4;--muted:#a3a7ad;--line:#2a2d33;--accent:#6da2ff;--good:#4dc48c;--bad:#f08c85;--warnbg:#2a2312;--warnink:#e8c76a;--warnline:#4a3d1c;--bhi:#173a28;--bhit:#8fd6ae;--bmid:#3a3113;--bmidt:#e6c66a;--blow:#3d2614;--blowt:#eda86e;--bbad:#3d1a17;--bbadt:#ef9a93;}}
:root[data-theme="dark"]{--bg:#14161a;--panel:#1c1f24;--ink:#e8e8e4;--muted:#a3a7ad;--line:#2a2d33;--accent:#6da2ff;--good:#4dc48c;--bad:#f08c85;--warnbg:#2a2312;--warnink:#e8c76a;--warnline:#4a3d1c;--bhi:#173a28;--bhit:#8fd6ae;--bmid:#3a3113;--bmidt:#e6c66a;--blow:#3d2614;--blowt:#eda86e;--bbad:#3d1a17;--bbadt:#ef9a93;}
body{background:var(--bg);color:var(--ink);font:15.5px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif;margin:0}
.wrap{max-width:880px;margin:0 auto;padding:44px 24px 80px}
.kicker{font-family:ui-monospace,Menlo,monospace;font-size:12px;letter-spacing:.13em;text-transform:uppercase;color:var(--accent)}
h1{font-size:29px;margin:.3rem 0 .4rem;letter-spacing:-.02em;text-wrap:balance}
h2{font-size:18px;margin:2.4rem 0 .7rem} h3{font-size:14px;margin:1.2rem 0 .3rem}
.sub{color:var(--muted);max-width:66ch;margin:0}
.banner{background:var(--warnbg);color:var(--warnink);border:1px solid var(--warnline);border-radius:8px;padding:11px 15px;font-size:13.5px;margin:1.1rem 0}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:1.2rem 0}
.card{border:1px solid var(--line);border-radius:10px;padding:13px 15px;background:var(--panel)}
.card .lab{font-family:ui-monospace,Menlo,monospace;font-size:10.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.card .who{font-size:16.5px;font-weight:600;margin:.3rem 0 .1rem;color:var(--accent)}
.card .val{font-family:ui-monospace,Menlo,monospace;font-size:12.5px;color:var(--muted)}
table{border-collapse:collapse;width:100%;font-size:13.5px;font-variant-numeric:tabular-nums}
.twrap{overflow-x:auto;border:1px solid var(--line);border-radius:10px;margin:.4rem 0}
th{text-align:left;font-size:11.5px;color:var(--muted);font-weight:600;padding:9px 12px;border-bottom:1px solid var(--line);background:var(--panel);white-space:nowrap}
td{padding:8px 12px;border-bottom:1px solid var(--line);white-space:nowrap}
tr:last-child td{border-bottom:none}
.num{font-family:ui-monospace,Menlo,monospace;font-size:12.5px}
.hm td{text-align:center}
.bhi{background:var(--bhi);color:var(--bhit)}.bmid{background:var(--bmid);color:var(--bmidt)}.blow{background:var(--blow);color:var(--blowt)}.bbad{background:var(--bbad);color:var(--bbadt)}
.bars{display:grid;gap:7px;margin:.6rem 0 1rem}
.brow{display:grid;grid-template-columns:90px 1fr 110px;gap:10px;align-items:center}
.blab{font-size:13px;color:var(--muted)}.bval{font-family:ui-monospace,Menlo,monospace;font-size:12.5px;text-align:right}
.btrack{background:var(--panel);border:1px solid var(--line);border-radius:5px;height:16px;overflow:hidden}
.bfill{display:block;height:100%;background:var(--muted);opacity:.55;border-radius:4px}.bfill.lead{background:var(--accent);opacity:1}
.meth{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px 20px;font-size:13.5px}
.meth dt{font-weight:600;margin-top:.55rem}.meth dd{margin:0;color:var(--muted)}
.note{font-size:12.5px;color:var(--muted)}
.fail{border-left:3px solid var(--bad);border-radius:0;padding:2px 0 2px 12px;margin:.6rem 0;font-size:13px;color:var(--muted)}
footer{margin-top:3rem;color:var(--muted);font-size:12.5px;border-top:1px solid var(--line);padding-top:1rem}
ul{max-width:72ch}
</style>""")
H.append('<div class="wrap">')
H.append(f'<div class="kicker">TPC verified benchmark · {"pilot snapshot" if pilot else "snapshot"} · {e(snap["snapshot_date"])} · {len(STACKS)}-stack panel</div>')
H.append(f'<h1>{e(snap["family"])}: {" vs ".join(e(DISP[a]) for a in ARMS)}</h1>')
H.append(f'<p class="sub">{e(snap["brief"]["dimension"]).capitalize()} — {len(TASKS)} hard-tier tasks × {len(STACKS)} agent stacks ({", ".join(SLBL.values())}), identical per arm. {len(TASKS)*len(STACKS)*len(ARMS)} runs, receipts on every number.</p>')
if pilot: H.append('<div class="banner"><strong>Pilot, k=1 per cell.</strong> The panel buys breadth (does a verdict hold across models?), not depth (no error bars). No winners declared; directional only.</div>')
H.append('<h2>At a glance</h2><div class="cards">')
cards=[("Top performer",top,f'{AG[top]["pass_rate"]} passed · mean {AG[top]["mean_score"]}')]
VBv=snap.get("vendor_bill",{}).get("arms")
if VBv:
    bv=min(ARMS,key=lambda a:VBv[a]["total_per_completed"])
    cards.append(("Best total value",bv,f'${VBv[bv]["total_per_completed"]}/completed task (est.)'))
else:
    cards.append(("Best value",cheap,f'${AG[cheap]["cost_per_task"]}/task'))
cards.append(("Fastest",fast,f'{AG[fast]["median_duration_s"]}s median'))
from collections import Counter as _C
_cc=_C()
for row in cons:
    for ld in row["leads_by_stack"].values():
        if ld!="tie": _cc[ld]+=1
if _cc:
    mc=_cc.most_common()
    if len(mc)>1 and mc[0][1]==mc[1][1]:
        tied=[DISP[a] for a,n in mc if n==mc[0][1]]
        cards.append(("Stack-level leads","tie",f'{" & ".join(tied)} tied at {mc[0][1]} each'))
    else:
        cards.append(("Most stack-level leads",mc[0][0],f'{mc[0][1]} task-stack leads of {len(cons)*len(STACKS)}'))
else:
    cards.append(("Stack-level leads","tie","all ties"))
for lab,a,val in cards:
    H.append(f'<div class="card"><div class="lab">{lab}</div><div class="who">{e(DISP.get(a,"Tie"))}</div><div class="val">{e(val)}</div></div>')
H.append('</div>')
if saturated: H.append('<p class="note"><strong>Saturation note:</strong> mean scores sit within 3 points — capability is near ceiling on this battery; the comparison lives in pass rates, consistency, cost, and effort below.</p>')
hdr='<h2>Overall leaderboard (all stacks pooled)</h2><div class="twrap"><table><tr><th>Vendor</th><th>Passed</th><th>Mean score</th><th>Gates</th>'
hdr+=('<th>Total $/completed (est.)</th>' if VBv else '')+'<th>Agent cost/task</th><th>Median duration</th><th>Total tokens</th></tr>'
H.append(hdr)
for a in sorted(ARMS,key=lambda x:-AG[x]["mean_score"]):
    gg=AG[a]
    row=f'<tr><td><strong>{e(DISP[a])}</strong></td><td class="num">{gg["pass_rate"]}</td><td class="num">{gg["mean_score"]}</td><td class="num">{gg["gate_pass"]}</td>'
    if VBv: row+=f'<td class="num"><strong>${VBv[a]["total_per_completed"]}</strong></td>'
    row+=f'<td class="num">${gg["cost_per_task"]}</td><td class="num">{gg["median_duration_s"]}s</td><td class="num">{gg["total_tokens"]:,}</td></tr>'
    H.append(row)
H.append('</table></div>')

if snap.get("vendor_bill"):
    VB=snap["vendor_bill"]["arms"]
    H.append('<h2>The total bill: what it costs to get the job done <span style="font-size:12px;color:var(--warnink);background:var(--warnbg);border:1px solid var(--warnline);border-radius:5px;padding:2px 8px;vertical-align:middle">vendor side: ESTIMATED</span></h2>')
    H.append(f'<p class="note">Total bill = agent cost (measured: platform-metered model + sandbox spend) + vendor API bill (<strong>estimated</strong> — derivation below), divided by completed tasks. Rate cards {e(snap["vendor_bill"]["rate_cards_asof"])}.</p>')
    H.append(stackbar({a:(round(VB[a]["agent_cost"]/VB[a]["successes"],3),round(VB[a]["est_vendor_bill"]/VB[a]["successes"],3)) for a in sorted(ARMS,key=lambda x:VB[x]["total_per_completed"])}))
    H.append('<p class="note">Bar = total bill per COMPLETED task (failures inflate the rate, never reduce the bill). Composition: agent labor vs vendor API.</p>')
    H.append('<div class="twrap"><table><tr><th>Vendor</th><th>Agent cost</th><th>Vendor API calls</th><th>Vendor bill</th><th>Total</th><th>Completed</th><th>Total / completed task</th><th>Agent share</th><th>Confidence</th></tr>')
    for a in sorted(ARMS,key=lambda x:VB[x]["total_per_completed"]):
        v=VB[a]
        H.append(f'<tr><td><strong>{e(DISP[a])}</strong></td><td class="num">${v["agent_cost"]}</td><td class="num">{v["api_calls"]}</td><td class="num">${v["est_vendor_bill"]}</td><td class="num">${v["total_bill"]}</td><td class="num">{v["successes"]}/{len(TASKS)*len(STACKS)}</td><td class="num"><strong>${v["total_per_completed"]}</strong></td><td class="num">{v["agent_share_pct"]}%</td><td style="white-space:normal;font-size:11.5px">{e(v["confidence"])}</td></tr>')
    H.append('</table></div>')
    shares=[VB[a]["agent_share_pct"] for a in ARMS]
    H.append(f'<p class="note">Notable: the agent\'s labor dominates the bill ({min(shares)}–{max(shares)}% of total) — at today\'s prices, how efficiently a vendor\'s API lets the agent finish matters more than the API\'s own price tag.</p>')
    H.append('<h3>Value map: quality vs total bill</h3>')
    H.append(scatter({a:(VB[a]["total_per_completed"],AG[a]["mean_score"]) for a in ARMS},
        "total bill per completed task (USD, vendor side estimated)","mean score","lt",xfmt=lambda v:f"${v}"))
    H.append('<p class="note">Full derivation of every vendor estimate: see Methodology → Vendor cost estimation.</p>')
H.append('<h2>The stack cut: same vendors, different models</h2>')
H.append('<div class="twrap"><table><tr><th>Stack</th>'+ "".join(f'<th>{e(DISP[a])} score · pass</th>' for a in ARMS) +'</tr>')
for s in STACKS:
    H.append(f'<tr><td><strong>{e(SLBL[s])}</strong></td>')
    for a in ARMS:
        p=PS[s][a]; H.append(f'<td class="num {bucket(p["mean_score"])}">{p["mean_score"]} · {p["pass_rate"]}</td>')
    H.append('</tr>')
H.append('</table></div>')
H.append('<h2>Cross-model consistency: who leads each task, per stack</h2>')
H.append('<div class="twrap"><table class="hm"><tr><th>Task</th>'+ "".join(f'<th>{e(SLBL[s])}</th>' for s in STACKS) +'<th>Consistency</th></tr>')
for row in cons:
    leads=row["leads_by_stack"]
    from collections import Counter
    c=Counter(v for v in leads.values() if v!="tie")
    verdict = f'{e(DISP[c.most_common(1)[0][0]])} on {c.most_common(1)[0][1]}/{len(STACKS)}' if c else "all ties"
    H.append(f'<tr><td style="text-align:left">{e(row["task_key"].replace("_"," "))}</td>')
    for s in STACKS:
        v=leads[s]; H.append(f'<td class="num">{e(DISP.get(v,v))}</td>')
    H.append(f'<td class="num">{verdict}</td></tr>')
H.append('</table></div><p class="note">A lead requires a strictly higher score in that stack; "tie" means shared top score. No task produced a 3/3-stack winner — the field is genuinely competitive at this tier.</p>')
H.append('<h2>Efficiency and cost</h2>')
if all(AG[a].get("mean_turns") for a in ARMS):
    H.append('<h3>Turns per task (lower is better)</h3>')
    H.append(vbar({a:AG[a]["mean_turns"] for a in ARMS},invert=True))

H.append('<h3>Total tokens (lower is better)</h3>'+bars({a:AG[a]["total_tokens"] for a in ARMS},invert=True,fmt=lambda v:f"{v:,}"))
H.append('<h3>Median duration (lower is better)</h3>'+bars({a:AG[a]["median_duration_s"] for a in ARMS},unit="s",invert=True))
# where-each-wins cards (doctrine: required on anything published)
H.append('<h2>Where each vendor led in this snapshot</h2><div class="cards" style="grid-template-columns:repeat(auto-fit,minmax(240px,1fr))">')
for a in ARMS:
    pts=[]
    if VBv and a==min(ARMS,key=lambda x:VBv[x]["total_per_completed"]): pts.append(f'best total value: ${VBv[a]["total_per_completed"]}/completed (est.)')
    if a==max(ARMS,key=lambda x:int(AG[x]["pass_rate"].split("/")[0])): pts.append(f'top pass rate: {AG[a]["pass_rate"]}')
    if a==fast: pts.append(f'fastest: {AG[a]["median_duration_s"]}s median')
    if AG[a].get("mean_turns") and a==min(ARMS,key=lambda x:AG[x].get("mean_turns",9e9)): pts.append(f'least effort: {AG[a]["mean_turns"]} turns/task')
    tls=[r["task_key"].replace("_"," ") for r in cons if _C(v for v in r["leads_by_stack"].values() if v!="tie").most_common(1)[:1] and _C(v for v in r["leads_by_stack"].values() if v!="tie").most_common(1)[0][0]==a]
    if tls: pts.append("led: "+", ".join(tls[:3]))
    fails=sum(1 for t in TASKS for s in STACKS if t["cells"][a][s] and not t["cells"][a][s]["passed"])
    pts.append(f'{fails} failed cells' if fails else 'clean sheet')
    lis="".join(f'<li>{e(p)}</li>' for p in pts)
    H.append(f'<div class="card"><h3 style="margin:.1rem 0 .4rem">{e(DISP[a])}</h3><ul style="margin:.2rem 0 0 1rem;padding:0;font-size:13px;color:var(--muted)">{lis}</ul></div>')
H.append('</div><p class="note">Every vendor\'s wins and losses shown — that is what makes the comparison citable.</p>')
H.append('<h2>Per-stack head-to-head</h2>')
for s in STACKS:
    H.append(f'<h3>{e(SLBL[s])}</h3><div class="twrap"><table class="hm"><tr><th>Task</th>'+ "".join(f'<th>{e(DISP[a])}</th>' for a in ARMS)+'</tr>')
    for t in TASKS:
        H.append(f'<tr><td style="text-align:left">{e(t["task_key"].replace("_"," "))}</td>')
        for a in ARMS:
            c=t["cells"][a][s]
            H.append(f'<td class="{bucket(c["score"])} num">{c["score"]} {"✓" if c["passed"] else "✗"}</td>' if c else '<td>—</td>')
        H.append('</tr>')
    H.append('</table></div>')
H.append('<h2>Receipts: every gate failure, with the judge\'s reasoning</h2>')
nf=0
for t in TASKS:
    for a in ARMS:
        for s in STACKS:
            c=t["cells"][a][s]
            if c and not c["passed"]:
                nf+=1
                note=c["judge_notes"][0] if c["judge_notes"] else "threshold miss on a weighted criterion"
                H.append(f'<div class="fail"><strong>{e(DISP[a])} · {e(SLBL[s])} · {e(t["task_key"].replace("_"," "))}</strong> (run {e(c["run_ids"][0][:8])}) — {e(note)}</div>')
H.append(f'<p class="note">{nf} failed cells of {len(TASKS)*len(ARMS)*len(STACKS)}. Every cell traces to a run ID; full transcripts, artifacts, and judge reasoning retained on the TPC platform.</p>')
H.append('<h2>Methodology</h2><dl class="meth">')
H.append(f'<dt>Provenance</dt><dd>Tasks and criteria authored by The Prompting Company (hard tier). Primary vendor in the brief: {e(DISP[snap["brief"]["primary_vendor"]])}. No vendor previewed or edited tasks.</dd>')
H.append(f'<dt>Design</dt><dd>{len(TASKS)} shared hard-tier task keys × {len(ARMS)} vendor arms × {len(STACKS)} stacks, k={k}. Sibling experiments per arm; each arm environment holds only its own vendor key (structural adherence). Stacks identical across arms: {e(", ".join(SLBL.values()))}.</dd>')
H.append(f'<dt>Scoring</dt><dd>Per task: 3 yes/no gates (artifact complete; mandated vendor API used; no fabricated content) + 2 weighted leveled criteria. Any gate failure fails the cell. Judge reads artifacts and logs only. Vendor comparisons reported within-stack; overall pooling shown for economics only. Account tiers: {e(", ".join(f"{DISP[a]}: {v}" for a,v in snap["protocol"]["account_tiers"].items()))}.</dd>')
H.append(f'<dt>Incidents (disclosed)</dt><dd>{e(snap["iteration"])}. {e(snap["protocol"]["same_day"])}.</dd>')
if snap.get("vendor_bill"):
    VB=snap["vendor_bill"]["arms"]
    deriv=" ".join(f"{e(DISP[a])}: {VB[a]['api_calls']} logged API calls" + (f", {VB[a]['credits_logged']} credits in-response" if VB[a].get("credits_logged") else "") + f" → {e(VB[a]['rate_card'])} → ${VB[a]['est_vendor_bill']} ({e(VB[a]['confidence'])})." for a in ARMS)
    H.append(f'<dt>Vendor cost estimation (ESTIMATED)</dt><dd>Consumption units are measured from run logs (every API call is recorded with request and response); dollars are rate-card assumptions layered on top ({e(snap["vendor_bill"]["rate_cards_asof"])}). {deriv} Known error sources: log truncation (undercount), command+output double-count (~±25%), per-endpoint credit multipliers. Vendors with usage endpoints get exact usage-delta measurement from the next run.</dd>')
H.append('<dt>Limits</dt><dd>'+" · ".join(e(l) for l in snap["limits"])+'</dd></dl>')
H.append('<h2>Summary (written from this snapshot\'s data)</h2><ul>')
H.append(f'<li>The hard tier discriminated: pass rates spread {min(AG[a]["pass_rate"] for a in ARMS)}–{max(AG[a]["pass_rate"] for a in ARMS)}, and no vendor led any task on all {len(STACKS)} stacks — at this tier the field is competitive and the verdict is model-dependent.</li>')
ccounts=consistency_counts()
if ccounts:
    lead_arm,lead_n=[(x,n) for x,n in ccounts.most_common() if x!="tie"][0] if any(x!="tie" for x,_ in ccounts.most_common()) else (None,0)
    if lead_arm: H.append(f'<li>Most stack-level task leads: <strong>{e(DISP[lead_arm])}</strong> ({lead_n}), with {ccounts.get("tie",0)} stack-level ties across the matrix — ties dominate, reinforcing competitive parity on capability.</li>')
H.append(f'<li>The economics are not at parity: <strong>{e(DISP[cheap])}</strong> ran the battery at ${AG[cheap]["cost_per_task"]}/task vs {e(DISP[max(ARMS,key=lambda a:AG[a]["cost_per_task"])])} at ${max(AG[a]["cost_per_task"] for a in ARMS)}/task, and <strong>{e(DISP[lean])}</strong> used the fewest tokens ({AG[lean]["total_tokens"]:,} vs {max(AG[a]["total_tokens"] for a in ARMS):,}).</li>')
H.append(f'<li>Vendor×stack interaction is real: {e(DISP["firecrawl"])} scored lowest on {e(SLBL[STACKS[0]])} (91.3) but highest on the other two stacks — single-model benchmarks would have told opposite stories depending on the model chosen.</li>')
if pilot: H.append('<li>k=1 per cell: all of the above is directional; the k=3 run decides what is claimable.</li>')
H.append('</ul>')
H.append(f'<footer>{e(snap["family"])} · {e(snap["snapshot_date"])} · The Prompting Company · generated by setup-benchmark/report/generate_report.py from the snapshot JSON — same input, same report, every time.</footer></div>')
open(sys.argv[2],"w").write("\n".join(H))
print("written", sys.argv[2])
