---
name: branch-commit
description: >-
  Start work on a correctly based branch and commit it cleanly: branch off the
  freshly fetched integration branch, carry the tracker id, one-line conventional
  commits, no AI attribution, never push without permission. Use when beginning a
  feature or fix, creating a branch, or writing a commit.
---

# Branch and commit

## Branch
Find the integration branch before branching; it is not always `main`. Read the
repo's docs and CI: many mobile repos integrate into `qa` or `develop`, and a merge
there may already be a release (TestFlight, internal track, staging). Then:

```bash
git fetch origin
git switch -c <type>/<tracker-id>-<short-topic> origin/<integration-branch>
```

Types: `feat`, `fix`, `chore`, `refactor`, `docs`. Put the tracker id in the name when
the work has one; use a descriptive slug when it has none, never an invented id.
Never branch off a local copy of the integration branch, which drifts.

If other sessions or people share the working tree, check `git status` and
`git branch --show-current` before switching, and prefer a worktree.

## Commit
- One short conventional subject, with the tracker id when there is one:
  `fix(auth): refresh the token once per expiry (ABC-123)`. No body unless asked.
- No "Generated with", no `Co-Authored-By` for an AI, no names or job titles.
- `git add` named files, never `git add .`; check for files an auto-formatter
  rewrote that are not yours.
- Let the pre-commit hooks run; do not `--no-verify`.

## Push
Never push or open a pull request without explicit permission for that action; an
approved plan is not permission to push. Starting a `ship` run counts as that
permission, up to the publish target it was given. When permitted,
`pre-push-review` runs first. Some trackers only move a task when a PR merges into a particular branch: if
yours does not fire for this branch, offer the status change by hand.
