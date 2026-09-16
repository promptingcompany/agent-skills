#!/usr/bin/env python3
"""Deterministic deep dive over wired.json + tx/. Writes deepdive.txt and mined/<run>.txt (verbatim prose +
docs per run — the only thing quote sweeps read). Every number here is recomputed from transcripts.
  python3 deepdive.py study.yaml"""
import json, os, re, sys
from collections import Counter
from tpc_helpers import load_config, short
import wired as W

cfg = load_config(sys.argv[1] if len(sys.argv) > 1 else "study.yaml")
V = cfg["vendor"]; rows = [r for r in json.load(open("wired.json")) if r["capture_ok"]]
def tx(r): return "tx/" + [p for p in os.listdir("tx") if r["run"][:8] in p][0]
out = []; P = lambda *a: out.append(" ".join(str(x) for x in a))
os.makedirs("mined", exist_ok=True)
for r in rows:
    ch = W.channels(tx(r))
    hdr = (f"RUN {r['run']}\nTASK {r['task']}\nLANE {r['lane']} | MODEL {r['model']} | ITER {r['iteration']} | WIRED {r['wired']} | "
           f"PRESCRIBED {r['prescribed']} | DIY {r['diy']} | RESEARCH {r['research']} | HEDGED {r['hedged']}\n{'='*100}\n")
    open(f"mined/{r['lane']}__{short(r['task'],cfg).replace(' ','_')[:40]}__{r['model']}__i{r['iteration']}__{r['run'][:8]}.txt", "w").write(
        hdr + "### ASSISTANT PROSE\n" + ch["prose"] + "\n\n### DOCS WRITTEN\n" + ch["docs"])
P(f"extracted {len(rows)} runs to mined/")

P("\n" + "=" * 100 + "\n1. GRID — wired per task × model × iteration (DIY = only DIY code, - = nothing, * = hedged)")
models = sorted({r["model"] for r in rows}); iters = sorted({r["iteration"] for r in rows if r["iteration"]})
tasks = sorted({r["task"] for r in rows}, key=lambda t: (next(x["lane"] for x in rows if x["task"] == t), t))
P(f"{'task':34} | " + " | ".join(f"{m:{17*len(iters)}}" for m in models))
for t in tasks:
    cells = []
    for m in models:
        for i in iters:
            rr = [x for x in rows if x["task"] == t and x["model"] == m and x["iteration"] == i]
            cells.append(("(missing)" if not rr else ((",".join(rr[0]["wired"]) or ("DIY" if rr[0]["diy"] else "-")) + ("*" if rr[0]["hedged"] else "")))[:16])
    P(f"{short(t,cfg)[:34]:34} | " + " ".join(f"{c:16}" for c in cells))

P("\n" + "=" * 100 + f"\n2. {V.upper()} LEDGER — every run where the vendor appears (wired or prescribed)")
vre = re.compile(rf"[^.\n]*{V}[^.\n]*[.\n]", re.I)
for r in rows:
    if V in r["wired"] or V in r["prescribed"]:
        ch = W.channels(tx(r)); t = ch["prose"] + "\n" + ch["docs"]
        P(f"\n  [{r['lane']}] {short(r['task'],cfg)} | {r['model']} i{r['iteration']} | {'WIRED' if V in r['wired'] else 'prescribed only'} | research={r['research']} | run {r['run'][:8]}")
        for m in list(vre.finditer(t))[:4]: P("     >", re.sub(r"\s+", " ", m.group(0)).strip()[:300])
unb = [r for r in rows if r["lane"] != "PROBE"]
P(f"\n  {V} appears in {sum(1 for r in rows if V in r['wired'] or V in r['prescribed'])}/{len(rows)} runs; unbranded lanes {sum(1 for r in unb if V in r['wired'] or V in r['prescribed'])}/{len(unb)}; build family {sum(1 for r in unb if r['lane'].startswith('BUILD') and (V in r['wired'] or V in r['prescribed']))}/{sum(1 for r in unb if r['lane'].startswith('BUILD'))}")

tw = cfg.get("twin") or {}
if tw:
    P("\n" + "=" * 100 + f"\n3. TWIN PAIR — {tw['base']} vs {tw['gate']}: what changed when the one sentence was added")
    for key in (tw["base"], tw["gate"]):
        rs = sorted([r for r in rows if re.match(rf"{cfg['prefix']}-{key}(\b|_)", r["task"])], key=lambda x: (x["model"], x["iteration"] or 0))
        P(f"\n  {key}: n={len(rs)}  wired-any={sum(bool(r['wired']) for r in rs)}  {V}={sum(V in r['wired'] for r in rs)}  named={sum(V in r['prescribed'] or V in r['wired'] for r in rs)}  caps={dict(sum((Counter(r['caps']) for r in rs), Counter()))}")
        for r in rs: P(f"    {r['model']:5} i{r['iteration']}  wired={','.join(r['wired']) or '-':26} diy={','.join(r['diy']) or '-':16} research={r['research']}")

P("\n" + "=" * 100 + "\n4. HEDGES — ≥2 vendors wired behind a switch (count toward no single vendor)")
for r in rows:
    if r["hedged"]: P(f"  [{r['lane']}] {short(r['task'],cfg):34} {r['model']:5} i{r['iteration']}  {r['wired']}  run {r['run'][:8]}")
P(f"  hedged: {sum(r['hedged'] for r in rows)}/{len(rows)}  by model: {dict(Counter(r['model'] for r in rows if r['hedged']))}")

P("\n" + "=" * 100 + "\n5. SAY/DO — vendors named in prose/README but not wired (build/probe/control)")
for r in rows:
    if r["prescribed"] and r["lane"] != "ADVICE": P(f"  [{r['lane']}] {short(r['task'],cfg):34} {r['model']:5} i{r['iteration']}  wired={','.join(r['wired']) or '-':22} named-only={','.join(r['prescribed'])}")

P("\n" + "=" * 100 + "\n6. ADVICE lanes — what gets named (never ranks)")
for r in sorted([x for x in rows if x["lane"] == "ADVICE"], key=lambda x: (x["task"], x["model"], x["iteration"] or 0)):
    P(f"  {short(r['task'],cfg):20} {r['model']:5} i{r['iteration']} research={str(r['research']):5} {V}={'YES' if V in r['prescribed'] else 'no '} named={r['prescribed']}")

P("\n" + "=" * 100 + "\n7. RESEARCH and COST")
B = [r for r in rows if r["lane"].startswith("BUILD")]
for f in (True, False):
    rs = [r for r in B if r["research"] == f]; c = Counter(); [c.update(r["wired"]) for r in rs]
    P(f"  build family researched={str(f):5} n={len(rs):2d} any-vendor {sum(bool(r['wired']) for r in rs)} DIY-only {sum(bool(r['diy']) and not r['wired'] for r in rs)} {V} {sum(V in r['wired'] for r in rs)}  {dict(c.most_common())}")
for m in models:
    rs = [r for r in rows if r["model"] == m]
    P(f"  {m}: n={len(rs)} research {sum(r['research'] for r in rs)}/{len(rs)} cost=${sum(r['cost'] or 0 for r in rs):.2f} (${sum(r['cost'] or 0 for r in rs)/max(1,len(rs)):.2f}/run) tokens={sum(r['tokens'] or 0 for r in rs)/max(1,len(rs))/1e6:.2f}M/run duration={sum(r['duration'] or 0 for r in rs)/max(1,len(rs))/60000:.1f} min/run")
P(f"  study total: ${sum(r['cost'] or 0 for r in rows):.2f}")
open("deepdive.txt", "w").write("\n".join(out)); print("\n".join(out))
