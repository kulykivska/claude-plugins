---
name: ios-coding
description: >-
  How to write correct iOS code in Swift and SwiftUI: Observation, structured
  concurrency, failure handling, memory and security while implementing, plus the
  Xcode and test traps that waste an afternoon. Use when writing or changing an iOS
  screen, view model, service or push / call code.
---

# iOS coding guide

Read **`engineering-standards`** first; `swiftui-reviewer` marks against it. Then the
repo's own rules (`CLAUDE.md`, `AGENTS.md`) and a sibling feature to copy.

## While writing
- **Observation.** `@Observable` classes held in `@State` and passed through
  `@Environment`; do not mix in `ObservableObject` / `@Published` where the project
  has moved off them.
- **Concurrency.** `async/await` and `Task`; UI on `@MainActor`; cancel long-lived
  tasks when the view goes away; `[weak self]` in escaping closures.
- **Failure handling.** No empty `catch`, no ignored task error, no silent early
  return on a network or permission failure: the user sees a state or a message.
- **States.** Loading, error with retry, empty, data. Show the error only when the
  list is empty, and clear it in the same step that sets loading, or the empty state
  flashes between the two.
- **No crashes by construction.** No force unwraps or `try!` in app code.
- **Strings** through the String Catalog; **secrets and tokens** in the Keychain.
- **Push and calls** (PushKit / CallKit): report an incoming call before any `await`,
  or the system stops delivering VoIP pushes. Token refresh is single-flight.
- **Accessibility:** the `mobile-accessibility` skill.

## Traps
- A project in a subfolder: run `xcodebuild` where the `.xcodeproj` lives.
- Tests may run only under one scheme: check the test target's `TEST_HOST` against
  each scheme's product name before trusting "Could not find test host". Prove a new
  test compiles with `xcodebuild build-for-testing` first.
- Check `TARGETED_DEVICE_FAMILY` before building an iPad layout.
- A dead host can spin forever: `URLSession`'s resource timeout defaults to seven
  days. To test the error state, make the connection fail fast (a local listener that
  refuses TLS) rather than turning the network off, which usually shows a global
  offline screen instead.
- Keep `project.pbxproj` requoting noise out of commits.

## Before done
Clean build with no warnings, tests green, the `mobile-accessibility` pass, then
`swiftui-reviewer` on the diff and `task-review`.
