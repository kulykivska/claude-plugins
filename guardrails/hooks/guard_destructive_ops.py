#!/usr/bin/env python3
"""PreToolUse(Bash) guard for destructive prod operations; exit 2 blocks, 0 allows.

Scope and known limits are listed in guardrails/README.md.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

PROTECTED_BRANCHES = {"main", "master"}
SHELLS = {"bash", "sh", "zsh", "dash", "ksh", "fish", "eval", "source", "."}
SQL_CLIENTS = {
    "psql", "pgcli", "mysql", "mariadb", "sqlite3", "duckdb", "usql",
    "clickhouse", "clickhouse-client", "cockroach",
}
GREP_LIKE = {"grep", "egrep", "fgrep", "rg", "ag", "ack"}
WRAPPERS = {"sudo", "doas", "env", "command", "exec", "time", "nohup", "nice", "builtin"}

SQL_CLIENT_RE = re.compile(
    r"\b(" + "|".join(re.escape(c) for c in sorted(SQL_CLIENTS)) + r")\b"
    r"|\b(pg|postgres|mpg)\s+connect\b",
    re.I,
)
REMOTE_EXEC_RE = re.compile(
    r"\b(kubectl|docker|podman)\s+exec\b|\bfly(ctl)?\b.*\b(connect|console)\b", re.I
)
DROP_RE = re.compile(
    r"\bdrop\s+(table|database|schema|view|materialized\s+view|index|sequence|type"
    r"|function|extension|owned|role|user|column)\b",
    re.I,
)
TRUNCATE_RE = re.compile(r"\btruncate\b(\s+table)?\s+(only\s+)?[\w\"`$]", re.I)
DELETE_RE = re.compile(r"\bdelete\s+from\b", re.I)
WHERE_RE = re.compile(r"\bwhere\b", re.I)
FLY_RE = re.compile(r"(^|[\s/;&|(])fly(ctl)?(\s|$)", re.I)
FLY_DESTROY_RE = re.compile(
    r"\bdestroy\b"
    r"|\b(apps?|volumes?|vol|machines?|m|postgres|pg|mpg|redis|tigris|storage|ext)\s+"
    r"(delete|remove|rm)\b",
    re.I,
)
HEREDOC_RE = re.compile(
    r"<<(-?)[ \t]*(['\"]?)([A-Za-z_][\w.-]*)\2([^\n]*)\n(.*?)(?:\n[ \t]*\3[ \t]*(?=\n|$)|\Z)",
    re.S,
)
MAX_SQL_FILE_BYTES = 4 << 20


class Blocked(Exception):
    pass


def split_segments(text: str) -> list[tuple[int, str]]:
    """Split on unquoted ; && || | & and newlines into (pipeline_id, text).

    Commands joined by a single | share a pipeline id."""
    out: list[tuple[int, str]] = []
    buf: list[str] = []
    pipeline = 0
    quote = ""
    i = 0
    n = len(text)

    def flush(next_pipeline: bool) -> None:
        nonlocal pipeline
        seg = "".join(buf).strip()
        if seg:
            out.append((pipeline, seg))
        buf.clear()
        if next_pipeline:
            pipeline += 1

    while i < n:
        ch = text[i]
        if quote:
            buf.append(ch)
            if ch == "\\" and quote == '"' and i + 1 < n:
                buf.append(text[i + 1])
                i += 2
                continue
            if ch == quote:
                quote = ""
            i += 1
            continue
        if ch == "\\" and i + 1 < n:
            buf.append(ch + text[i + 1])
            i += 2
            continue
        if ch in "'\"`":
            quote = ch
            buf.append(ch)
            i += 1
            continue
        two = text[i : i + 2]
        if two in ("&&", "||"):
            flush(True)
            i += 2
            continue
        if ch == "|":
            flush(False)
            i += 1
            continue
        if ch in ";\n" or (ch == "&" and text[i - 1 : i] not in (">", "<") and two != "&>"):
            flush(True)
            i += 1
            continue
        buf.append(ch)
        i += 1
    flush(True)
    return out


def tokens(segment: str) -> list[str]:
    try:
        return shlex.split(segment, comments=False)
    except ValueError:
        return segment.split()


def argv(segment: str) -> list[str]:
    """Tokens with leading assignments, subshell marks and wrappers removed."""
    toks = [t for t in tokens(segment.lstrip("({! \t"))]
    while toks:
        head = toks[0]
        if re.match(r"^[A-Za-z_]\w*=", head):
            toks.pop(0)
        elif head in WRAPPERS:
            toks.pop(0)
            while toks and toks[0].startswith("-"):
                toks.pop(0)
        else:
            break
    if toks:
        toks[0] = os.path.basename(toks[0])
    return toks


def is_grep(av: list[str]) -> bool:
    if not av:
        return False
    return av[0] in GREP_LIKE or (av[0] == "git" and "grep" in av[1:3])


def is_executor(segment: str, av: list[str]) -> bool:
    """True when stdin of this command is executed as shell or SQL."""
    if av and (av[0] in SHELLS or av[0] in SQL_CLIENTS or av[0] == "ssh"):
        return True
    return bool(SQL_CLIENT_RE.search(segment) or REMOTE_EXEC_RE.search(segment))


class Analysis:
    def __init__(self, cwd: str) -> None:
        self.cwd = cwd
        self.segments: list[str] = []
        self.sql_units: list[str] = []
        self.sql_client = False

    def add(self, command: str, depth: int = 0, body: bool = False) -> None:
        bodies: list[str] = []

        def stash(m: re.Match[str]) -> str:
            bodies.append(m.group(5))
            return f" __HEREDOC_{len(bodies) - 1}__ {m.group(4)}\n"

        flat = HEREDOC_RE.sub(stash, command)
        segs = split_segments(flat)
        exec_pipelines = {pid for pid, s in segs if is_executor(s, argv(s))}
        for pid, seg in segs:
            av = argv(seg)
            if is_grep(av):
                continue
            self.segments.append(seg)
            if not body:
                self.sql_units.extend(seg.split(";"))
            if SQL_CLIENT_RE.search(seg):
                self.sql_client = True
                self.read_sql_files(av)
            if depth < 3 and av:
                inner = inner_command(av)
                if inner:
                    self.add(inner, depth + 1)
            for idx in map(int, re.findall(r"__HEREDOC_(\d+)__", seg)):
                if pid in exec_pipelines and idx < len(bodies):
                    text = bodies[idx]
                    self.sql_units.extend(text.split(";"))
                    if depth < 3:
                        self.add(text, depth + 1, body=True)

    def read_sql_files(self, av: list[str]) -> None:
        paths: list[str] = []
        for i, tok in enumerate(av):
            if tok in ("-f", "--file", "<") and i + 1 < len(av):
                paths.append(av[i + 1])
            elif tok.startswith("--file="):
                paths.append(tok.split("=", 1)[1])
            elif tok.startswith("<") and len(tok) > 1 and not tok.startswith("<<"):
                paths.append(tok[1:])
        for raw in paths:
            p = Path(os.path.expanduser(raw))
            if not p.is_absolute() and self.cwd:
                p = Path(self.cwd) / p
            try:
                with p.open("rb") as fh:
                    text = fh.read(MAX_SQL_FILE_BYTES).decode("utf-8", "replace")
            except OSError:
                continue
            self.sql_units.extend(text.split(";"))


def inner_command(av: list[str]) -> str:
    """The command string a shell wrapper runs: bash -c '...', eval ..."""
    if av[0] == "eval":
        return " ".join(av[1:])
    if av[0] in SHELLS:
        for i, tok in enumerate(av[1:], 1):
            if re.fullmatch(r"-[a-z]*c[a-z]*", tok) and i + 1 < len(av):
                return av[i + 1]
    return ""


def check_sql(a: Analysis) -> None:
    if not a.sql_client:
        return
    for unit in a.sql_units:
        if DROP_RE.search(unit) or TRUNCATE_RE.search(unit):
            raise Blocked(
                "DROP/TRUNCATE through a database client. Migrations or a deliberate "
                "operator action only."
            )
        for m in DELETE_RE.finditer(unit):
            if not WHERE_RE.search(unit[m.end() :]):
                raise Blocked("DELETE FROM without a WHERE clause through a database client.")


def check_fly(a: Analysis) -> None:
    for seg in a.segments:
        if not FLY_RE.search(seg):
            continue
        if FLY_DESTROY_RE.search(seg):
            raise Blocked("destroying a Fly.io app/machine/volume/postgres cluster.")
        if re.search(r"\bscale\s+count\b(\s+-\S+)*\s+0\b", seg, re.I):
            raise Blocked("scaling a Fly app to 0 machines (takes prod down).")
        if re.search(r"\bsecrets\s+unset\b", seg, re.I):
            raise Blocked("unsetting Fly secrets (can break a running prod app).")


GIT_OPTS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}
PUSH_OPTS_WITH_VALUE = {"-o", "--push-option", "--repo", "--receive-pack", "--exec"}


def current_branch(cwd: str) -> str:
    if not cwd:
        return ""
    try:
        done = subprocess.run(  # noqa: S603
            ["git", "-C", cwd, "symbolic-ref", "--short", "-q", "HEAD"],
            capture_output=True, text=True, timeout=3, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return done.stdout.strip() if done.returncode == 0 else ""


def check_git_push(a: Analysis) -> None:
    for seg in a.segments:
        av = argv(seg)
        if not av or av[0] != "git":
            continue
        i, workdir = 1, a.cwd
        while i < len(av) and av[i].startswith("-"):
            if av[i] in GIT_OPTS_WITH_VALUE and i + 1 < len(av):
                if av[i] == "-C":
                    workdir = os.path.join(a.cwd or ".", os.path.expanduser(av[i + 1]))
                i += 2
            else:
                i += 1
        if i >= len(av) or av[i] != "push":
            continue
        check_push_args(av[i + 1 :], workdir)


def check_push_args(args: list[str], workdir: str) -> None:
    force = delete = everything = False
    positionals: list[str] = []
    skip = False
    for j, tok in enumerate(args):
        if skip:
            skip = False
            continue
        if tok in PUSH_OPTS_WITH_VALUE:
            skip = True
        elif tok == "--force" or tok.startswith("--force-with-lease") or tok == "--force-if-includes":
            force = True
        elif tok in ("--delete",):
            delete = True
        elif tok in ("--all", "--branches", "--mirror"):
            everything = True
            force = force or tok == "--mirror"
        elif tok == "--":
            positionals.extend(args[j + 1 :])
            break
        elif re.fullmatch(r"-[A-Za-z]+", tok):
            force = force or "f" in tok
            delete = delete or "d" in tok
        elif not tok.startswith("-"):
            positionals.append(tok)
    refspecs = positionals[1:]
    targets: list[str] = []
    for spec in refspecs:
        if spec.startswith("+"):
            force = True
            spec = spec[1:]
        if spec.startswith(":"):
            delete = True
        dst = spec.split(":", 1)[1] if ":" in spec else spec
        targets.append(re.sub(r"^refs/heads/", "", dst))
    if not (force or delete):
        return
    what = "deleting" if delete and not force else "force-pushing"
    if everything:
        raise Blocked(f"{what} every branch, which includes main/master.")
    if not targets:
        targets = ["HEAD"]
    for t in targets:
        if t in PROTECTED_BRANCHES:
            raise Blocked(f"{what} to {t}.")
        if "$" in t or "`" in t:
            raise Blocked(f"{what} to a branch that cannot be resolved ({t}).")
        if t in ("HEAD", "@", ""):
            branch = current_branch(workdir)
            if branch in PROTECTED_BRANCHES:
                raise Blocked(f"{what} the checked-out {branch} branch.")


def check_rm(a: Analysis) -> None:
    home = os.path.expanduser("~").rstrip("/")
    danger = {"/", "/*", "~", "~/", "~/*", "$HOME", "$HOME/", "$HOME/*", "${HOME}",
              "${HOME}/", "${HOME}/*", home, home + "/", home + "/*"}
    for seg in a.segments:
        av = argv(seg)
        if not av or av[0] != "rm":
            continue
        flags = [t for t in av[1:] if t.startswith("-")]
        recursive = any(
            t in ("--recursive",) or (re.fullmatch(r"-[A-Za-z]+", t) and ("r" in t or "R" in t))
            for t in flags
        )
        if recursive and any(t in danger for t in av[1:] if not t.startswith("-")):
            raise Blocked("recursive rm of / or the home directory.")


KUBE_WORKLOADS = re.compile(
    r"^(deploy(ment)?s?|sts|statefulsets?|ds|daemonsets?|pvc|persistentvolumeclaims?"
    r"|pv|persistentvolumes?|svc|services?|jobs?|cronjobs?|cj)(\.[\w.]+)?(/.*)?$",
    re.I,
)


def check_kubectl(a: Analysis) -> None:
    for seg in a.segments:
        av = argv(seg)
        if not av or av[0] != "kubectl" or "delete" not in av:
            continue
        rest = av[av.index("delete") + 1 :]
        kinds = [k for t in rest if not t.startswith("-") for k in t.split(",")]
        if any(re.fullmatch(r"(ns|namespaces?)(/.*)?", k, re.I) for k in kinds):
            raise Blocked("kubectl delete of a namespace.")
        prod = re.search(r"prod", seg, re.I)
        if prod and ("--all" in rest or any(KUBE_WORKLOADS.match(k) for k in kinds)
                     or "-f" in rest or "-k" in rest):
            raise Blocked("kubectl delete of a production workload.")


def analyse(command: str, cwd: str) -> str:
    a = Analysis(cwd)
    a.add(command)
    try:
        for check in (check_sql, check_fly, check_git_push, check_rm, check_kubectl):
            check(a)
    except Blocked as b:
        return str(b)
    return ""


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
        command = (payload.get("tool_input") or {}).get("command") or ""
        cwd = payload.get("cwd") or ""
        reason = analyse(command, cwd) if command else ""
    except Exception:  # noqa: BLE001 - a guard bug must not wedge the session
        return 0
    if not reason:
        return 0
    print(f"BLOCKED by guardrails: {reason}", file=sys.stderr)
    print(
        "This is a destructive/irreversible operation. If it is truly intended, run it "
        "yourself outside Claude Code.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
