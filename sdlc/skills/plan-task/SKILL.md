---
name: plan-task
description: >-
  Plan the implementation of a defined task before writing code. Trigger on
  "спланируй", "plan this", or before starting any multi-file change. Produces
  the file-level plan, risks, and verification strategy, grounded in the
  actual code (not assumptions).
---

# Plan task

## Steps

1. **Read before planning**: locate every file the change touches (Grep/Glob),
   read the relevant parts. Never plan against an imagined codebase.
2. **File-level plan**: ordered list of edits, per file, with what changes and
   why. Call out shared contracts that must stay in sync across repos
   (e.g. RaceModel FEATURE_COLS ↔ f1-predictor shared.py).
3. **Risks**: what can regress; which tests / LORO / manual flows gate the
   change. For model changes the gate is multi-season LORO, not noisy
   single-season deltas.
4. **Verification strategy**: exact commands to prove it works end-to-end
   (tests with the project's CI --ignore set, curl of the real endpoint,
   running the app), not just typecheck.
5. Keep the plan proportional: a one-file fix needs three lines, not a
   document.
