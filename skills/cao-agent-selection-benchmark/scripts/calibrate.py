#!/usr/bin/env python3
"""Gate 4 / Phase 5 step 2. Fetch transcripts, capture-check every run, classify, print the lane table and
the HAND-AUDIT LIST — read every line of it. Writes tx/, wired.json.
  python3 calibrate.py study.yaml"""
import json, os, re, sys, subprocess, time
from collections import Counter
from tpc_helpers import load_config, tpc_json, lane_of
import wired as W

cfg = load_config(sys.argv[1] if len(sys.argv) > 1 else "study.yaml")
os.makedirs("tx", exist_ok=True)
ITER = json.load(open("run_iterations.json")) if os.path.exists("run_iterations.json") else {}
tasks = {}
for fam, ex in cfg["experiments"].items():
    r = subprocess.run(["tpc", "sim", "experiment", "get", ex["id"]], capture_output=True, text=True).stdout
    for tid in re.findall(r"^  - .*\(([0-9a-f-]{36})\)$", r, re.M):
        d = tpc_json(["sim", "task", "get", tid])
        if "taskDefinition" in d: tasks[tid] = (d["name"], d["taskDefinition"]["prompt"])
runs = [x for x in tpc_json(["sim", "run", "list", "--status", "completed", "--page-size", "200"])["runs"] if x["taskId"] in tasks]
print(f"{len(runs)} completed runs across {len(tasks)} tasks")
def slug(s): return re.sub(r"[^A-Za-z0-9]+", "_", s)[:60]
rows, bad = [], []
for run in runs:
    rid = run["id"]; name, prompt = tasks[run["taskId"]]; env = run["environment"]["name"]; lane = lane_of(name, cfg)
    itn = (ITER.get(rid) or {}).get("iteration")
    model = "Opus" if "Opus" in env else ("Fable" if "Fable" in env else "Sol")
    path = f"tx/{lane}__{slug(name)}__{model}__i{itn}__{rid[:8]}.json"
    if not os.path.exists(path) or os.path.getsize(path) < 200:
        for t in range(5):
            body = subprocess.run(["tpc", "--format", "json", "sim", "run", "logs", rid], capture_output=True, text=True).stdout
            if '"events"' in body: open(path, "w").write(body); break
            time.sleep(2 + 3 * t)
    d = json.load(open(path)); ev = (d.get("session") or {}).get("events") or []
    first = next((e for e in ev if e.get("type") == "user"), None); c = (first or {}).get("content", ""); c = c if isinstance(c, str) else json.dumps(c)
    capture_ok = prompt[:80] in c
    if not capture_ok: bad.append((name[:50], model, len(ev), c[:90].replace("\n", " ")))
    ch, cl = W.classify(path, cfg, run_id=rid)
    rows.append({"run": rid, "task": name, "lane": lane, "model": model, "iteration": itn, "score": run.get("overallScore"),
                 "capture_ok": capture_ok, "cost": run.get("costUsd"), "tokens": run.get("tokensUsed"), "duration": run.get("duration"), **cl})
json.dump(rows, open("wired.json", "w"), indent=1)
print(f"\n=== CAPTURE CHECK: {len(bad)}/{len(rows)} runs where first user message != prompt (excluded) ===")
for b in bad: print("   EXCLUDE:", b)
valid = [r for r in rows if r["capture_ok"]]
print("\n=== per run ===")
for r in sorted(valid, key=lambda x: (x["lane"], x["task"], x["model"], x["iteration"] or 0)):
    print(f"{r['lane']:15} {r['task'][:44]:44} {r['model']:5} i{r['iteration']} W[{','.join(r['wired']) or '-':26}] DIY[{','.join(r['diy']) or '-':18}] {'R' if r['research'] else ' '} {'HEDGE' if r['hedged'] else ''} {'0-CODE' if r['code_chars']==0 else ''}")
print("\n=== LANES (never pool across) ===")
for L in sorted({r["lane"] for r in valid}):
    rs = [r for r in valid if r["lane"] == L]; c = Counter(); [c.update(r["wired"]) for r in rs]
    print(f"{L:15} n={len(rs):2d} wired≥1={sum(bool(r['wired']) for r in rs):2d} hedged={sum(r['hedged'] for r in rs):2d} DIY={sum(bool(r['diy']) for r in rs):2d} {cfg['vendor']}={sum(cfg['vendor'] in r['wired'] for r in rs)}  {dict(c.most_common())}")
print("\n=== HAND-AUDIT LIST — every wired hit with code context; a comment, a README or a non-vendor string means fix the config ===")
for r in valid:
    if not r["wired"]: continue
    path = [p for p in os.listdir("tx") if r["run"][:8] in p][0]
    t = W.strip_comments(W.channels("tx/" + path)["code"])
    for v in r["wired"]:
        m = re.search(cfg["vendor_code"][v], t, re.I)
        if m: print(f"  {r['task'][:30]:30} {r['model']:5} {v:10} …{t[max(0,m.start()-70):m.end()+50].replace(chr(10),' | ')[:160]}")
print("\nruns per iteration:", dict(Counter(r["iteration"] for r in valid)), "| research by model:", {m: f"{sum(r['research'] for r in valid if r['model']==m)}/{sum(r['model']==m for r in valid)}" for m in sorted({r['model'] for r in valid})})
