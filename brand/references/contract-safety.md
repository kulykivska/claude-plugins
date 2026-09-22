# Employer-safety filter

Every idea and every draft about day-job work passes this filter before it
reaches a queue. The test is not "is this true" but "could this be used against
the company, or against me, by someone who wants it to be".

## Never publish

- Anything negative about the employer, its people, its customers or its
  investors. Not as a joke, not as a "lesson learned", not anonymized.
- Incidents, outages, breaches, data loss, or a security finding that is not
  already public. A postmortem about your own side project is fine; a
  postmortem about the company's production is not.
- Unreleased features, roadmap, pricing plans, contract terms, headcount plans,
  hiring or firing, acquisition or funding talk.
- Real numbers belonging to the company: revenue, user counts, conversion,
  churn, infrastructure cost, request volume, error rates.
- Internal names that identify systems, services, hostnames, buckets,
  repositories, tickets, environments or accounts.
- Screenshots or logs from internal tools, dashboards, admin panels, trackers,
  Slack, or anything containing another person's data.
- Named colleagues, managers or customers without their explicit agreement.
- Anything covered by an NDA, and anything a reasonable lawyer would read as
  disparagement.

## Safe to publish

- Techniques, patterns and tradeoffs, written generically: how a problem class
  is solved, not which company had it.
- Your own tooling, your own repositories, your own side projects, with real
  numbers from those.
- Publicly released features, once they are public, described the way the
  company describes them.
- Craft: how you work, how you review, how you test, how you use agents.
- Failures that are yours: your bug, your wrong assumption, your fix.

## Rewrite rules

When an idea is interesting but unsafe, do not drop it. Lift it one level:

- "Our payout service double-charged" → "Idempotency in payout flows: the two
  traps that survive a code review."
- "Our staging DB passwords were shared" → "Rotating every database password
  without downtime: the ordering that matters."
- "The iOS call feature is broken in prod" → "Debugging a call failure you
  cannot reproduce: what the client logs have to carry."

The technique is publishable. The incident is not.

## When unsure

Ask before queueing, and default to not publishing. One post is never worth a
conversation with legal. If a draft needs a caveat to be safe, it is not safe.
