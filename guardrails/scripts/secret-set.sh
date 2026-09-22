#!/usr/bin/env bash
# Stores a named secret in the macOS login keychain.
#   interactive:  secret-set.sh NAME          -> prompts, no echo, value never in argv
#   piped:        printf %s "$v" | secret-set.sh NAME --stdin
set -uo pipefail

SERVICE="${CLAUDE_SECRET_SERVICE:-claude-local-secrets}"
name="${1:-}"
[ -z "$name" ] && { echo "usage: secret-set.sh <NAME> [--stdin]" >&2; exit 2; }

if [ "${2:-}" = "--stdin" ] || [ ! -t 0 ]; then
  IFS= read -r value || true
  [ -z "${value:-}" ] && { echo "secret-set: empty value, nothing stored" >&2; exit 1; }
  # NOTE: this path puts the value in argv, briefly visible to `ps` on a shared
  # machine. Prefer the interactive form below when a terminal is available.
  security add-generic-password -U -s "$SERVICE" -a "$name" -w "$value"
else
  echo "Enter the value for $name (it will not be echoed):"
  security add-generic-password -U -s "$SERVICE" -a "$name" -w
fi

echo "stored: $name (keychain service '$SERVICE'). The value was not printed."
