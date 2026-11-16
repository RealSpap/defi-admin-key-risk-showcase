# Contributing

This repository publishes a measurement: where one key still holds admin power over a live DeFi contract. Every way of helping ends in something anyone can re-read, not in an opinion. Replies are best effort, with no promised delay.

## Five first tasks

Each needs only Python 3 and a public RPC endpoint.

1. **Run the check.** `python3 scripts/watch_admin_keys.py --out "$(mktemp -d)"` re-reads each authority the README states. Tell me the exit code and the two last lines, with the date you ran it.
2. **Re-read one case by hand.** Pick a row of the table, read the owner or admin of its contract with `cast call`, and compare with the row.
3. **Check one bare key.** For a row marked Bare EOA, check that the address still has no code, and tell me if the key has since moved to a contract.
4. **Re-read one entry that came back safe.** Pick a protocol under What came back safe in docs/findings.md and re-read its admin role; tell me if the setup changed.
5. **Propose a case.** Open the Propose a case form with the address, the network and the chain ID of a contract held by one key.

## What I do not accept

- A change to a finding without evidence anyone can re-read (a transaction hash, a block number, an address with the call to make, a public document).
- Anything that holds a private key, a seed phrase, a password or private data.
- Statements about the character or intent of a named person.
- Promotional additions.

## Running the checks

```bash
python3 scripts/check_structure.py
```

It refuses a new entry at the root, a forbidden file name, a README over 80 lines or holding a dash.
