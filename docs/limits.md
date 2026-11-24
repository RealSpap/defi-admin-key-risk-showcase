# Limits, disclaimer and status

This research analyzes publicly available on-chain data specific to admin-key risk (smart contract code, multisig signer sets, governance transactions). None of the protocols named above were contacted prior to publication; every finding rests solely on that public on-chain data, not private communication. Full disclaimer and program-wide notes: [methodology](https://realspap.github.io/methodology.html).

## Caveats

This is a first-pass filter plus manual verification, not an audit. A few things it does not resolve:

- Aurus also runs a fourth, much smaller tokenized asset (a Canadian-gold product, "CGR") not counted in DefiLlama's TVL for the protocol: real, but negligible activity (7 transactions ever, $0 current balance).
- Six cases carry no dollar figure (DeFIL, Fake World Assets, TokenWorks NFT Strategies, 1337 USDC, Not Gauntlet and Socket Gateway), each for the reason given in its row: none of DeFIL's three collateral tokens (eFIL, mFIL, FILST) has a real DEX pool anywhere; FWA's and TokenWorks' risk is about fee and proceeds routing rather than funds within the key's reach; 1337 USDC's and Not Gauntlet's stated assets are accrued interest on frozen positions; Socket Gateway holds almost nothing itself, its exposure is the token approvals users have granted it.
- Amounts are measured on the check date given in each section, or at the first check where no date is given, and move with token prices: Smilee's gBERA went from ~$750K to ~$1.05M on the WBERA price alone.
- Reservoir's figure covers Ethereum only; the protocol is deployed on other chains that were not decomposed.
- Block explorers' "token holdings" aggregates can be badly inflated by spam tokens carrying fabricated prices. Every dollar figure in this research was decomposed token-by-token and cross-checked against a second price source before being trusted. Don't take a headline aggregate at face value, here or anywhere else.
- The tool only recognizes standard `Ownable`/`AccessControl`/Gnosis Safe patterns. A protocol that rolls its own bespoke access control (as Wasabi itself did) needs the source read by hand.
- An EOA seen on-chain could be an institutional MPC wallet; nothing on-chain can confirm or rule that out, and no case here claims otherwise.

This is independent research, not an audit or a security guarantee. Everything above is stated at the confidence level the on-chain data actually supports.

## Status

Last research pass: 2026-10-05 (issuer and bridge keys added 2026-10-01, Notional corrected 2026-10-05; before that, Reservoir rUSD and OpenEden USDO added, Treehouse tETH checked clean, Smilee gBERA re-checked on 2026-09-30). Cases were checked on different dates during September and October 2026, each section gives its date where it has one, and a key checked earlier can read differently today.

108 entries (protocols and Morpho vault owner addresses) checked by hand, under the counting rule in [At a glance](../README.md#at-a-glance). By severity, across the 30 cases in the table: 2 Critical, 13 High, 7 Medium, 8 Low. Each case is pushed to a real dollar figure or to a documented reason none is possible or none is reachable (six cases, listed in the caveats). The $20M-$100M TVL band has two zero-audit data points, Aegis YUSD and 3F, both clean at the root; Reservoir (protocol TVL $72.1M across chains, found outside that filter) is rated High. Still too few to call a pattern, so this isn't a finished survey.

Between research passes, every authority named above is re-read on-chain every day by [`.github/workflows/watch.yml`](../.github/workflows/watch.yml) (standard library, read-only, the protocols' own contracts and the key holders already named here, listed in [`watch/cases.json`](../watch/cases.json)). The last run is in [`status.json` on the `watch-data` branch](https://github.com/RealSpap/defi-admin-key-risk-showcase/blob/watch-data/status.json); when a read moves, the run opens an internal issue (a run that cannot raise that alarm turns red) and this published state stays at the last run without a move; the detail of the move is not published (the run shows only that something moved) until the case is re-verified by hand and this README changes. Every case in the table is covered, cVault's seven contracts and DELTA LSW included (addresses from cVault's own repository README).
