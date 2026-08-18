---
name: ai-code-report
description: "Report how much code was written with Claude Code assistance. Trigger on 'ai code report', 'сколько кода написал Claude', 'AI-assist share', or when preparing engineering metrics. Aggregates the local shmoozer-metrics edit log per repo/period and, inside a checkout, estimates the AI share of committed lines. Arguments: $ARGUMENTS"
---

# AI code report

The `shmoozer-metrics` plugin logs every Claude Code edit (repo, file, lines
written) to `~/.claude/shmoozer-metrics/ai-edits.jsonl`. This skill turns that
log into a report.

## Steps

1. Parse `$ARGUMENTS` for a period ("last week", a date, "since 2026-08-01") and
   an optional repo name. Default: last 7 days.
2. Run the aggregator:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ai_code_report.py" --since YYYY-MM-DD [--repo NAME] [--git-dir /path/to/checkout]
   ```

   Pass `--git-dir` when the session is inside one of the app repos (or the user
   names one) so the report includes the estimated share of committed added
   lines for the same period.
3. Present the table as-is, then one or two sentences of interpretation:
   which repo got the most AI-assisted work and how the share compares to the
   previous period if the user asks for a trend.

## Caveats to state when relevant

- The log is per-machine: it only covers sessions run on this computer. Team
  totals need each developer's log (or a later central collector).
- "AI lines" are written pre-commit; some never get committed, so the share
  against `git numstat` is an upper bound, not an exact ratio.
- Records exist only from the day the plugin was installed onward.
