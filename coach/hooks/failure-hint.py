#!/usr/bin/env python3
"""PostToolUseFailure(Bash): map a failed command's error to a known local
pitfall and add a hint. Non-blocking; silent when nothing matches."""
import sys, json, re

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

resp = data.get("tool_response", "")
if isinstance(resp, (dict, list)):
    resp = json.dumps(resp)
resp = str(resp)

hints = []
def h(pat, msg):
    if re.search(pat, resp, re.I):
        hints.append(msg)

h(r"eaddrinuse|address already in use",
  "port in use: 8001 = RaceModel API, 8000 = the other app, 5180 = frontend; `lsof -i :<port>` and kill the process")
h(r"cannot connect to the docker daemon|docker daemon",
  "Docker isn't running: start Docker Desktop/Colima. Also: macOS Docker --reload does NOT pick up host edits, `docker restart` the container")
h(r"modulenotfounderror|no module named",
  "missing Python dep: activate the project venv and pip install; check which interpreter is running")
h(r"feature.?names|shape mismatch|feature_names mismatch",
  "likely FEATURE_COLS drift between racemodel predictor.py and f1-predictor shared.py: sync them exactly, mind deploy ordering")
h(r"econnrefused.*5432|could not connect to (server|database)",
  "database not reachable: is the local DB container up / fly proxy running?")
h(r"release_command|machines? (stuck|in state) created",
  "known Fly gotcha: machines stuck in `created` because of release_command; deploy via local flyctl without release_command")

if hints:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PostToolUseFailure",
        "additionalContext": "coach hint: " + "; ".join(hints)}}))
sys.exit(0)
