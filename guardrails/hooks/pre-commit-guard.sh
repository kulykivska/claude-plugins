#!/usr/bin/env bash
# PreToolUse(Bash): enforce commit hygiene before a `git commit`:
#   1) message: no AI attribution / co-author trailers
#   2) no real secrets/PII in the staged diff (reuses the secret scanner)
# Blocks (exit 2) on violation. Fail open on anything unexpected.

input="$(cat)"
cmd="$(printf '%s' "$input" | python3 -c 'import sys,json
try: print(json.load(sys.stdin).get("tool_input",{}).get("command",""))
except Exception: print("")' 2>/dev/null || true)"

printf '%s' "$cmd" | grep -qE 'git[[:space:]].*commit' || exit 0
git rev-parse --show-toplevel >/dev/null 2>&1 || exit 0

root="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"

# 1) commit-message policy (attribution ban)
if printf '%s' "$cmd" | grep -qiE 'co-authored-by|generated with claude|noreply@anthropic'; then
  echo "BLOCKED by guardrails (commit policy): remove AI attribution / co-author trailer from the commit message." >&2
  exit 2
fi

# 2) secrets/PII in the staged changes (catch them before they enter history)
staged="$(git diff --cached --unified=0 --no-color 2>/dev/null)"
if [ -n "$staged" ]; then
  printf '%s' "$staged" | SCAN_CONTEXT="staged changes" \
    python3 "$root/hooks/secrets_scan.py" "$root/hooks/secrets-allowlist.txt" || exit 2
fi
exit 0
