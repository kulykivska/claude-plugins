---
description: Switch this session to another claude.ai account (profile) and continue the conversation there
argument-hint: <profile>   e.g. personal | default
allowed-tools: Bash(claude-switch:*)
---
Run exactly this via Bash: `claude-switch $ARGUMENTS`

That command hands the session over to the other account: the `claude-as` wrapper relaunches Claude Code under the requested profile and continues this same conversation. Do nothing else. If the command prints an error or instructions, show them to the user verbatim.
