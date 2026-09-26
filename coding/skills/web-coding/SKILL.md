---
name: web-coding
description: >-
  How to write correct web frontend code (React, TypeScript, Vite-style SPAs): follow
  the repo's conventions and apply failure handling, performance, security and
  accessibility while implementing. Use when writing or changing a web page,
  component, hook or client-side data flow.
---

# Web coding guide

Read **`engineering-standards`** first; it is the list the `web-reviewer` marks
against. Then read the repo's own rules (`CLAUDE.md`, `AGENTS.md`, `README`) and copy
the shape of a sibling feature before inventing one.

## While writing
- **Types.** No `any` and no non-null `!` to silence the compiler; model the states
  a value really has. Run the same type check CI runs (often `tsc -b`, which is
  stricter than the editor).
- **Data.** Use the repo's server-state library (TanStack Query, SWR, RTK Query) for
  anything fetched; keep only UI state in local or global stores. Keys are stable
  and include every input the request depends on.
- **Every request has four states:** loading, error with a retry, empty, data. Show
  the error only when there is nothing to show instead, so a failed refresh does not
  wipe a list the user is reading.
- **Failure handling.** No empty `catch`, no floating promise. A user-facing failure
  gets a visible message; an unexpected one also gets logged or reported.
- **Forms.** Validate with the same schema the API uses where one is shared; disable
  double submit; keep what the user typed on error.
- **Security.** Never render untrusted HTML without sanitising; no secrets in client
  code or `VITE_*`-style public env vars; tokens in the storage the repo already uses.
- **Performance.** Split routes, avoid effects that fetch in a loop, memoise only what
  profiling shows is hot, size images.
- **Accessibility.** Semantic elements (`button`, `a`, `label`), visible focus,
  keyboard reachability, text alternatives for meaningful images, no colour-only
  state. Check at 320px width and at 200% zoom.
- **Text.** No hardcoded user-facing strings where the repo has i18n.

## Before done
Type check, lint and tests green; drive the changed flow in a browser (Playwright if
available) including the error and empty states. Then run `web-reviewer` on the diff
and `task-review`.
