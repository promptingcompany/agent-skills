#!/usr/bin/env python3
"""Wait until every RUN across all iterations of all experiments is terminal. Keys on run status, never
iteration status (iterations hang in generating_results after all runs complete). Polls every 45 s.
  python3 wait_runs.py study.yaml [--iterations 3] [--max-minutes 120]"""
import sys, time
from collections import Counter
from tpc_helpers import load_config, tpc_json

cfg = load_config(sys.argv[1] if len(sys.argv) > 1 else "study.yaml")
iters = int(sys.argv[sys.argv.index("--iterations") + 1]) if "--iterations" in sys.argv else 3
maxm = int(sys.argv[sys.argv.index("--max-minutes") + 1]) if "--max-minutes" in sys.argv else 120
TERMINAL = {"completed", "failed", "cancelled"}
start = time.time()
while True:
    pending = 0; summary = []
    for fam, ex in cfg["experiments"].items():
        for n in range(1, iters + 1):
            try:
                d = tpc_json(["sim", "experiment", "run", "status", ex["id"], "--iteration", str(n)])
            except RuntimeError:
                summary.append(f"{fam}#{n}: no data"); pending += 1; continue
            runs = d.get("runs") or []
            if not runs: summary.append(f"{fam}#{n}: not fired"); continue
            c = Counter(r.get("status") for r in runs)
            pending += sum(v for k, v in c.items() if k not in TERMINAL)
            summary.append(f"{fam}#{n}: {dict(c)}")
    print(time.strftime("%H:%M:%S"), "|", " · ".join(summary), flush=True)
    if pending == 0:
        print("ALL RUNS TERMINAL"); sys.exit(0)
    if (time.time() - start) / 60 > maxm:
        print(f"TIMEOUT after {maxm} min, pending={pending}"); sys.exit(1)
    time.sleep(45)
