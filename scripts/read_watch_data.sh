#!/bin/bash
# Puts the previous state of the Watch (status.json, snapshot.json) from the watch-data branch into ./watch, before the run reads it.
# main keeps no state file: the branch is the only place the state lives. A missing branch, a missing file or a file that is not JSON is an ERROR (exit 1):
# starting from nothing would read as "nothing moved" and the alarm would go silent, so the run stops red and records nothing.
# Usage (in the Watch workflow, before the run): GITHUB_TOKEN=... bash scripts/read_watch_data.sh
# Tests: WATCH_REMOTE=<path of a local bare repository> (no token, no network).
set -u
REMOTE="${WATCH_REMOTE:-https://github.com/${GITHUB_REPOSITORY:?GITHUB_REPOSITORY is not set}.git}"
WORK="${RUNNER_TEMP:-${TMPDIR:-/tmp}}/watch-data-read-$$"
FILES="status.json snapshot.json"
AUTH=()
case "$REMOTE" in https://*) AUTH=(-c "http.https://github.com/.extraheader=AUTHORIZATION: basic $(printf x-access-token:%s "${GITHUB_TOKEN:?GITHUB_TOKEN is not set}" | base64 | tr -d '\n')");; esac

ERR="$WORK.err"
git ${AUTH[@]+"${AUTH[@]}"} clone -q --depth 1 --branch watch-data "$REMOTE" "$WORK" 2>"$ERR" || { echo "::error::cannot read the watch-data branch ($(head -c 160 "$ERR" | tr '\n' ' ')): the previous state is unknown, nothing is read and nothing will be recorded"; exit 1; }
mkdir -p watch
for f in $FILES; do
  [ -f "$WORK/$f" ] || { echo "::error::$f is missing on watch-data: the previous state is incomplete, the run stops"; exit 1; }
  # valid JSON of the right shape: a snapshot that is null or {} would be read as "no previous run" (a new baseline, no drift seen), so it stops the run
  python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); ok=isinstance(d,dict) and (sys.argv[2]!="snapshot.json" or isinstance(d.get("results"),dict)) and (sys.argv[2]!="status.json" or "run_utc" in d); sys.exit(0 if ok else 1)' "$WORK/$f" "$f" 2>/dev/null || { echo "::error::$f on watch-data is not valid JSON of the expected shape: the run stops"; exit 1; }
  cp "$WORK/$f" "watch/$f"
done
echo "watch/: previous state read from watch-data at $(git -C "$WORK" rev-parse --short HEAD) (last run $(python3 -c 'import json; print(json.load(open("watch/status.json")).get("run_utc","unknown"))'))"
