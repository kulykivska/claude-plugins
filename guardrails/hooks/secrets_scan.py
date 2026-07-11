#!/usr/bin/env python3
"""Scan a unified git diff (on stdin) for real credentials / secrets / PII in
ADDED lines. Prints a grouped report to stderr and exits 2 on any hit, else 0.

Never prints the offending value itself, only the category and the file(s),
so the secret isn't echoed into logs/transcripts.

Usage: git diff <range> --unified=0 | secrets_scan.py [allowlist.txt]
"""
import sys, re, os

allow = []
if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
    for ln in open(sys.argv[1], encoding="utf-8", errors="ignore"):
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        try:
            allow.append(re.compile(s))
        except re.error:
            pass

HIGH = [
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private key block"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key id"),
    (re.compile(r"ghp_[A-Za-z0-9]{30,}"), "GitHub token"),
    (re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}"), "Anthropic API key"),
    (re.compile(r"sk_live_[A-Za-z0-9]{10,}"), "Stripe live secret key"),
    (re.compile(r"AIza[0-9A-Za-z_\-]{35}"), "Google API key"),
    (re.compile(r"xox[baprs]-[0-9A-Za-z\-]{10,}"), "Slack token"),
    (re.compile(r"FlyV1[A-Za-z0-9_\-+/=]{20,}"), "Fly.io API token"),
    (re.compile(r"eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{6,}"), "JWT"),
    (re.compile(r"(?i)(password|passwd|pwd|secret|api[_-]?key|access[_-]?token|auth[_-]?token|private[_-]?key)\s*[:=]\s*[\"']?[^\"'\s,;)]{8,}"), "hardcoded secret assignment"),
]
PII = [
    (re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"), "email address"),
    (re.compile(r"(?<!\d)\+[1-9]\d{7,14}(?!\d)"), "phone number (E.164)"),
]

cur = "?"
high, pii = {}, {}

def allowed(line):
    return any(p.search(line) for p in allow)

for raw in sys.stdin:
    if raw.startswith("+++ "):
        cur = raw[4:].strip()
        if cur.startswith("b/"):
            cur = cur[2:]
        continue
    if raw.startswith("+++") or raw.startswith("---") or raw.startswith("@@"):
        continue
    if not raw.startswith("+"):
        continue
    line = raw[1:].rstrip("\n")
    if not line.strip() or allowed(line):
        continue
    for rx, label in HIGH:
        if rx.search(line):
            high.setdefault(label, set()).add(cur)
    for rx, label in PII:
        if rx.search(line):
            pii.setdefault(label, set()).add(cur)

if not high and not pii:
    sys.exit(0)

def emit(title, hits):
    print(title, file=sys.stderr)
    for label, files in sorted(hits.items()):
        fl = ", ".join(sorted(files)[:6])
        more = "" if len(files) <= 6 else f" (+{len(files) - 6} more)"
        print(f"     - {label}: {fl}{more}", file=sys.stderr)

ctx = os.environ.get("SCAN_CONTEXT", "pushed diff")
print(f"BLOCKED by guardrails: possible sensitive data in the {ctx}.", file=sys.stderr)
if high:
    emit("  High-confidence secrets:", high)
if pii:
    emit("  Possible PII (may be a false positive):", pii)
print("Remove real creds/emails/phone numbers, or add a legitimate test value/pattern", file=sys.stderr)
print("to hooks/secrets-allowlist.txt. If it's a false positive, push it yourself.", file=sys.stderr)
sys.exit(2)
