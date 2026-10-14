#!/usr/bin/env python3
"""Tests de watch_admin_keys.py : une erreur de réseau n'est jamais un changement.

Avant le correctif, classify() avalait toute exception pendant la lecture du seuil d'un Safe : une panne de transport
rangeait donc un Safe parmi les « contract » et la veille annonçait un faux MOVED. Une lecture qui revert vraiment
(« ce n'est pas un Safe ») reste une réponse, une panne n'en est pas une.
Lancer : python3 test_watch_admin_keys.py   (aucun réseau, aucun fichier du dépôt modifié)
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
    def classify(self, handler):
        with mock.patch.object(m.urllib.request, "urlopen", fake_urlopen(handler)), mock.patch.object(m.time, "sleep"):
            return m.classify(m.Rpc(["http://rpc.example"]), ADDR)

    def test_panne_de_transport_n_est_pas_un_contract(self):
        def h(method, params):
            if method == "eth_getCode":
                return ("ok", "0x6080")
            return ("transport",)
        with self.assertRaises(Exception):
            self.classify(h)

    def test_revert_franc_reste_un_contract(self):
        # témoin : un contrat qui revert vraiment sur getThreshold et getMinDelay n'est ni un Safe ni un timelock
        def h(method, params):
            if method == "eth_getCode":
                return ("ok", "0x6080")
            return ("revert",)
        self.assertEqual(self.classify(h), {"kind": "contract"})

    def test_safe_reconnu(self):
        def h(method, params):
            if method == "eth_getCode":
                return ("ok", "0x6080")
            return ("ok", ONE_WORD(2)) if selector(params) == m.SEL["getThreshold"] else ("ok", OWNERS5)
        self.assertEqual(self.classify(h), {"kind": "safe", "threshold": 2, "owners": 5})


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

    def test_panne_ne_declenche_pas_de_moved(self):
        def h(method, params):
            if method == "eth_blockNumber":
                return ("ok", "0x10")
            if method == "eth_getCode":
                return ("ok", "0x6080")
            if selector(params) == m.SEL["owner"]:
                return ("ok", PAD(ADDR))
            return ("transport",)  # getThreshold et le reste : le réseau tombe
        code, out = self.run_main(h)
        self.assertNotIn("MOVED", out)
        self.assertEqual(code, 1, "code 1 = lecture manquée, rien n'a bougé")

    def test_vrai_changement_reste_detecte(self):
        # témoin : si le Safe a vraiment perdu son statut (revert franc), le changement est bien annoncé
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
