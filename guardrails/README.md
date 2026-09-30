# guardrails

Blocking PreToolUse hooks. Exit 2 vetoes the Bash call and tells Claude why.

## guard-destructive-ops

`hooks/guard-destructive-ops.sh` is a thin wrapper around
`hooks/guard_destructive_ops.py`. It reads the whole command, including heredoc
bodies that a shell, `ssh` or a SQL client will execute, and blocks:

| Area | Blocked |
|------|---------|
| Fly.io (`fly`, `flyctl`) | `apps destroy`, `destroy`, `machines destroy`/`rm`, `volumes destroy`/`delete`, `scale count 0`, `secrets unset` |
| SQL through a client (`psql`, `mysql`, `sqlite3`, `fly pg connect`, ...) | `DROP TABLE/DATABASE/SCHEMA/VIEW/INDEX/COLUMN/...`, `TRUNCATE`, `DELETE FROM` without `WHERE`. Case-insensitive. Looks at `-c`, `-e`, here-strings, piped input, heredocs, and the file given to `-f`, `--file=` or `<` |
| `git push` | force in any spelling (`--force`, `-f`, `-uf`, `--force-with-lease`, `+refspec`, `--mirror`) or deletion (`--delete`, `:main`) when the target is `main`/`master`, the checked-out `main`/`master`, every branch, or a `$VARIABLE` it cannot resolve |
| `rm` | recursive removal of `/`, `/*`, `~`, `$HOME` or the home directory path |
| `kubectl delete` | any namespace; deployments, statefulsets, daemonsets, services, jobs, volumes, `-f`/`-k` or `--all` when the command mentions `prod` |

Not blocked on purpose: `git push origin main`, force-pushes to feature
branches, `SELECT`, `DELETE ... WHERE`, and searches such as
`grep -rn 'DROP TABLE' migrations/`. Heredocs written to a file (`cat > f <<EOF`),
commit messages and `python3 - <<EOF` scripts are data, not operations.

Known limits:

- SQL assembled inside a program (Python, Node) is not seen.
- A string literal that contains `drop table` counts as SQL when a client runs in the same command.
- `DELETE FROM` inside a shell heredoc passes if the word `WHERE` appears later in that body.
- The current kube context is not read. A prod workload is recognised only when
  `prod` appears in the command (context, namespace, path or name).
- `cd repo && git push -f` checks the branch of the session directory, not `repo`.
- `git reset --hard` is not guarded: it is local and recoverable from the reflog.
- If `python3` is missing or the parser fails, the hook allows the call.

Tests: `python3 scripts/test_guardrails.py`.
