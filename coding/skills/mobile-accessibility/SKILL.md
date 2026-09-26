---
name: mobile-accessibility
description: >-
  Accessibility, keyboard/focus order, screen sizes and orientation for iOS
  (SwiftUI) and Android (Compose) apps: what to write, and how to check it on a
  simulator or emulator. Use when building or changing any mobile screen, dialog or
  sheet, or when reviewing a mobile diff that renders UI.
---

# Mobile accessibility

Anything that renders gets this pass. Write it in, then run the checks: an
accessibility claim with no list of what was checked counts as not checked.

## 1. While writing

- **Labels.** Meaningful icons and images get `contentDescription` /
  `.accessibilityLabel`; decorative ones get `null` / `.accessibilityHidden(true)` on
  purpose.
- **Roles and state.** Android: `Modifier.semantics { role = Role.Button }`,
  `heading()`, `stateDescription`, `mergeDescendants = true` so a card announces once.
  iOS: `.accessibilityAddTraits(.isHeader)`, `.accessibilityValue` on stateful
  controls, `.accessibilityElement(children: .combine)` on composed rows. A styled
  `Box { clickable }` with no role announces nothing.
- **Targets and text.** Touch targets at least 48dp / 44pt; layouts that survive
  200% font scale (no fixed heights around text). Never signal state by colour alone.
- **Focus order.** Every dialog, sheet and multi-field form gets a deliberate order.
  Android: `focusRequester` + `focusProperties`, `focusGroup()`, `imeAction` +
  `KeyboardActions` to chain fields; a `clickable` that is not `focusable` cannot be
  reached without touch. iOS: `@FocusState`, `.defaultFocus`,
  `.accessibilitySortPriority`, `.keyboardShortcut(.cancelAction)` on modals.
  A modal holds focus while it is up and always offers a keyboard way out.
- **Sizes and rotation.** No hardcoded widths or `UIScreen.main.bounds`; adapt on
  `horizontalSizeClass` / `WindowSizeClass`. State that must survive rotation lives in
  the ViewModel or `rememberSaveable`. Check the orientation lock (Android manifest
  `screenOrientation`, iOS `UISupportedInterfaceOrientations`) before calling a
  rotation bug, and `TARGETED_DEVICE_FAMILY` before promising an iPad layout.

## 2. Checking it

**Android (emulator):**
```bash
adb shell settings put system font_scale 2.0           # then back to 1.0
adb shell wm size 720x1280 && adb shell wm density 320  # small phone
adb shell wm size 1600x2560 && adb shell wm density 320 # tablet
adb shell wm size reset && adb shell wm density reset
adb shell settings put system accelerometer_rotation 0
adb shell settings put system user_rotation 1           # landscape; 0 = portrait
adb shell input keyevent KEYCODE_TAB                    # walk focus; ESCAPE closes a dialog
```
Then one TalkBack swipe-through and an Accessibility Scanner run on the changed screen.

**iOS (simulator):**
```bash
xcrun simctl ui booted content-size accessibility-extra-large   # then medium
xcrun simctl list devices available    # pick a small phone, a large phone, an iPad
```
Rotate with Cmd+Left/Right, walk every control with Full Keyboard Access, do one
VoiceOver pass, and run the Accessibility Inspector Audit on the changed screen.

Rotate **while a dialog, sheet, keyboard or load is on screen**: an idle screen
surviving rotation proves little.

## 3. Report

One sentence, filled in: *font scales X and Y; sizes A, B, C; portrait and landscape;
focus walked with TAB/D-pad; TalkBack/VoiceOver pass on screen Z; scanner/Inspector N
findings (M pre-existing).* Name anything skipped and why.

A layout or target-size rule that can be pulled out as a pure function
(`fun columns(widthDp: Int): Int`) gets unit tests at its breakpoints.
