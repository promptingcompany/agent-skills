#!/usr/bin/env python3
"""Pull runs + logs for the configured experiments into a local cache.

Usage:  python3 pull.py tracker.yaml [--iteration N | --latest] [--label 2026-W41]
Writes: <workdir>/<label>/runs.json and <workdir>/<label>/logs/<run_id>.log
Logs are cached across weeks (a run id's log never changes), so re-pulls are cheap."""
import json, os, re, subprocess, sys, time, argparse, datetime, concurrent.futures as cf
import yaml


def tpc(args, scope, want_json=True, retries=5):
    for i in range(retries):
        cmd = ["tpc", *args, "--scope", scope] + (["-f", "json"] if want_json else [])
        o = subprocess.run(cmd, capture_output=True, text=True)
        out = o.stdout
        if want_json:
            m = re.search(r"[\[{].*", out, re.S)
            if m:
                try:
                    return json.loads(m.group(0))
                except json.JSONDecodeError:
                    pass
        elif o.returncode == 0 and out.strip():
            return out
        time.sleep(2 + 3 * i)
    raise RuntimeError(f"tpc returned nothing after retries: tpc {' '.join(args)} ({o.stderr.strip()[:200]})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--iteration", type=int, help="same iteration number for every experiment")
    g.add_argument("--latest", action="store_true", help="latest COMPLETED iteration per experiment (default)")
    ap.add_argument("--label", help="folder name for this pull (default: ISO week, e.g. 2026-W41)")
    a = ap.parse_args()
    cfg = yaml.safe_load(open(a.config))
    scope = cfg["scope"]
    label = a.label or datetime.date.today().strftime("%G-W%V")
    base = os.path.join(cfg.get("workdir", "cao-tracker"), label)
    cache = os.path.join(cfg.get("workdir", "cao-tracker"), "_logcache")
    os.makedirs(base, exist_ok=True); os.makedirs(cache, exist_ok=True)

    runs = []
    for ex in cfg["experiments"]:
        info = tpc(["sim", "experiment", "get", ex["id"]], scope)
        info = info.get("experiment", info)
        its = sorted(info.get("iterations") or [], key=lambda x: x["iterationNumber"])
        if a.iteration:
            pick = [x for x in its if x["iterationNumber"] == a.iteration]
        else:
            # an iteration stuck in generating_results still has completed runs + logs; use it, but say so
            done = [x for x in its if x["status"] in ("completed", "generating_results")]
            pick = done[-1:] if done else []
            if pick and pick[0]["status"] != "completed":
                print(f"   note: {ex['prompt_type']} {ex['id'][:8]} iteration {pick[0]['iterationNumber']} is '{pick[0]['status']}' (platform summary not finished); runs are still usable")
        if not pick:
            print(f"!! {ex['prompt_type']} {ex['id'][:8]}: no matching completed iteration (have: "
                  f"{[(x['iterationNumber'], x['status']) for x in its]})")
            continue
        n = pick[0]["iterationNumber"]
        envs = {e["id"]: e for e in info.get("environments") or []}
        sig = tpc(["sim", "experiment", "signals", ex["id"], "--iteration", str(n)], scope)
        for r in sig.get("runs", []):
            env = envs.get(r["environmentId"], {})
            runs.append(dict(id=r["id"], experiment=ex["id"], prompt_type=ex["prompt_type"], mode=ex.get("mode", "research"),
                             iteration=n, task_id=r["taskId"], task=r["taskName"], env_id=r["environmentId"],
                             env=r.get("environmentName", ""), harness=(env.get("agentConfig") or {}).get("harness", ""),
                             model=(env.get("agentConfig") or {}).get("model", ""), status=r["status"],
                             signals={k: v.get("value") for k, v in ((r.get("signalValues") or {}).get("values") or {}).items()}))
        print(f"   {ex['prompt_type']:<13} {ex['id'][:8]} iteration {n}: {len(sig.get('runs', []))} runs")

    def detail(r):
        try:
            gget = tpc(["sim", "run", "get", r["id"]], scope)
            gget = gget.get("run", gget)
            r["status"] = gget.get("status", r["status"])
            r["cost"] = gget.get("costUsd")
            r["goals"] = {x.get("goalName"): x.get("score") for x in gget.get("goalResults") or []}
        except RuntimeError as e:
            r["goals"] = {}; r["detail_error"] = str(e)[:200]
        p = os.path.join(cache, r["id"] + ".log")
        if r["status"] == "completed" and (not os.path.exists(p) or os.path.getsize(p) < 200):
            try:
                open(p, "w").write(tpc(["sim", "run", "logs", r["id"]], scope, want_json=False))
            except RuntimeError as e:
                r["log_error"] = str(e)[:200]
        r["log"] = p if os.path.exists(p) else None
        return r

    with cf.ThreadPoolExecutor(6) as pool:
        runs = list(pool.map(detail, runs))
    json.dump(dict(label=label, pulled_at=datetime.datetime.now().isoformat(timespec="seconds"), runs=runs),
              open(os.path.join(base, "runs.json"), "w"), indent=1)
    ok = sum(1 for r in runs if r.get("log"))
    print(f"\n{len(runs)} runs, {ok} with logs, {sum(r['status'] != 'completed' for r in runs)} not completed → {base}/runs.json")


if __name__ == "__main__":
    main()
