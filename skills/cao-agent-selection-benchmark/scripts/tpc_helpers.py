#!/usr/bin/env python3
"""Shared helpers: config loading, tpc JSON with retry, whoami verification, lane keying."""
import json, re, subprocess, time, sys, pathlib

def load_config(path="study.yaml"):
    try:
        import yaml
    except ImportError:
        sys.exit("pip install pyyaml")
    return yaml.safe_load(open(path))

def tpc_json(args, retries=5):
    """tpc returns an empty body under load; retry with backoff and RAISE rather than return nothing.
    (An empty body once read as 'zero pending' and declared a study finished.)"""
    for i in range(retries):
        out = subprocess.run(["tpc", "--format", "json"] + list(args), capture_output=True, text=True).stdout
        m = re.search(r"[\[{].*", out, re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                pass
        time.sleep(2 + 3 * i)
    raise RuntimeError("tpc returned no JSON after retries: tpc " + " ".join(args))

def tpc_text(args):
    return subprocess.run(["tpc"] + list(args), capture_output=True, text=True).stdout

def verify_scope(cfg):
    """`tpc org switch` has silently no-op'd. Read whoami and compare to the config before creating anything."""
    who = tpc_text(["auth", "whoami"])
    org = re.search(r"Organization:\s*(.+)", who); prod = re.search(r"Product:\s*(.+)", who)
    ok = True
    if not org or cfg.get("org_display", cfg["org"]).lower().replace("-", " ") not in org.group(1).lower().replace("-", " "):
        print(f"SCOPE MISMATCH org: whoami says {org.group(1) if org else '?'} | config {cfg['org']}"); ok = False
    if not prod or prod.group(1).strip().lower() in ("none selected", ""):
        print("SCOPE MISMATCH product: none selected — run `tpc product switch <slug>`"); ok = False
    return ok

def lane_of(name, cfg):
    """Lane from the task-name prefix EM-<GROUP>…; longest matching group key wins."""
    m = re.match(rf"{cfg['prefix']}-([A-Z][A-Z0-9]*)", name)   # digits allowed: H2H, J1, L5
    if not m: return "?"
    key = m.group(1)
    for k in sorted(cfg["lanes"], key=len, reverse=True):
        if key.startswith(k): return cfg["lanes"][k]
    return key

def short(task_name, cfg):
    return re.sub(rf"^{cfg['prefix']}-", "", task_name.split(" — ")[0]).strip()

def resolve_link(url):
    """Dashboard link → (org_slug, product_slug). Accepts any page under app.promptingco.com/<org>/p/<product>/…
    so an operator can paste what they have open instead of guessing slugs."""
    m = re.search(r"app\.promptingco\.com/([^/]+)/p/([^/?#]+)", url)
    if not m:
        raise ValueError("not a dashboard link: expected app.promptingco.com/<org>/p/<product>/…")
    return m.group(1), m.group(2)

if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "resolve":
        org, prod = resolve_link(sys.argv[2])
        print(f"org: {org}\nproduct: {prod}\n\ntpc org switch {org} && tpc product switch {prod} && tpc auth whoami")
    else:
        print("usage: tpc_helpers.py resolve <dashboard-url>")
