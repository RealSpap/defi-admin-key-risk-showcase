"""sync_badges.py --check : exit 0 when the badge follows the README, exit 3 (and no write) when it does not."""
import json, subprocess, sys, tempfile, unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "sync_badges.py"


def run(cases_in_readme, badge_message):
    d = Path(tempfile.mkdtemp())
    (d / "README.md").write_text("By severity: 2 Critical, 13 High, across the %s cases above.\n" % cases_in_readme, encoding="utf-8")
    (d / "badge-data-cases-found.json").write_text(json.dumps({"schemaVersion": 1, "label": "cases found", "message": badge_message}) + "\n", encoding="utf-8")
    r = subprocess.run([sys.executable, "-I", str(SCRIPT), "--repo-root", str(d), "--check"], capture_output=True, text=True)
    return r.returncode, json.loads((d / "badge-data-cases-found.json").read_text())["message"]


class CheckMode(unittest.TestCase):
    def test_matching_badge_passes(self):
        self.assertEqual(run(30, "30"), (0, "30"))

    def test_stale_badge_fails_and_is_not_rewritten(self):
        self.assertEqual(run(30, "29"), (3, "29"))


if __name__ == "__main__":
    unittest.main()
