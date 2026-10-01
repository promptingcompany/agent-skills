#!/usr/bin/env python3
"""run id → (family, experiment, iteration). De-duplicates by run id (a prior corpus summed per-experiment
counts and overstated by 75). Writes run_iterations.json.
  python3 iterations_map.py study.yaml [--iterations 3]"""
import json, sys
from collections import Counter
from tpc_helpers import load_config, tpc_json

cfg = load_config(sys.argv[1] if len(sys.argv) > 1 else "study.yaml")
iters = int(sys.argv[sys.argv.index("--iterations") + 1]) if "--iterations" in sys.argv else 3
m, seen = {}, Counter()
for fam, ex in cfg["experiments"].items():
    for n in range(1, iters + 1):
        try:
            d = tpc_json(["sim", "experiment", "run", "status", ex["id"], "--iteration", str(n)])
        except RuntimeError:
            print(f"{fam} iter {n}: no data"); continue
        it = d.get("iteration") or {}
        for r in d.get("runs") or []:
            seen[r["id"]] += 1
            m[r["id"]] = {"family": fam, "experiment": ex["id"], "iteration": n, "iteration_id": it.get("id"),
                          "status": r.get("status"), "taskId": r["taskId"], "environmentId": r["environmentId"]}
        print(f"  {fam:7} iter {n}: {it.get('status'):18} {dict(Counter(r.get('status') for r in d.get('runs') or []))}")
json.dump(m, open("run_iterations.json", "w"), indent=1)
dups = [k for k, v in seen.items() if v > 1]
print(f"{len(m)} unique runs; duplicates across iterations: {len(dups)}{'  ← would inflate counts' if dups else ' ✓'}")
