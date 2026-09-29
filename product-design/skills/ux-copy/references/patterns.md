# Microcopy patterns

Before and after examples per state. RaceModel strings are examples; the
structure is what carries over.

## Empty states

Structure: what goes here, why it is empty now, one action.

| Where | Before | After |
|-------|--------|-------|
| Followed drivers | "No data" | "No followed drivers yet. Follow a driver to see their chances first. [Choose drivers]" |
| Predictions, off week | "No predictions available" | "No race this weekend. The next prediction arrives Thursday before Singapore." |
| Search, no results | "0 results" | "No driver or team called 'Hamiltn'. Try 'Hamilton'?" |
| History, new user | (blank) | "Your picks will show up here after your first race weekend." |

First-use empty states can teach; empty states after deleting everything
should not lecture.

## Errors

Structure: what happened, what is safe, what to do.

| Cause | Before | After |
|-------|--------|-------|
| Network | "Error 503" | "We could not reach RaceModel. Check your connection and try again. [Try again]" |
| Server | "Something went wrong" | "Predictions are taking longer than usual to load. We are on it. Your saved picks are safe." |
| Validation | "Invalid input" | "Enter an email like name@example.com." |
| Payment | "Transaction declined" | "Your bank declined the payment. Try another card or contact your bank. You have not been charged." |
| Permission | "Notifications disabled" | "Notifications are off for RaceModel. Turn them on in Settings to get alerts before sessions. [Open Settings]" |
| Offline, cached data | "Offline" | "You are offline. Showing predictions from Saturday 14:02." |

Rules: never blame ("You entered an invalid..."), keep the user's input,
put the technical code in a details line or the log, never in the title.

## Loading

- Under 1 s: no text, a skeleton shaped like the content.
- 1 to 10 s: say what: "Loading qualifying predictions".
- Over 10 s: "This is taking longer than usual." plus [Keep waiting] or a
  way back.
- Long jobs: progress in real units ("Checking 18 of 24 races").

## Success and confirmation

| Before | After |
|--------|-------|
| "Success!" | "Alert set for qualifying, Sat 16:00." |
| "Saved" | "Picks saved. You can change them until lights out." |
| "Subscription activated" | "You are on Pro. Full predictions for Monaco are ready." |

## Destructive actions

```
Delete "Sunday League"?
The league and its picks are removed for all 8 members. This cannot be undone.
[ Delete league ]  [ Cancel ]
```

Button pairs name the action. Put the destructive style on the destructive
button only.

## Labels and buttons

| Before | After |
|--------|-------|
| Submit | Save picks |
| OK | Got it (information) or the specific action |
| MAE: 2.14 | Average error: 2.1 places |
| P(win) 0.337 | 34% chance to win |
| Upgrade | See full predictions |
| Settings > Notifications > Push | Notifications |

## Dates and times

| Distance | Format | Example (viewer in Chicago, 24h locale) |
|----------|--------|------------------------------------------|
| Under an hour | Relative | in 25 minutes |
| Today, tomorrow | Day word and time | Tomorrow, 07:00 |
| Within 6 days | Weekday and time | Sat 16:00 |
| Further, same year | Weekday, date, time | Sun 12 Oct, 15:00 |
| Other year | Full date | 3 Mar 2027 |
| Past, under a day | Relative | 2 hours ago |

Web example:

```js
const time = new Intl.DateTimeFormat(undefined, {
  weekday: "short", hour: "numeric", minute: "2-digit",
}).format(new Date(sessionStartUtc));
const rel = new Intl.RelativeTimeFormat(undefined, { numeric: "auto" });
rel.format(Math.round(minutesUntil), "minute"); // "in 25 minutes"
```

SwiftUI example:

```swift
Text(session.start, format: .dateTime.weekday(.abbreviated).hour().minute())
Text(session.start, style: .relative) // "in 25 min", updates live
```

## Notification text

Title carries the fact, body carries the detail, no teaser-only text.

```
Qualifying in 15 minutes
Predicted top 3: Leclerc, Norris, Verstappen.
```
