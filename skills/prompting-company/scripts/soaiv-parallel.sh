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
# Concurrency limit (measured): the analytics backend returns
# "API error 500: Failed to fetch share of voice" once ~6 requests from one
# account run at once; 3 concurrent is reliable. So CONCURRENCY defaults to 3
# and should stay low (≤4). Failed calls are retried with backoff and, if still
# failing, recorded as `err` — never as a silent 0.
#
# Usage:
#   ORG=nvidia-com ./soaiv-parallel.sh
#   ORG=nvidia-com CONCURRENCY=4 OUT=/tmp/nv.tsv ./soaiv-parallel.sh
#   ORG=nvidia-com LIMIT=20 ./soaiv-parallel.sh        # first 20 products (smoke test)
#
# After the parallel pass, a sequential repair phase re-resolves any rows still
# flagged err/cit_err — one at a time, no contention, extra retries — so a
# single invocation self-heals to complete data (or reports what truly failed).
#
# Env:
#   ORG             required — organization slug
#   CONCURRENCY     parallel workers (default 3; keep ≤4 — backend 500s above that)
#   OUT             output TSV path (default /tmp/soaiv_<ORG>.tsv)
#   LIMIT           cap number of products (for testing)
#   RETRIES         retries per call on empty/timeout/500 (default 4)
#   REPAIR_RETRIES  retries per call in the sequential repair phase (default 8)
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

  # IMPORTANT: a successful call always prints a non-empty JSON array (a dark
  # product returns `[{...,"runs":0}]`; a product with no cited sources returns
  # `[]`). An API error (e.g. the backend's "500: Failed to fetch share of
  # voice" under concurrency) prints NOTHING to stdout. So empty stdout == real
  # failure — never record it as a zero. Retry with linear backoff, then mark
  # the row `err` so a degraded run can't masquerade as clean data.
  retries="${RETRIES:-4}"
  sov=""; n=0
  while :; do
    sov=$(TPC_CONFIG_PATH="$cfg" tpc analytics sov --last 30d --json 2>/dev/null)
    [ -n "$sov" ] && break
    n=$((n + 1)); [ "$n" -ge "$retries" ] && break
    sleep "$n"
  done
  if [ -z "$sov" ]; then                                # sov unrecoverable
    rm -f "$cfg"
    printf '%s\t\t\t\t\t\terr\n' "$slug" > "$RESDIR/$hash"
    exit 0
  fi

  # Skip the expensive citations aggregation when the product has no
  # conversations (runs==0) — citation rate is undefined there anyway. This is
  # the bulk of a big org (e.g. 121/183 dark products), so it dominates speed.
  runs=$(printf '%s' "$sov" | python3 -c "import sys,json
try:
    d = json.load(sys.stdin); print(int((d[0].get('runs',0) or 0)) if d else 0)
except Exception: print(0)")
  cit="[]"; cstatus="ok"
  if [ "${runs:-0}" -gt 0 ] 2>/dev/null; then
    cit=""; n=0
    while :; do                                         # retry empty (= timeout/500), the GTC case
      cit=$(TPC_CONFIG_PATH="$cfg" tpc analytics citations --last 30d --by category --json 2>/dev/null)
      [ -n "$cit" ] && break                            # "[]" is a valid "no citations" answer
      n=$((n + 1)); [ "$n" -ge "$retries" ] && break
      sleep "$n"
    done
    [ -z "$cit" ] && { cit="[]"; cstatus="cit_err"; }   # citations unresolved: runs known, self unknown
  fi
  rm -f "$cfg"

  SOV_JSON="$sov" CIT_JSON="$cit" SLUG="$slug" CSTATUS="$cstatus" python3 - >"$RESDIR/$hash" <<'PY'
import os, json
def parse(v):
    try: return json.loads(v) if v.strip() else []
    except Exception: return None
slug = os.environ['SLUG']
sov = parse(os.environ.get('SOV_JSON', ''))
cit = parse(os.environ.get('CIT_JSON', ''))
if sov is None:                                         # unparseable sov despite non-empty
    print('\t'.join([slug, '', '', '', '', '', 'err'])); raise SystemExit
s = sov[0] if sov else {}
runs = s.get('runs', 0) or 0
mentions = s.get('mentions', 0) or 0
sov_pct = s.get('sov', 0) or 0
status = os.environ.get('CSTATUS', 'ok')
self_m = ''
if status != 'cit_err':
    self_m = 0
    for r in (cit or []):
        if r.get('key') == 'self':
            self_m = r.get('mentions', 0) or 0
            break
rate = '' if (not runs or status == 'cit_err') else round(100.0 * self_m / runs, 2)
print('\t'.join([slug, str(sov_pct), str(mentions), str(runs), str(self_m), str(rate), status]))
PY
  exit 0
fi

# ---------------------------------------------------------------------------
# Orchestrator mode.
# ---------------------------------------------------------------------------
ORG="${ORG:-${1:-}}"
[ -n "$ORG" ] || { echo "ERROR: set ORG=<org-slug>"; exit 2; }
CONC="${CONCURRENCY:-3}"
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

# Sequential repair pass: re-resolve any rows the parallel pass flagged (err /
# cit_err) one at a time with extra patience. With no contention the transient
# 500s clear and the heavy aggregations (e.g. GTC) get a clean shot. Slugs may
# contain spaces, so collect newline-delimited and read with `while read`.
flagged="$WORKDIR/flagged"; : > "$flagged"
for fp in "$RESDIR"/*; do
  case "$(awk -F'\t' '{print $NF}' "$fp" 2>/dev/null)" in
    err|cit_err) awk -F'\t' 'NR==1{print $1}' "$fp" >> "$flagged" ;;
  esac
done
nflag=$(grep -c . "$flagged" 2>/dev/null || echo 0)
if [ "$nflag" -gt 0 ]; then
  echo "repairing $nflag flagged row(s) sequentially (retries=${REPAIR_RETRIES:-8})..."
  while IFS= read -r slug; do
    [ -n "$slug" ] && RETRIES="${REPAIR_RETRIES:-8}" bash "$0" --worker "$slug"
  done < "$flagged"
fi

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
    w = csv.writer(fh, delimiter='\t', lineterminator='\n')  # LF, not csv's default \r\n
    w.writerow(['slug', 'name', 'sov', 'mentions', 'runs', 'self_mentions', 'citation_rate_pct', 'status'])
    for r in rows:
        w.writerow([r[0], names.get(r[0], ''), r[1], r[2], r[3], r[4], r[5], r[6]])
def inum(x):
    try: return int(float(x))
    except: return 0
by = lambda st: [r for r in rows if r[6] == st]
ok = by('ok'); cit_err = by('cit_err'); err = by('err')
sov_ok = ok + cit_err                                   # rows with trustworthy sov/runs
active = [r for r in sov_ok if fnum(r[1]) > 0]
tot_runs = sum(inum(r[3]) for r in ok)                  # rate uses only fully-ok rows
tot_self = sum(inum(r[4]) for r in ok)
print('--- rollup ---')
print('products: %d  (sov ok: %d, with SOV>0: %d, citations-unresolved: %d, sov-errors: %d)'
      % (len(rows), len(sov_ok), len(active), len(cit_err), len(err)))
if tot_runs:
    print('ORG CITATION RATE = %.2f%%  (%d self-cite convos / %d runs)'
          % (100.0 * tot_self / tot_runs, tot_self, tot_runs))
if err or cit_err:
    print('WARNING: %d sov-error + %d citations-unresolved row(s) excluded from the rate:'
          % (len(err), len(cit_err)))
    for r in (err + cit_err)[:25]:
        print('  ! %s [%s]' % (names.get(r[0], r[0]), r[6]))
PY

echo "done in ${SECONDS}s"
