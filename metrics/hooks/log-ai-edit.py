#!/usr/bin/env python3
"""PostToolUse(Edit|Write|NotebookEdit) — append one JSONL record per Claude Code
edit to ~/.claude/shmoozer-metrics/ai-edits.jsonl. Never touches the codebase,
never blocks, never prints: telemetry must be invisible to the session."""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG_DIR = Path.home() / ".claude" / "shmoozer-metrics"
LOG_FILE = LOG_DIR / "ai-edits.jsonl"


def git(args, cwd):
    try:
        out = subprocess.run(
            ["git", *args], cwd=cwd, capture_output=True, text=True, timeout=3
        )
        return out.stdout.strip() if out.returncode == 0 else ""
    except Exception:
        return ""


def main():
    data = json.load(sys.stdin)
    ti = data.get("tool_input", {}) or {}
    path = str(ti.get("file_path", "") or ti.get("notebook_path", "") or "")
    if not path:
        return

    # Lines the model wrote in this call: the added side of an Edit, or the whole
    # file body for a Write. Good enough for a share-of-changes metric.
    added = ti.get("new_string") or ti.get("content") or ti.get("new_source") or ""
    lines = added.count("\n") + 1 if added else 0

    file_dir = os.path.dirname(path) or "."
    repo_root = git(["rev-parse", "--show-toplevel"], file_dir)
    record = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repo": os.path.basename(repo_root) if repo_root else None,
        "branch": git(["branch", "--show-current"], file_dir) or None,
        "file": os.path.relpath(path, repo_root) if repo_root else path,
        "tool": data.get("tool_name", ""),
        "lines": lines,
        "session": data.get("session_id") or None,
    }

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a") as f:
        f.write(json.dumps(record) + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # never block the session; keep the failure visible
        try:
            LOG_DIR.mkdir(parents=True, exist_ok=True)
            with (LOG_DIR / "hook-errors.log").open("a") as f:
                f.write(f"{datetime.now(timezone.utc).isoformat(timespec='seconds')} {exc!r}\n")
        except Exception:
            pass
    sys.exit(0)
