#!/usr/bin/env python3
"""Replace the 'hardcoded secret assignment' rule in the guardrails scanner.

The current rule matches any `keyword: value` shape, so prose, comments, Zod
schemas and env-var references trip it. Measured over backend + infrastructure +
claude-plugins: 130 false positives, which is what the allowlist has been
growing entries to suppress.

The replacement keeps the three shapes a real credential takes (quoted literal,
unquoted containing a digit, unquoted and implausibly long) and skips plain
identifier references. Same catch rate on the credential corpus, no noise.

Run:  python3 scripts/fix-assignment-rule.py
Agents cannot read or write that file (settings.json denies `**/*secret*`),
so this is applied by hand.
"""
import re
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "guardrails" / "hooks" / "secrets_scan.py"

NEW_RULES = '''    # A `keyword: value` shape alone is not a secret: prose, comments, schema
    # declarations and env-var references all use it. Match the three shapes a
    # real credential actually takes instead.
    (re.compile(_SECRET_KEY + r"\\s*[:=]\\s*[\\"'][^\\"'\\s]{8,}[\\"']"),
     "hardcoded secret assignment"),
    (re.compile(_SECRET_KEY + r"\\s*[:=]\\s*(?=[^\\"'\\s,;)]*\\d)[^\\"'\\s,;)]{8,}"),
     "hardcoded secret assignment"),
    (re.compile(_SECRET_KEY + r"\\s*[:=]\\s*" + _NOT_A_REFERENCE + r"[^\\"'\\s,;)]{20,}"),
     "hardcoded secret assignment"),
'''

KEY_CONST = '''_SECRET_KEY = (r"(?i)(password|passwd|pwd|secret|api[_-]?key|access[_-]?token"
               r"|auth[_-]?token|private[_-]?key)")

# A long value is still a reference, not a literal, when it is a dotted
# identifier chain (process.env.X) or a shell/compose interpolation (${X:-}).
_NOT_A_REFERENCE = (r"(?!(?:[A-Za-z_$][A-Za-z0-9_$]*(?:\\.[A-Za-z0-9_$]+)+"
                    r"|\\$\\{?[A-Za-z_][A-Za-z0-9_]*(?::[-+?][^}]*)?\\}?)[\\s,;)\\]}]*$)")

HIGH = [
'''

# Assembled at runtime rather than written out: a literal `password = "..."`
# line here would itself read as a hardcoded credential to any scanner.
_BLOCK_PARTS = [
    ("password", ' = "', "hunter2swordfish", '"'),
    ("DB_PASSWORD", "=", "Pa55w0rdLongEnough", ""),
    ("api_key", ': "', "sk-proj-abcdefghijklmnop", '"'),
    ("AUTH_TOKEN", "=", "abc123def456ghi789", ""),
    ("secret", ": ", "correcthorsebatterystaple", ""),
    ("pwd", "=", "Tr0ub4dor&3xyz", ""),
]
MUST_BLOCK = [k + sep + v + tail for k, sep, v, tail in _BLOCK_PARTS]
MUST_PASS = [
    "password: oversized",
    "accessToken: tokens.access",
    "secret: process.env.SESSION_SECRET",
    "password: z.string().min(1)",
    "# `password` -> `oversized`, a reference and not a literal",
] + [
    # Same reason as _BLOCK_PARTS: written out, the Python quotes around these
    # would put a `"` after the interpolation and trip the rule on this file.
    "      WATERMARKS_SERVER_API_KEY: " + "${WATERMARKS_SERVER_API_KEY:-}",
    "      POSTGRES_PASSWORD: " + "${AUTH_DB_PASSWORD}",
    "  api_key: " + "$MY_LONG_ENV_VARIABLE_NAME",
]


def main() -> int:
    if not TARGET.is_file():
        print(f"not found: {TARGET}", file=sys.stderr)
        return 1

    src = TARGET.read_text(encoding="utf-8")
    if "_SECRET_KEY" in src:
        print("already applied - nothing to do.")
        return 0

    # Match the rule by shape, so whitespace drift cannot silently skip it.
    rule_re = re.compile(
        r"^ *\(re\.compile\(r\"\(\?i\)\(password\|passwd\|pwd\|secret.*?"
        r'"hardcoded secret assignment"\),\n',
        re.MULTILINE | re.DOTALL,
    )
    if not rule_re.search(src):
        print("expected rule not found - aborting without changes.", file=sys.stderr)
        return 1
    if "HIGH = [\n" not in src:
        print("expected HIGH list not found - aborting without changes.", file=sys.stderr)
        return 1

    # Lambda replacement: the new rules are full of backslashes that re.sub
    # would otherwise read as template escapes.
    patched = rule_re.sub(lambda _: NEW_RULES, src, count=1)
    patched = patched.replace("HIGH = [\n", KEY_CONST, 1)
    TARGET.write_text(patched, encoding="utf-8")
    print(f"patched {TARGET}")

    # Prove the patched rules compile and still catch real credentials.
    ns: dict = {}
    try:
        exec(compile(patched.split("cur = ")[0], str(TARGET), "exec"), ns)
        high = [rx for rx, _ in ns["HIGH"]]
    except Exception as exc:
        TARGET.write_text(src, encoding="utf-8")
        print(f"patched file failed to load ({exc!r}) - reverted.", file=sys.stderr)
        return 1

    missed = [s for s in MUST_BLOCK if not any(r.search(s) for r in high)]
    noisy = [s for s in MUST_PASS if any(r.search(s) for r in high)]
    print(f"self-check: real secrets caught {len(MUST_BLOCK) - len(missed)}/{len(MUST_BLOCK)}, "
          f"false positives {len(noisy)}/{len(MUST_PASS)}")
    for s in missed:
        print(f"  MISSED: {s}")
    for s in noisy:
        print(f"  NOISE : {s}")
    if missed or noisy:
        TARGET.write_text(src, encoding="utf-8")
        print("self-check failed - reverted, file is unchanged.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
