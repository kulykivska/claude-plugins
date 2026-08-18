#!/usr/bin/env python3
"""Aggregate the ai-edits JSONL into an AI-assist report.

Usage:
  python3 ai_code_report.py [--since YYYY-MM-DD] [--repo NAME] [--git-dir PATH]

Prints per-repo totals (edits, files, AI-written lines) for the period. When
--git-dir points at a checkout, also compares against `git log --numstat` for
the same period to estimate the share of AI-assisted added lines.
"""
import argparse
import json
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

LOG_FILE = Path.home() / ".claude" / "shmoozer-metrics" / "ai-edits.jsonl"


def load_records(since, repo):
    if not LOG_FILE.exists():
        return []
    records = []
    with LOG_FILE.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue  # a torn write from a crashed hook; skip just that line
            if since and r.get("ts", "") < since:
                continue
            if repo and r.get("repo") != repo:
                continue
            records.append(r)
    return records


def git_added_lines(git_dir, since):
    args = ["git", "-C", git_dir, "log", "--numstat", "--no-merges",
            "--pretty=format:"]
    if since:
        args.append(f"--since={since}")
    out = subprocess.run(args, capture_output=True, text=True, timeout=30)
    if out.returncode != 0:
        raise RuntimeError(f"git log failed: {out.stderr.strip()}")
    total = 0
    for line in out.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) == 3 and parts[0].isdigit():
            total += int(parts[0])
    return total


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--since", help="YYYY-MM-DD (UTC)")
    p.add_argument("--repo", help="repo name as logged (git toplevel basename)")
    p.add_argument("--git-dir", help="checkout to compare against via git numstat")
    args = p.parse_args()

    records = load_records(args.since, args.repo)
    if not records:
        print("No AI-edit records for the given filters.")
        return

    per_repo = defaultdict(lambda: {"edits": 0, "lines": 0, "files": set()})
    for r in records:
        bucket = per_repo[r.get("repo") or "(no repo)"]
        bucket["edits"] += 1
        bucket["lines"] += r.get("lines", 0)
        bucket["files"].add(r.get("file"))

    period = f"since {args.since}" if args.since else "all time"
    print(f"AI-assisted edits ({period}), generated "
          f"{datetime.now(timezone.utc).date()}:\n")
    print(f"{'repo':<24} {'edits':>6} {'files':>6} {'AI lines':>9}")
    for name, b in sorted(per_repo.items(), key=lambda kv: -kv[1]["lines"]):
        print(f"{name:<24} {b['edits']:>6} {len(b['files']):>6} {b['lines']:>9}")

    if args.git_dir:
        total_added = git_added_lines(args.git_dir, args.since)
        ai_lines = sum(b["lines"] for b in per_repo.values())
        if total_added:
            share = 100.0 * min(ai_lines, total_added) / total_added
            print(f"\nCommitted added lines in {args.git_dir} for the period: "
                  f"{total_added}")
            print(f"Estimated AI-assisted share: ~{share:.0f}% "
                  f"(AI lines are pre-commit, so treat as an upper bound)")
        else:
            print(f"\nNo committed added lines found in {args.git_dir} "
                  f"for the period.")


if __name__ == "__main__":
    main()
