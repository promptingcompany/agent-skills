#!/usr/bin/env bash
#
# soaiv-parallel.sh — org-wide SOAIV / Share-of-Voice + citation-rate rollup,
# parallelized. CLI-first (uses the `tpc` CLI only).
#
# Why this exists: `tpc analytics sov|citations` are scoped to ONE active
# product, stored in a single shared config (~/.tpc/config.json). Running them
# in a sequential loop over a large org (e.g. nvidia-com, 183 products) is slow
# because each product needs 3 round-trips and the `citations --by category`
# call is a cold backend aggregation (5–25s, occasionally a multi-minute
# timeout for the largest products).
#
# How it parallelizes safely: each worker gets its OWN config copy via
# TPC_CONFIG_PATH and switches THAT copy to its product, so N workers never
# clobber each other's active-product. The user's real config is never touched.
#
# Citation rate = unique conversations citing the org's own sources / all unique
# conversations = (self-category `mentions`) / (sov `runs`).
#
# Usage:
#   ORG=nvidia-com ./soaiv-parallel.sh
#   ORG=nvidia-com CONCURRENCY=12 OUT=/tmp/nv.tsv ./soaiv-parallel.sh
#   ORG=nvidia-com LIMIT=20 ./soaiv-parallel.sh        # first 20 products (smoke test)
#
# Env:
#   ORG          required — organization slug
#   CONCURRENCY  parallel workers (default 8). Keep modest to avoid backend load.
#   OUT          output TSV path (default /tmp/soaiv_<ORG>.tsv)
#   LIMIT        cap number of products (for testing)
#   RETRIES      citations retries on empty/timeout (default 3)
set -uo pipefail

# ---------------------------------------------------------------------------
# Worker mode: process ONE product in an isolated config, emit one TSV row.
# ---------------------------------------------------------------------------
if [ "${1:-}" = "--worker" ]; then
  slug="$2"
  hash=$(printf '%s' "$slug" | shasum | cut -c1-16)
  cfg="$WORKDIR/cfg_$hash.$EXT"
  cp "$LISTER" "$cfg"                                   # already org-switched
  TPC_CONFIG_PATH="$cfg" tpc product switch "$slug" >/dev/null 2>&1

  sov=$(TPC_CONFIG_PATH="$cfg" tpc analytics sov --last 30d --json 2>/dev/null)

  # Skip the expensive citations aggregation when the product has no
  # conversations (runs==0) — citation rate is undefined there anyway. This is
  # the bulk of a big org (e.g. 121/183 dark products), so it dominates speed.
  runs=$(printf '%s' "$sov" | python3 -c "import sys,json
try:
    d = json.load(sys.stdin); print(int((d[0].get('runs',0) or 0)) if d else 0)
except Exception: print(0)")
  cit="[]"
  if [ "${runs:-0}" -gt 0 ] 2>/dev/null; then
    n=0
    while [ "$n" -lt "${RETRIES:-3}" ]; do             # retry empty result (the GTC timeout case)
      cit=$(TPC_CONFIG_PATH="$cfg" tpc analytics citations --last 30d --by category --json 2>/dev/null)
      [ -n "$cit" ] && [ "$cit" != "[]" ] && break
      n=$((n+1))
    done
  fi
  rm -f "$cfg"

  SOV_JSON="$sov" CIT_JSON="$cit" SLUG="$slug" python3 - >"$RESDIR/$hash" <<'PY'
import os, json
def parse(v):
    try: return json.loads(v) if v.strip() else []
    except Exception: return None
slug = os.environ['SLUG']
sov = parse(os.environ.get('SOV_JSON', ''))
cit = parse(os.environ.get('CIT_JSON', ''))
if sov is None or cit is None:                          # hard parse error
    print('\t'.join([slug, '', '', '', '', '', 'err'])); raise SystemExit
s = sov[0] if sov else {}
runs = s.get('runs', 0) or 0
mentions = s.get('mentions', 0) or 0
sov_pct = s.get('sov', 0) or 0
self_m = 0
for r in (cit or []):
    if r.get('key') == 'self':
        self_m = r.get('mentions', 0) or 0
        break
rate = '' if not runs else round(100.0 * self_m / runs, 2)
print('\t'.join([slug, str(sov_pct), str(mentions), str(runs), str(self_m), str(rate), 'ok']))
PY
  exit 0
fi

# ---------------------------------------------------------------------------
# Orchestrator mode.
# ---------------------------------------------------------------------------
ORG="${ORG:-${1:-}}"
[ -n "$ORG" ] || { echo "ERROR: set ORG=<org-slug>"; exit 2; }
CONC="${CONCURRENCY:-8}"
OUT="${OUT:-/tmp/soaiv_${ORG}.tsv}"
SECONDS=0

# Resolve the base config and its format (json vs toml), without mutating it.
if [ -n "${TPC_CONFIG_PATH:-}" ]; then BASE_CFG="$TPC_CONFIG_PATH"
elif [ -f "$HOME/.tpc/config.toml" ]; then BASE_CFG="$HOME/.tpc/config.toml"
else BASE_CFG="$HOME/.tpc/config.json"; fi
EXT="${BASE_CFG##*.}"

WORKDIR="$(mktemp -d)"
RESDIR="$WORKDIR/res"; mkdir -p "$RESDIR"
LISTER="$WORKDIR/lister.$EXT"
cp "$BASE_CFG" "$LISTER"
export WORKDIR RESDIR LISTER EXT RETRIES="${RETRIES:-3}"
trap 'rm -rf "$WORKDIR"' EXIT

# Switch the throwaway lister config (not the user's) to the target org and
# enumerate products as NUL-delimited slugs (handles slugs containing spaces).
TPC_CONFIG_PATH="$LISTER" tpc org switch "$ORG" >/dev/null 2>&1
TPC_CONFIG_PATH="$LISTER" tpc --format json product list 2>/dev/null \
  > "$WORKDIR/products.json"
LIMIT="${LIMIT:-0}" python3 - <<'PY' > "$WORKDIR/slugs0"
import os, json, sys
data = json.load(open(os.environ['WORKDIR'] + '/products.json'))
lim = int(os.environ.get('LIMIT', '0') or 0)
if lim > 0: data = data[:lim]
# Trailing NUL after every slug so `read -d ''` processes the final one too.
sys.stdout.write(''.join(p['slug'] + '\0' for p in data))
PY
TOTAL=$(python3 -c "s=open('$WORKDIR/slugs0','rb').read(); print(s.count(b'\0'))")
echo "org=$ORG  products=$TOTAL  concurrency=$CONC  out=$OUT"

# Concurrency-capped worker pool via a FIFO semaphore (portable to bash 3.2;
# true streaming pool — a slow product occupies one slot, others keep flowing).
sem="$WORKDIR/sem"; mkfifo "$sem"
exec 9<>"$sem"; rm -f "$sem"
for _ in $(seq 1 "$CONC"); do printf '\n' >&9; done
done_count=0
while IFS= read -r -d '' slug; do
  read -r -u 9 _                                        # take a token (blocks at cap)
  { bash "$0" --worker "$slug"; printf '\n' >&9; } &    # return token when worker exits
done < "$WORKDIR/slugs0"
wait

# Assemble: join worker rows with product names, sort by SOV desc, roll up.
OUT="$OUT" python3 - <<'PY'
import os, json, glob, csv
work = os.environ['WORKDIR']; resdir = os.environ['RESDIR']; out = os.environ['OUT']
names = {p['slug']: p.get('name', '') for p in json.load(open(work + '/products.json'))}
rows = []
for fp in glob.glob(resdir + '/*'):
    line = open(fp).read().rstrip('\n')
    if not line: continue
    f = line.split('\t')                                # slug,sov,ment,runs,self,rate,status
    rows.append(f)
def fnum(x):
    try: return float(x)
    except: return 0.0
rows.sort(key=lambda r: fnum(r[1]), reverse=True)
with open(out, 'w', newline='') as fh:
    w = csv.writer(fh, delimiter='\t')
    w.writerow(['slug', 'name', 'sov', 'mentions', 'runs', 'self_mentions', 'citation_rate_pct', 'status'])
    for r in rows:
        w.writerow([r[0], names.get(r[0], ''), r[1], r[2], r[3], r[4], r[5], r[6]])
ok = [r for r in rows if r[6] == 'ok']
def inum(x):
    try: return int(float(x))
    except: return 0
tot_runs = sum(inum(r[3]) for r in ok)
tot_self = sum(inum(r[4]) for r in ok)
active = [r for r in ok if fnum(r[1]) > 0]
print('--- rollup ---')
print('products: %d  (ok %d, with SOV>0: %d, errors: %d)'
      % (len(rows), len(ok), len(active), len(rows) - len(ok)))
if tot_runs:
    print('ORG CITATION RATE = %.2f%%  (%d self-cite convos / %d runs)'
          % (100.0 * tot_self / tot_runs, tot_self, tot_runs))
PY

echo "done in ${SECONDS}s"
