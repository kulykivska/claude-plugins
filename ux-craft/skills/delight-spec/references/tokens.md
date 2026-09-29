# Motion tokens in code

The same six springs as the `delight-spec` table, for the web and for
SwiftUI. Change a value here and in the table together; the screens only
ever reference token names.

## The maths

Mass `m = 1`, response `R` (seconds), damping fraction `z`:

```
stiffness k = (2 * pi / R)^2
damping   c = 4 * pi * z / R
```

SwiftUI's newer form uses `duration` and `bounce`: `duration = R` and
`bounce = 1 - z` for springs that overshoot.

The CSS `linear()` curves below are the unit step response of each spring,
sampled at 17 points over the CSS duration. To regenerate one after a change,
use the helper at the end of this file.

## CSS

```css
:root {
  --spring-press-duration: 180ms;
  --spring-press: linear(0, 0.062, 0.2, 0.362, 0.519, 0.655, 0.766, 0.85,
    0.911, 0.953, 0.98, 0.997, 1.006, 1.01, 1.011, 1.01, 1);

  --spring-release-duration: 450ms;
  --spring-release: linear(0, 0.102, 0.324, 0.567, 0.778, 0.932, 1.027,
    1.072, 1.083, 1.074, 1.055, 1.035, 1.017, 1.005, 0.997, 0.994, 1);

  --spring-snap-duration: 300ms;
  --spring-snap: linear(0, 0.088, 0.277, 0.487, 0.675, 0.822, 0.925, 0.989,
    1.023, 1.037, 1.038, 1.032, 1.025, 1.017, 1.01, 1.005, 1);

  --spring-reorder-duration: 320ms;
  --spring-reorder: linear(0, 0.07, 0.225, 0.404, 0.573, 0.715, 0.825,
    0.904, 0.958, 0.991, 1.009, 1.018, 1.02, 1.018, 1.015, 1.012, 1);

  --spring-sheet-duration: 420ms;
  --spring-sheet: linear(0, 0.054, 0.175, 0.319, 0.462, 0.589, 0.696,
    0.782, 0.848, 0.898, 0.934, 0.96, 0.977, 0.988, 0.995, 0.999, 1);

  --spring-celebrate-duration: 900ms;
  --spring-celebrate: linear(0, 0.163, 0.495, 0.818, 1.042, 1.147, 1.159,
    1.119, 1.062, 1.014, 0.985, 0.974, 0.976, 0.984, 0.993, 1, 1);

  --press-scale-button: 0.96;
  --press-scale-card: 0.98;
  --stagger-step: 40ms;
  --stagger-max: 300ms;
}

/* Browsers without linear(): close cubic approximations. */
@supports not (transition-timing-function: linear(0, 1)) {
  :root {
    --spring-press: cubic-bezier(0.25, 0.9, 0.3, 1);
    --spring-release: cubic-bezier(0.3, 1.35, 0.5, 1);
    --spring-snap: cubic-bezier(0.3, 1.2, 0.5, 1);
    --spring-reorder: cubic-bezier(0.3, 1.1, 0.5, 1);
    --spring-sheet: cubic-bezier(0.25, 0.9, 0.3, 1);
    --spring-celebrate: cubic-bezier(0.3, 1.6, 0.5, 1);
  }
}

.button {
  transition: transform var(--spring-release-duration) var(--spring-release);
}
.button:active {
  transform: scale(var(--press-scale-button));
  transition: transform var(--spring-press-duration) var(--spring-press);
}

.sheet {
  transition: transform var(--spring-sheet-duration) var(--spring-sheet);
}

@media (prefers-reduced-motion: reduce) {
  :root {
    --spring-press: ease-out;
    --spring-release: ease-out;
    --spring-snap: ease-out;
    --spring-reorder: ease-out;
    --spring-sheet: ease-out;
    --spring-celebrate: ease-out;
    --spring-release-duration: 180ms;
    --spring-sheet-duration: 200ms;
    --spring-celebrate-duration: 200ms;
    --press-scale-button: 1;
    --press-scale-card: 1;
  }
  .idle-motion { animation: none; }
}
```

CSS transitions cannot carry the finger's velocity. For drags, sheets and
toggles on the web, run the spring in JavaScript (a small spring integrator,
or the platform's Web Animations API with a spring library already in the
project) and keep CSS tokens for taps and state changes.

## SwiftUI

```swift
import SwiftUI

enum Motion {
    static let press     = Animation.spring(response: 0.18, dampingFraction: 0.82)
    static let release   = Animation.spring(response: 0.35, dampingFraction: 0.62)
    static let snap      = Animation.spring(response: 0.25, dampingFraction: 0.72)
    static let reorder   = Animation.spring(response: 0.30, dampingFraction: 0.78)
    static let sheet     = Animation.spring(response: 0.45, dampingFraction: 0.88)
    static let celebrate = Animation.spring(response: 0.55, dampingFraction: 0.50)

    static let staggerStep = 0.04
    static let staggerMax = 0.30

    /// Reduced motion: no overshoot, short fades.
    static func resolved(_ animation: Animation, reduceMotion: Bool) -> Animation {
        reduceMotion ? .easeOut(duration: 0.18) : animation
    }
}

struct PressableStyle: ButtonStyle {
    var scale: CGFloat = 0.96
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .scaleEffect(configuration.isPressed && !reduceMotion ? scale : 1)
            .animation(
                configuration.isPressed ? Motion.press
                    : Motion.resolved(Motion.release, reduceMotion: reduceMotion),
                value: configuration.isPressed
            )
    }
}
```

iOS 17 and later can write the same springs as
`.spring(duration: 0.35, bounce: 0.38)` (release) and so on, with
`bounce = 1 - dampingFraction`.

### Velocity projection for toggles, sheets and carousels

```swift
/// Where a flick would come to rest, from the gesture's velocity in pt/s.
func project(_ position: CGFloat, velocity: CGFloat,
             decelerationRate r: CGFloat = 0.998) -> CGFloat {
    position + (velocity / 1000) * r / (1 - r)
}
```

Pick the nearest detent to `project(...)`, then animate there with `snap` or
`sheet`, passing the gesture's velocity so the motion continues without a
jolt.

### Rubber-band

```swift
func rubberBand(_ overshoot: CGFloat, dimension d: CGFloat,
                coefficient c: CGFloat = 0.55) -> CGFloat {
    (1 - 1 / (overshoot * c / d + 1)) * d
}
```

## Helper: regenerate a CSS linear() curve

```js
// Unit step response of a mass-1 spring, sampled for CSS linear().
function springLinear(response, dampingFraction, durationS, samples = 16) {
  const w = (2 * Math.PI) / response;
  const z = dampingFraction;
  const x = (t) => {
    if (z >= 1) return 1 - Math.exp(-w * t) * (1 + w * t);
    const wd = w * Math.sqrt(1 - z * z);
    return 1 - Math.exp(-z * w * t) *
      (Math.cos(wd * t) + (z * w / wd) * Math.sin(wd * t));
  };
  const pts = Array.from({ length: samples + 1 }, (_, i) =>
    i === samples ? 1 : +x((durationS * i) / samples).toFixed(3));
  return `linear(${pts.join(", ")})`;
}
// springLinear(0.35, 0.62, 0.45) gives the release curve above.
```
