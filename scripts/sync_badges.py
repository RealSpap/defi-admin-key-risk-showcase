#!/usr/bin/env python3
"""
Sync badge-data-cases-found.json against the headline case count README.md
itself actually states, so the shields.io badge never silently goes stale.

Deterministic, no external API. Pure text parsing + JSON rewrite
+ optional git commit/push.

Source of truth in README.md:
  - Headline case count: the "By severity: N Critical, N High, N Medium,
    N Low, across the N cases above" sentence in the At a glance section,
    the same total the severity table itself is built from. Every other
    "across the N cases" sentence (the Status section) must give the same N,
    otherwise the script fails, so the README never cites two counts.

Usage:
  python3 sync_badges.py [--repo-root PATH] [--no-commit] [--no-push] [--dry-run]

Exit codes:
  0  ran successfully (whether or not a change was made)
  1  could not parse the expected value out of README.md
  2  git commit/push failed
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

README_NAME = "README.md"
CASES_FOUND_BADGE = "badge-data-cases-found.json"

# "By severity: 2 Critical, 4 High, 2 Medium, 4 Low, across the 12 cases above."
HEADLINE_PATTERN = re.compile(
    r"across\s+(?:the\s+)?(\d+)\s+cases",
    re.IGNORECASE,
)


class ParsedCounts(NamedTuple):
    cases_found: str


def parse_readme(readme_text: str) -> ParsedCounts:
    counts = HEADLINE_PATTERN.findall(readme_text)
    if not counts:
        raise ValueError(
            "Could not find the 'across N cases' headline sentence in "
            "README.md"
        )
    if len(set(counts)) > 1:
        raise ValueError(
            f"README.md gives different case counts: {sorted(set(counts))}"
        )
    return ParsedCounts(cases_found=counts[0])


def load_badge_message(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    return str(data.get("message", ""))


def write_badge_message(path: Path, new_message: str) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    data["message"] = new_message
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def run(cmd, cwd: Path):
    return subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--no-commit", action="store_true")
    parser.add_argument("--no-push", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    readme_path = repo_root / README_NAME
    cases_found_path = repo_root / CASES_FOUND_BADGE

    for p in (readme_path, cases_found_path):
        if not p.is_file():
            print(f"ERROR: expected file not found: {p}", file=sys.stderr)
            return 1

    readme_text = readme_path.read_text(encoding="utf-8")

    try:
        counts = parse_readme(readme_text)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    cases_found_message = counts.cases_found
    cases_found_current = load_badge_message(cases_found_path)

    print(f"README says headline cases found = {cases_found_message} "
          f"(badge currently says {cases_found_current})")

    changed_files = []

    if cases_found_current != cases_found_message:
        print(f"MISMATCH: {CASES_FOUND_BADGE} message "
              f"'{cases_found_current}' -> '{cases_found_message}'")
        if not args.dry_run:
            write_badge_message(cases_found_path, cases_found_message)
        changed_files.append(cases_found_path)

    if not changed_files:
        print("Badge already matches README.md. Nothing to do.")
        return 0

    if args.dry_run:
        print("Dry run: not writing files or committing.")
        return 0

    print(f"Updated {len(changed_files)} file(s): "
          f"{', '.join(p.name for p in changed_files)}")

    if args.no_commit:
        print("--no-commit set: leaving changes uncommitted.")
        return 0

    try:
        run(["git", "config", "user.name", "badge-sync-bot"], repo_root)
        run(["git", "config", "user.email",
             "badge-sync-bot@users.noreply.github.com"], repo_root)
        run(["git", "add"] + [str(p.relative_to(repo_root)) for p in changed_files],
            repo_root)

        diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=repo_root)
        if diff.returncode == 0:
            print("No staged changes after write. Skipping commit.")
            return 0

        names = ", ".join(p.name for p in changed_files)
        run(["git", "commit", "-m", f"chore: sync badge data with README ({names})"],
            repo_root)
        print("Committed badge sync.")

        if args.no_push:
            print("--no-push set: leaving commit unpushed.")
            return 0

        run(["git", "push"], repo_root)
        print("Pushed badge sync commit.")
    except subprocess.CalledProcessError as exc:
        print(f"ERROR: git command failed: {exc.cmd}", file=sys.stderr)
        print(exc.stdout, file=sys.stderr)
        print(exc.stderr, file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
