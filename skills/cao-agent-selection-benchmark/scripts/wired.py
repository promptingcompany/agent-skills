#!/usr/bin/env python3
"""Origination ("wired") parser. Channel logic is the kit's reference implementation plus the fixes from
the AgentMail study. Regex sets come from study.yaml. Do not edit channels(); edit the config.

WIRED      = vendor pattern (vendor_code) in authored CODE or deps, after comment stripping
PRESCRIBED = vendor pattern (vendor_prose) in DOCS or PROSE only
DIY        = a `local` pattern in CODE
"""
import json, re, os
from tpc_helpers import load_config

DOC_RE = re.compile(r"\.(md|mdx|txt|rst)$|readme|/docs?/|changelog|notes|/memory/|\.claude/", re.I)
INSTALL_RE = re.compile(r"(?:npm|pnpm|yarn|bun)\s+(?:add|install|i)\s+([^\n&|;]+)|(?:pip3?|uv pip|uv add|poetry)\s+(?:install|add)\s+([^\n&|;]+)", re.I)
HEREDOC_RE = re.compile(r"(?:cat|tee)\s*(?:-a)?\s*>?>?\s*['\"]?([\w./@\-]+)['\"]?\s*<<-?\s*['\"]?(\w+)['\"]?\n(.*?)\n\2", re.S)
PATCH_FILE_RE = re.compile(r"\*\*\*\s+(?:Add|Update)\s+File:\s*([^\n]+)")
UDIFF_FILE_RE = re.compile(r"^\+\+\+ (?:b/)?([^\n\t]+)", re.M)
RESEARCH_RE = re.compile(r"WebSearch|WebFetch|web\.run|web_search|browser\.|curl\s+-?[sSL]*\s*https?://|wget\s+https?://", re.I)
CITATION_RE = re.compile(r"utm_source=(openai|chatgpt\.com)|\(https?://[^)]+\?utm_source=", re.I)   # Codex native search leaves no tool event
MCP_WIRE_RE = re.compile(r"claude mcp add[^\n]*|mcpServers|\.mcp\.json", re.I)
COMMENT_LINE = re.compile(r"^\s*(#|//|/\*|\*|<!--|--)\s?.*$", re.M)
WRITE_TOOLS = {"write", "edit", "create_file", "str_replace", "apply_patch", "write_file", "multi_edit", "notebook_edit", "str_replace_editor"}
SHELL_TOOLS = {"bash", "exec_command", "shell", "run_command", "write_stdin"}

def parse_apply_patch(cmd):
    if "apply_patch" not in cmd and "*** Add File:" not in cmd: return
    parts = PATCH_FILE_RE.split(cmd)
    for i in range(1, len(parts) - 1, 2):
        yield parts[i].strip(), "\n".join(l[1:] for l in parts[i + 1].split("\n") if l.startswith("+") and not l.startswith("+++"))

def parse_unified_diff(body):
    if "+++ " not in body or "@@" not in body: return
    parts = UDIFF_FILE_RE.split(body)
    for i in range(1, len(parts) - 1, 2):
        yield parts[i].strip(), "\n".join(l[1:] for l in parts[i + 1].split("\n") if l.startswith("+") and not l.startswith("+++"))

def _targs(e):
    md = e.get("metadata") or {}; a = md.get("toolArgs") or md.get("tool_args") or md.get("args") or ""
    return a if isinstance(a, str) else json.dumps(a)
def _tname(e):
    md = e.get("metadata") or {}
    for k in ("toolName", "tool_name", "name", "tool"):
        if md.get(k): return str(md[k]).lower()
    return ""
def _unescape(s):
    try:
        o = json.loads(s); return "\n".join(str(v) for v in o.values()) if isinstance(o, dict) else str(o)
    except Exception:
        return s.replace("\\n", "\n").replace('\\"', '"')

def channels(path):
    d = json.load(open(path)); ev = (d.get("session") or {}).get("events") or d.get("events") or []
    code, docs, deps, prose, looked = [], [], [], [], []
    for e in ev:
        t = e.get("type"); c = e.get("content"); c = c if isinstance(c, str) else (json.dumps(c) if c is not None else "")
        if t == "assistant": prose.append(c); continue
        if t != "tool": continue
        tn, raw = _tname(e), _targs(e); payload = _unescape(raw) if raw else c
        if tn in WRITE_TOOLS or any(w in tn for w in ("write", "edit", "patch")):
            md = e.get("metadata") or {}; p = md.get("filePath") or md.get("file_path") or md.get("path") or ""
            if not p:
                mm = re.search(r'"(?:file_path|path|filePath)"\s*:\s*"([^"]+)"', raw); p = mm.group(1) if mm else ""
            (docs if DOC_RE.search(p or "") else code).append(payload)
        elif tn in SHELL_TOOLS:
            cmd = payload
            for m in INSTALL_RE.finditer(cmd): deps.append(m.group(1) or m.group(2) or "")
            for tgt, _tag, body in HEREDOC_RE.findall(cmd):
                files = list(parse_unified_diff(body)) or list(parse_apply_patch(body))
                if files:
                    for fp, fb in files: (docs if DOC_RE.search(fp) else code).append(fb)
                else:
                    (docs if DOC_RE.search(tgt) else code).append(body)
            for tgt, body in parse_apply_patch(cmd): (docs if DOC_RE.search(tgt) else code).append(body)
            for m in MCP_WIRE_RE.finditer(cmd): code.append(m.group(0))
            looked.append(cmd)
        else:
            looked.append(tn + " " + payload[:2000])
    return {"code": "\n".join(code), "docs": "\n".join(docs), "deps": "\n".join(deps), "prose": "\n".join(prose), "looked": "\n".join(looked), "n_events": len(ev)}

def strip_comments(t): return COMMENT_LINE.sub("", t or "")
def hits(pats, text, code=False):
    t = strip_comments(text) if code else text
    return sorted({k for k, p in pats.items() if t and re.search(p, t, re.I)})

def classify(path, cfg, run_id=None):
    """run_id (or its 8-char prefix) enables manual_exclude from study.yaml: a hit that a human verified is NOT the
    vendor (an agent naming its own CLI `agentmail`) is dropped here, so every caller gets the same answer."""
    ch = channels(path); codedeps = ch["code"] + "\n" + ch["deps"]
    wired = hits(cfg["vendor_code"], codedeps, code=True)
    prescribed = sorted(set(hits(cfg["vendor_prose"], ch["docs"] + "\n" + ch["prose"])) - set(wired))
    if run_id:
        ex = (cfg.get("manual_exclude") or {}).get(str(run_id)[:8]) or {}
        wired = [v for v in wired if v not in ex]; prescribed = [v for v in prescribed if v not in ex]
    return ch, {"wired": wired, "prescribed": prescribed, "diy": hits(cfg.get("local", {}), codedeps, code=True),
                "caps": hits(cfg.get("caps", {}), codedeps, code=True),
                "research": bool(RESEARCH_RE.search(ch["looked"]) or CITATION_RE.search(ch["prose"] + ch["docs"])),
                "code_chars": len(ch["code"]), "events": ch["n_events"], "hedged": len(wired) >= 2}
