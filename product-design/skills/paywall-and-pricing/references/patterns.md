# Paywall and pricing patterns

Worked examples for the `paywall-and-pricing` skill. Numbers are
illustrative; use the product's real prices and compute every saving from
them.

## Gate patterns

### Partial preview (default)

Free users see the first rows, Pro sees all of it. The cut is marked by a
fade and an inline card, not by a modal.

```
 1  VER  Red Bull     38%
 2  NOR  McLaren      24%
 3  LEC  Ferrari      13%
 ------------ fade -------------
 [ See all 20 drivers with Pro ]
   Full order for every session, alerts before lights out.
```

Why it works: the user sees the product is real and how deep it goes.

### Blurred preview

Real layout, real row count, values replaced by bars or blurred. Use when the
list shape itself sells (a 20-row table, a chart with a curve).

Rules: never blur more attractive fake data; keep labels readable so the user
knows what they would get; the blur is decorative, the data is not sent to
the client (a blurred DOM with real numbers is a leak).

### Gated action

The control stays where it would be. On tap, a sheet opens with the context:

```
Get an alert before qualifying
Pro sends one notification 15 minutes before the session, with the
predicted top 3.
[ Start 7-day free trial ]
then $39.99 per year. Cancel any time.
Not now
```

## Upgrade moments for a sports product

| Moment | Surface | Prompt |
|--------|---------|--------|
| Followed driver finished where predicted | Result card | "Your prediction for Norris was right. See the full order next time with Pro." |
| Third race weekend in a row opened | Home, inline card | "Three weekends running. Pro adds qualifying and sprint predictions." |
| Tapped a locked session | Sheet | Context of that session, as above |
| Shared a prediction | After share | Nothing. Let the share be the win. |

Never prompt: on cold launch, during onboarding, when the prediction was
wrong, in the middle of live timing.

## Pricing page anatomy

```
See every session before it happens

  [ Monthly | Annual  2 months free ]

  Free                 Pro                     Team
  $0                   $39.99 per year         $199 per year
                       ($3.33 a month)         up to 10 seats
  Race winner          Full finishing order    Everything in Pro
  Public track record  Qualifying and sprint   Shared workspace
                       Alerts before sessions  CSV export
  [ Current plan ]     [ Start free trial ]    [ Contact us ]
                       7 days free, then
                       $39.99 per year

  Track record: podium right in 14 of 22 races in 2026. See every pick.
  FAQ   Restore purchases   Terms   Privacy
```

- The recommended plan is marked with one label ("Most popular" only if it
  is true; otherwise "Recommended").
- Anchoring: the annual price next to 12 x monthly ("$59.88 billed monthly,
  $39.99 billed yearly") is honest anchoring. An invented "was $99" is not.
- Decoy: a Team tier that real teams buy makes Pro look reasonable and is a
  real product. A "Pro Lite" that nobody should ever pick is a decoy built to
  mislead; do not ship it.

## Copy patterns

Headline formulas:

- Outcome plus moment: "See Sunday's full grid before the lights go out."
- Continuation of what they tapped: "Qualifying predictions are in Pro."

Button labels (the outcome, then the terms under it):

- "Start 7-day free trial" / "then $39.99 per year, cancel any time"
- "Get Pro for $39.99 a year"

Dismiss labels, neutral always: "Not now", "Maybe later", "Close".

Objection lines placed next to the button:

- "Cancel in two taps in Settings."
- "We remind you a day before the trial ends."
- "Your free predictions stay free."

## Trial reminder message

```
Your RaceModel Pro trial ends tomorrow, 2 Oct.
We will charge $39.99 for a year unless you cancel.
Cancel in Settings, Subscriptions, or here: [Manage subscription]
```

## Cancellation flow

- One entry point in Settings, labelled "Cancel subscription".
- At most one screen before the confirmation: optional reason (single tap,
  skippable) and, if relevant, one honest alternative (pause, switch to
  monthly). Then "Cancel subscription" as a normal button, not hidden.
- Confirmation states the date access ends.
- On iOS, send users to the system subscription management page; do not
  build a maze in front of it.

## First A/B tests worth running

1. Partial preview versus blurred preview on the main Pro surface. Metric:
   paywall view to purchase. Guardrail: free 7-day retention.
2. Annual default versus monthly default on the toggle. Metric: revenue per
   paywall view at 30 days (not only conversion). Guardrail: refunds.
3. Upgrade card after a success moment versus no card. Metric: purchases per
   weekly active user. Guardrail: notification opt-outs, session length.
