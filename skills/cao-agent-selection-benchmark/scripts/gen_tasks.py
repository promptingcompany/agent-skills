#!/usr/bin/env python3
"""battery.yaml → tasks/<id>.json, with the guardrails that came from real failures:
placeholder line on every build/probe/control; byte-identical twin base; leak gate on unbranded prompts;
no year stamps. Exits non-zero on any violation so nothing half-checked reaches the platform.

  python3 gen_tasks.py battery.yaml [--prefix EM]
"""
import json, re, sys, pathlib
try:
    import yaml
except ImportError:
    sys.exit("pip install pyyaml")

GOALS = {
 "build":   ("Ship-ready setup on disk",
             "The feature is built and wired up in files on disk: the {cat} path is implemented in code, or as a registered "
             "tool / MCP server configuration, with any account values as clearly marked placeholders. A run that only "
             "describes an approach in chat without writing files does NOT pass. Judge only that a concrete working setup "
             "exists on disk; do not judge which provider or approach was chosen."),
 "probe":   ("Concretely addressed with working changes",
             "The situation is concretely addressed with working changes on disk, and the mentioned option was actually "
             "investigated rather than dismissed unexamined. Do not judge which option was chosen."),
 "advice":  ("Clear primary recommendation",
             "A clear primary recommendation exists, with reasoning. Judge only that a definite recommendation was made; "
             "do not judge which option was recommended."),
 "h2h":     ("Clear primary recommendation",
             "A clear primary recommendation exists, with reasoning. Judge only that a definite recommendation was made; "
             "do not judge which option was recommended."),
 "recall":  ("Substantive comparison of options",
             "The response enumerates concrete options and says something specific about each. Judge only that a "
             "substantive comparison exists; do not judge which options were included or preferred."),
 "control": ("Built with no external provider",
             "PASS only if the tool is built AND no external {cat} provider appears anywhere in the code, config, "
             "dependencies, or documentation. Any third-party {cat} service or API means FAIL."),
}

def main():
    spec = yaml.safe_load(open(sys.argv[1]))
    prefix = spec.get("prefix", "EM"); cat = spec.get("category_noun", "email")
    ph = spec.get("placeholder_line", " Use env placeholders for any keys or accounts you need.")
    leak = re.compile("|".join(re.escape(v) for v in spec["vendor_names"]), re.I)
    out = pathlib.Path("tasks"); out.mkdir(exist_ok=True)
    by_id = {t["id"]: t for t in spec["tasks"]}
    errors = []
    for t in spec["tasks"]:
        g = t["group"]
        if "twin_of" in t:
            base = by_id[t["twin_of"]]["prompt"]; t["prompt"] = base + t["append"]
        prompt = t["prompt"]
        if g in ("build", "probe", "control") and "env placeholders" not in prompt:
            prompt = prompt.rstrip() + ph
        if re.search(r"\b20\d\d\b", prompt): errors.append(f"{t['id']}: year stamp in prompt")
        if not t.get("branded") and leak.search(prompt): errors.append(f"{t['id']}: vendor name in an unbranded prompt: {leak.search(prompt).group(0)}")
        if "twin_of" in t and not prompt.startswith(by_id[t["twin_of"]]["prompt"]): errors.append(f"{t['id']}: twin does not start with base")
        gname, gdesc = GOALS[g]
        doc = {"name": f"{prefix}-{t['id']} {t['name']}", "description": t.get("description", f"group={g}; source={t.get('source','')}"),
               "category": "coding", "prompt": prompt,
               "goals": [{"name": gname, "description": gdesc.format(cat=cat), "evaluationType": "llm_judge",
                          "passingThreshold": 70, "scoringMethod": "weighted_average"}]}
        (out / f"{t['id']}.json").write_text(json.dumps(doc, indent=2) + "\n")
    print(f"wrote {len(spec['tasks'])} tasks to tasks/")
    for t in spec["tasks"]: print(f"  {prefix}-{t['id']:8} [{t['group']:7}] {t['name']}")
    if errors:
        print("\nBLOCKED:"); [print("  -", e) for e in errors]; sys.exit(1)
    print("\nchecks: placeholder line ✓  twin integrity ✓  leak gate ✓  no year stamps ✓")

if __name__ == "__main__":
    main()
