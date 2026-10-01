#!/usr/bin/env python3
"""Turn a pull (runs.json + logs) into per-run facts, metrics, and a review queue.

Usage:  python3 analyze.py tracker.yaml <label>
Reads:  <workdir>/<label>/runs.json, <workdir>/<label>/reviews.json (optional manual/agent verdicts)
Writes: <workdir>/<label>/facts.json, metrics.json, review_queue.json

Outcome per prompt type (success = what we report):
  build         main / shared (needs review) / absent        success = main
  tool-seeking  top / listed / absent                         success = top
  head-to-head  win / split / loss                            success = win
  usability     pass / fail                                   success = pass
Heuristics + the platform grader decide first; anything ambiguous goes to review_queue.json and is
settled by reading the run (see workflows/review.md). reviews.json always wins."""
import json, os, re, sys, math
from collections import Counter, defaultdict
import yaml
from logparse import parse, urls_in, domain

SUCCESS = {"build": "main", "tool-seeking": "top", "head-to-head": "win", "usability": "pass"}


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0, c - h), min(1, c + h))


class Cfg:
    def __init__(self, path):
        c = yaml.safe_load(open(path)); self.raw = c
        self.target = c["target"]
        self.vendors = {"target": c["target"], **c.get("rivals", {})}
        self.name_re = {k: re.compile(v["name_regex"], re.I) for k, v in self.vendors.items() if v.get("name_regex")}
        self.code_re = {k: re.compile(v["code_markers"], re.I) for k, v in self.vendors.items() if v.get("code_markers")}
        self.dom = {k: [d.lower() for d in v.get("domains", [])] for k, v in self.vendors.items()}
        self.label = {k: v.get("label", k) for k, v in self.vendors.items()}
        self.agents = c["agents"]; self.use_cases = c.get("use_cases", [])
        self.goals = c.get("grader_goals", {})
        self.published = c.get("published_pages", []) or []
        self.facts = c.get("planted_facts", []) or []
        self.negs = c.get("negative_claims", []) or []
        self.own_sub = re.compile(c.get("own_subdomains_regex", r"$^"), re.I)
        self.model_docs = {k: re.compile(v, re.I) for k, v in (c.get("model_docs") or {}).items()}

    def agent(self, r):
        blob = f"{r.get('harness','')} {r.get('env','')} {r.get('model','')}"
        for a in self.agents:
            if re.search(a["match"], blob, re.I):
                return a["name"]
        return "?"

    def use_case(self, task, prompt):
        for u in self.use_cases:
            if re.search(u["match"], task, re.I) or re.search(u["match"], prompt[:1500], re.I):
                return u["key"]
        return "?"

    def vendor_of_url(self, u):
        d = domain(u)
        for k, ds in self.dom.items():
            if any(d == x or d.endswith("." + x) for x in ds):
                return k
        return None

    def page_cat(self, u):
        ul = u.lower(); v = self.vendor_of_url(u)
        if v == "target":
            if self.own_sub.search(ul): return "target: own subdomain pages"
            for lab, pat in (self.target.get("page_types") or {}).items():
                if re.search(pat, ul): return f"target: {lab}"
            return "target: other"
        if v:
            kind = "comparison" if re.search(r"/(compare|vs|versus|alternatives?)/|-vs-|/articles/|/blog/.*(best|compar|vs|alternativ)", ul) else "own"
            return f"rival: {self.label[v]} ({kind})"
        for lab, rx in self.model_docs.items():
            if rx.search(ul): return f"model docs: {lab}"
        return f"third-party: {domain(u)}"

    def qkind(self, q):
        ql = q.lower()
        if "site:" in ql or ql.startswith("site."): return "inside a vendor site"
        if re.search(r"\bvs\.?\b|versus|compar|alternativ", ql): return "named comparison"
        named = [k for k, rx in self.name_re.items() if rx.search(q)]
        if named: return "vendor by name"
        return "neutral category"


REC = re.compile(r"(?:my recommendation(?: is)?|i(?:'|’)?d (?:use|pick|go with|choose|build (?:it )?on)|i would (?:use|pick|go with|choose)|"
                 r"i recommend|recommendation:|use \*\*|go with|pick)[:\s]*(.{0,160})", re.I)


def recommended(cfg, final):
    """First vendor named inside the first recommendation phrase of the answer (first ~1,200 chars)."""
    for m in REC.finditer(final[:1200]):
        seg = m.group(1)
        pos = sorted((mm.start(), k) for k, rx in cfg.name_re.items() for mm in [rx.search(seg)] if mm)
        if pos:
            return pos[0][1]
    return None


def classify(cfg, pt, P, goals, wired):
    """Return (outcome, reason, needs_review)."""
    final = P["final"]
    if pt == "build":
        others = [v for v in wired if v != "target"]
        if "target" in wired and not others: return "main", "only target wired", False
        if "target" in wired: return "shared", "target wired with " + ",".join(others), True
        return "absent", "target not wired", False
    if pt == "usability":
        g = goals.get(cfg.goals.get("usability", ""), None)
        if g is None: return "fail" if not wired else ("pass" if "target" in wired else "fail"), "no grader; wiring only", True
        return ("pass" if g >= 50 and "target" in wired else "fail"), f"grader {g}", g >= 50 and "target" not in wired
    # advice: grader first, then check against first vendor named in the answer
    pos = sorted((m.start(), k) for k, rx in cfg.name_re.items() for m in [rx.search(final)] if m)
    first = pos[0][1] if pos else None
    mentioned = "target" in [k for _, k in pos]
    pick = recommended(cfg, final)          # vendor named in the answer's own recommendation sentence
    g = goals.get(cfg.goals.get(pt, ""), None)
    if pt == "tool-seeking":
        if g is None:
            out = "top" if first == "target" else ("listed" if mentioned else "absent")
            return out, "no grader; first-named heuristic", True
        out = "top" if g >= 100 else ("listed" if g >= 50 else "absent")
        disagree = (pick is not None and (out == "top") != (pick == "target")) or (out == "absent" and mentioned)
        return out, f"grader {g}; recommends {pick or '?'}; first named {first}", disagree or not final
    if pt == "head-to-head":
        if g is None: return "split", "no grader", True
        out = "win" if g >= 100 else ("split" if g >= 50 else "loss")
        disagree = (out == "win" and not mentioned) or (pick is not None and (out == "win") != (pick == "target"))
        return out, f"grader {g}; recommends {pick or '?'}; first named {first}", disagree or not final
    return "?", "unknown prompt type", True


def main():
    cfg = Cfg(sys.argv[1]); label = sys.argv[2]
    base = os.path.join(cfg.raw.get("workdir", "cao-tracker"), label)
    pull = json.load(open(os.path.join(base, "runs.json")))
    rv_path = os.path.join(base, "reviews.json")
    reviews = json.load(open(rv_path)) if os.path.exists(rv_path) else {}
    facts, queue = [], []
    for r in pull["runs"]:
        if r["status"] != "completed" or not r.get("log"):
            facts.append(dict(id=r["id"], prompt_type=r["prompt_type"], status=r["status"], excluded="not completed / no log")); continue
        s = open(r["log"], errors="ignore").read()
        P = parse(s)
        if not P["final"] and not P["code"]:
            facts.append(dict(id=r["id"], prompt_type=r["prompt_type"], status="empty", excluded="empty run (0-byte/blank log)")); continue
        pt = r["prompt_type"]; agent = cfg.agent(r)
        wired = sorted(k for k, rx in cfg.code_re.items() if rx.search(P["code"]))
        out, why, rev = classify(cfg, pt, P, r.get("goals") or {}, wired)
        if r["id"] in reviews:
            out, why, rev = reviews[r["id"]], "reviewed", False
        queries = [q for x in P["searches"] for q in x["queries"]]
        qk = Counter(cfg.qkind(q) for q in queries)
        # neutral-search visibility: target domain in the top 10 of a neutral search
        neutral = [x for x in P["searches"] if x["queries"] and all(cfg.qkind(q) == "neutral category" for q in x["queries"]) and x["results"]]
        neutral_vis = sum(1 for x in neutral if any(cfg.vendor_of_url(u) == "target" for _, u in x["results"][:10]))
        # own-name searches: name only the target; did a target page come back first?
        own = [x for x in P["searches"] if x["queries"] and x["results"] and all(
            cfg.name_re["target"].search(q) and not any(rx.search(q) for k, rx in cfg.name_re.items() if k != "target") for q in x["queries"])]
        own_first = sum(1 for x in own if cfg.vendor_of_url(x["results"][0][1]) == "target")
        own_outranked_by = [domain(x["results"][0][1]) for x in own if cfg.vendor_of_url(x["results"][0][1]) != "target"]
        opens = [dict(url=o["url"], cat=cfg.page_cat(o["url"]), via_search=o["via_search"], prompt=o["prompt"][:300]) for o in P["opens"]]
        cited = urls_in(P["final"])
        written_urls = urls_in(P["code"])
        text_all = P["final"] + "\n" + P["code"]
        pub = []
        for pg in cfg.published:
            rx = re.compile(pg["url_regex"], re.I)
            pub.append(dict(label=pg["label"], opened=any(rx.search(o["url"]) for o in P["opens"]),
                            seen=any(rx.search(u) for x in P["searches"] for _, u in x["results"]),
                            cited=any(rx.search(u) for u in cited + written_urls)))
        planted = {f["label"]: bool(re.search(f["regex"], text_all, re.I)) for f in cfg.facts}
        negs = {n["label"]: bool(re.search(n["regex"], P["final"], re.I)) for n in cfg.negs}
        f = dict(id=r["id"], prompt_type=pt, mode=r.get("mode", "research"), agent=agent, task=r["task"],
                 use_case=cfg.use_case(r["task"], P["user_prompt"]), outcome=out, why=why, success=out == SUCCESS.get(pt),
                 wired=wired, searched=bool(P["searches"] or P["opens"]), n_queries=len(queries), query_kinds=dict(qk),
                 queries=queries[:40], neutral_searches=len(neutral), neutral_visible=neutral_vis,
                 own_name_searches=len(own), own_name_first=own_first, own_outranked_by=own_outranked_by,
                 opens=opens, opened_target=any(o["cat"].startswith("target") for o in opens),
                 cited_urls=cited[:60], cited_cats=[cfg.page_cat(u) for u in cited[:60]],
                 published=pub, planted=planted, negative_claims=negs,
                 fetch_errors=[u for u in P["fetch_errors"] if cfg.vendor_of_url(u) == "target"],
                 grader=r.get("goals") or {}, cost=r.get("cost"), final_excerpt=P["final"][:1500])
        facts.append(f)
        if rev:
            queue.append(dict(id=r["id"], prompt_type=pt, agent=agent, task=r["task"], proposed=out, why=why,
                              options=list({"build": ["main", "secondary", "absent"], "tool-seeking": ["top", "listed", "absent"],
                                            "head-to-head": ["win", "split", "loss"], "usability": ["pass", "fail"]}[pt]),
                              log=r["log"], final_excerpt=P["final"][:2500], wired=wired))
    json.dump(facts, open(os.path.join(base, "facts.json"), "w"), indent=1)
    json.dump(queue, open(os.path.join(base, "review_queue.json"), "w"), indent=1)
    json.dump(metrics(cfg, [f for f in facts if "excluded" not in f]), open(os.path.join(base, "metrics.json"), "w"), indent=1)
    ex = [f for f in facts if "excluded" in f]
    print(f"{len(facts) - len(ex)} runs analysed, {len(ex)} excluded, {len(queue)} need review → {base}/review_queue.json")


def rate(rows, key="success"):
    k = sum(1 for r in rows if r[key]); n = len(rows); lo, hi = wilson(k, n)
    return dict(k=k, n=n, rate=round(k / n, 3) if n else None, ci=[round(lo, 3), round(hi, 3)])


def metrics(cfg, F):
    M = dict(by_type={}, pages={}, citations={}, published={}, planted={}, negative={}, behavior={}, won_instead={}, errors={})
    for pt in ["build", "tool-seeking", "head-to-head", "usability"]:
        rows = [f for f in F if f["prompt_type"] == pt]
        if not rows: continue
        d = dict(pooled=rate(rows), outcomes=dict(Counter(f["outcome"] for f in rows)), by_agent={})
        for a in sorted({f["agent"] for f in rows}):
            ar = [f for f in rows if f["agent"] == a]
            d["by_agent"][a] = rate(ar)
        if pt == "build":
            reach = [f for f in rows if f["opened_target"]]
            d["reach"] = rate([dict(success=f["opened_target"]) for f in rows])
            d["conversion"] = rate(reach)
            d["no_target_page_success"] = rate([f for f in rows if not f["opened_target"]])
        d["by_use_case"] = {u: f"{sum(f['success'] for f in rows if f['use_case']==u)}/{sum(1 for f in rows if f['use_case']==u)}"
                            for u in sorted({f["use_case"] for f in rows})}
        M["by_type"][pt] = d
        # behaviour per agent
        for a in sorted({f["agent"] for f in rows}):
            ar = [f for f in rows if f["agent"] == a]
            qk = Counter()
            for f in ar: qk.update(f["query_kinds"])
            asks = Counter()
            for f in ar:
                for o in f["opens"]:
                    for k, pat in [("how to call it", r"request|endpoint|param|sdk|example|code|install|curl|response"), ("price per 1,000", r"price|pricing|cost|\$"),
                                   ("latency", r"latenc|speed|fast"), ("free tier", r"free"), ("rate limits", r"rate limit|qps"), ("benchmark", r"benchmark|accuracy"),
                                   ("who runs it / affiliation", r"who runs|affiliat|sponsor|conflict|independen")]:
                        if re.search(pat, o["prompt"], re.I): asks[k] += 1
            M["behavior"][f"{pt} | {a}"] = dict(runs=len(ar), searched=sum(f["searched"] for f in ar), queries=dict(qk),
                                               neutral=sum(f["neutral_searches"] for f in ar), neutral_visible=sum(f["neutral_visible"] for f in ar),
                                               own_name=sum(f["own_name_searches"] for f in ar), own_name_first=sum(f["own_name_first"] for f in ar),
                                               typed_from_memory=sum(1 for f in ar for o in f["opens"] if not o["via_search"]),
                                               opens=sum(len(f["opens"]) for f in ar), fetch_asks=dict(asks))
        # what won instead (builds) / rival first
        if pt == "build":
            M["won_instead"]["build"] = dict(Counter(",".join(v for v in f["wired"] if v != "target") or "none/DIY" for f in rows if not f["success"]))
    # pages: which runs opened each page category / exact page, with outcome
    cat_stats = defaultdict(lambda: [0, 0]); page_stats = defaultdict(lambda: [0, 0])
    for f in F:
        if f["prompt_type"] == "usability": continue
        for c in {o["cat"] for o in f["opens"]}: cat_stats[c][0 if f["success"] else 1] += 1
        for u in {re.sub(r"^https?://(www\.)?", "", o["url"]).split("?")[0].rstrip("/") for o in f["opens"]}: page_stats[u][0 if f["success"] else 1] += 1
    M["pages"]["by_category"] = {k: dict(won=v[0], lost=v[1]) for k, v in sorted(cat_stats.items(), key=lambda x: -sum(x[1]))}
    M["pages"]["by_page"] = {k: dict(won=v[0], lost=v[1]) for k, v in sorted(page_stats.items(), key=lambda x: -sum(x[1])) if sum(v) >= 2}
    cc = Counter(); cd = Counter()
    for f in F:
        for c in f["cited_cats"]: cc[c] += 1
        for u in f["cited_urls"]: cd[re.sub(r"^https?://(www\.)?", "", u).split("?")[0].rstrip("/")] += 1
    M["citations"] = dict(runs_citing_anything=sum(1 for f in F if f["cited_urls"]), by_category=dict(cc.most_common(30)), top_urls=dict(cd.most_common(30)))
    for pg in cfg.published:
        rows = [p for f in F for p in f["published"] if p["label"] == pg["label"]]
        M["published"][pg["label"]] = dict(seen=sum(p["seen"] for p in rows), opened=sum(p["opened"] for p in rows), cited=sum(p["cited"] for p in rows), runs=len(rows))
    for fc in cfg.facts:
        opened = [f for f in F if any(re.search(fc.get("page_regex", r"$^"), o["url"], re.I) for o in f["opens"])]
        M["planted"][fc["label"]] = dict(reach=sum(f["planted"][fc["label"]] for f in F), runs=len(F),
                                         conversion=sum(f["planted"][fc["label"]] for f in opened), opened_page=len(opened))
    for n in cfg.negs:
        M["negative"][n["label"]] = sum(f["negative_claims"][n["label"]] for f in F)
    M["errors"]["target_pages_erroring"] = dict(Counter(u for f in F for u in f["fetch_errors"]))
    M["own_name_outranked_by"] = dict(Counter(d for f in F for d in f["own_outranked_by"]).most_common(10))
    M["own_subdomain"] = dict(opened=sum(1 for f in F for o in f["opens"] if o["cat"] == "target: own subdomain pages"),
                              cited=sum(1 for f in F for c in f["cited_cats"] if c == "target: own subdomain pages"))
    return M


if __name__ == "__main__":
    main()
