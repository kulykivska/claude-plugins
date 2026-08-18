# shmoozer-metrics

Telemetry for AI-assisted coding, without touching the codebase.

A `PostToolUse` hook logs every Claude Code edit (Edit / Write / NotebookEdit)
as one JSONL record — repo, branch, file, tool, lines written, timestamp — to
`~/.claude/shmoozer-metrics/ai-edits.jsonl` on the developer's machine. Nothing
is added to the code, commits, or PRs.

The `/ai-code-report` skill aggregates the log per repo and period and, when run
inside a checkout, estimates the AI-assisted share of committed added lines via
`git log --numstat`.

Notes:

- The log is local to each machine; team-wide numbers need each developer's log
  (a central collector can be added later if we want org-level metrics).
- Hook failures never block the session; they land in
  `~/.claude/shmoozer-metrics/hook-errors.log`.
