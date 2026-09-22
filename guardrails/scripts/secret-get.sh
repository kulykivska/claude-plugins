#!/usr/bin/env bash
# Prints the stored value for a named secret, or exits 1 explaining how to add it.
# Values live in the macOS login keychain; nothing is ever written to the repo.
set -uo pipefail

SERVICE="${CLAUDE_SECRET_SERVICE:-claude-local-secrets}"
name="${1:-}"
[ -z "$name" ] && { echo "usage: secret-get.sh <NAME>" >&2; exit 2; }
here="$(cd "$(dirname "$0")" && pwd)"

if value=$(security find-generic-password -s "$SERVICE" -a "$name" -w 2>/dev/null); then
  printf '%s' "$value"
  exit 0
fi

cat >&2 <<MSG
secret-get: nothing stored for $name.
Ask the person to run this in the session — it prompts on their terminal and the
value is never echoed, never sent to the model, and never written to a file:
  ! $here/secret-set.sh $name
MSG
exit 1
