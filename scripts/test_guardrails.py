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
import tempfile
from pathlib import Path

HOOK = Path(__file__).resolve().parents[1] / "guardrails/hooks/guard-destructive-ops.sh"

BLOCKED = 2
ALLOWED = 0


def verdict(command: str, cwd: str = "") -> int:
    payload = json.dumps({"tool_input": {"command": command}, "cwd": cwd})
    done = subprocess.run(  # noqa: S603
        ["/bin/bash", str(HOOK)], input=payload, text=True, capture_output=True, check=False
    )
    return done.returncode


MUST_BLOCK = [
    # Fly.io
    "fly apps destroy racemodel-api",
    "flyctl apps destroy racemodel-api --yes",
    "fly destroy racemodel-api",
    "fly machines destroy 148e --force -a racemodel-api",
    "fly machine destroy 148e",
    "flyctl machine rm 148e",
    "fly -a racemodel-api machines destroy 148e",
    "flyctl volumes delete vol_123",
    "fly volumes destroy vol_123",
    "fly scale count 0 --app racemodel-api",
    "fly secrets unset DATABASE_URL --app racemodel-api",
    "cd infra && FLY_API_TOKEN=x fly apps destroy racemodel-api",
    # SQL through a client, any case, any delivery
    "psql $DATABASE_URL -c 'DROP TABLE predictions'",
    "psql $DATABASE_URL -c 'drop table predictions'",
    'psql "$DATABASE_URL" -c "Drop Database racemodel"',
    "psql -c 'DROP SCHEMA public CASCADE'",
    "psql -c 'ALTER TABLE users DROP COLUMN email'",
    "sqlite3 evidence.db 'TRUNCATE mentions'",
    "psql -c 'truncate table sessions'",
    "psql -c 'DELETE FROM users'",
    "psql -c 'delete from users; select 1'",
    "psql $DATABASE_URL <<'SQL'\nDROP TABLE predictions;\nSQL",
    "psql $DATABASE_URL <<SQL\nbegin;\ndelete from users;\ncommit;\nSQL",
    "cat <<'SQL' | psql $DATABASE_URL\nTRUNCATE predictions;\nSQL",
    "echo 'DROP TABLE x' | psql",
    "psql <<< 'drop table x'",
    "mysql -e 'DROP DATABASE shop'",
    "fly postgres connect -a racemodel-db <<'SQL'\ndrop table predictions;\nSQL",
    "kubectl exec -it pg-0 -- psql -c 'DROP TABLE users'",
    "bash -c \"psql -c 'DROP TABLE users'\"",
    # git push: force in every spelling, to main/master
    "git push --force origin main",
    "git push -f origin main",
    "git push origin main -f",
    "git push -uf origin main",
    "git push --force-with-lease origin main",
    "git push --force-with-lease=main:abc123 origin main",
    "git push origin +main",
    "git push origin +HEAD:main",
    "git push origin +feature:refs/heads/master",
    "git -C repo push --force origin main",
    "git push --mirror origin",
    "git push --all --force origin",
    "git push origin --delete main",
    "git push origin :main",
    "git push -f origin $BRANCH",
    "bash -c 'git push -f origin main'",
    # rm -rf of / or home
    "rm -rf /",
    "rm -rf ~",
    "rm -fr ~/",
    "rm -r -f $HOME",
    "sudo rm -rf /*",
    "rm --recursive --force ${HOME}/*",
    # kubectl
    "kubectl delete namespace shmoozer",
    "kubectl delete ns shmoozer-dev",
    "kubectl --context prod delete deployment api",
    "kubectl delete deploy/api -n shmoozer-prod",
    "kubectl delete statefulset redis --context arn:aws:eks:us-east-1:1:cluster/prod",
    "kubectl delete -f k8s/prod/",
]

MUST_ALLOW = [
    "fly status --app racemodel-api",
    "fly logs --app racemodel-api",
    "fly machines list -a racemodel-api",
    "fly deploy --app racemodel-api",
    "git push origin main",
    "git push -u origin main",
    "git push origin feature/thing",
    "git push --force origin feature/thing",
    "git push --force-with-lease origin feature/thing",
    "git push origin +feature/thing",
    "git push origin --delete feature/thing",
    "git push origin HEAD:refs/heads/feature/x",
    "pytest -q",
    "psql -c 'SELECT count(*) FROM users'",
    "psql -c \"select * from predictions where race_id = 3\"",
    "psql -c 'DELETE FROM sessions WHERE expires_at < now()'",
    "psql $DATABASE_URL <<'SQL'\nDELETE FROM sessions\nWHERE expires_at < now();\nSQL",
    "psql -c '\\dt'",
    # A search for the words is not the operation.
    "grep -rn 'DROP TABLE' migrations/",
    "grep -rn \"DROP TABLE\" migrations/ && psql -c 'SELECT 1'",
    "rg -i 'truncate table' src | head",
    "git grep 'fly apps destroy'",
    "rm -rf ./build",
    "rm -rf ~/tmp/cache",
    "rm -rf /tmp/x",
    "kubectl delete pod api-7d9f -n shmoozer-dev",
    "kubectl --context dev delete deployment api",
    "kubectl get ns",
    "truncate -s 0 app.log && psql -c 'select 1'",
    # Documentation that names a destructive operation is not one. This is the
    # false positive that blocked a README rewrite.
    "cat > README.md <<'EOF'\nGuards fly apps destroy and secrets unset.\nEOF",
    "cat > deploy.sh <<'EOF'\nnever run fly apps destroy here\nEOF",
    "python3 - <<'PY'\nprint('fly apps destroy is only text here')\nPY",
    "git commit -F - <<'EOF'\nfix: guard fly apps destroy and DROP TABLE\nEOF",
]

MUST_BLOCK_INSIDE_HEREDOC = [
    # A heredoc fed to a shell IS executed, so its body still counts.
    "bash <<'EOF'\nfly apps destroy racemodel-api\nEOF",
    "ssh box <<'EOF'\nfly machines destroy 148e\nEOF",
    "sh <<'EOF'\necho hi\ngit push -f origin main\nEOF",
]


def repo_on(branch: str, root: Path) -> str:
    path = root / branch
    path.mkdir()
    subprocess.run(["git", "init", "-q", "-b", branch, str(path)], check=True)  # noqa: S603,S607
    return str(path)


def main() -> int:
    failures: list[str] = []
    for command in MUST_BLOCK + MUST_BLOCK_INSIDE_HEREDOC:
        if verdict(command) != BLOCKED:
            failures.append(f"should have blocked: {command!r}")
    for command in MUST_ALLOW:
        if verdict(command) != ALLOWED:
            failures.append(f"should have allowed: {command!r}")

    # The implied target is the checked-out branch.
    with tempfile.TemporaryDirectory() as tmp:
        main_repo = repo_on("main", Path(tmp))
        feature_repo = repo_on("feature", Path(tmp))
        branch_cases = [
            ("git push -f", main_repo, BLOCKED),
            ("git push --force origin", main_repo, BLOCKED),
            ("git push origin +HEAD", main_repo, BLOCKED),
            ("git push -f", feature_repo, ALLOWED),
            ("git push origin +HEAD", feature_repo, ALLOWED),
            ("git push", main_repo, ALLOWED),
            ("git push -f origin feature", main_repo, ALLOWED),
        ]
        for command, cwd, want in branch_cases:
            if verdict(command, cwd) != want:
                label = "blocked" if want == BLOCKED else "allowed"
                failures.append(f"should have {label} in {Path(cwd).name}: {command!r}")

        # psql -f reads the file it is given.
        sql = Path(tmp) / "drop.sql"
        sql.write_text("BEGIN;\nDROP TABLE users;\nCOMMIT;\n")
        safe = Path(tmp) / "report.sql"
        safe.write_text("SELECT count(*) FROM users;\n")
        file_cases = [
            (f"psql $DATABASE_URL -f {sql}", BLOCKED),
            ("psql $DATABASE_URL -f drop.sql", BLOCKED),
            ("psql $DATABASE_URL < drop.sql", BLOCKED),
            (f"psql --file={safe}", ALLOWED),
        ]
        for command, want in file_cases:
            if verdict(command, tmp) != want:
                label = "blocked" if want == BLOCKED else "allowed"
                failures.append(f"should have {label}: {command!r}")
        branch_cases += file_cases  # counted below

    for line in failures:
        print(f"FAIL {line}")
    total = (
        len(MUST_BLOCK) + len(MUST_BLOCK_INSIDE_HEREDOC) + len(MUST_ALLOW) + len(branch_cases)
    )
    print(f"{total - len(failures)}/{total} guardrail cases correct")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
