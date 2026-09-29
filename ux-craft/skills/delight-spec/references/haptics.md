# Haptics and sound

The full mapping behind section 7 of `delight-spec`, with UIKit and SwiftUI
forms. One moment, one haptic: if two moments feel the same to the finger,
they should mean the same thing.

## Vocabulary

| Kind | UIKit | SwiftUI (iOS 17+) | Feels like |
|------|-------|-------------------|------------|
| Light impact | `UIImpactFeedbackGenerator(style: .light)` | `.sensoryFeedback(.impact(weight: .light), trigger:)` | A small tap |
| Medium impact | `style: .medium` | `.impact(weight: .medium)` | Lifting an object |
| Heavy impact | `style: .heavy` | `.impact(weight: .heavy)` | Rarely right; reserve for large collisions |
| Soft impact | `style: .soft` | `.impact(flexibility: .soft)` | Landing on a cushion (sheet detents) |
| Rigid impact | `style: .rigid` | `.impact(flexibility: .rigid)` | A click into a slot (drop into place) |
| Selection | `UISelectionFeedbackGenerator` | `.sensoryFeedback(.selection, trigger:)` | A detent tick |
| Success | `UINotificationFeedbackGenerator` `.success` | `.sensoryFeedback(.success, trigger:)` | Two quick taps, rising |
| Warning | `.warning` | `.sensoryFeedback(.warning, trigger:)` | Hesitation |
| Error | `.error` | `.sensoryFeedback(.error, trigger:)` | Three sharp taps |

`impactOccurred(intensity:)` takes 0 to 1 for finer control; 0.6 to 0.8 is
usually right for drops.

## Mapping by moment

| Moment | Haptic | Visual it pairs with | Throttle |
|--------|--------|----------------------|----------|
| Press on a primary custom button | light impact on touch-down | scale to 0.96 with `press` | none |
| Long-press menu opens | system (context menus already do it) | system | none |
| Drag pick-up | medium impact | lift: scale 1.03, shadow grows, `release` | once per drag |
| Neighbour moves aside while reordering | selection | `reorder` | 1 per 50 ms |
| Drop | rigid impact at 0.7 | settle with `snap` | once |
| Sheet settles at a detent | soft impact | `sheet` | once per settle |
| Slider crosses a detent | selection | thumb magnetises with `snap` | 1 per 50 ms |
| Custom toggle flips | light impact | thumb with `snap` | none |
| Pull-to-refresh threshold | system refresh control does it | system | none |
| Prediction came true, purchase done | success | `celebrate` reveal | once per event |
| Form cannot be submitted yet | warning | field highlight | once per attempt |
| Action failed | error | horizontal shake, 3 cycles, 6 pt | once per failure |

## SwiftUI example

```swift
struct FollowButton: View {
    @Binding var isFollowing: Bool

    var body: some View {
        Button(isFollowing ? "Following" : "Follow") { isFollowing.toggle() }
            .buttonStyle(PressableStyle())
            .sensoryFeedback(.impact(weight: .light), trigger: isFollowing)
            .accessibilityLabel(isFollowing ? "Unfollow driver" : "Follow driver")
    }
}
```

For UIKit, keep one generator per gesture, call `prepare()` when the gesture
begins, and release it when the gesture ends.

## Rules

- Never a haptic without a visual; never a haptic on every scroll frame.
- Do not add haptics to system controls that already emit them (`Toggle`,
  wheel pickers, context menus, pull-to-refresh). Check on a device before
  adding one to any other system control.
- The system "System Haptics" setting is respected by the generators; do not
  add an in-app override that ignores it.
- Haptics stay on under reduced motion.

## Web fallback

- `navigator.vibrate` works on Android browsers and is absent in iOS Safari;
  feature-detect and treat it as a bonus, never as the feedback.
- Patterns: selection 5 ms, impact 10 to 15 ms, success `[10, 40, 10]`. No
  vibration for warning or error on the web; use the visual.
- Only after a user gesture, and behind the same in-app setting as sound.

## Sound (optional, off by default)

- A settings toggle, default off. First enable plays a sample.
- Sounds under 200 ms, peak well below system alert volume, no music.
- iOS: ambient audio session category, so the silent switch mutes it and
  the user's music keeps playing.
- Never on repeated actions (scrolling, typing), never the only feedback,
  and never during a call or screen recording.
