---
name: android-coding
description: >-
  How to write correct Android code in Kotlin and Jetpack Compose (Clean Architecture,
  MVI): layering, coroutines, failure handling, recomposition and security while
  implementing, plus the Gradle and test traps. Use when writing or changing an
  Android screen, view model, repository or push / call code.
---

# Android coding guide

Read **`engineering-standards`** first; `android-reviewer` marks against it. Then the
repo's own rules (`CLAUDE.md`, `AGENTS.md`) and a sibling feature to copy.

## While writing
- **Layers.** Domain models, repository interfaces and use cases in the domain
  module; implementations in data; screens in feature modules. No feature reaching
  into another's internals.
- **MVI.** Screen, ViewModel, State, Action, Effect. State as `StateFlow`, one-off
  effects through a `Channel`; no business logic in a composable.
- **Coroutines.** `viewModelScope`, the right dispatcher, nothing blocking on Main;
  collect with `collectAsStateWithLifecycle` or the repo's lifecycle-aware helper.
- **Failure handling.** `Result` / `runCatching` at boundaries; no empty `onFailure`;
  every failure gets an effect or a log.
- **Compose.** Stable state, keys on lazy lists, `remember` for work, no allocation
  in a hot recomposition path.
- **Security.** No keys in code; secrets in the Keystore or encrypted storage; no
  logging in release builds.
- **Optional system features** (telephony, camera, sensors) are guarded with
  `hasSystemFeature` and a `catch`, at every entry point.
- **Stored data.** A changed DataStore or database shape needs a migration or a
  tolerated default; users upgrade in place and must keep their session.
- **Accessibility:** the `mobile-accessibility` skill.

## Traps
- A `stateIn(WhileSubscribed)` state does not start until collected: a test that
  reads `state.value` with no collector asserts the initial state and passes
  vacuously. Launch a collector, `advanceUntilIdle()`, then assert.
- Flavors usually live only in `:app`; library modules test with `testDebugUnitTest`.
- `detekt` / `ktlint` with auto-correct rewrites files you never touched: check
  `git status` afterwards and restore what is not yours.
- Set `ANDROID_HOME` inline rather than committing `local.properties`.
- The emulator ignores the host's `/etc/hosts`: to test a network error, point the dev
  base URL at an unresolvable host temporarily, then revert.

## Before done
Lint, build and tests green, the `mobile-accessibility` pass, then `android-reviewer`
on the diff and `task-review`.
