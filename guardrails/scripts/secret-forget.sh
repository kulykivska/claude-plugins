#!/usr/bin/env bash
# Removes a stored secret — use when it stopped working, then ask for a new one.
set -uo pipefail
SERVICE="${CLAUDE_SECRET_SERVICE:-claude-local-secrets}"
name="${1:-}"
[ -z "$name" ] && { echo "usage: secret-forget.sh <NAME>" >&2; exit 2; }
if security delete-generic-password -s "$SERVICE" -a "$name" >/dev/null 2>&1; then
  echo "forgotten: $name — ask for a fresh value before retrying."
else
  echo "nothing stored for $name" >&2
fi
