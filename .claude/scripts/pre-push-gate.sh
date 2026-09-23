#!/usr/bin/env bash
# PreToolUse gate for `git push`.
# Blocks the push until a pre-push review has run. Applies to EVERY project
# and EVERY branch, except `hotfix*` branches in Shmoozer repos.
# After the review passes, prepush-approve.sh (next to this script) writes the
# marker ($GIT_DIR/PREPUSH_REVIEW_OK = HEAD sha); the gate lets that exact commit
# through while the marker matches HEAD. A stale marker (different sha) is
# removed. The marker is NOT deleted on a matching read, so the gate stays
# correct when registered at more than one settings scope (user + project).
#
# Signals: exit 0 = allow, exit 2 + stderr = block (reason shown to Claude).
# JSON is parsed with plutil (always present on macOS) — no jq dependency.
set -uo pipefail

input=$(cat)

extract() { printf '%s' "$input" | plutil -extract "$1" raw -o - - 2>/dev/null; }

# Only act on `git push` (optionally with global flags like `git --no-pager push`).
cmd=$(extract tool_input.command)
printf '%s' "$cmd" | grep -Eq 'git([[:space:]]+-[^[:space:]]+)*[[:space:]]+push' || exit 0

# Run in the session's working directory.
cwd=$(extract cwd)
# A failed cd would gate whatever directory the hook happens to be in, so
# bail out instead and let the push through (fail open, as everywhere else).
[ -n "$cwd" ] && { cd "$cwd" 2>/dev/null || exit 0; }

# Not a git repo -> nothing to gate.
root=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
gitdir=$(git rev-parse --git-dir 2>/dev/null || echo "")
head=$(git rev-parse HEAD 2>/dev/null || echo "")

# Shmoozer hotfix branches skip the review so an urgent fix ships without delay.
case "$root" in
  *Shmoozer*|*shmoozer*)
    case "$branch" in hotfix*) exit 0 ;; esac
    ;;
esac

# Approval marker: review already done & approved for this exact commit.
# Valid while it matches HEAD (any new commit invalidates it); stale = removed.
marker="$gitdir/PREPUSH_REVIEW_OK"
approve="$(cd "$(dirname "$0")" && pwd)/prepush-approve.sh"
if [ -n "$gitdir" ] && [ -f "$marker" ]; then
  if [ "$(cat "$marker" 2>/dev/null)" = "$head" ]; then
    exit 0
  fi
  rm -f "$marker"
fi

cat >&2 <<EOF
PRE-PUSH POLICY: a review-and-fix pass is required before this push.
Repo: $root | Branch: ${branch:-unknown}
Cover all five dimensions: code smells, architectural patterns, security, scalability, performance.

Claude performs every step below. Do not hand any of them to the user, and
never ask a person for a commit hash — the approval script resolves it itself.
1. Invoke the pre-push-review skill against the diff that will be pushed.
2. FIX the findings (smells / security / scalability / performance) in the working tree, then re-verify. Escalate only genuinely ambiguous or behavior-changing fixes.
3. Commit the fixes (amend or a new commit) so the push contains clean code.
4. Run  $approve  and then re-run git push. It records approval for the final HEAD, which the gate consumes once.
EOF
exit 2
