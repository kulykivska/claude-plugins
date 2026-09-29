# Implementation plan template

Written in stage E, only after the owner approved the design. Store it where
the project keeps plans (its docs folder or its task tracker, by that
project's rules).

```markdown
# Redesign implementation plan: <product>

Approved design: <link to the design system> and <link to the screens>
Approved on: <date>, by <owner>
Feature flag: <flag name and rollout policy, or "none: project has no flag system">

## Phase 1: tokens (no visual change)
- Web: CSS custom properties for colour (light, dark, increased contrast),
  type ramp, spacing, radius, motion (delight-spec springs), in <path>.
- iOS: colour assets, a `Motion` enum, type styles mapped to Dynamic Type,
  a haptics helper, in <path>.
- Done when: tokens exist, old screens unchanged, tests green.

## Phase 2: shared components
| Component | States | Platforms | Replaces | Events |
|-----------|--------|-----------|----------|--------|
| PrimaryButton | default, pressed, disabled, loading | web, iOS | <old component> | none (screens own events) |
| ProGate | preview, blurred, locked, purchasing, error | web, iOS | ad-hoc gate checks | paywall_view, paywall_cta_tap |
| EmptyState | first-use, cleared, offline | web, iOS | <old> | none |

- Done when: every component has all states, a preview, reduced-motion
  behaviour, and accessibility labels.

## Phase 3: screens (behind the flag)
Order by traffic or revenue:
1. <screen>: components used, states, behaviour events (entry, success,
   failure, drop-out), QA states to check, rollback = flag off.
2. ...

## Rollout
- Internal, then a percentage, then everyone, per the project's policy.
- Metrics to watch per step: the conversion and retention metrics from
  stage D, crash-free rate, frame hitches on the key screens.
- Removal of old screens and the flag: a separate task after full rollout.

## Hand-off
Each phase and each screen becomes one task in the project's normal
lifecycle (plan, implement, QA, review, pre-push gate). Nothing merges
without passing that gate.

## Open questions and loose ends
- <assets, decisions, screens not designed yet>
```
