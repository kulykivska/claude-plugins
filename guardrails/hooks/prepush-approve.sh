#!/usr/bin/env bash
# Records pre-push-review approval for the CURRENT HEAD.
# Resolves the sha itself, so no commit hash is ever typed, echoed or asked for.
# Refuses unless verify-run.sh has produced a passing receipt for this same HEAD,
# so a review cannot be approved with the checks skipped.
set -uo pipefail

gitdir=$(git rev-parse --git-dir 2>/dev/null) || {
  echo "prepush-approve: not a git repository" >&2; exit 1; }
head=$(git rev-parse --verify HEAD 2>/dev/null) || {
  echo "prepush-approve: cannot resolve HEAD (unborn branch?)" >&2; exit 1; }

here="$(cd "$(dirname "$0")" && pwd)"
receipt="$gitdir/PREPUSH_VERIFY_OK"
if [ ! -f "$receipt" ] || [ "$(head -n1 "$receipt" 2>/dev/null)" != "$head" ]; then
  echo "prepush-approve: no passing verification for ${head:0:8}." >&2
  echo "Run the checks first (they run in parallel):  $here/verify-run.sh" >&2
  exit 1
fi

printf '%s\n' "$head" > "$gitdir/PREPUSH_REVIEW_OK"
echo "pre-push review approved for ${head:0:8} on $(git rev-parse --abbrev-ref HEAD) — push will pass once."
echo "verified: $(tail -n +3 "$receipt" | tr '\n' ' ')"
