#!/usr/bin/env python3
"""Stop: at end of a turn, remind about uncommitted changes.
Non-blocking (exit 0 + additionalContext); never blocks the stop."""
import sys, json, subprocess

try:
    data = json.load(sys.stdin)
except Exception:
    data = {}

if data.get("stop_hook_active"):
    sys.exit(0)

def git(*a):
    try:
        return subprocess.run(["git", *a], capture_output=True, text=True, timeout=5).stdout.strip()
    except Exception:
        return ""

if not git("rev-parse", "--show-toplevel"):
    sys.exit(0)

branch = git("rev-parse", "--abbrev-ref", "HEAD")
dirty = git("status", "--porcelain")
n = len([l for l in dirty.splitlines() if l.strip()])

if n:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "Stop",
        "additionalContext": f"coach: {n} uncommitted file(s) on `{branch}`. Commit when the work is at a good checkpoint."}}))
sys.exit(0)
