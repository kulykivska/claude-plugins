#!/usr/bin/env bash
# PreToolUse(Bash) guard: blocks destructive operations against production
# resources (Fly.io apps/volumes, prod databases) and force-pushes to main.
# Reads the tool-call JSON on stdin; exit 2 blocks the call and feeds stderr
# back to Claude. Exit 0 allows. Fail open (allow) if anything unexpected.

input="$(cat)"
cmd="$(printf '%s' "$input" | python3 -c 'import sys,json
try: print(json.load(sys.stdin).get("tool_input",{}).get("command",""))
except Exception: print("")' 2>/dev/null || true)"

[ -z "$cmd" ] && exit 0

block() {
  echo "BLOCKED by guardrails: $1" >&2
  echo "This is a destructive/irreversible operation. If it is truly intended, run it yourself outside Claude Code." >&2
  exit 2
}

# 1) Destroying Fly.io resources (apps, volumes, postgres clusters)
if printf '%s' "$cmd" | grep -qiE '\bfly(ctl)?\b'; then
  if printf '%s' "$cmd" | grep -qiE '\b(apps|volumes|postgres)[[:space:]]+(destroy|delete)\b'; then
    block "destroying a Fly.io app/volume/postgres cluster."
  fi
  if printf '%s' "$cmd" | grep -qiE '\bscale[[:space:]]+count[[:space:]]+0\b'; then
    block "scaling a Fly app to 0 machines (takes prod down)."
  fi
  if printf '%s' "$cmd" | grep -qiE '\bsecrets[[:space:]]+unset\b'; then
    block "unsetting Fly secrets (can break a running prod app)."
  fi
fi

# 2) Dropping tables/databases through any client (psql, fly pg connect, sqlite3)
if printf '%s' "$cmd" | grep -qiE '\b(psql|pg[[:space:]]+connect|sqlite3)\b'; then
  if printf '%s' "$cmd" | grep -qiE 'DROP[[:space:]]+(TABLE|DATABASE|SCHEMA)|TRUNCATE[[:space:]]'; then
    block "DROP/TRUNCATE through a database client. Migrations or a deliberate operator action only."
  fi
fi

# 3) Force-push to main/master
if printf '%s' "$cmd" | grep -qE 'git([[:space:]]+-[^[:space:]]+)*[[:space:]]+push'; then
  if printf '%s' "$cmd" | grep -qE '(--force|-f)\b' && printf '%s' "$cmd" | grep -qE '\b(main|master)\b'; then
    block "force-pushing to main/master."
  fi
fi

exit 0
