# workspace

Plumbing for Claude itself rather than for a codebase.

## gmail-sorter-setup

Creates a daily cloud routine that triages the Gmail inbox of whichever
claude.ai account the session is logged in as, into Attention / Health /
Receipts, and flags obvious junk. It creates the routine and stops there; it
never triages the inbox itself. Labels are created on the routine's first run.

Requires the Gmail connector on the target account. The connector UUID differs
per account, so the skill reads it live and never reuses a remembered one.

## /switch

Hands the current session to another claude.ai profile and continues the same
conversation there. It shells out to a local `claude-switch` wrapper around
`claude-as`, which is machine-local and not part of this repo. Without that
wrapper on PATH the command is a no-op, so take this one only if you already
run multiple profiles.
