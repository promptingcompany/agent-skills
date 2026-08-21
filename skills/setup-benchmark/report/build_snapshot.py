#!/usr/bin/env python3
"""Runs -> snapshot JSON for setup-benchmark families.
Usage: build_snapshot.py <creation-ids.json> <family-name> <out-snapshot.json>
creation-ids.json shape: {"tasks":{"<taskkey>--<arm>": id}, "envs":{arm:{stack:envid}} OR {arm: envid},
"exps":{arm: expid}}. Handles single- and multi-stack. Newest completed run per cell wins.
Encodes: goalName/details parsing, gate-zeroing inputs, per-stack aggregates, cross-model
consistency, turns/toolcalls from log headers. Vendor-bill fields are left null for the
usage-delta/estimation step (see criteria-and-gates.md)."""
import json, sys, subprocess, time, re, statistics as st

ids=json.load(open(sys.argv[1])); FAMILY=sys.argv[2]; OUT=sys.argv[3]
ARMS=list(ids["exps"].keys())
multi=isinstance(next(iter(ids["envs"].values())),dict)
ENVMAP={}
for arm,v in ids["envs"].items():
    if multi:
        for stack,e in v.items(): ENVMAP[e]=(arm,stack)
    else: ENVMAP[v]=(arm,"default")
STACKS=sorted({s for _,s in ENVMAP.values()})
T2K={v:k for k,v in ids["tasks"].items()}

def tpc(*a):
    for _ in range(3):
        r=subprocess.run(["tpc","--format","json"]+list(a),capture_output=True,text=True)
        out="\n".join(l for l in r.stdout.splitlines() if "newer TPC CLI" not in l)
        try: return json.loads(out)
        except: time.sleep(3)
    raise RuntimeError(f"tpc {' '.join(a[:4])} failed")

cells={}
def consider(x):
    tid,eid=x.get("taskId"),x.get("environmentId")
    if tid not in T2K or eid not in ENVMAP or x.get("status")!="completed": return
    base,arm=T2K[tid].rsplit("--",1); _,stack=ENVMAP[eid]
    k=(base,arm,stack)
    if k not in cells or x.get("createdAt","")>cells[k].get("createdAt",""): cells[k]=x
for arm in ARMS:
    d=tpc("sim","experiment","run","status",ids["exps"][arm])
    for x in (d if isinstance(d,list) else d.get("runs") or []): consider(x)
d=tpc("sim","run","list")
for x in (d if isinstance(d,list) else d.get("runs") or []): consider(x)
print(f"cells: {len(cells)} (expect tasks×arms×stacks)")

TURNPAT=re.compile(r"(\d+) assistant \| (\d+) tool calls")
detail={}
for key,x in cells.items():
    rd=tpc("sim","run","get",x["id"])
    goals=[dict(n=g.get("goalName"),s=g.get("score"),p=g.get("passed"),
                detail=(g.get("details") or "")[:260]) for g in (rd.get("goalResults") or [])]
    log=subprocess.run(["tpc","sim","run","logs",x["id"]],capture_output=True,text=True).stdout[:2000]
    m=TURNPAT.search(log)
    detail["|".join(key)]=dict(rid=x["id"],passed=rd.get("passed"),score=rd.get("overallScore"),
        cost=rd.get("costUsd"),dur=rd.get("duration"),tokens=rd.get("tokensUsed"),
        turns=int(m.group(1)) if m else None, toolcalls=int(m.group(2)) if m else None, goals=goals)
    time.sleep(0.3)

TKEYS=sorted({k.split("|")[0] for k in detail})
def cell(t,a,s):
    c=detail.get(f"{t}|{a}|{s}")
    if not c: return None
    return dict(run_ids=[c["rid"]],passed=c["passed"],score=c["score"],cost_usd=c["cost"],
        duration_ms=c["dur"],tokens=c["tokens"],turns=c["turns"],
        gates={g["n"][6:].strip():g["p"] for g in c["goals"] if g["n"] and g["n"].startswith("GATE")},
        weighted={g["n"]:g["s"] for g in c["goals"] if g["n"] and not g["n"].startswith("GATE")},
        judge_notes=[f"{g['n']}: {g['detail']}" for g in c["goals"] if g["p"] is False and g.get("detail")][:2])

snap=dict(family=FAMILY,snapshot_date=time.strftime("%Y-%m-%d"),iteration="latest completed run per cell",
 provenance="tpc_authored",
 brief=dict(primary_vendor=ARMS[0],comparison_vendors=ARMS[1:],dimension="FILL",persona="FILL"),
 protocol=dict(k=1,stacks=[dict(id=s,label=s) for s in STACKS],judge="llm_judge",gates="v2_yes_no",
   same_day="FILL",account_tiers={a:"FILL" for a in ARMS}),
 arms={a:dict(experiment_id=ids["exps"][a],environment_ids=ids["envs"][a],valid=True,display=a.capitalize()) for a in ARMS},
 tasks=[dict(task_key=t,cells={a:{s:cell(t,a,s) for s in STACKS} for a in ARMS}) for t in TKEYS],
 aggregates={},per_stack={},vendor_bill=None,
 limits=["k=1 unless stated: directional only","REVIEW: arm validity (uniform gate failures = void, not a vendor result)"])
for a in ARMS:
    cs=[c for t in TKEYS for s in STACKS if (c:=cell(t,a,s))]
    snap["aggregates"][a]=dict(pass_rate=f"{sum(1 for c in cs if c['passed'])}/{len(cs)}",
        mean_score=round(st.mean([c["score"] for c in cs if c["score"] is not None]),1),
        total_cost=round(sum(c["cost_usd"] or 0 for c in cs),2),
        cost_per_task=round(sum(c["cost_usd"] or 0 for c in cs)/max(len(cs),1),3),
        median_duration_s=int(st.median([c["duration_ms"] for c in cs if c["duration_ms"]])/1000),
        total_tokens=sum(c["tokens"] or 0 for c in cs),
        mean_turns=round(st.mean([c["turns"] for c in cs if c["turns"]]),1) if any(c["turns"] for c in cs) else None,
        gate_pass=f"{sum(1 for c in cs for p in c['gates'].values() if p)}/{sum(len(c['gates']) for c in cs)}")
for s in STACKS:
    snap["per_stack"][s]={}
    for a in ARMS:
        cs=[c for t in TKEYS if (c:=cell(t,a,s))]
        if cs: snap["per_stack"][s][a]=dict(pass_rate=f"{sum(1 for c in cs if c['passed'])}/{len(cs)}",
            mean_score=round(st.mean([c["score"] for c in cs]),1))
cons=[]
for t in TKEYS:
    leads={}
    for s in STACKS:
        sc={a:(cell(t,a,s) or {}).get("score") for a in ARMS}; sc={a:v for a,v in sc.items() if v is not None}
        if sc:
            mx=max(sc.values()); l=[a for a,v in sc.items() if v==mx]
            leads[s]=l[0] if len(l)==1 else "tie"
    cons.append(dict(task_key=t,leads_by_stack=leads))
snap["cross_model_consistency"]=cons
json.dump(snap,open(OUT,"w"),indent=1)
print(f"snapshot -> {OUT} | FILL the brief/protocol placeholders, run arm-validity review, add vendor_bill per criteria-and-gates.md, then generate_report.py")
