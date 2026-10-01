#!/usr/bin/env python3
"""The send gate for the condensed report. Exits non-zero unless ALL CHECKS PASS.
  python3 check_report.py study.yaml build_report.py report/<file>.pdf
(1) every "quoted span" ≥25 chars inside each string literal of the builder is a contiguous substring of a
    mined/ transcript, or of a task prompt (labels) — verified from SOURCE, never from PDF text;
(2) every cited 8-hex run id resolves; (3) every fact in study.yaml `facts` appears in a transcript;
(4) layout: no table split, no footer-only page, no stranded heading; (5) lists every N/M in the PDF so you
    can compare against deepdive.txt — rerun after ANY parser change."""
import fitz, re, os, json, glob, unicodedata, ast, sys, math
from collections import Counter
from tpc_helpers import load_config

cfg = load_config(sys.argv[1]); builder = sys.argv[2]; pdf = sys.argv[3]
def norm(s):
    s = unicodedata.normalize("NFKC", s)
    for a, b in (("‘", "'"), ("’", "'"), ("“", '"'), ("”", '"'), ("—", "-"), ("–", "-"), ("…", "...")): s = s.replace(a, b)
    return re.sub(r"\s+", " ", re.sub(r"[*_`]+", "", s)).strip().lower()
files = {f: norm(open("mined/" + f).read()) for f in os.listdir("mined")}; corpus = " ".join(files.values())
prompts = [norm(json.load(open(f))["prompt"]) for f in glob.glob("tasks/*.json")]
bad = 0
texts = [n.value for n in ast.walk(ast.parse(open(builder).read())) if isinstance(n, ast.Constant) and isinstance(n.value, str) and len(n.value) > 25]
ok = skip = 0
for t in texts:
    for q in re.findall(r'"([^"\n]{25,})"', t):
        if not q[0].isalnum(): continue
        nq = norm(q)
        if any(nq in p for p in prompts): skip += 1
        elif any(nq in f for f in files.values()): ok += 1
        else: bad += 1; print("QUOTE FAIL:", q[:140])
print(f"(1) quotes: {ok} agent quotes verified, {skip} prompt fragments")
d = fitz.open(pdf); txt = re.sub(r"\s+", " ", " ".join(p.get_text("text") for p in d))
ids = set(re.findall(r"\b([0-9a-f]{8})\b", txt)); missing = [i for i in ids if not any(i in f for f in files)]
bad += len(missing); print(f"(2) run ids cited: {len(ids)}, missing: {missing or 'none'}")
facts = [f.lower() for f in cfg.get("facts", [])]; miss = [f for f in facts if f not in corpus]
bad += len(miss); print(f"(3) named facts present in transcripts: {len(facts)-len(miss)}/{len(facts)}" + (f"  MISSING: {miss}" if miss else ""))
fo = [i + 1 for i, p in enumerate(d) if sum(len(l["spans"]) for b in p.get_text("dict")["blocks"] if b.get("lines") and b["bbox"][3] < p.rect.height - 40 for l in b["lines"]) < 6]
hdr = Counter(); [hdr.update(re.findall(r"^LANE\b|BUILD CELL|EXACTLY WHERE|^ARM\b", p.get_text("text"), re.M)) for p in d]
split = [k for k, c in hdr.items() if c > 1]
stranded = []
for i, p in enumerate(d):
    ls = [l.strip() for l in p.get_text("text").splitlines() if l.strip() and not l.startswith("THE PROMPTING COMPANY") and not l.startswith("PAGE ")]
    if len(ls) >= 2 and re.match(r"^[A-F] · [A-Z ]+$|^FINDINGS · ", ls[-2]): stranded.append(i + 1)
bad += len(fo) + len(split) + len(stranded)
print(f"(4) pages: {len(d)}  footer-only: {fo or 'none'}  table split: {split or 'none'}  stranded heading: {stranded or 'none'}")
print("(5) ratios in PDF — compare each to deepdive.txt:", sorted(set(re.findall(r"\b(\d+)\s*(?:/|of)\s*(\d+)\b", txt)), key=lambda x: (int(x[1]), int(x[0]))))
n = len(d); cols = 4; rows_ = math.ceil(n / cols); Wd, Hd = 420, 545
sheet = fitz.open(); pg = sheet.new_page(width=cols * Wd, height=rows_ * Hd)
for i, p in enumerate(d): pg.show_pdf_page(fitz.Rect((i % cols) * Wd, (i // cols) * Hd, (i % cols + 1) * Wd, (i // cols + 1) * Hd), d, i)
pg.get_pixmap(dpi=110).save(os.path.splitext(pdf)[0] + "_contact.png"); print("contact sheet written — look at every page")
print("\nRESULT:", "ALL CHECKS PASS" if bad == 0 else f"{bad} PROBLEM(S) — do not send"); sys.exit(1 if bad else 0)
