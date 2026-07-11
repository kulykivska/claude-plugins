---
name: pre-push-review
description: >-
  Comprehensive pre-push review that FIXES issues before pushing — covering code
  smells, architectural patterns, security, scalability, and performance. MUST
  run BEFORE any `git push`, for EVERY project on EVERY branch. Reviews the
  diff to be pushed, fixes the findings, re-verifies, and only then pushes
  clean code.
  Trigger on "проверь перед пушем", "запусти проверку перед пушем", "review
  before push", "pre-push review", the PRE-PUSH POLICY gate message, or
  proactively whenever about to run `git push` / the user asks to push.
---

# Pre-Push Review (fix-and-verify)

A gated review run against the commits about to be pushed. It does not just
report — it **fixes** the findings so the pushed code is free of code smells and
of security / scalability / performance problems.

## Step 1 — Decide whether the gate applies

```bash
git rev-parse --show-toplevel 2>/dev/null || { echo "not a git repo"; exit 0; }
```

The gate applies to EVERY project on EVERY branch. Only skip when there is
nothing to review (not a git repo, or an empty push diff in Step 2).

## Step 2 — Collect the diff to review

Review exactly what will be pushed:

```bash
git diff @{upstream}..HEAD              # if an upstream exists
git diff origin/main...HEAD 2>/dev/null || git diff main...HEAD   # new branch fallback
git diff --name-only <same range>       # scope to changed files
```

If the diff is empty, report "нечего проверять" and allow the push.

## Step 3 — Review across all five dimensions

Go through every changed hunk and find real issues (with `file:line`):

1. **Code smells & maintainability** — duplication, dead code, long/complex
   functions, deep nesting, magic numbers, unclear names, missing error
   handling, leaky abstractions, leftover TODO/FIXME/debug.
   - **Exhaustive failure handling (always):** every failure mode must be
     handled deliberately, per best practices — never silently swallowed. Flag
     any early-return / empty-catch / disabled-feature / falsy-response /
     `Promise.allSettled` rejection / external-call error that exits without a
     log, metric, or caller-visible signal. A "nothing happened" path that an
     operator can't see in logs and a user can't see in the UI is a bug, even
     when the types compile. Prefer: log at the right level (warn/error for
     unexpected, debug for benign), and surface terminal failures to the caller
     instead of leaving them hanging.
2. **Architectural patterns** — layer/boundary violations, wrong responsibility
   placement, tight coupling, circular deps, God objects, business logic in the
   wrong layer, breaking the project's established patterns.
3. **Security** — injection (SQL/command/path), unsanitized input, hardcoded
   secrets/tokens/keys, broken authn/authz, unsafe deserialization, sensitive
   data in logs, missing TLS/cert validation, over-broad permissions, CORS/CSRF.
4. **Scalability** — N+1 queries, unbounded loops/collections, missing
   pagination, in-memory growth with input, blocking calls on hot paths,
   non-idempotency, shared mutable state, lock contention.
5. **Performance** — needless allocations, O(n²) where O(n) is possible,
   repeated work that should be cached/memoized, sync I/O that should be async,
   chatty network calls, large payloads, missing indexes.

For large diffs, fan the five dimensions out as parallel subagents (one lens
each), then merge and dedup. For small diffs, do it inline. You may corroborate
with `/code-review` and `/security-review`, but this skill owns all five
dimensions and the fixing.

## Step 4 — FIX the findings (this is the point of the skill)

For every confirmed finding, apply the fix in the working tree:

- **Auto-fix** anything concrete and behavior-preserving: code smells,
  injection/secret/logging security holes, N+1 / unbounded / blocking
  scalability issues, obvious performance fixes (caching, async, algorithmic).
- **Escalate to the user first** only when a fix would meaningfully change
  behavior, public API, or architecture, or when intent is ambiguous — explain
  the tradeoff and let them choose. Default to fixing; ask only when genuinely
  unsure.
- Keep each fix minimal and matched to the surrounding code style.

After fixing, **re-verify**: re-read the changed hunks (and re-run the relevant
dimension checks / build / tests / linters if the project has them) to confirm
the issue is actually resolved and nothing regressed. Loop fix → re-verify until
no blocking findings remain.

Then fold the fixes into the push: either `git commit --amend` (if fixing your
last commit is appropriate) or add a new commit (e.g. `fix: address pre-push
review findings`). The push must contain the cleaned code, not a follow-up.

## Step 5 — Verdict and push

Show a short summary: what was found, what was fixed, and anything escalated.

- **🟢 Clean** — no blocking findings remain. Proceed to push.
- **🟠 Needs a decision** — an escalated item is waiting on the user. Stop and ask.

When clean and the user is ready to push, record the one-shot approval marker for
the **current** HEAD (the gate consumes it to let this exact commit through),
then push:

```bash
echo "$(git rev-parse HEAD)" > "$(git rev-parse --git-dir)/PREPUSH_REVIEW_OK"
git push        # the pre-push-gate hook sees the marker and allows it once
```

If you committed fixes in Step 4, HEAD changed — write the marker AFTER the final
commit so its sha matches.

## Notes

- Scope strictly to the push diff and code it touches; don't refactor unrelated
  pre-existing code.
- Match severity to real impact — a style nit is not a blocker, but still fix
  cheap nits while you're there.
- Never push silently when an escalated decision is pending.
