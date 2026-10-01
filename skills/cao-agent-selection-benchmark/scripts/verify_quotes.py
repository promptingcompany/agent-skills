#!/usr/bin/env python3
"""Contiguous-match verification of sweep quotes against mined/. A quote that fails is a lead, not evidence.
  python3 verify_quotes.py sweep_build.md sweep_twin.md sweep_advice.md
Parses blocks 'FILE: <name>.txt' followed by lines with "quoted" spans; stops at ## PATTERNS / ## BELIEF AUDIT
(subagent summaries are paraphrase by design)."""
import json, re, sys, os, unicodedata

def norm(s):
    s = unicodedata.normalize("NFKC", s)
    for a, b in (("‘", "'"), ("’", "'"), ("“", '"'), ("”", '"'), ("—", "-"), ("–", "-"), ("…", "...")): s = s.replace(a, b)
    return re.sub(r"\s+", " ", re.sub(r"[*_`]+", "", s)).strip().lower()

FILES = {f: norm(open("mined/" + f).read()) for f in os.listdir("mined")}
ledger, ok, bad = [], 0, 0
for path in sys.argv[1:]:
    cur = None
    for line in open(path):
        if re.match(r"\s*##\s*(PATTERNS|BELIEF AUDIT)", line): break
        m = re.match(r"\s*FILE:\s*(\S+\.txt)", line)
        if m: cur = m.group(1).strip("`* "); continue
        if not cur: continue
        for q in re.findall(r'"([^"]{12,})"', line):
            if q.strip().lower() in ("none", "n/a", "no stated reason"): continue
            hit = cur in FILES and norm(q) in FILES[cur]
            ledger.append({"source": path, "file": cur, "quote": q, "verified": hit}); ok += hit; bad += (not hit)
json.dump(ledger, open("quotes_verified.json", "w"), indent=1)
print(f"quotes checked: {ok+bad}   VERIFIED: {ok}   FAILED: {bad}")
for r in ledger:
    if not r["verified"]: print(f"  FAIL  {r['file'][:55]}  \"{r['quote'][:90]}…\"")
