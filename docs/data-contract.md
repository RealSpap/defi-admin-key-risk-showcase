# Data contract (v1)

The machine-readable files of this repository, who reads them, and how they are written. A published URL keeps answering: when a path is replaced, the same bytes are written to both places until the old one is retired, and the old one is retired only when I say so in writing.

| URL (base `https://raw.githubusercontent.com/RealSpap/defi-admin-key-risk-showcase/`) | What it holds | Version | Read by | Written by |
|---|---|---|---|---|
| `main/badge-data-cases-found.json` | the "Cases found" badge (shields.io endpoint) | v1 | the README badge | me, in the commit that changes the README (`scripts/sync_badges.py`); a workflow only checks it |
| `main/watch/cases.json` | the registry of published cases, one entry per authority the Watch re-reads | v1 | the Watch workflow, `scripts/test_cases_vs_readme.py`, the command in the README | me |
| `main/watch/status.json`, `main/watch/snapshot.json` | the state of the last Watch run and the authorities it read | v1 | the Watch workflow itself; no other reader known | the Watch (github-actions[bot]), while the transition lasts |
| `watch-data/status.json`, `watch-data/snapshot.json` | the same two files, on a branch that only grows | v1 | no reader known yet | the Watch (github-actions[bot]) |

## The Watch and the branch

The Watch runs on GitHub Actions once a day (`.github/workflows/watch.yml`). It reads each authority named in `watch/cases.json` and writes `status.json` and `snapshot.json`. During the transition it writes them to two places: the `watch/` folder of `main`, as before, and the `watch-data` branch. `scripts/check_mirror.py` compares the two byte for byte after each run; a difference turns the run red. Once the old path is retired, `main` receives no commit from the Watch and its history is the history of the work.

The `watch-data` branch is created by hand once, with a seed commit. It only grows: nothing rewrites it, nothing forces it.

## What does not change

- The command `python3 scripts/watch_admin_keys.py --out "$(mktemp -d)"` and its exit codes.
- The name `watch.yml`, the registry `watch/cases.json` and the badge URL.
