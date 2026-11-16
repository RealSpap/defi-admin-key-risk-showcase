"""publish_watch_data.sh and check_mirror.py against local bare repositories : each rule has its planted fault."""
import os, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PUBLISH, MIRROR = HERE / "publish_watch_data.sh", HERE / "check_mirror.py"
G = ["-c", "user.name=t", "-c", "user.email=t@example.com"]


def git(cwd, *a):
    return subprocess.run(["git", "-C", str(cwd)] + list(a), capture_output=True, text=True)


def make(with_branch=True):
    """a bare remote with main (watch/status.json, watch/snapshot.json, watch/cases.json) and optionally watch-data (the seed)"""
    t = Path(tempfile.mkdtemp()); remote = t / "remote.git"; work = t / "w"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(remote)], check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(work)], check=True)
    (work / "watch").mkdir()
    for n, c in (("status.json", "S0"), ("snapshot.json", "P0"), ("cases.json", "C0")):
        (work / "watch" / n).write_text(c)
    git(work, "add", "-A"); git(work, *G, "commit", "-qm", "main")
    git(work, "push", "-q", str(remote), "main")
    if with_branch:
        git(work, "checkout", "-q", "--orphan", "watch-data"); git(work, "rm", "-rqf", ".")
        (work / "status.json").write_text("S0"); (work / "snapshot.json").write_text("P0"); (work / "README.md").write_text("seed")
        git(work, "add", "-A"); git(work, *G, "commit", "-qm", "seed"); git(work, "push", "-q", str(remote), "watch-data")
    return t, remote


def publish(remote, status, snapshot, extra=None):
    d = Path(tempfile.mkdtemp()); (d / "watch").mkdir()
    (d / "watch" / "status.json").write_text(status); (d / "watch" / "snapshot.json").write_text(snapshot)
    (d / "watch" / "drift.md").write_text("must never be copied")
    for n, c in (extra or {}).items():
        (d / "watch" / n).write_text(c)
    env = dict(os.environ, WATCH_REMOTE=str(remote), RUNNER_TEMP=str(d))
    return subprocess.run(["bash", str(PUBLISH)], cwd=d, capture_output=True, text=True, env=env)


class Publish(unittest.TestCase):
    def test_missing_branch_is_skipped_not_created(self):
        t, remote = make(with_branch=False)
        r = publish(remote, "S1", "P1")
        self.assertEqual(r.returncode, 0); self.assertIn("does not exist yet", r.stdout)
        self.assertNotIn("watch-data", git(remote, "branch").stdout)

    def test_changed_state_is_committed_by_the_bot_with_two_files_only(self):
        t, remote = make()
        r = publish(remote, "S1", "P1"); self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(git(remote, "show", "watch-data:status.json").stdout, "S1")
        self.assertEqual(git(remote, "log", "-1", "--format=%an <%ae>", "watch-data").stdout.strip(), "github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>")
        names = git(remote, "ls-tree", "-r", "--name-only", "watch-data").stdout.split()
        self.assertEqual(sorted(names), ["README.md", "snapshot.json", "status.json"])

    def test_unchanged_state_makes_no_commit(self):
        t, remote = make()
        before = git(remote, "rev-parse", "watch-data").stdout
        r = publish(remote, "S0", "P0"); self.assertEqual(r.returncode, 0); self.assertIn("unchanged", r.stdout)
        self.assertEqual(git(remote, "rev-parse", "watch-data").stdout, before)

    def test_history_only_grows(self):
        t, remote = make()
        publish(remote, "S1", "P1"); publish(remote, "S2", "P2")
        self.assertEqual(git(remote, "rev-list", "--count", "watch-data").stdout.strip(), "3")

    def test_missing_state_file_is_an_error(self):
        t, remote = make()
        d = Path(tempfile.mkdtemp()); (d / "watch").mkdir(); (d / "watch" / "status.json").write_text("S1")
        r = subprocess.run(["bash", str(PUBLISH)], cwd=d, capture_output=True, text=True, env=dict(os.environ, WATCH_REMOTE=str(remote), RUNNER_TEMP=str(d)))
        self.assertEqual(r.returncode, 1)


class Mirror(unittest.TestCase):
    def test_same_files_give_0(self):
        t, remote = make()
        self.assertEqual(subprocess.run([sys.executable, str(MIRROR), str(remote)], capture_output=True).returncode, 0)

    def test_a_difference_gives_1(self):
        t, remote = make(); publish(remote, "S1", "P0")
        self.assertEqual(subprocess.run([sys.executable, str(MIRROR), str(remote)], capture_output=True).returncode, 1)

    def test_a_missing_branch_gives_3(self):
        t, remote = make(with_branch=False)
        self.assertEqual(subprocess.run([sys.executable, str(MIRROR), str(remote)], capture_output=True).returncode, 3)


if __name__ == "__main__":
    unittest.main()
