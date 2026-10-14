#!/usr/bin/env python3
"""Re-read, on-chain, every admin key this research has published, and say what moved.

The README states, case by case, who holds the upgrade or admin authority of a contract: a bare EOA, a 1-of-N Safe,
a timelock with a given delay. Those are point-in-time reads. This script re-reads the same things from a public RPC,
compares them with the previous run (watch/snapshot.json) and reports every change: the authority address moved, code
appeared at an address that was a bare wallet, a Safe's threshold or owner count changed, a timelock's delay changed,
a role was granted or revoked. Standard library only, read-only, no key.

Registry: watch/cases.json. Each case lists checks; each check is one read:
  owner | admin | eip1967_admin | zeppelin_admin | getter (any address-returning view, by selector)
      -> the address read, then what it is (eoa / safe t-of-n / timelock delay / contract / zero)
  safe        -> threshold and owner count of a Safe
  min_delay   -> getMinDelay() of an OpenZeppelin TimelockController
  has_role    -> hasRole(role, account) on an AccessControl contract
  code        -> whether an address has code (a bare wallet that becomes a contract, or the reverse)
  uint        -> any uint-returning view, by selector (a vault's timelock(), for instance)
An optional "expect" on a check (eoa, safe:1, safe, timelock, contract, zero, true, false, or a number) is what the
README claims; the first run refuses to write a baseline that contradicts it, so the registry is proven against the
chain before it is trusted. Later runs compare with the snapshot, not with "expect".

Exit codes: 0 nothing moved; 2 something moved (watch/drift.md written); 1 a read failed and nothing moved (an RPC
error is never "unchanged"); 3 the registry contradicts the chain at baseline. watch/status.json is always written.
Usage: python3 watch_admin_keys.py [--registry watch/cases.json] [--out watch] [--published-only]
"""
import argparse, json, os, sys, time, urllib.request
from datetime import datetime, timezone

SEL = {"owner": "8da5cb5b", "admin": "f851a440", "getThreshold": "e75235b8", "getOwners": "a0e67e2b",
       "getMinDelay": "f27a0c92", "hasRole": "91d14854"}
SLOT = {"eip1967_admin": "0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103",
        "zeppelin_admin": "0x10d6a54a4754c8869d6886b5f5d7fbfa5b4522237ea5c60d11bc4e7a1ff9390b"}
UA = "Mozilla/5.0 (admin-key watch; github.com/RealSpap)"


class Reverted(RuntimeError):
    """Every endpoint answered, and the answer was "execution reverted": the contract says no. That is a result,
    unlike a transport failure, which is no result at all."""


def is_revert(err):
    return err.get("code") == 3 or "revert" in str(err.get("message", "")).lower()


class Rpc:
    def __init__(self, urls):
        self.urls, self.errors = urls, []

    def call(self, method, params):
        last = None
        answered = reverts = 0
        for u in self.urls:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
            req = urllib.request.Request(u, body, {"Content-Type": "application/json", "User-Agent": UA})
            for attempt in range(2):
                try:
                    with urllib.request.urlopen(req, timeout=25) as r:
                        d = json.loads(r.read())
                    if "error" in d:
                        last = "%s: %s" % (u, d["error"])   # a protocol error: try the next endpoint
                        answered += 1
                        reverts += is_revert(d["error"])
                        break
                    return d["result"]
                except Exception as e:   # transport: one retry, then the next endpoint
                    last = "%s: %s" % (u, e); time.sleep(1.5)
        if answered == len(self.urls) and reverts == answered:
            raise Reverted("all endpoints reverted for %s: %s" % (method, last))
        raise RuntimeError("all endpoints failed for %s: %s" % (method, last))

    def eth_call(self, to, data):
        return self.call("eth_call", [{"to": to, "data": data}, "latest"])

    def code_len(self, addr):
        return (len(self.call("eth_getCode", [addr, "latest"])) - 2) // 2

    def storage(self, addr, slot):
        return self.call("eth_getStorageAt", [addr, slot, "latest"])

    def head(self):
        return int(self.call("eth_blockNumber", []), 16)


def word_addr(w):
    w = (w or "0x")[2:].rjust(64, "0")
    return "0x" + w[-40:]


def pad_addr(a):
    return a[2:].lower().rjust(64, "0")


def classify(rpc, addr):
    """What an address is: zero / eoa / safe (threshold, owners) / timelock (delay) / contract.
    A transport failure raises (the check is then "unread"); only a real revert means "not a Safe"."""
    if int(addr, 16) == 0:
        return {"kind": "zero"}
    if rpc.code_len(addr) == 0:
        return {"kind": "eoa"}
    try:
        t = int(rpc.eth_call(addr, "0x" + SEL["getThreshold"]), 16)
        raw = rpc.eth_call(addr, "0x" + SEL["getOwners"])
        n = int(raw[2 + 64:2 + 128], 16) if len(raw) >= 2 + 128 else 0
        if 0 < t <= 50 and n >= t:
            return {"kind": "safe", "threshold": t, "owners": n}
    except (Reverted, ValueError):   # the contract answered "not a Safe"; a network failure is NOT caught here
        pass
    try:
        d = rpc.eth_call(addr, "0x" + SEL["getMinDelay"])
        if d and d != "0x":
            return {"kind": "timelock", "delay_seconds": int(d, 16)}
    except (Reverted, ValueError):
        pass
    return {"kind": "contract"}


def read(rpc, c):
    on = c["on"]
    kind = c["read"]
    if kind in ("owner", "admin"):
        a = word_addr(rpc.eth_call(on, "0x" + SEL[kind])); return dict(address=a, **classify(rpc, a))
    if kind in SLOT:
        a = word_addr(rpc.storage(on, SLOT[kind])); return dict(address=a, **classify(rpc, a))
    if kind == "getter":
        a = word_addr(rpc.eth_call(on, "0x" + c["selector"])); return dict(address=a, **classify(rpc, a))
    if kind == "safe":
        r = classify(rpc, on)
        if r["kind"] != "safe":
            return {"kind": r["kind"], "note": "no longer answers as a Safe"}
        return r
    if kind == "min_delay":
        return {"kind": "timelock", "delay_seconds": int(rpc.eth_call(on, "0x" + SEL["getMinDelay"]), 16)}
    if kind == "has_role":
        data = "0x" + SEL["hasRole"] + c["role"][2:].lower().rjust(64, "0") + pad_addr(c["account"])
        return {"kind": "bool", "value": int(rpc.eth_call(on, data), 16) == 1}
    if kind == "code":
        n = rpc.code_len(on); return {"kind": "eoa" if n == 0 else "contract", "code_bytes": n}
    if kind == "uint":
        return {"kind": "uint", "value": int(rpc.eth_call(on, "0x" + c["selector"]), 16)}
    raise ValueError("unknown read kind %r" % kind)


def matches(expect, r):
    if expect is None:
        return True
    if expect in ("eoa", "safe", "timelock", "contract", "zero"):
        return r.get("kind") == expect
    if expect.startswith("safe:"):
        return r.get("kind") == "safe" and r.get("threshold") == int(expect[5:])
    if expect in ("true", "false"):
        return r.get("kind") == "bool" and r.get("value") is (expect == "true")
    return str(r.get("value") if "value" in r else r.get("delay_seconds")) == expect   # a number: a uint read, or a timelock delay


def same(a, b):
    keys = ("address", "kind", "threshold", "owners", "delay_seconds", "value")
    return all(a.get(k) == b.get(k) for k in keys) and (a.get("kind") != "eoa" or b.get("kind") == "eoa")


def describe(r):
    k = r.get("kind")
    s = {"eoa": "bare EOA", "zero": "zero address", "contract": "contract", "bool": str(r.get("value")).lower(),
         "uint": str(r.get("value")), "timelock": "timelock, %ss delay" % r.get("delay_seconds"),
         "safe": "Safe %s-of-%s" % (r.get("threshold"), r.get("owners"))}.get(k, k)
    return ("%s (%s)" % (r["address"], s)) if r.get("address") else s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", default="watch/cases.json"); ap.add_argument("--out", default="watch")
    ap.add_argument("--published-only", action="store_true", help="skip cases not yet in the public write-up")
    a = ap.parse_args()
    reg = json.load(open(a.registry))
    os.makedirs(a.out, exist_ok=True)
    snap_path = os.path.join(a.out, "snapshot.json")
    snap = json.load(open(snap_path)) if os.path.exists(snap_path) else None
    baseline = snap is None
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rpcs = {k: Rpc(v["rpc"]) for k, v in reg["chains"].items()}
    heads = {}
    for k, r in rpcs.items():
        try: heads[k] = r.head()
        except Exception as e: heads[k] = "unread: %s" % e
    results, drifts, unread, contradictions = {}, [], [], []
    n_cases = n_checks = 0
    for case in reg["cases"]:
        if a.published_only and not case.get("published", True):
            continue
        n_cases += 1
        for i, c in enumerate(case["checks"]):
            n_checks += 1
            key = "%s#%d" % (case["id"], i)
            label = "%s: %s" % (case["name"], c["what"])
            try:
                r = read(rpcs[case["chain"]], c)
            except Exception as e:
                unread.append({"key": key, "label": label, "error": str(e)[:300]})
                print("UNREAD  %s: %s" % (label, str(e)[:160])); continue
            results[key] = dict(r, label=label, chain=case["chain"], on=c["on"], read=c["read"])
            if baseline and not matches(c.get("expect"), r):
                contradictions.append({"key": key, "label": label, "expect": c["expect"], "read": describe(r)})
                print("CONTRADICTS  %s: expected %s, chain says %s" % (label, c["expect"], describe(r))); continue
            prev = (snap or {}).get("results", {}).get(key)
            if prev and not same(prev, r):
                drifts.append({"key": key, "label": label, "chain": case["chain"], "on": c["on"], "severity": case.get("severity"),
                               "before": describe(prev), "after": describe(r), "published": case.get("published", True)})
                print("MOVED   %s: %s -> %s" % (label, describe(prev), describe(r)))
            else:
                print("ok      %s: %s" % (label, describe(r)))
    status = {"run_utc": now, "baseline_established": baseline and not contradictions, "chain_heads": heads,
              "cases": n_cases, "checks": n_checks, "read": len(results), "unread": unread, "moved": len(drifts),
              "contradictions": contradictions, "note": "an unread check is a check not made this run, never an unchanged one"}
    json.dump(status, open(os.path.join(a.out, "status.json"), "w"), indent=1)
    if contradictions:
        print("\n%d check(s) contradict the registry: no baseline written, fix watch/cases.json or the README first." % len(contradictions))
        sys.exit(3)
    if baseline:
        json.dump({"written_utc": now, "results": results}, open(snap_path, "w"), indent=1)
        print("\nBaseline written: %d checks on %d cases, %d unread." % (len(results), n_cases, len(unread)))
    else:
        # the snapshot moves forward only for checks read this run; an unread check keeps its last known state
        merged = dict(snap["results"]); merged.update(results)
        json.dump({"written_utc": now, "results": merged, "previous_utc": snap.get("written_utc")}, open(snap_path, "w"), indent=1)
    md = os.path.join(a.out, "drift.md")
    if drifts or unread:
        lines = ["## Admin-key watch, %s" % now, ""]
        if drifts:
            lines += ["### %d published read(s) moved" % len(drifts), ""]
            for d in drifts:
                exp = reg["chains"][d["chain"]].get("explorer", "")
                lines.append("- **%s** (%s): %s -> %s. Contract [`%s`](%s%s)." % (d["label"], d["severity"] or "-", d["before"], d["after"], d["on"], exp, d["on"]))
            lines += ["", "Re-read the case by hand, then update the README and the registry if a published finding changed."]
        if unread:
            lines += ["", "### %d check(s) not read this run (RPC), not compared" % len(unread), ""]
            lines += ["- %s: `%s`" % (u["label"], u["error"][:200]) for u in unread]
        open(md, "w").write("\n".join(lines) + "\n")
    elif os.path.exists(md):
        os.remove(md)
    print("\n%d case(s), %d check(s): %d moved, %d unread." % (n_cases, n_checks, len(drifts), len(unread)))
    sys.exit(2 if drifts else (1 if unread else 0))


if __name__ == "__main__":
    main()
