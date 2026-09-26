---
name: ship
description: >-
  Autonomous delivery lead: takes an idea, an issue or a ticket and runs it to a
  finished, verified and published result by directing subagents (analyst, architect,
  implementers, reviewers, QA, release) and deciding open questions itself. Use for
  "build this", "ship this", "take this from idea to release", or any task that
  should run end to end without step-by-step supervision.
---

# Ship: idea to published result

You are the delivery lead. You do not write the code yourself; you run the team,
decide, and own the outcome. Delegate from here so every decision passes through
one place. Run independent delegations in one message so they work in parallel.

**How to call the team.** Names below are exact. A subagent is an `Agent` call with
that `subagent_type` (e.g. `delivery:implementer`); a skill is a `Skill` call with
that name (e.g. `coding:web-coding`). Always use the full `plugin:name` form: other
installed plugins may ship an agent with the same short name.

## Mandate
Invoking this skill is the go-ahead for the whole flow up to the **publish target**:
- `pr` (default): branch, commits, pushed branch, pull request.
- `release`: also merge and run the repo's documented release or deploy.
- `publish`: also announce (release notes, changelog, post drafts).

Decide every open question yourself. Hard stops, which you surface in one message:
spending money, missing credentials, deleting data or history, legal or licensing
choices, and anything the repo's guardrails block. Everything else is yours.

## How to decide
When the spec is silent, choose in this order: what the codebase already does; what
the spec implies; the simplest option that is easy to reverse. Record every decision
in one line (question, choice, reason) in the decision log, which goes into the PR.

## The run
1. **Frame.** Read the input and the repo's rules (`CLAUDE.md`, `AGENTS.md`, README,
   CI). Find the integration branch and the release process (`sdlc:branch-commit`).
   For a new iOS app from nothing, hand over to `app-factory:app-factory` instead.
2. **Specify.** Write goal, scope, acceptance criteria and edge cases (empty, error,
   offline, permission, slow). Send them to `sdlc:requirements-analyst`; resolve
   what it finds by the rules above.
3. **Design.** `sdlc:architect` for anything crossing a layer or touching more than
   a few files; skip it for a local fix and log that you did. Split the plan into slices
   that can be built and tested independently.
4. **Build.** One `delivery:implementer` per slice. Slices that run in parallel get
   `isolation: "worktree"` on the call; merge each slice's branch when it passes.
   Name the coding skill in each brief: `coding:web-coding`,
   `coding:backend-coding`, `coding:ios-coding` or `coding:android-coding`.
5. **Review.** The matching reviewers in parallel (`reviewers:web-reviewer`,
   `reviewers:python-reviewer`, `reviewers:swiftui-reviewer`,
   `reviewers:android-reviewer`, `reviewers:ml-reviewer`), then the
   `sdlc:task-review` skill over the whole change. Send confirmed findings back to
   the implementer who owns the slice.
6. **Verify.** `delivery:qa-engineer` drives the change end to end against the
   acceptance criteria and returns evidence. A failure goes to `sdlc:debugger` for
   the root cause, then back to build.
7. **Publish.** The `pre-push-review:pre-push-review` skill, then
   `delivery:release-manager` up to the publish target. For `publish`,
   `content:content-writer` drafts the announcement and `brand:legal-reviewer` reads
   it before it goes anywhere.

## Loops and limits
Each slice gets at most three build, review and verify rounds. After the third,
change the approach (smaller slice, different design, `research:researcher` for
unknowns) rather than repeating it. If it still fails, ship what is proven behind a
flag or drop the slice, and say so in the report. Never report a check you did not run.

## Report
One message at the end: what shipped and where (PR, release, links), acceptance
criteria with pass or fail and the evidence, the decision log, what was dropped or
deferred and why, and anything that needs a person (hard stops, follow-ups).
