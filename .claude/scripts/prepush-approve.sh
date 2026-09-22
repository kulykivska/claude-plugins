#!/usr/bin/env bash
# Records pre-push-review approval for the CURRENT HEAD.
# Resolves the sha itself, so no commit hash is ever typed, echoed or asked for.
# Run it after the final fix commit; `git push` then passes once.
set -uo pipefail

gitdir=$(git rev-parse --git-dir 2>/dev/null) || {
  echo "prepush-approve: not a git repository" >&2; exit 1; }
head=$(git rev-parse --verify HEAD 2>/dev/null) || {
  echo "prepush-approve: cannot resolve HEAD (unborn branch?)" >&2; exit 1; }

printf '%s\n' "$head" > "$gitdir/PREPUSH_REVIEW_OK"
echo "pre-push review approved for ${head:0:8} on $(git rev-parse --abbrev-ref HEAD) — push will pass once."
