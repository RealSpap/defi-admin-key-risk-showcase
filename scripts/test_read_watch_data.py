"""read_watch_data.sh, publish_watch_data.sh and the shape of watch.yml, with local bare repositories: the state lives on watch-data only, main receives nothing.
Each rule has its planted fault: branch missing, a state file missing, a file that is not JSON, an unreadable remote, a stale copy on main, a branch that is behind, a red run."""
import json, os, subprocess, tempfile, textwrap, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
READ, PUBLISH, WORKFLOW = HERE / "read_watch_data.sh", HERE / "publish_watch_data.sh", HERE.parent / ".github" / "workflows" / "watch.yml"
G = ["-c", "user.name=t", "-c", "user.email=t@example.com"]
S0 = json.dumps({"run_utc": "2026-11-24T07:40:27Z"}); P0 = json.dumps({"written_utc": "2026-11-24T07:40:27Z", "results": {}})


def git(cwd, *a):
    return subprocess.run(["git", "-C", str(cwd)] + list(a), capture_output=True, text=True)


def make(branch_files=("status.json", "snapshot.json"), contents=None):
    """a bare remote: main (code and cases only, NO state file) and optionally watch-data holding branch_files"""
    contents = contents or {"status.json": S0, "snapshot.json": P0}
    t = Path(tempfile.mkdtemp()); remote = t / "remote.git"; work = t / "w"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(remote)], check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(work)], check=True)
    (work / "watch").mkdir(); (work / "watch" / "cases.json").write_text("{}")
    git(work, "add", "-A"); git(work, *G, "commit", "-qm", "main"); git(work, "push", "-q", str(remote), "main")
    if branch_files is not None:
        git(work, "checkout", "-q", "--orphan", "watch-data"); git(work, "rm", "-rqf", ".")
        for f in branch_files:
            (work / f).write_text(contents[f])
        (work / "README.md").write_text("seed")
        git(work, "add", "-A"); git(work, *G, "commit", "-qm", "seed"); git(work, "push", "-q", str(remote), "watch-data")
    return t, remote


def run(script, remote, cwd):
    env = dict(os.environ, WATCH_REMOTE=str(remote), RUNNER_TEMP=str(cwd))
    return subprocess.run(["bash", str(script)], cwd=cwd, capture_output=True, text=True, env=env)


def checkout():
    d = Path(tempfile.mkdtemp()); (d / "watch").mkdir(); (d / "watch" / "cases.json").write_text("{}")
    return d


class Read(unittest.TestCase):
    def test_the_state_comes_from_watch_data(self):
        t, remote = make(); d = checkout()
        r = run(READ, remote, d); self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual((d / "watch" / "status.json").read_text(), S0); self.assertEqual((d / "watch" / "snapshot.json").read_text(), P0)
        self.assertIn("2026-11-24T07:40:27Z", r.stdout)

    def test_a_stale_copy_left_on_main_never_wins(self):
        t, remote = make(); d = checkout()
        (d / "watch" / "status.json").write_text('{"run_utc": "STALE"}'); (d / "watch" / "snapshot.json").write_text('{"results": "STALE"}')
        r = run(READ, remote, d); self.assertEqual(r.returncode, 0)
        self.assertEqual((d / "watch" / "snapshot.json").read_text(), P0)

    def test_a_branch_that_is_behind_is_read_as_it_is(self):
        old = {"status.json": json.dumps({"run_utc": "2026-11-20T07:40:00Z"}), "snapshot.json": P0}
        t, remote = make(contents=old); d = checkout()
        r = run(READ, remote, d); self.assertEqual(r.returncode, 0)
        self.assertIn("2026-11-20T07:40:00Z", r.stdout)   # the run compares with the last state recorded, older or not: a later drift is still seen

    def test_missing_branch_is_an_error_and_writes_nothing(self):
        t, remote = make(branch_files=None); d = checkout()
        r = run(READ, remote, d); self.assertEqual(r.returncode, 1); self.assertIn("cannot read the watch-data branch", r.stdout); self.assertIn("watch-data", r.stdout)
        self.assertFalse((d / "watch" / "status.json").exists()); self.assertFalse((d / "watch" / "snapshot.json").exists())

    def test_a_missing_state_file_is_an_error(self):
        t, remote = make(branch_files=("snapshot.json",)); d = checkout()
        r = run(READ, remote, d); self.assertEqual(r.returncode, 1); self.assertIn("status.json is missing", r.stdout)

    def test_a_file_that_is_not_json_is_an_error(self):
        t, remote = make(contents={"status.json": S0, "snapshot.json": "<<<not json"}); d = checkout()
        r = run(READ, remote, d); self.assertEqual(r.returncode, 1); self.assertIn("not valid JSON", r.stdout)

    def test_a_snapshot_of_the_wrong_shape_is_an_error(self):
        for bad in ("null", "{}", '{"results": []}', "[]"):
            t, remote = make(contents={"status.json": S0, "snapshot.json": bad}); d = checkout()
            r = run(READ, remote, d); self.assertEqual(r.returncode, 1, bad); self.assertIn("expected shape", r.stdout)
        t, remote = make(contents={"status.json": "{}", "snapshot.json": P0}); d = checkout()
        self.assertEqual(run(READ, remote, d).returncode, 1)   # a status without run_utc

    def test_an_unreadable_remote_is_an_error(self):
        d = checkout(); r = run(READ, Path(tempfile.mkdtemp()) / "no-such-repository", d)
        self.assertEqual(r.returncode, 1)


class RoundTrip(unittest.TestCase):
    def test_a_run_moves_only_watch_data_and_main_receives_nothing(self):
        t, remote = make(); d = checkout()
        main_before = git(remote, "rev-parse", "main").stdout
        self.assertEqual(run(READ, remote, d).returncode, 0)
        (d / "watch" / "status.json").write_text(json.dumps({"run_utc": "2026-11-25T07:40:00Z"})); (d / "watch" / "snapshot.json").write_text(P0)
        (d / "watch" / "drift.md").write_text("must never leave the runner")
        r = run(PUBLISH, remote, d); self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(git(remote, "rev-parse", "main").stdout, main_before)
        self.assertIn("2026-11-25", git(remote, "show", "watch-data:status.json").stdout)
        self.assertNotIn("drift.md", git(remote, "ls-tree", "-r", "--name-only", "watch-data").stdout)
        d2 = checkout(); self.assertEqual(run(READ, remote, d2).returncode, 0)   # the next run starts from what this one recorded
        self.assertIn("2026-11-25", (d2 / "watch" / "status.json").read_text())


class Workflow(unittest.TestCase):
    """watch.yml read as text (no yaml module in the runner's standard library): the order of the steps is the safety."""
    def steps(self):
        text = WORKFLOW.read_text(); body = text[text.index("    steps:"):]
        return [s for s in body.split("\n      - ")[1:]]

    def test_the_workflow_is_valid_yaml(self):
        try: import yaml
        except ImportError: self.skipTest("PyYAML is not installed here")
        d = yaml.safe_load(WORKFLOW.read_text()); self.assertIn("watch", d["jobs"])   # a step name with a colon once broke the file: the tests read it as text, so the parse is tested here

    def test_the_order_read_run_alarm_record(self):
        st = self.steps(); idx = lambda key: next(i for i, s in enumerate(st) if key in s)
        a, b, c, d = idx("read_watch_data.sh"), idx("watch_admin_keys.py"), idx("Alarm (an issue"), idx("publish_watch_data.sh")
        self.assertLess(a, b); self.assertLess(b, c); self.assertLess(c, d); self.assertEqual(d, len(st) - 1)   # recording is the last step

    def test_a_red_run_records_nothing(self):
        st = self.steps(); rec = [s for s in st if "publish_watch_data.sh" in s][0]
        self.assertNotIn("always()", rec); self.assertNotIn("continue-on-error", rec); self.assertNotIn("failure()", rec)
        alarm = [s for s in st if s.startswith("name: Alarm")][0]; self.assertIn("exit 1", alarm)   # no token: red, before the recording

    def test_a_run_that_moved_or_contradicts_the_chain_is_not_published(self):
        st = self.steps(); rec = [s for s in st if "publish_watch_data.sh" in s][0]
        self.assertIn("if: steps.run.outputs.code != '2' && steps.run.outputs.code != '3'", rec)   # the same two codes that raise the alarm
        alarm = [s for s in st if s.startswith("name: Alarm")][0]; self.assertIn("steps.run.outputs.code == '2' || steps.run.outputs.code == '3'", alarm)
        note = [s for s in st if "is not recorded on watch-data" in s][0]; self.assertIn("code == '2' || steps.run.outputs.code == '3'", note)

    def run_step(self, code, lines):
        """runs the real `run:` text of the step that reads the chain, with a stub of the script that prints `lines` and exits with `code`; returns (stdout, GITHUB_OUTPUT)"""
        step = [s for s in self.steps() if "id: run" in s][0]
        script = textwrap.dedent(step[step.index("run: |") + len("run: |\n"):])
        d = Path(tempfile.mkdtemp()); (d / "scripts").mkdir(); (d / "watch").mkdir(); (d / "watch" / "cases.json").write_text("{}")
        (d / "scripts" / "watch_admin_keys.py").write_text("import sys\nprint(%r)\nsys.exit(%d)\n" % ("\n".join(lines), code))
        out = d / "out.txt"; out.write_text("")
        r = subprocess.run(["bash", "-c", script], cwd=d, capture_output=True, text=True, env=dict(os.environ, RUNNER_TEMP=str(d), GITHUB_OUTPUT=str(out)))
        return r.stdout, out.read_text()

    def test_the_public_log_of_a_moved_run_names_neither_the_moved_read_nor_the_unmoved_ones(self):
        lines = ["MOVED   Alpha vault admin: 0xaaaa -> 0xbbbb", "ok      Beta vault admin: 0xcccc", "ok      Gamma timelock: 172800", "", "31 case(s), 78 check(s): 1 moved, 0 unread."]
        for code in (2, 3):
            out, github_output = self.run_step(code, lines)
            for hidden in ("Alpha", "Beta", "Gamma", "0xaaaa", "0xcccc"):
                self.assertNotIn(hidden, out, "code %d shows %s" % (code, hidden))
            self.assertIn("31 case(s)", out); self.assertIn("code=%d" % code, github_output)

    def test_the_public_log_of_a_quiet_run_keeps_the_reads(self):
        out, github_output = self.run_step(0, ["ok      Beta vault admin: 0xcccc", "31 case(s), 78 check(s): 0 moved, 0 unread."])
        self.assertIn("Beta vault admin", out); self.assertIn("code=0", github_output)

    def test_main_receives_no_commit_from_the_watch(self):
        text = WORKFLOW.read_text()
        for bad in ("git push", "git commit", "git add", "check_mirror", "watch/status.json"):
            self.assertNotIn(bad, text.replace("# ", "\n# "), bad)
        self.assertIn("watch-data", text)
        pub = (HERE / "publish_watch_data.sh").read_text()
        self.assertIn("HEAD:refs/heads/watch-data", pub); self.assertNotIn("refs/heads/main", pub); self.assertNotIn("--force", pub)

    def test_the_state_files_are_not_on_main_any_more(self):
        self.assertFalse((HERE.parent / "watch" / "status.json").exists()); self.assertFalse((HERE.parent / "watch" / "snapshot.json").exists())
        self.assertTrue((HERE.parent / "watch" / "cases.json").exists()); self.assertFalse((HERE / "check_mirror.py").exists())


if __name__ == "__main__":
    unittest.main()
