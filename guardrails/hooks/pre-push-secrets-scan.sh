#!/usr/bin/env bash
# PreToolUse(Bash): scan the diff being pushed for real credentials / secrets /
# PII (private keys, cloud tokens, secret assignments, real emails/phones).
# Blocks (exit 2) on hits; the allowlist covers placeholders & test fixtures.
# Fail open on anything unexpected so a legitimate push is never wedged.

input="$(cat)"
cmd="$(printf '%s' "$input" | python3 -c 'import sys,json
try: print(json.load(sys.stdin).get("tool_input",{}).get("command",""))
except Exception: print("")' 2>/dev/null || true)"

# Only act on an actual git push.
printf '%s' "$cmd" | grep -qiE 'git[[:space:]].*push' || exit 0
git rev-parse --show-toplevel >/dev/null 2>&1 || exit 0

# Scan ONLY what this push will actually send = commits on HEAD not yet on the
# remote. Prefer the branch's push/upstream tracking ref; if the branch was
# never pushed, fall back to its new work vs origin/main.
if base="$(git rev-parse --verify --quiet '@{push}' 2>/dev/null)" && [ -n "$base" ]; then
  :
elif base="$(git rev-parse --verify --quiet '@{upstream}' 2>/dev/null)" && [ -n "$base" ]; then
  :
elif base="$(git merge-base HEAD origin/main 2>/dev/null)" && [ -n "$base" ]; then
  :
else
  exit 0     # can't determine what's new — fail open
fi
range="${base}..HEAD"

root="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
git diff "$range" --unified=0 --no-color 2>/dev/null \
  | python3 "$root/hooks/secrets_scan.py" "$root/hooks/secrets-allowlist.txt"
exit $?
