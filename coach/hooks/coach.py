#!/usr/bin/env python3
"""PostToolUse(Edit|Write): non-blocking convention nudges for the edited file's
stack. Emits `additionalContext` (exit 0) only when it actually finds something;
stays silent otherwise. Never mutates files. Inspects only the ADDED text."""
import sys, json, re

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

ti = data.get("tool_input", {}) or {}
path = str(ti.get("file_path", "") or "")
added = ti.get("new_string") or ti.get("content") or ""
if not path or not added:
    sys.exit(0)

low = path.replace("\\", "/").lower()
notes = []

def hit(pattern, msg, flags=0):
    if re.search(pattern, added, flags):
        notes.append(msg)

if low.endswith(".py"):
    hit(r"\bexcept[^:\n]*:\s*(pass|\.\.\.)\s*(\n|$)",
        "empty except swallows the error: log it or surface it to the caller")
    hit(r"\bbreakpoint\(\)|pdb\.set_trace\(", "leftover debugger breakpoint")
    if "feature_cols" in added.lower() and re.search(r"(predictor|shared)\.py$", low):
        notes.append("FEATURE_COLS touched: it must stay EXACTLY synced between racemodel predictor.py and f1-predictor shared.py, or live predictions 500 with a shape mismatch. Sync both repos and mind deploy ordering.")

elif low.endswith((".ts", ".tsx", ".js", ".jsx")):
    hit(r"\bconsole\.log\b", "leftover console.log: remove or use the project's logger")
    hit(r":\s*any\b", "avoid `any`: use a proper type")
    hit(r"\.\./\.\./\.\./", "deep relative import: prefer the project's path alias if it has one")

elif low.endswith(".swift"):
    hit(r"\btry!\s", "`try!` crashes on error: handle or propagate instead")
    hit(r"(?<![A-Za-z0-9_])print\(", "leftover print(): remove or use a logger")

# User-facing text policy: no em-dashes anywhere users can see them.
if low.endswith((".tsx", ".swift", ".xcstrings", ".html")) and ("—" in added or "–" in added):
    notes.append("em/en dash in user-facing text: the owner's rule is NO long dashes anywhere users see; use a comma, colon, or parentheses")

if notes:
    msg = "coach nudges for " + path + ":\n- " + "\n- ".join(notes)
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PostToolUse", "additionalContext": msg}}))
sys.exit(0)
