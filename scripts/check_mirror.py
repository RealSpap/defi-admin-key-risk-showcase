#!/usr/bin/env python3
"""Compares the two state files of the Watch on main (watch/) and on the watch-data branch (mirror), byte for byte.
    python3 scripts/check_mirror.py [REMOTE]          REMOTE defaults to origin ; a local path works (tests)
Exit 0 identical, 1 different, 3 the branch or a file is missing (never read as a pass). Reads with git, writes nothing.
During the transition (both places are written, for at least 14 days) a difference after a run is an alarm; the run that has just written both must give 0."""
import subprocess, sys, tempfile
FILES = ["status.json", "snapshot.json"]


def show(repo, ref, path):
    r = subprocess.run(["git", "-C", repo, "show", "%s:%s" % (ref, path)], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def main(argv):
    repo = argv[1] if len(argv) > 1 else "."
    work = repo
    if len(argv) > 1 and argv[1] != ".":
        # a remote path or URL : fetch both refs into a scratch repository
        work = tempfile.mkdtemp()
        subprocess.run(["git", "init", "-q", work], check=True)
        for ref, dst in (("main", "m"), ("watch-data", "w")):
            r = subprocess.run(["git", "-C", work, "fetch", "-q", argv[1], "refs/heads/%s:refs/heads/%s" % (ref, dst)], capture_output=True)
            if r.returncode != 0:
                print("MISSING: cannot read %s of %s" % (ref, argv[1])); return 3
        main_ref, data_ref = "m", "w"
    else:
        main_ref, data_ref = "origin/main", "origin/watch-data"
    bad = 0
    for f in FILES:
        a, b = show(work, main_ref, "watch/" + f), show(work, data_ref, f)
        if a is None or b is None:
            print("MISSING: %s on %s" % (f, "main" if a is None else "watch-data")); return 3
        if a != b:
            print("DIFFERENT: %s (main %d bytes, watch-data %d bytes)" % (f, len(a), len(b))); bad = 1
        else:
            print("SAME: %s" % f)
    return bad


if __name__ == "__main__":
    sys.exit(main(sys.argv))
