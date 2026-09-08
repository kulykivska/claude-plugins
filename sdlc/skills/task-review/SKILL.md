---
name: task-review
description: >-
  Task-scoped review after implementing: regressions, bugs, and smells on the
  touched files only. Trigger on "проверь задачу", "review the task", or after
  finishing a multi-file change before commit. Complements pre-push-review
  (which gates the push); this one runs right after implementation.
---

# Task review

Review exactly what this task changed, nothing else.

## Steps

1. Scope: `git diff` (unstaged + staged) or the task's commit range. List the
   touched files.
2. For every hunk check:
   - **Regression risk**: callers of changed functions, changed contracts,
     changed defaults. Grep for usages; don't assume.
   - **Bugs**: off-by-one, None/undefined paths, error paths that silently
     swallow failures, race conditions in async code.
   - **Smells**: dead code, leftover debug output, duplication with an
     existing helper, magic numbers.
   - **Behaviour analytics**: a new feature or changed logic with no events is
     a finding. The entry, success, failure and drop-out paths each emit
     something, the names come from the project's taxonomy, and a tracking
     failure cannot break the flow it measures.
   - **Cross-repo sync**: if a shared contract changed (feature columns, API
     shapes), verify the counterpart repo is updated too.
3. Fix what you find (small and safe: just fix; behavior-changing: flag).
4. Run the project's real gate: its test suite with the same flags CI uses.
5. Output: findings with file:line, what was fixed, what remains.
