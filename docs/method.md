# Method, counting rule and what happened

Every case below is described in [What it found, checked by hand](findings.md#what-it-found-checked-by-hand) (the case about 1337 USDC is on top of [that file](findings.md)), with the contract addresses and on-chain reads it rests on. Defect types build on the categories defined in [Method](#method), with a short qualifier added where the case itself has one (a wrapper contract, a dormant key). Every dollar figure here is copied as-is from the case's own section; nothing here is a new calculation.

**Counting rule.** A *checked* entry is a protocol, or for Morpho vaults one owner address, whose admin roles were read on-chain by hand and which is named in this README: 108 in total, 30 in the table below and 78 under [What came back safe](findings.md#what-came-back-safe). A *case* is one product or vault set under one admin key, so a team can appear twice (Fake World Assets and TokenWorks share one key; DELTA LSW, a cVault Finance product, is counted as its own case).

Severity is not a code-bug scale, so the usual Critical/High/Medium/Low vocabulary is adapted to what actually matters for an admin key: **Critical** = the key is demonstrably active and there is documented hostile activity against it by a third party (phishing-tagged incoming transfers, address poisoning, or an unauthorized/malicious mint), not merely use of the key. **High** = the key is demonstrably active and holds real, undiminished power, but no hostile third-party activity has been documented; ordinary use by the project's own team, however risky the setup, falls here rather than Critical. **Medium** = the key or role is real but its practical reach is limited, either by a small amount at stake or by narrow on-chain powers (a bounded fee redirect rather than a full sweep). **Low** = the key has been dormant for years, or the amount at stake is negligible.

A single-key admin setup is a governance fact read from public chain data, not a code vulnerability: using the key requires its private key.



A few of these severity calls (Aurus, cVault Finance/CORE and FWA, DELTA LSW and JayPeggers, APY Finance) are not obvious from the number alone; see each case's own section below for the reasoning.

## What happened

On 2026-04-30, Wasabi Protocol lost ~$5.9M across Ethereum, Base, Berachain and Blast after an attacker compromised the private key of `wasabideployer.eth`. That single key held unchecked admin authority over every one of Wasabi's upgradeable vaults, with no multisig and no timelock. The protocol's own framework supported a timelock; it was just set to 0.

That is the whole reason admin keys matter: one key with upgrade or admin authority can move everything the contracts behind it control, whatever the quality of the code itself.

## Method

Checks the two most common real-world admin patterns, a single-address getter (`owner()`/`admin()`) and OpenZeppelin's standard `AccessControl`, and reports what actually holds that power today:

- **Renounced (0x0)**: nobody can call it. Immutable. The safe end of the spectrum.
- **Bare EOA**: a plain wallet, zero contract code. One leaked or phished key from total loss.
- **1-of-N Safe**: a real Gnosis Safe, but with a single signer. A multisig in name only.
- **Real multisig / Safe with threshold ≥ 2**: genuinely distributed control.
- **Other contract**: a Timelock or custom governance module, needing a manual look at who can actually propose into it.
