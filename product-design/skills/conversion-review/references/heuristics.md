# Conversion heuristics in detail

Each heuristic: what to check, what good looks like, the usual failure, and
the event that proves a fix. RaceModel (an F1 prediction site with a free
tier, a Pro tier and an iOS app) is the running example.

## 1. Value proposition on the first screen

Check at 390x844 (phone) and 1440x900 (laptop). Cover everything below the
fold with your hand; what is left must answer "what is this, for whom, what
next".

- Good: "Know the race result before the lights go out. Predictions for every
  F1 session, with our track record in public." plus one button.
- Failure: a brand slogan ("Data. Speed. Victory."), an abstract hero image,
  a feature list with no outcome.
- Five-second test: show the first screen for five seconds to someone who has
  never seen it, then ask what the product does. If the answer is wrong, the
  headline is wrong.
- Prove it: `landing_view` to `landing_cta_tap` rate; bounce rate on landing
  sessions; time to first tap.

## 2. One primary action per screen

- Exactly one filled, high-contrast button per viewport. Repeat the same
  action further down; never introduce a second, different primary action.
- Navigation links and "Learn more" are secondary styles.
- Failure: "Sign up" and "Download the app" and "Go Pro" as three equal
  buttons in the hero.
- Prove it: share of taps landing on the primary action; conversion to the
  page's goal event.

## 3. Proof

Ranked from strongest to weakest:

1. A public, complete track record the visitor can check (every prediction,
   hits and misses, with dates). Showing the misses is what makes the hits
   believable.
2. Numbers with a date and a definition ("Podium picked correctly in 14 of
   22 races in 2026").
3. Named people and organisations with permission.
4. Press and awards with links.
5. Review counts and ratings from the store.

- Put proof next to the claim it supports, not in a testimonials ghetto at
  the bottom.
- Failure: "the most accurate F1 model", "trusted by thousands", no date, no
  source.
- Prove it: tap-through to the track record page; conversion of visitors who
  saw the proof block versus those who did not (scroll-depth segment).

## 4. Sign-up friction

Count: fields, screens, decisions, and waits (email codes) between the
primary action and the first moment of value.

- Offer Sign in with Apple and Google where the platform allows it.
- Let people see value before the account: the free prediction is visible
  without sign-up; sign-up is asked for when saving, following or alerting.
- Email verification can happen after first use, not before it.
- No password rules revealed only after failure.
- Prove it: `signup_start`, `signup_step_complete{step}`, `signup_success`,
  `signup_fail{reason}`, `signup_abandon{last_step}`; step-to-step drop.

## 5. Checkout friction

- The price, the billing period and what is included are visible before the
  payment form.
- Mobile uses the native payment sheet (StoreKit in the iOS app, Apple Pay or
  Google Pay on the web). Web checkout keeps the user on a trusted, branded
  page.
- Coupon field collapsed behind a link, so people without a code do not go
  hunting for one.
- Errors are inline, keep entered data, and say what to do.
- Prove it: `checkout_start`, `checkout_success`, `checkout_fail{reason}`,
  `checkout_abandon{step}`; payment failure rate by method.

## 6. Trust

- Who runs it (a real about page), how to contact, how to cancel (one
  sentence and a link), refund policy, privacy in plain words.
- Hygiene that silently costs trust: broken images, placeholder copy, a stale
  year in the footer, mixed-content warnings, prices that differ between the
  page and the checkout.
- Prove it: support tickets tagged "is this legit" or "how do I cancel";
  checkout abandonment at the payment step.

## 7. Pricing clarity

- Free versus Pro in one comparison, outcomes rather than feature names.
- The number charged, not only a per-month equivalent of an annual price.
- Taxes and currency stated for the visitor's region.
- Full rules in the `paywall-and-pricing` skill.

## 8. Mobile

- Primary action in the thumb zone or sticky at the bottom after the hero
  scrolls away (not both a sticky bar and a popup).
- Targets at least 44x44 pt, 8 pt apart.
- No horizontal scroll at 320 px; tables scroll inside their own container.
- Body text at least 16 px on the web so iOS does not zoom inputs.
- Core Web Vitals: LCP under 2.5 s, INP under 200 ms, CLS under 0.1.

## 9. Speed and stability

- Render the first screen without waiting on client JavaScript where
  possible; reserve space for images and embeds to avoid layout shift.
- Skeletons shaped like the content, not a centered spinner.
- Prove it: field Web Vitals by page; conversion by LCP bucket.

## 10. Copy on the conversion path

- Buttons name the outcome: "Get Sunday's prediction" beats "Submit".
- No internal jargon ("MAE", "LORO", "ensemble") on pages for newcomers. The
  `ux-copy` skill has the replacements.
- Objections answered where they arise: "Cancel any time in two taps" next to
  the trial button, not in the FAQ only.

## Event naming template

When the project has no taxonomy, use `<surface>_<object>_<verb>` in
snake_case with properties for variants:

- `landing_view{variant, audience, referrer}`
- `landing_cta_tap{position, label}`
- `pricing_view{source}`
- `plan_select{plan, period}`
- `checkout_start{plan, period, method}`
- `checkout_success{plan, period, trial}`
- `checkout_fail{reason}`
- `checkout_abandon{step}`

Tracking calls never block or break the flow they measure.
