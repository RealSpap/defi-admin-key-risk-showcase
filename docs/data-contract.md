# Data contract (v1)

The machine-readable files of this repository, who reads them, and how they are written. A published URL keeps answering: when a path is replaced, the same bytes are written to both places until the old one is retired, and the old one is retired only when I say so in writing.

| URL (base `https://raw.githubusercontent.com/RealSpap/defi-admin-key-risk-showcase/`) | What it holds | Version | Read by | Written by |
|---|---|---|---|---|
| `main/badge-data-cases-found.json` | the "Cases found" badge (shields.io endpoint) | v1 | the README badge | me, in the commit that changes the README (`scripts/sync_badges.py`); a workflow only checks it |
| `main/watch/cases.json` | the registry of published cases, one entry per authority the Watch re-reads | v1 | the Watch workflow, `scripts/test_cases_vs_readme.py`, the command in the README | me |
| `watch-data/status.json`, `watch-data/snapshot.json` | the state of the last Watch run and the authorities it read, on a branch that only grows | v1 | the Watch workflow itself, at the start of its next run | the Watch (github-actions[bot]) |
| `main/watch/status.json`, `main/watch/snapshot.json` | retired on 2026-11-24, in writing, as the first paragraph requires: the two files no longer exist on `main` | v1 | nobody | nobody |

## The Watch and the branch

The Watch runs on GitHub Actions once a day (`.github/workflows/watch.yml`). It reads each authority named in `watch/cases.json` and writes `status.json` and `snapshot.json`. Since 2026-11-24 the state lives on the `watch-data` branch only: the run reads the previous state from it (`scripts/read_watch_data.sh`), then records the new state on it (`scripts/publish_watch_data.sh`). A missing branch, a missing file or a file that is not JSON stops the run red and nothing is recorded, so the next run raises the alarm again instead of starting from nothing. A run in which a published read moved, or the registry contradicts the chain, records nothing either: the published state stays at the last run without a move, and the next run compares with that state and raises the alarm again, until the case is re-verified by hand and the new state is recorded by hand: run `python3 scripts/watch_admin_keys.py --registry watch/cases.json --out <a clone of the watch-data branch> --published-only`, check that the MOVED lines are exactly the case that was re-verified (a second move must be re-verified before its state is recorded), delete the `drift.md` it writes, then `git add status.json snapshot.json` (never `git add -A`) and commit to that branch. `main` receives no commit from the Watch and its history is the history of the work.

The `watch-data` branch is created by hand once, with a seed commit. It only grows: nothing rewrites it, nothing forces it.

## What does not change

- The command `python3 scripts/watch_admin_keys.py --out "$(mktemp -d)"` and its exit codes.
- The name `watch.yml`, the registry `watch/cases.json` and the badge URL.
