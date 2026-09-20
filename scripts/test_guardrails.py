#!/usr/bin/env python3
"""What the blocking hooks must stop, and what they must not.

A guard that cries wolf gets turned off, and a guard that is turned off stops
nothing. Both halves are tested here.

    python3 scripts/test_guardrails.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).resolve().parents[1] / "guardrails/hooks/guard-destructive-ops.sh"

BLOCKED = 2
ALLOWED = 0


def verdict(command: str) -> int:
    payload = json.dumps({"tool_input": {"command": command}})
    done = subprocess.run(  # noqa: S603
        ["/bin/bash", str(HOOK)], input=payload, text=True, capture_output=True, check=False
    )
    return done.returncode


MUST_BLOCK = [
    "fly apps destroy racemodel-api",
    "flyctl volumes delete vol_123",
    "fly scale count 0 --app racemodel-api",
    "fly secrets unset DATABASE_URL --app racemodel-api",
    "psql $DATABASE_URL -c 'DROP TABLE predictions'",
    "sqlite3 evidence.db 'TRUNCATE mentions'",
    "git push --force origin main",
]

MUST_ALLOW = [
    "fly status --app racemodel-api",
    "fly logs --app racemodel-api",
    "git push origin feature/thing",
    "git push --force origin feature/thing",
    "pytest -q",
    # Documentation that names a destructive operation is not one. This is the
    # false positive that blocked a README rewrite.
    "cat > README.md <<'EOF'\nGuards fly apps destroy and secrets unset.\nEOF",
    "python3 - <<'PY'\nprint('fly apps destroy is only text here')\nPY",
]

MUST_BLOCK_INSIDE_HEREDOC = [
    # A heredoc fed to a shell IS executed, so its body still counts.
    "bash <<'EOF'\nfly apps destroy racemodel-api\nEOF",
]


def main() -> int:
    failures: list[str] = []
    for command in MUST_BLOCK + MUST_BLOCK_INSIDE_HEREDOC:
        if verdict(command) != BLOCKED:
            failures.append(f"should have blocked: {command!r}")
    for command in MUST_ALLOW:
        if verdict(command) != ALLOWED:
            failures.append(f"should have allowed: {command!r}")
    for line in failures:
        print(f"FAIL {line}")
    total = len(MUST_BLOCK) + len(MUST_BLOCK_INSIDE_HEREDOC) + len(MUST_ALLOW)
    print(f"{total - len(failures)}/{total} guardrail cases correct")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
