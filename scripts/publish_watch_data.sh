#!/bin/bash
# Copies the two state files of the Watch (watch/status.json, watch/snapshot.json) to the watch-data branch, as github-actions[bot].
# The branch is created by hand once (a seed commit) and only ever grows: this script never creates it, never rewrites it, never forces.
# Usage (in the Watch workflow, after the run): GITHUB_TOKEN=... bash scripts/publish_watch_data.sh
# Tests: WATCH_REMOTE=<path of a local bare repository> (no token, no network).
set -u
REMOTE="${WATCH_REMOTE:-https://github.com/${GITHUB_REPOSITORY:?GITHUB_REPOSITORY is not set}.git}"
WORK="${RUNNER_TEMP:-${TMPDIR:-/tmp}}/watch-data-$$"
FILES="status.json snapshot.json"
AUTH=()
case "$REMOTE" in https://*) AUTH=(-c "http.https://github.com/.extraheader=AUTHORIZATION: basic $(printf x-access-token:%s "${GITHUB_TOKEN:?GITHUB_TOKEN is not set}" | base64 | tr -d '\n')");; esac

rc=0; git ${AUTH[@]+"${AUTH[@]}"} ls-remote --exit-code --heads "$REMOTE" watch-data >/dev/null 2>&1 || rc=$?
if [ "$rc" -eq 2 ]; then
  echo "::warning::the watch-data branch does not exist yet: the copy is skipped (create it with the seed commit first)"; exit 0
elif [ "$rc" -ne 0 ]; then
  echo "::error::cannot read the remote (git ls-remote exit code $rc): nothing copied"; exit 1
fi
git ${AUTH[@]+"${AUTH[@]}"} clone -q --depth 1 --branch watch-data "$REMOTE" "$WORK" || { echo "::error::cannot clone watch-data"; exit 1; }
for f in $FILES; do
  [ -f "watch/$f" ] || { echo "::error::watch/$f is missing: nothing copied"; exit 1; }
  cp "watch/$f" "$WORK/$f"
done
git -C "$WORK" add $FILES
if git -C "$WORK" diff --cached --quiet; then echo "watch-data: state unchanged"; exit 0; fi
GIT_AUTHOR_NAME='github-actions[bot]' GIT_COMMITTER_NAME='github-actions[bot]' GIT_AUTHOR_EMAIL='41898282+github-actions[bot]@users.noreply.github.com' GIT_COMMITTER_EMAIL='41898282+github-actions[bot]@users.noreply.github.com' git -C "$WORK" commit -qm "Watch $(date -u +%Y-%m-%dT%H:%MZ)" || exit 1
# a plain push: if the branch moved in between, the push is refused and the run is red; nothing is forced
git ${AUTH[@]+"${AUTH[@]}"} -C "$WORK" push -q origin HEAD:refs/heads/watch-data || { echo "::error::push to watch-data refused (not a fast-forward?)"; exit 1; }
echo "watch-data: updated"
