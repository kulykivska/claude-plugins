# Notification plan template

Fill one table per product. The RaceModel values are an example of a
calendar-driven product; replace them with the product's own moments.

## Types

| Type | Default | Trigger time (user local) | Cap | Example copy |
|------|---------|---------------------------|-----|--------------|
| Weekend preview | On after opt-in | Thursday 18:00 | 1 per weekend | "Monaco this weekend. The model has Leclerc on pole at 31%." |
| Qualifying alert | Off, opt-in from the qualifying screen | 15 min before the session, or 20:00 the evening before if inside quiet hours | 1 per session | "Qualifying in 15 minutes. Predicted top 3: Leclerc, Norris, Verstappen." |
| Race alert | Off, opt-in | 30 min before lights out, same quiet-hours rule | 1 per race | "Lights out in 30 minutes. Leclerc to win at 34%." |
| Result check | On after opt-in | 30 min after the flag, never inside quiet hours (held until 08:00) | 1 per race | "Leclerc won. The model had him first. See how your picks did." |
| Weekly digest (email) | On for email sign-ups | Monday 09:00 | 1 per week, skipped in off weeks with no news | Last result, next race date in the user's time |
| Product news | Off | Never more than monthly | 1 per month | Only for changes the user can use |

Weekend cap: 3 pushes per race weekend in total, whatever types are on.
The server picks the highest-value ones when more are eligible (result check
beats preview when the user followed a driver who won).

## Quiet hours

- Default 22:00 to 08:00 in the device's current time zone; user-editable.
- Held notifications are either delivered at the end of quiet hours (results)
  or moved earlier (alerts for a session that will already have happened by
  08:00 move to 20:00 the evening before).
- Live alerts inside quiet hours only for users who switched on "Live alerts
  at night" explicitly, per race if possible.

## Time zones

- Store the event's start in UTC; compute the send time per user from their
  zone at send time (the user may be travelling to the race).
- Copy says the time in the user's zone with the zone implied: "starts at
  15:00" in their local time, never "15:00 CEST" to a user in Chicago.

## Back-off

| Condition | Effect |
|-----------|--------|
| 3 consecutive unopened | Halve eligible sends (keep only the top-ranked type) |
| 6 consecutive unopened | Pause everything except explicit alerts; tell the user in Settings, not by push |
| Opt-out of one type | That type only; never re-ask within 30 days |
| iOS permission denied | No in-app nagging; one gentle settings hint after a success moment, at most once |

## Platform notes

- iOS: ask for permission with context first (a soft in-app screen), then
  the system prompt. Consider provisional authorization for quiet delivery
  to Notification Center for users who have not decided.
- iOS Live Activities suit a live session (position updates), with an update
  budget; plan for fewer updates than laps.
- Web push: only after a user action on a page that explains it; browsers
  penalise sites that prompt on load.
- Email: one unsubscribe link that works in one click.

## Events for the plan

`notif_scheduled{type}`, `notif_suppressed{type, reason}`, `notif_sent{type}`,
`notif_failed{type, reason}`, `notif_open{type}`, `notif_opt_in{type,
source}`, `notif_opt_out{type}`, `notif_permission_prompt{result}`.
Suppression is logged, so a cap that silently eats the important message is
visible.
