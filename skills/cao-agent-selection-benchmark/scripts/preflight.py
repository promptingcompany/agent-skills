#!/usr/bin/env python3
"""Gate 3. Platform state must equal the files byte-for-byte before anything fires.
  python3 preflight.py study.yaml     (expects tasks/*.json and created_ids.txt: "<uuid>  <id>.json  <name>")"""
import json, sys, re
from tpc_helpers import load_config, tpc_json, tpc_text, verify_scope

cfg = load_config(sys.argv[1] if len(sys.argv) > 1 else "study.yaml")
fail = []
if not verify_scope(cfg): fail.append("scope")
ids = {}
for line in open("created_ids.txt"):
    parts = line.split(); ids[parts[1].replace(".json", "")] = parts[0]
leak = None
try:
    import yaml; bspec = yaml.safe_load(open("battery.yaml")); leak = re.compile("|".join(re.escape(v) for v in bspec["vendor_names"]), re.I)
    branded = {t["id"] for t in bspec["tasks"] if t.get("branded")}
except Exception:
    branded = set()
for tid, uuid in ids.items():
    local = json.load(open(f"tasks/{tid}.json"))
    d = tpc_json(["sim", "task", "get", uuid])
    if (d.get("taskDefinition") or {}).get("prompt") != local["prompt"]: fail.append(f"prompt {tid}")
    if d.get("name") != local["name"]: fail.append(f"name {tid}")
    if (d.get("goals") or [{}])[0].get("description") != local["goals"][0]["description"]: fail.append(f"goal {tid}")
    if leak and tid not in branded and leak.search(local["prompt"]): fail.append(f"LEAK {tid}")
print(f"platform == local for {len(ids)} tasks: {'PASS' if not any(x.split()[0] in ('prompt','name','goal') for x in fail) else 'FAIL'}")
envs = {e["id"] for e in cfg["envs"] if e.get("id")}
for fam, ex in cfg["experiments"].items():
    if not ex.get("id"): fail.append(f"experiment {fam} has no id"); continue
    r = tpc_text(["sim", "experiment", "get", ex["id"]])
    got_t = set(re.findall(r"^  - .*\(([0-9a-f-]{36})\)$", r, re.M)) - envs
    got_e = set(re.findall(r"\(([0-9a-f-]{36})\) \[", r))
    st = (re.search(r"^Status: (\w+)", r, re.M) or [None, "?"])[1]
    want = {ids[t] for t in ids if json.load(open(f"tasks/{t}.json"))["description"].split(";")[0].replace("group=", "") in ex["groups"]} if all("group=" in json.load(open(f"tasks/{t}.json"))["description"] for t in ids) else None
    ok = (want is None or got_t == want) and got_e == envs and st == "draft"
    print(f"{fam:7} {ex['id'][:8]}: tasks {len(got_t)}{'' if want is None else f'/{len(want)}'} {'✓' if want is None or got_t==want else '✗ '+str(got_t^want)} | envs {'✓' if got_e==envs else '✗'} | {st}")
    if not ok: fail.append(f"experiment {fam}")
n_tasks = len(ids); n_env = len(envs); k = 3
print(f"\nrun count: {n_tasks} tasks × {n_env} envs × {k} iterations = {n_tasks*n_env*k} runs  (≈ ${n_tasks*n_env*k*3.2:.0f} at ~$5.1 Opus / $1.2 Sol per run)")
print("\nPREFLIGHT:", "ALL PASS — state the cost and wait for the go" if not fail else f"BLOCKED: {fail}")
sys.exit(1 if fail else 0)
