#!/usr/bin/env python3
"""SessionStart: inject a short status banner (repo, branch, uncommitted count)
into the session context. Non-blocking."""
import sys, json, subprocess

def git(*a):
    try:
        return subprocess.run(["git", *a], capture_output=True, text=True, timeout=5).stdout.strip()
    except Exception:
        return ""

root = git("rev-parse", "--show-toplevel")
if not root:
    sys.exit(0)

branch = git("rev-parse", "--abbrev-ref", "HEAD") or "?"
dirty = git("status", "--porcelain")
n = len([l for l in dirty.splitlines() if l.strip()])
repo = root.rstrip("/").split("/")[-1]

parts = [f"branch `{branch}`", (f"{n} uncommitted file(s)" if n else "clean tree")]
msg = f"coach · {repo}: " + ", ".join(parts)

print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "SessionStart", "additionalContext": msg}}))
sys.exit(0)
