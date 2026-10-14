#!/usr/bin/env python3
"""Tests for watch_admin_keys.py: a network failure is never a change.

Before the fix, classify() swallowed every exception while reading a Safe's threshold, so a transport failure filed the
Safe as a plain contract and the watch reported a false MOVED. A real revert ("this is not a Safe") is an answer; an
outage is not. One endpoint being down while another answers "reverted" is still an answer.
Run: python3 test_watch_admin_keys.py   (no network, no repository file is modified)
"""
import contextlib
import importlib.util
import io
import json
import os
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("watch_admin_keys", os.path.join(HERE, "watch_admin_keys.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

ADDR = "0x" + "11" * 20
ON = "0x" + "aa" * 20
PAD = lambda a: "0x" + "0" * 24 + a[2:]
ONE_WORD = lambda n: "0x" + hex(n)[2:].rjust(64, "0")
OWNERS5 = "0x" + hex(32)[2:].rjust(64, "0") + hex(5)[2:].rjust(64, "0") + "".join("0" * 63 + str(i + 1) for i in range(5))
CURRENT = {"url": None}


class Resp:
    def __init__(self, obj):
        self.b = json.dumps(obj).encode()

    def read(self):
        return self.b

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def fake_urlopen(handler):
    def urlopen(req, timeout=None):
        CURRENT["url"] = req.full_url
        body = json.loads(req.data)
        kind, *val = handler(body["method"], body["params"])
        if kind == "transport":
            raise OSError("connection reset")
        if kind == "revert":
            return Resp({"jsonrpc": "2.0", "id": 1, "error": {"code": 3, "message": "execution reverted"}})
        return Resp({"jsonrpc": "2.0", "id": 1, "result": val[0]})
    return urlopen


def selector(params):
    return params[0].get("data", "")[2:10]


class ClassifyTest(unittest.TestCase):
    def classify(self, handler, urls=("http://rpc.example",)):
        with mock.patch.object(m.urllib.request, "urlopen", fake_urlopen(handler)), mock.patch.object(m.time, "sleep"):
            return m.classify(m.Rpc(list(urls)), ADDR)

    def test_transport_failure_is_not_a_contract(self):
        def h(method, params):
            if method == "eth_getCode":
                return ("ok", "0x6080")
            return ("transport",)
        with self.assertRaises(Exception):
            self.classify(h)

    def test_plain_revert_stays_a_contract(self):
        # control: a contract that really reverts on getThreshold and getMinDelay is neither a Safe nor a timelock
        def h(method, params):
            if method == "eth_getCode":
                return ("ok", "0x6080")
            return ("revert",)
        self.assertEqual(self.classify(h), {"kind": "contract"})

    def test_safe_recognised(self):
        def h(method, params):
            if method == "eth_getCode":
                return ("ok", "0x6080")
            return ("ok", ONE_WORD(2)) if selector(params) == m.SEL["getThreshold"] else ("ok", OWNERS5)
        self.assertEqual(self.classify(h), {"kind": "safe", "threshold": 2, "owners": 5})

    def test_one_endpoint_down_and_one_revert_is_a_contract(self):
        # an endpoint that refuses eth_call (drpc answers HTTP 400) must not turn a real revert elsewhere into "unread"
        def h(method, params):
            if method == "eth_getCode":
                return ("ok", "0x6080")
            return ("transport",) if CURRENT["url"] == "http://down.example" else ("revert",)
        self.assertEqual(self.classify(h, urls=("http://down.example", "http://up.example")), {"kind": "contract"})

    def test_every_endpoint_down_stays_an_error(self):
        # control for the rule above: with no endpoint answering at all, nothing is concluded
        def h(method, params):
            if method == "eth_getCode":
                return ("ok", "0x6080")
            return ("transport",)
        with self.assertRaises(Exception):
            self.classify(h, urls=("http://a.example", "http://b.example"))


class MainTest(unittest.TestCase):
    def run_main(self, handler):
        with tempfile.TemporaryDirectory() as d:
            reg = os.path.join(d, "cases.json")
            out = os.path.join(d, "out")
            os.makedirs(out)
            json.dump({"chains": {"eth": {"rpc": ["http://rpc.example"]}},
                       "cases": [{"id": "c1", "name": "Case", "chain": "eth", "severity": "High",
                                  "checks": [{"what": "owner", "read": "owner", "on": ON}]}]}, open(reg, "w"))
            json.dump({"written_utc": "2026-10-13T00:00:00Z",
                       "results": {"c1#0": {"address": ADDR, "kind": "safe", "threshold": 2, "owners": 5}}},
                      open(os.path.join(out, "snapshot.json"), "w"))
            buf = io.StringIO()
            code = None
            with mock.patch.object(m.urllib.request, "urlopen", fake_urlopen(handler)), mock.patch.object(m.time, "sleep"), \
                 mock.patch("sys.argv", ["watch_admin_keys.py", "--registry", reg, "--out", out]), contextlib.redirect_stdout(buf):
                try:
                    m.main()
                except SystemExit as e:
                    code = e.code
            return code, buf.getvalue()

    def test_outage_does_not_trigger_moved(self):
        def h(method, params):
            if method == "eth_blockNumber":
                return ("ok", "0x10")
            if method == "eth_getCode":
                return ("ok", "0x6080")
            if selector(params) == m.SEL["owner"]:
                return ("ok", PAD(ADDR))
            return ("transport",)  # getThreshold and the rest: the network goes down
        code, out = self.run_main(h)
        self.assertNotIn("MOVED", out)
        self.assertEqual(code, 1, "exit 1 = a read was missed, nothing moved")

    def test_real_change_is_still_reported(self):
        # control: if the Safe really stopped being a Safe (plain revert), the change is announced
        def h(method, params):
            if method == "eth_blockNumber":
                return ("ok", "0x10")
            if method == "eth_getCode":
                return ("ok", "0x6080")
            if selector(params) == m.SEL["owner"]:
                return ("ok", PAD(ADDR))
            return ("revert",)
        code, out = self.run_main(h)
        self.assertIn("MOVED", out)
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
