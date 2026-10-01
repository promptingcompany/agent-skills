#!/usr/bin/env python3
"""Write the weekly markdown report from metrics.json, with deltas vs last run and vs baseline.

Usage:  python3 report.py tracker.yaml <label> [--no-history]
Writes: <workdir>/<label>/report.md and appends <workdir>/history.json"""
import json, os, sys, re, datetime
import yaml

TYPES = ["build", "tool-seeking", "head-to-head", "usability"]
NAMES = {"build": "Build: Exa is the main search path", "tool-seeking": "Tool-seeking: Exa recommended first",
         "head-to-head": "Head-to-head: Exa wins", "usability": "Usability: the Exa build works"}


def pct(x): return "—" if x is None else f"{round(100 * x)}%"


def cell(d): return f"{d['k']}/{d['n']} ({pct(d['rate'])})" if d and d.get("n") else "—"


def delta(now, prev, thr):
    if now is None or prev is None: return ""
    d = round(100 * (now - prev))
    flag = " ⚑" if abs(d) >= thr else ""
    return f"{'+' if d > 0 else ''}{d} pts{flag}"


def main():
    cfg = yaml.safe_load(open(sys.argv[1])); label = sys.argv[2]
    wd = cfg.get("workdir", "cao-tracker"); base = os.path.join(wd, label)
    M = json.load(open(os.path.join(base, "metrics.json")))
    F = [f for f in json.load(open(os.path.join(base, "facts.json"))) if "excluded" not in f]
    Q = json.load(open(os.path.join(base, "review_queue.json")))
    hist_path = os.path.join(wd, "history.json")
    H = json.load(open(hist_path)) if os.path.exists(hist_path) else []
    prev = next((h for h in reversed(H) if h["label"] != label), None)
    basel = next((h for h in H if h["label"] == cfg.get("baseline_label")), None)
    thr = cfg.get("real_move_points", 15)
    tgt = cfg["target"].get("label", "Target")
    an = "an" if tgt[:1].lower() in "aeiou" else "a"
    bt = M["by_type"]

    pub_runs = sum(1 for f in F if any(p["cited"] for p in f["published"]))
    pub_open = sum(1 for f in F if any(p["opened"] for p in f["published"]))
    snap = dict(label=label, date=datetime.date.today().isoformat(),
                published_cited=pub_runs, published_opened=pub_open, runs=len(F),
                rates={pt: bt[pt]["pooled"]["rate"] for pt in bt},
                by_agent={pt: {a: v["rate"] for a, v in bt[pt]["by_agent"].items()} for pt in bt},
                build_reach=bt.get("build", {}).get("reach", {}).get("rate"), build_conversion=bt.get("build", {}).get("conversion", {}).get("rate"))

    L = []
    w = L.append
    w(f"# {tgt} × coding agents: weekly tracker, {label}")
    w(f"*{snap['date']} · {len(F)} runs analysed · mode: {', '.join(sorted({f['mode'] for f in F}))} · "
      f"agents: {', '.join(sorted({f['agent'] for f in F}))}*\n")
    if Q:
        w(f"> **Provisional:** {len(Q)} runs still need review (`review_queue.json`). Settle them before sharing any number.\n")

    w("## 1. Headline")
    w("| Metric | This run | vs last run | vs baseline |")
    w("|---|---|---|---|")
    d_prev = f"{pub_runs - prev.get('published_cited', 0):+d} runs" if prev else ""
    d_base = f"{pub_runs - basel.get('published_cited', 0):+d} runs" if basel else ""
    if cfg.get("published_pages"):
        w(f"| **Runs citing a page we published** | {pub_runs}/{len(F)} (opened: {pub_open}) | {d_prev} | {d_base} |")
    else:
        w("| **Runs citing a page we published** | no pages listed in `published_pages` yet | | |")
    for pt in ["head-to-head", "build"]:
        if pt in bt:
            r = bt[pt]["pooled"]
            w(f"| **{NAMES[pt]}** | {cell(r)}, 95% range {pct(r['ci'][0])}–{pct(r['ci'][1])} | "
              f"{delta(r['rate'], prev and prev['rates'].get(pt), thr)} | {delta(r['rate'], basel and basel['rates'].get(pt), thr)} |")
    if "build" in bt:
        b = bt["build"]
        w(f"\nBuild rate = reach × conversion: **reach** (agent opened {an} {tgt} page) {cell(b['reach'])} × **conversion** "
          f"(then built with {tgt}) {cell(b['conversion'])}. Builds that never opened {an} {tgt} page: {cell(b['no_target_page_success'])} built with {tgt}.")
    w(f"\n⚑ = a move of {thr}+ points. Smaller moves are within noise at this sample size; read them as a trend.\n")

    w("## 2. Results by prompt type and agent")
    agents = sorted({f["agent"] for f in F})
    w("| Prompt type | Pooled | " + " | ".join(agents) + " | Outcomes |")
    w("|---|---|" + "---|" * len(agents) + "---|")
    for pt in TYPES:
        if pt in bt:
            d = bt[pt]
            w(f"| {NAMES[pt]} | {cell(d['pooled'])} | " + " | ".join(cell(d["by_agent"].get(a)) for a in agents) +
              f" | {', '.join(f'{k} {v}' for k, v in d['outcomes'].items())} |")
    w("\nPer use case (small samples, for diagnosis only, never report these):")
    for pt in TYPES:
        if pt in bt:
            w(f"- **{pt}:** " + ", ".join(f"{u} {v}" for u, v in bt[pt]["by_use_case"].items()))

    w("\n## 3. Agent behavior")
    w("| Prompt type · agent | Searched | Query mix | Neutral searches with " + tgt + " in top 10 | " + tgt + "-name searches with " + tgt + " first | Pages typed from memory |")
    w("|---|---|---|---|---|---|")
    for k, v in M["behavior"].items():
        tq = sum(v["queries"].values()) or 1
        mix = ", ".join(f"{q} {round(100 * c / tq)}%" for q, c in sorted(v["queries"].items(), key=lambda x: -x[1]))
        w(f"| {k} | {v['searched']}/{v['runs']} | {mix or '—'} | {v['neutral_visible']}/{v['neutral']} | {v['own_name_first']}/{v['own_name']} | "
          f"{v['typed_from_memory']}/{v['opens']} |")
    asks = {}
    for k, v in M["behavior"].items():
        for a, c in v["fetch_asks"].items(): asks[a] = asks.get(a, 0) + c
    if asks:
        w("\nWhat agents asked for when they opened a page (Claude Code states this; Codex doesn't): " +
          ", ".join(f"{a} {c}" for a, c in sorted(asks.items(), key=lambda x: -x[1])))

    w("\n## 4. Pages that decided outcomes")
    w(f"Runs that opened each kind of page, split by whether {tgt} won (build main path, recommended first, or won the head-to-head).\n")
    w("| Page type | Won | Lost |"); w("|---|---|---|")
    for k, v in list(M["pages"]["by_category"].items())[:18]:
        w(f"| {k} | {v['won']} | {v['lost']} |")
    rival_doms = tuple(d for k, vv in cfg.get("rivals", {}).items() for d in vv.get("domains", []))
    tgt_doms = tuple(cfg["target"].get("domains", []))
    def dom_of(k): return k.split("/")[0]
    def is_rival_own(k): return dom_of(k).endswith(rival_doms) and not re.search(r"/(compare|vs|versus|alternatives?)/|-vs-|/articles/|/blog/.*(best|compar|vs|alternativ)", k)
    swing = [(k, v) for k, v in M["pages"]["by_page"].items() if v["won"] + v["lost"] >= cfg.get("min_page_runs", 3)]
    swing.sort(key=lambda x: -abs(x[1]["won"] - x[1]["lost"]))
    deciding = [(k, v) for k, v in swing if not is_rival_own(k)]
    rival_own = [(k, v) for k, v in swing if is_rival_own(k)]
    if deciding:
        w(f"\n**Pages that can sway the choice** ({tgt} pages, comparisons, benchmarks, model docs; opened in {cfg.get('min_page_runs', 3)}+ runs), biggest swing first:\n")
        w("| Page | Won | Lost |"); w("|---|---|---|")
        for k, v in deciding[:15]:
            w(f"| `{k[:90]}` | {v['won']} | {v['lost']} |")
    if rival_own:
        w(f"\n**Rivals' own docs and pricing.** Agents often open these *after* choosing that rival, to build with it, so treat them as a symptom, not a cause: " +
          ", ".join(f"`{k[:60]}` {v['won']}/{v['lost']}" for k, v in rival_own[:8]) + " (won/lost)")
    if M["errors"]["target_pages_erroring"]:
        w(f"\n**{tgt} pages that returned errors to agents:** " + ", ".join(f"`{u}` ×{c}" for u, c in M["errors"]["target_pages_erroring"].items()))

    w("\n## 5. Citations, published pages and planted facts")
    c = M["citations"]
    w(f"- **Runs whose answer or written files cite at least one URL:** {c['runs_citing_anything']}/{len(F)}")
    w("- **Cited, by page type:** " + ", ".join(f"{k} {v}" for k, v in list(c["by_category"].items())[:12]))
    w("- **Most-cited URLs:** " + ", ".join(f"`{k[:70]}` {v}" for k, v in list(c["top_urls"].items())[:10]))
    if M["published"]:
        w("\n| Page we published | Seen in results | Opened | Cited |"); w("|---|---|---|---|")
        for k, v in M["published"].items():
            w(f"| {k} | {v['seen']} | {v['opened']} | {v['cited']} |")
    if M["planted"]:
        w("\n| Planted fact | In answers (reach) | Runs that opened its page | Of those, repeated it (conversion) |"); w("|---|---|---|---|")
        for k, v in M["planted"].items():
            w(f"| {k} | {v['reach']}/{v['runs']} | {v['opened_page']} | {v['conversion']}/{v['opened_page']} |")
    if M["negative"]:
        w("\n**Negative claims repeated in answers:** " + ", ".join(f"{k} {v}" for k, v in M["negative"].items()))
    w(f"\n**{tgt} subdomain pages we own:** opened {M['own_subdomain']['opened']}, cited {M['own_subdomain']['cited']}.")
    if M.get("own_name_outranked_by"):
        w(f"\n**Pages that came first when agents searched {tgt} by name:** " + ", ".join(f"`{k}` {v}" for k, v in M["own_name_outranked_by"].items()))

    if M["won_instead"].get("build"):
        w("\n## 6. What won instead (builds where " + tgt + " wasn't the main path)")
        for k, v in sorted(M["won_instead"]["build"].items(), key=lambda x: -x[1]):
            w(f"- {k}: {v}")

    w("\n## 7. Action-item candidates (generated by rules; confirm with evidence before sending)")
    acts = []
    ignore = tuple(cfg.get("ignore_domains_for_actions", ["pypi.org", "npmjs.com", "github.com"]))
    for k, v in deciding[:15]:
        if v["lost"] >= 3 and v["lost"] >= 2 * v["won"] and not dom_of(k).endswith(tgt_doms) and not dom_of(k).endswith(ignore):
            acts.append(f"**Answer `{k[:80]}`**: opened in {v['won'] + v['lost']} runs, {tgt} lost {v['lost']}. Read what it claims and answer it on the {tgt} page agents open for that job.")
    for k, v in [x for x in deciding if dom_of(x[0]).endswith(tgt_doms)][:3]:
        if v["won"] >= 3 and v["won"] >= 2 * v["lost"]:
            acts.append(f"**Keep `{k[:80]}` strong**: opened in {v['won'] + v['lost']} runs, {tgt} won {v['won']}. It's doing its job; get it opened more (link to it from pricing and versus pages).")
    nv = sum(v["neutral_visible"] for v in M["behavior"].values()); nn = sum(v["neutral"] for v in M["behavior"].values())
    if nn >= 5 and nv / nn < 0.1:
        acts.append(f"**Neutral searches:** {tgt} is in the top 10 for only {nv}/{nn}. That's slow ranking work (a 2026 ranking, per-job pages, a benchmark), so don't target it short term.")
    of = sum(v["own_name_first"] for v in M["behavior"].values()); on = sum(v["own_name"] for v in M["behavior"].values())
    if on >= 5 and of / on < 0.6:
        top = ", ".join(list(M.get("own_name_outranked_by", {}))[:4])
        acts.append(f"**Own-name ranking:** {an} {tgt} page came first for only {of}/{on} searches naming {tgt}. Outranked by: {top}.")
    wi = M["won_instead"].get("build", {})
    nat = sum(v for k, v in wi.items() if "native" in k)
    if nat >= 2:
        acts.append(f"**The model's own search won {nat} builds.** Add a short 'when {tgt} beats the built-in search' section on the docs page agents already open.")
    if "build" in bt and bt["build"]["reach"]["rate"] is not None and bt["build"]["reach"]["rate"] < 0.7:
        acts.append(f"**Build reach is {pct(bt['build']['reach']['rate'])}.** Builds that never open a {tgt} page almost never use {tgt}, so getting agents onto the docs is the first gate.")
    for k, v in M["published"].items():
        if v["seen"] + v["opened"] == 0:
            acts.append(f"**Published page '{k}' was never seen or opened.** Link it from pages agents already open (pricing, docs, versus pages).")
    for k, v in M["negative"].items():
        if v >= 2:
            acts.append(f"**Negative claim '{k}' appeared in {v} answers.** Find the source page (`facts.json`: runs with negative_claims set, then their opens), and correct it on {tgt}'s pages or with the publisher.")
    for u, n in M["errors"]["target_pages_erroring"].items():
        acts.append(f"**Fix `{u}`**: it returned an error to agents {n}×.")
    w("\n".join(f"{i + 1}. {a}" for i, a in enumerate(acts)) if acts else "_No rule fired this run._")

    w("\n## 8. Caveats")
    w(f"- Research mode: every prompt carries the research sentence. Label it as research mode wherever these numbers go, never as unprompted behaviour.")
    w(f"- Sample: {len(F)} runs. Pooled rates by prompt type are the reportable unit; per-use-case numbers are noise.")
    w("- Codex opens several pages in one step, so its page-to-outcome attribution is approximate.")
    w("- These are associations. Cause and effect comes from before/after around a dated page change, plus planted facts.")
    if Q:
        w(f"- {len(Q)} runs are unreviewed, so the outcomes above are provisional.")

    open(os.path.join(base, "report.md"), "w").write("\n".join(L) + "\n")
    if "--no-history" not in sys.argv and not Q:
        H = [h for h in H if h["label"] != label] + [snap]
        json.dump(H, open(hist_path, "w"), indent=1)
        print("history updated")
    elif Q:
        print("history NOT updated: review queue not empty")
    print(f"report → {base}/report.md")


if __name__ == "__main__":
    main()
