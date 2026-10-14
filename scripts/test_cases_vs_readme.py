#!/usr/bin/env python3
"""Consistency guard: every published case of the watch registry must carry the severity the README table gives it.

The watch registry (cases.json) and the README table are written by hand in two places. TokenWorks was filed "High" in
the registry while the README, and the evidence behind it, say "Medium"; nothing noticed. This test reads both and
fails on any published case that has no README row, or whose severity differs from its row.
A case is matched to a README row by the first two words of its name (Clearstar and 3Jane is two watch cases, one row).
Run: python3 test_cases_vs_readme.py    (no network)
"""
import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
# showcase layout: scripts/ and watch/ next to README.md ; private layout: .github/scripts/ and .github/watch/, README in ../depot-showcase
CANDIDATES = [
    (os.path.join(HERE, "..", "watch", "cases.json"), os.path.join(HERE, "..", "README.md")),
    (os.path.join(HERE, "..", "..", ".github", "watch", "cases.json"), os.path.join(HERE, "..", "..", "..", "depot-showcase", "README.md")),
]


def key(name):
    return " ".join(re.findall(r"[a-z0-9]+", name.lower())[:2])


def readme_rows(path):
    rows = {}
    for line in open(path, encoding="utf-8"):
        if line.startswith("|") and re.search(r"\|\s*(Critical|High|Medium|Low)\s*\|\s*$", line):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            rows[key(cells[0])] = (cells[0], cells[-1])
    return rows


class CasesVsReadme(unittest.TestCase):
    def test_published_cases_match_readme_severity(self):
        pair = next(((c, r) for c, r in CANDIDATES if os.path.exists(c) and os.path.exists(r)), None)
        if pair is None:
            self.skipTest("no README next to the registry in this checkout")
        cases = json.load(open(pair[0]))["cases"]
        rows = readme_rows(pair[1])
        self.assertTrue(rows, "no severity table found in the README")
        problems = []
        for c in cases:
            if not c.get("published", True):
                continue
            row = rows.get(key(c["name"]))
            if row is None:
                problems.append("%s: no README row" % c["name"])
            elif row[1] != c["severity"]:
                problems.append("%s: registry %s, README %s (%s)" % (c["name"], c["severity"], row[1], row[0]))
        self.assertEqual(problems, [])

    def test_the_guard_sees_a_mismatch(self):
        # control: the matching logic flags a wrong severity (so a green run above means something)
        rows = {key("TokenWorks NFT Strategies (same key as FWA)"): ("TokenWorks NFT Strategies (same key as FWA)", "Medium")}
        case = {"name": "TokenWorks NFT Strategies", "severity": "High"}
        self.assertNotEqual(rows[key(case["name"])][1], case["severity"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
