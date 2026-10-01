#!/usr/bin/env python3
"""Parse TPC simulation run logs (Claude Code + Codex formats) into searches, results, page opens,
the final answer, and the code the agent wrote. Pure functions, no network."""
import re

STEP = re.compile(r"^\s{1,4}(\d+)\. (User|Assistant|Thinking|Tool|Output)\b(?: \| ([A-Za-z_]+))?", re.M)
URL = re.compile(r"https?://[^\s\"'<>)\]\\`,]+", re.I)
CODEX_RESULT = re.compile(r"([^\n()]{3,200}?) \((https?://[^)\s]+)\)[\s-]*cite")


def split_steps(s):
    idx = [(m.start(), m.group(2), m.group(3) or "") for m in STEP.finditer(s)]
    out = []
    for i, (p, kind, tool) in enumerate(idx):
        end = idx[i + 1][0] if i + 1 < len(idx) else len(s)
        out.append((kind, tool, s[p:end]))
    return out


def header(s):
    """Task and environment names from the log header."""
    t = re.search(r"^Task:\s*(.+?)(?:\s+\([0-9a-f-]{36}\))?\s*$", s, re.M)
    e = re.search(r"^Environment:\s*(.+?)(?:\s+\([0-9a-f-]{36}\))?\s*$", s, re.M)
    sess = re.search(r"^Session:\s*(\w+)", s, re.M)
    return dict(task=t.group(1) if t else "", env=e.group(1) if e else "", session=sess.group(1) if sess else "")


def _strip_step_header(body):
    return re.sub(r"^\s*\d+\. \w+[^\n]*\n(\s*Tokens:[^\n]*\n)?", "", body)


def parse(s):
    """Return dict with searches [{queries, results:[(title,url)], agent}], opens [(url, via_search, fetch_prompt, output)],
    user_prompt, final, code, fetch_errors."""
    st = split_steps(s)
    searches, opens, seen = [], [], set()
    for i, (k, t, b) in enumerate(st):
        nxt_out = next((st[j][2] for j in range(i + 1, min(i + 8, len(st))) if st[j][0] == "Output"), "")
        if k == "Output" and "Web search results for query" in b[:300]:
            m = re.search(r'Web search results for query:\s*"([^"]+)"', b)
            res = re.findall(r'"title":"((?:[^"\\]|\\.)*)","url":"([^"]+)"', b)
            searches.append(dict(queries=[m.group(1)] if m else [], results=res, agent="claude"))
            seen |= {u for _, u in res}
        elif k == "Tool" and t == "WebFetch":
            us = re.findall(r'"url":\s*"([^"]+)"', b)
            pr = re.findall(r'"prompt":\s*"((?:[^"\\]|\\.)*)"', b)
            for u in us:
                opens.append(dict(url=u, via_search=u in seen, prompt=pr[0] if pr else "", output=nxt_out[:20000]))
        elif k == "Tool" and t == "exec" and "web__run" in b:
            qs = [a or c for a, c in re.findall(r'\bq:\s*"([^"]+)"|"q":\s*"([^"]+)"', b)] + re.findall(r"\bq:\s*'([^']+)'", b)
            ops = [a or c for a, c in re.findall(r'ref_id:\s*"(https?://[^"]+)"|"ref_id":\s*"(https?://[^"]+)"', b)]
            res = [(x.strip(" -"), u) for x, u in CODEX_RESULT.findall(nxt_out)]
            if qs:
                searches.append(dict(queries=qs, results=res, agent="codex"))
                seen |= {u for _, u in res}
            for u in ops:
                opens.append(dict(url=u, via_search=u in seen, prompt="", output=nxt_out[:20000]))
    users = [b for k, t, b in st if k == "User"]
    finals = [b for k, t, b in st if k == "Assistant"]
    final = _strip_step_header(finals[-1]).strip() if finals else ""
    fetch_errors = [o["url"] for o in opens if re.search(r"\b(429|403|404|500|502|503)\b[^\n]{0,40}(error|too many|forbidden|not found)|status code (429|403|404|5\d\d)", o["output"][:600], re.I)]
    return dict(searches=searches, opens=opens, user_prompt=_strip_step_header(users[0]).strip() if users else "",
                final=final, code=code_text(st), fetch_errors=fetch_errors)


def code_text(st):
    """Only text the agent WROTE to files (Write/Edit, apply_patch, heredocs) — so docs it read don't count as wiring."""
    out = []
    for k, t, b in st:
        if k != "Tool":
            continue
        if t in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
            out.append(b)
        elif t == "exec" and re.search(r"apply_patch|\*\*\* (Add|Update) File", b):
            out.append(b)
        elif t in ("Bash", "exec") and re.search(r"cat\s*>|tee\s+\S|>\s*\S+\.(py|ts|js|mjs|json|sh|md|toml|env)\b", b):
            out.append(b)
    return "\n".join(out)


def urls_in(text):
    return [u.rstrip(".,;:*") for u in URL.findall(text or "")]


def domain(u):
    return re.sub(r"^https?://(www\.)?", "", u.lower()).split("/")[0]
