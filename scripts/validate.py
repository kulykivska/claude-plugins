#!/usr/bin/env python3
"""Structural validator for the personal plugin marketplace.
Checks: marketplace.json <-> plugin dirs consistency, plugin.json validity,
SKILL.md / agent frontmatter, hook scripts (syntax + exec bit), Python
compiles, JSON files parse. Exit 0 = all green."""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
errs = []

def err(m): errs.append(m)

# marketplace.json
mp_path = os.path.join(ROOT, ".claude-plugin", "marketplace.json")
try:
    mp = json.load(open(mp_path))
except Exception as e:
    print(f"FATAL: cannot parse marketplace.json: {e}"); sys.exit(1)

listed = {}
for p in mp.get("plugins", []):
    name, src = p.get("name"), p.get("source", "")
    d = os.path.join(ROOT, src.lstrip("./"))
    listed[name] = d
    if not os.path.isdir(d):
        err(f"marketplace lists {name} but dir {src} missing")

# plugin dirs not listed
for entry in sorted(os.listdir(ROOT)):
    d = os.path.join(ROOT, entry)
    if os.path.isdir(os.path.join(d, ".claude-plugin")) and entry != ".claude-plugin":
        if d not in listed.values():
            err(f"plugin dir {entry}/ not listed in marketplace.json")

FM = re.compile(r"^---\s*\nname:\s*\S", re.M)

for name, d in listed.items():
    pj = os.path.join(d, ".claude-plugin", "plugin.json")
    try:
        j = json.load(open(pj))
        if j.get("name") != name:
            err(f"{name}: plugin.json name mismatch ({j.get('name')})")
    except Exception as e:
        err(f"{name}: bad plugin.json: {e}")

    for sub, pat in (("skills", "SKILL.md"), ("agents", None)):
        base = os.path.join(d, sub)
        if not os.path.isdir(base):
            continue
        files = []
        if sub == "skills":
            files = [os.path.join(base, s, "SKILL.md") for s in os.listdir(base)
                     if os.path.isdir(os.path.join(base, s))]
        else:
            files = [os.path.join(base, f) for f in os.listdir(base) if f.endswith(".md")]
        for f in files:
            if not os.path.isfile(f):
                err(f"{name}: missing {f}"); continue
            txt = open(f, encoding="utf-8").read()
            if not txt.startswith("---") or not FM.search(txt[:400]):
                err(f"{name}: {os.path.relpath(f, ROOT)} lacks name frontmatter")

    hooks = os.path.join(d, "hooks")
    if os.path.isdir(hooks):
        hj = os.path.join(hooks, "hooks.json")
        try:
            json.load(open(hj))
        except Exception as e:
            err(f"{name}: bad hooks.json: {e}")
        for f in os.listdir(hooks):
            full = os.path.join(hooks, f)
            if f.endswith(".sh"):
                if not os.access(full, os.X_OK):
                    err(f"{name}: {f} not executable")
                r = subprocess.run(["bash", "-n", full], capture_output=True, text=True)
                if r.returncode:
                    err(f"{name}: {f} syntax error: {r.stderr.strip()}")
            elif f.endswith(".py"):
                r = subprocess.run([sys.executable, "-m", "py_compile", full],
                                   capture_output=True, text=True)
                if r.returncode:
                    err(f"{name}: {f} does not compile: {r.stderr.strip()}")

    for jf in (".lsp.json", os.path.join("monitors", "monitors.json")):
        full = os.path.join(d, jf)
        if os.path.isfile(full):
            try:
                json.load(open(full))
            except Exception as e:
                err(f"{name}: bad {jf}: {e}")

if errs:
    print("VALIDATION FAILED:")
    for e in errs:
        print("  -", e)
    sys.exit(1)
print(f"OK: {len(listed)} plugins valid.")
