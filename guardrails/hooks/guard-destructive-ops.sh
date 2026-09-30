#!/usr/bin/env bash
# PreToolUse(Bash) guard; the matching lives in guard_destructive_ops.py.
# Exit 2 blocks the call. Fails open (allows) when python3 is missing.
command -v python3 >/dev/null 2>&1 || exit 0
exec python3 "$(dirname "$0")/guard_destructive_ops.py"
