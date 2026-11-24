# DeFi Admin-Key Risk Scanner


Which DeFi protocols let one key change or move things? This repository lists single-key admin cases checked by hand on-chain, each with its source, and `python3 scripts/watch_admin_keys.py --out "$(mktemp -d)"` re-reads the cited keys. It is not an audit.

![License: CC BY 4.0](https://img.shields.io/badge/license-CC%20BY%204.0-blue) ![Code: MIT](https://img.shields.io/badge/code-MIT-blue)
![Cases found](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2FRealSpap%2Fdefi-admin-key-risk-showcase%2Fmain%2Fbadge-data-cases-found.json&cachebust=20260930)
[![Check a contract: free tool](https://img.shields.io/badge/check%20a%20contract-free%20tool-orange)](https://realspap.github.io/tools/admin-key-checker.html)

**The headline finding:** 30 single-key admin cases (2 Critical, 13 High, 7 Medium, 8 Low) among 108 DeFi protocols and Morpho vault owners checked by hand on-chain. The pattern is the one behind Wasabi Protocol's $5.9M loss in April 2026: admin control held by one key, with no multisig threshold in front of it. Several cases are bounded by a timelock or a guardian, and each row says so.

[Full findings](docs/findings.md) · [Method and counting rule](docs/method.md) · [Sample authority sheets](authority-sheets) · [Request a check of your protocol](https://x.com/RealSpap)

## At a glance

| Protocol | Defect type | Amount under the key | Severity |
|---|---|---|---|
| Aurus (TXAU/TXAG/TXPT) | Bare EOA | ~$900K (real market cap) | High |
| cVault Finance / CORE | Bare EOA | $3.84M+ | Critical |
| Smilee Finance / gBERA | AccessControl, 4 holders but only 2 effective keys, no threshold | ~$1.05M (was ~$750K at the first check, WBERA price up) | High |
| DELTA LSW (cVault legacy) | Bare EOA (via wrapper contract) | ~$36K | Medium |
| Fake World Assets / FWA | Bare EOA | No dollar figure (risk is future proceeds routing, not funds already parked; the contract itself holds ~$160) | Critical |
| TokenWorks NFT Strategies (same key as FWA) | Bare EOA | No dollar figure (fee routing and transfer gating; the ~22 ETH and 37 CryptoPunks treasury is walled off by a restricted final-owner contract) | Medium |
| UwU Lend | Bare EOA | $48,000 to $62,000 | High |
| JayPeggers | Bare EOA | ~$188,460 | Medium |
| APY Finance | 1-of-N Safe | ~$51,300 (of which ~$18,500 sits directly in the Safe) | High |
| DeFIL | Bare EOA, dormant | No dollar figure | Low |
| ChickenSwap | Bare EOA, dormant | ~$150.57 (pool liquidity) | Low |
| MiniSwap | Bare EOA, dormant | ~$277.41 (pool liquidity) | Low |
| Mars Poolin | Bare EOA, dormant | ~$0.10 (pool liquidity) | Low |
| Sentora (Morpho PYUSD and RLUSD vaults) | 1-of-1 Safe (owner and curator) | ~$743M deposited in the two vaults on 2026-11-14, not directly drainable (3-day timelock, withdrawals cannot be gated) | Medium |
| UltraYield (Morpho vaults) | 1-of-N Safe (1 of 5) | ~$240K | Medium |
| K3 Capital (Morpho vault) | 1-of-N Safe (1 of 3) | ~$0 (empty vault) | Low |
| frobUSDC (Morpho vault, Arbitrum) | 1-of-1 Safe | ~$1.1M deposited, not instantly drainable (24-hour timelock, live guardian) | Medium |
| Duplicated Key (Morpho vault) | Bare EOA, also its own guardian and curator, zero timelock | ~$1.26M of third-party assets, currently frozen at 100% market utilisation | Medium |
| 1337 USDC (Morpho vault) | Bare EOA, zero timelock, no guardian, no curator | No dollar figure (the vault's stated $175.7M is accrued interest on a frozen sdeUSD claim, see below) | Low |
| Not Gauntlet (Morpho vault, Arbitrum) | Bare EOA, zero timelock, no guardian | No dollar figure (owner holds 99.73% of the shares, and the position is frozen) | Low |
| Clearstar and 3Jane (15 Morpho vaults, 2 chains) | Bare EOA owner on Ethereum and Base at once | ~$6.3M stated, bounded by a 72-hour timelock and a separate guardian on every vault | Low |
| Reservoir rUSD / srUSD | Bare EOA, sole admin, can grant itself minting | ~$852K on Ethereum (rUSD ~$230K, srUSD ~$622K), protocol TVL $72.1M across chains | High |
| OpenEden USDO | Bare EOA on upgrade, admin and mint (regulated RWA issuer, where direct issuer control is often by design) | ~$14.0M to $14.3M | High |
| Agora AUSD | Bare EOA owns the proxy admin (upgrade), no timelock (fiat-backed issuer, where direct issuer control is often by design) | ~$77.2M | High |
| Socket Gateway | Bare EOA, sole owner, adds and removes the routes that run against users' token approvals | No dollar figure (exposure is users' outstanding approvals, not funds held by the contract) | High |
| Kraken kBTC | Bare EOA owns the token and its upgrade (regulated custodian, issuer control by design) | ~$573M | High |
| Coinbase cbETH | Bare EOA upgrade key, never used on-chain; owner and minter admin are also bare EOAs (regulated issuer) | ~$1.20B | High |
| Coinbase cbBTC | Bare EOA upgrade key, never used on-chain; owner and minter admin are also bare EOAs (regulated issuer) | ~$3.84B | High |
| Binance wBETH | Two bare EOAs: one upgrades the token, the other is owner, minter admin, pauser and blacklister at once (exchange issuer) | ~$9.4B | High |
| StakeStone STONE | Bare EOA owns the token's bridge trust settings (an indirect mint path) and the vault's fee and strategy cleanup, no timelock | ~$21.2M (Ethereum supply) | High |

By severity: 2 Critical, 13 High, 7 Medium, 8 Low, across the 30 cases above. cVault Finance/CORE and Fake World Assets currently share the top spot: both Critical, both with documented hostile activity around the key (phishing-tagged incoming transfers), not only a weak setup.

## Check it yourself

One command re-reads, on the chain, who holds each authority this README states: the 31 cases and 78 reads of `watch/cases.json` (the 30 cases of the table, with Clearstar and 3Jane counted once for each chain), on Ethereum mainnet (chain ID 1), Arbitrum One (chain ID 42161), Base (chain ID 8453) and Berachain (chain ID 80094). It needs no key, only public RPC endpoints and the Python standard library, and takes about 40 seconds:

- `python3 scripts/watch_admin_keys.py --out "$(mktemp -d)"`

My run, read at 07:00Z on 2026-11-14, read the heads Ethereum mainnet 26411588, Arbitrum One 524089473, Base 57246327 and Berachain 28812461, and printed these two last lines:

- `Baseline written: 78 checks on 31 cases, 0 unread.`
- `31 case(s), 78 check(s): 0 moved, 0 unread.`

In a fresh folder, as above, the script writes a baseline only if no read contradicts what the registry says the README claims; otherwise it stops with exit code 3. The other exit codes are 0 (every read matched), 1 (a read failed: an RPC error is never counted as unchanged) and 2 (something moved against the previous snapshot, kept on the `watch-data` branch). This shows that the type of each authority (a bare account, a Safe of t of n owners, a timelock delay) and its address are, at those heads, what the README says. It does not show amounts, intentions, or that a key held behind a Safe belongs to one person. The script never asks an endpoint for its chain ID: I asked each endpoint named in `watch/cases.json` on 2026-11-14, and the answer was 1 on all three Ethereum endpoints, 42161 on both Arbitrum endpoints, 8453 on both Base endpoints and 80094 on both Berachain endpoints.

## What is inside

| Where | What |
|---|---|
| [docs/findings.md](docs/findings.md) | The cases, each with its addresses, networks and on-chain reads, then what came back safe and the pattern |
| [docs/method.md](docs/method.md) | The counting rule, the severity scale, what happened to Wasabi, and the method |
| [docs/limits.md](docs/limits.md) | The disclaimer, the caveats and the status of the last research pass |
| [docs/about.md](docs/about.md) | Access to the tool, the sample authority sheets, about, licence |
| [watch/cases.json](watch/cases.json) | The cases the daily Watch re-reads |

## Help

Found a case that moved, or a read that does not match? Open an issue with the chain, the address and the command you ran: see [CONTRIBUTING](.github/CONTRIBUTING.md) and [SECURITY](.github/SECURITY.md).

## Licence

Findings, data, documentation and the sample authority sheets: [CC BY 4.0](LICENSE). Scripts and workflows: [MIT](LICENSE-CODE). Cite with [CITATION.cff](CITATION.cff). Details in [docs/about.md](docs/about.md).
