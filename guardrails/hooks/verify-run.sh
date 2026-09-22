#!/usr/bin/env bash
# Runs this repo's checks IN PARALLEL and writes a receipt the approval script
# requires. Without a receipt matching HEAD there is no approval and no push,
# so "the tests were skipped" stops being possible.
#
# Receipt: $GIT_DIR/PREPUSH_VERIFY_OK  — HEAD sha + what ran + result.
set -uo pipefail

root=$(git rev-parse --show-toplevel 2>/dev/null) || {
  echo "verify-run: not a git repository" >&2; exit 2; }
gitdir=$(git rev-parse --git-dir 2>/dev/null)
head=$(git rev-parse --verify HEAD 2>/dev/null) || {
  echo "verify-run: cannot resolve HEAD" >&2; exit 2; }

has() { [ -f "$root/package.json" ] && node -e "
const s=require('$root/package.json').scripts||{};process.exit(s['$1']?0:1)" 2>/dev/null; }
pick() { for c in "$@"; do has "$c" && { echo "$c"; return; }; done; }

typecheck=$(pick typecheck type-check)
lint=$(pick lint:affected lint:ci lint)
tests=$(pick test:ci test:affected test)

out=$(mktemp -d); pids=(); names=()
run() { # run <label> <npm-script>
  [ -z "${2:-}" ] && { echo "none-configured" > "$out/$1.status"; return; }
  ( cd "$root" && npm run --silent "$2" >"$out/$1.log" 2>&1 \
      && echo "pass" > "$out/$1.status" || echo "FAIL" > "$out/$1.status" ) &
  pids+=($!); names+=("$1:$2")
}

echo "verify-run: $root @ ${head:0:8}"
run typecheck "$typecheck"
run lint      "$lint"
run tests     "$tests"
if [ "${#pids[@]}" -gt 0 ]; then for p in "${pids[@]}"; do wait "$p"; done; fi

fail=0; lines=()
for k in typecheck lint tests; do
  s=$(cat "$out/$k.status" 2>/dev/null || echo "FAIL")
  case "$s" in
    pass)            printf '  %-10s pass\n' "$k" ;;
    none-configured) printf '  %-10s none configured in this repo\n' "$k" ;;
    *)               printf '  %-10s FAILED — see %s\n' "$k" "$out/$k.log"; fail=1 ;;
  esac
  lines+=("$k=$s")
done

if [ "$fail" -ne 0 ]; then
  echo "verify-run: checks failed — fix them, then run this again. No receipt written." >&2
  exit 1
fi

{ echo "$head"; echo "when=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; printf '%s\n' "${lines[@]}"; } \
  > "$gitdir/PREPUSH_VERIFY_OK"
echo "verify-run: receipt written for ${head:0:8} (${lines[*]})"
