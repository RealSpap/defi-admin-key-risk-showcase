# DeFi Admin-Key Risk Scanner

![License](https://img.shields.io/badge/license-all%20rights%20reserved-blue)
![Status](https://img.shields.io/badge/status-active%20research-brightgreen)
![Cases found](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2FRealSpap%2Fdefi-admin-key-risk-showcase%2Fmain%2Fbadge-data-cases-found.json&cachebust=20260930)
[![Check a contract: free tool](https://img.shields.io/badge/check%20a%20contract-free%20tool-orange)](https://realspap.github.io/tools/admin-key-checker.html)
![Follow](https://img.shields.io/badge/follow-%40RealSpap-000000?logo=x)

**The headline finding:** 30 single-key admin cases (2 Critical, 13 High, 7 Medium, 8 Low) among 108 DeFi protocols and Morpho vault owners checked by hand on-chain. The pattern is the one behind Wasabi Protocol's $5.9M loss in April 2026: admin control held by one key, with no multisig threshold in front of it. Several cases are bounded by a timelock or a guardian, and each row says so.

[Full findings below](#what-it-found-checked-by-hand) · [Contact for licensing / custom research](https://x.com/RealSpap)

Independent, on-chain verified research into who really holds the upgrade/admin keys behind live DeFi protocols, anchored on a real 2026 incident, plus a check that finds the same pattern elsewhere. Findings and on-chain sources are always public; the verification method is available under license.

## At a glance

Every case below is described in [What it found, checked by hand](#what-it-found-checked-by-hand) (1337 USDC just below), with the contract addresses and on-chain reads it rests on. Defect types build on the categories defined in [Method](#method), with a short qualifier added where the case itself has one (a wrapper contract, a dormant key). Every dollar figure here is copied as-is from the case's own section; nothing here is a new calculation.

**Counting rule.** A *checked* entry is a protocol, or for Morpho vaults one owner address, whose admin roles were read on-chain by hand and which is named in this README: 108 in total, 30 in the table below and 78 under [What came back safe](#what-came-back-safe). A *case* is one product or vault set under one admin key, so a team can appear twice (Fake World Assets and TokenWorks share one key; DELTA LSW, a cVault Finance product, is counted as its own case).

Severity is not a code-bug scale, so the usual Critical/High/Medium/Low vocabulary is adapted to what actually matters for an admin key: **Critical** = the key is demonstrably active and there is documented hostile activity against it by a third party (phishing-tagged incoming transfers, address poisoning, or an unauthorized/malicious mint), not merely use of the key. **High** = the key is demonstrably active and holds real, undiminished power, but no hostile third-party activity has been documented; ordinary use by the project's own team, however risky the setup, falls here rather than Critical. **Medium** = the key or role is real but its practical reach is limited, either by a small amount at stake or by narrow on-chain powers (a bounded fee redirect rather than a full sweep). **Low** = the key has been dormant for years, or the amount at stake is negligible.

A single-key admin setup is a governance fact read from public chain data, not a code vulnerability: using the key requires its private key.

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
| Sentora (Morpho PYUSD and RLUSD vaults) | 1-of-1 Safe (owner and curator) | ~$814.7M deposited, not directly drainable (3-day timelock, withdrawals cannot be gated) | Medium |
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

A few of these severity calls (Aurus, cVault Finance/CORE and FWA, DELTA LSW and JayPeggers, APY Finance) are not obvious from the number alone; see each case's own section below for the reasoning.

### The number that isn't there: 1337 USDC

Added 2026-09-21. On the governance surface alone this is the weakest configuration in the whole survey: a Morpho vault owned by a bare, active EOA, with `timelock()` at zero, no guardian and no curator. Nothing on the contract delays that key, because with a zero timelock MetaMorpho's `submitCap` sets a market cap immediately instead of queuing it, and `setIsAllocator` is owner-only and instant. The vault's `totalAssets()` reads 175,710,955 USDC, and the owner holds none of the shares, so the obvious write-up is "$175.7M of other people's money behind one key."

That write-up would be wrong, and this section exists because the check that catches it is the whole point of this repository.

Walking the vault's own `withdrawQueue` market by market shows its entire position sitting in a single market collateralised by sdeUSD, Elixir's staked deUSD. That market's `totalSupplyAssets` and `totalBorrowAssets` are exactly equal: 100% utilisation, nothing withdrawable. A market frozen at full utilisation keeps accruing interest on both sides, which inflates the accounting value of a claim nobody can realise. Morpho's own front end shows the matching symptom on this vault, a net APY above 1000% and a 30-day average around 271,673%, and the curator has filed no risk disclosure.

So the defect is real and the number is not. This repository asserts no dollar figure for this case, and the same test knocked down "Not Gauntlet" on Arbitrum the same day, where the stated $6.5M is frozen xUSD exposure and the owner holds 99.73% of the shares anyway.

| | |
|---|---|
| **Vault** | `0x94643e86aa5E38DDAc6c7791C1297f4E40cD96c1` (Ethereum) |
| **Owner** | a bare EOA, `eth_getCode` empty on two independent endpoints, nonce 422 |
| **Delay and vetoes** | `timelock()` 0, `guardian()` zero address, `curator()` zero address |
| **Stated assets** | 175,710,955.16 USDC, identical on both endpoints |
| **What that number actually is** | one position in an sdeUSD market at 100% utilisation, so accrued interest on a claim that cannot be withdrawn |
| **Figure asserted here** | none |

## What happened

On 2026-04-30, Wasabi Protocol lost ~$5.9M across Ethereum, Base, Berachain and Blast after an attacker compromised the private key of `wasabideployer.eth`. That single key held unchecked admin authority over every one of Wasabi's upgradeable vaults, with no multisig and no timelock. The protocol's own framework supported a timelock; it was just set to 0.

That is the whole reason admin keys matter: one key with upgrade or admin authority can move everything the contracts behind it control, whatever the quality of the code itself.

## Access to the tool

Findings and on-chain sources are always public; the verification method is available under license. A case checked days or weeks ago can read differently today: admin keys get rotated, renounced, or compromised on-chain. Want to check one yourself right now, free? [Admin Key Checker](https://realspap.github.io/tools/admin-key-checker.html) classifies any contract's admin-key pattern live from chain, in your browser, no account needed. For a full check of a named protocol, with the dollar-figure decomposition and a look for documented hostile activity around the key, reach out via [Spap on X](https://x.com/RealSpap).

## Disclaimer

This research analyzes publicly available on-chain data specific to admin-key risk (smart contract code, multisig signer sets, governance transactions). None of the protocols named above were contacted prior to publication; every finding rests solely on that public on-chain data, not private communication. Full disclaimer and program-wide notes: [methodology](https://realspap.github.io/methodology.html).

## Method

Checks the two most common real-world admin patterns, a single-address getter (`owner()`/`admin()`) and OpenZeppelin's standard `AccessControl`, and reports what actually holds that power today:

- **Renounced (0x0)**: nobody can call it. Immutable. The safe end of the spectrum.
- **Bare EOA**: a plain wallet, zero contract code. One leaked or phished key from total loss.
- **1-of-N Safe**: a real Gnosis Safe, but with a single signer. A multisig in name only.
- **Real multisig / Safe with threshold ≥ 2**: genuinely distributed control.
- **Other contract**: a Timelock or custom governance module, needing a manual look at who can actually propose into it.

## What it found, checked by hand

108 entries (protocols and Morpho vault owner addresses) have been checked by hand across Ethereum and several other chains (Base, Optimism, Linea, Berachain, Sonic, Blast, Arbitrum, HyperEVM, World Chain, Polygon): an original set of well-known protocols, a second pass focused on smaller, newer, zero-audit protocols pulled directly from DefiLlama's own listings, and a sweep of Morpho vault owners. Most came back clean, see [What came back safe](#what-came-back-safe). The 23 cases below have admin control sitting with a single key.

### Aurus (tokenized gold/silver/platinum)

`owner()` on all three of Aurus's real value-bearing tokens, TXAU (tGOLD), TXAG (tSILVER) and TXPT (tPLATINUM), resolves to the same bare EOA (`0x795B8dc0...`). This isn't theoretical: that EOA has actually executed "Owner Mint" transactions against these contracts, tagged as such by Etherscan.

One note worth flagging on its own: DefiLlama prices Aurus's TVL at the tokens' intended gold/silver peg (~$7.9M). The tokens' real, observed on-chain trading price is far lower: TXAU trades at $11.42 against an implied peg value of $142, TXAG at $0.51 against $2.13. Real, observable market cap is closer to **$900K**, not $7.9M. Either the peg has broken down or liquidity is too thin to enforce it. Either way, the admin-key risk is real but the headline TVL number is not.

### cVault Finance / CORE (est. 2020)

Seven separate proxy contracts, CoreVault, CLEND, CoreDEX Treasury, wCORE, cBTC, coreDAI and FannyVault, all resolve `owner()` to the identical bare EOA (`0x5A16552f...`). More importantly, each proxy's actual upgrade admin was confirmed on-chain (by calling `admin()` impersonated as the suspected admin contract, since transparent proxies only reveal the real admin to the admin itself, so this isn't a guess): all seven point to the same "Team Proxy Admin" contract, which is itself owned by that same EOA. The `CLending.sol` source on cVault Finance's own GitHub hardcodes it directly: `require(msg.sender == 0x5A16552f..., "BUM")`.

Real money, decomposed token-by-token rather than trusted from a block explorer's aggregate: **at least $3.84M**, most of it in CoreDAO and DAI, both cross-checked against two independent price sources. This required throwing out most of what Etherscan's own "token holdings" widget showed for some of these contracts. CLEND's page listed $2.92M across 18 tokens, but 15 of those are spam airdrops with fabricated prices ("Visit usd-coin.net to claim rewards" at ~4,000 units, and similar). Only ~$1.56M of that specific figure is real.

The same deployer wallet has recently received transactions tagged `Fake_Phishing` by Etherscan, plus at least two address-poisoning attempts (lookalike addresses sending dust, hoping a future copy-paste picks the wrong one from transaction history). That hostile activity is documented on-chain, not described after the fact.

One honest counter-example from the same team: DELTA, a related product line, is secured by a genuine 2-of-4 Gnosis Safe. Whoever built cVault Finance knows how to set up a multisig. They just never did it for the CORE contracts.

### Smilee Finance / gBERA (Berachain, launched 2025)

The actual fund-holding contract (GBeraAssetManager, found via DefiLlama's own TVL adapter code, not guessed) uses `AccessControl`. Its `DEFAULT_ADMIN_ROLE` has **4 holders**: two bare EOAs, a 1-of-1 Safe, and a 2-of-5 Safe. Re-checked on 2026-09-30 by replaying every role grant and revocation since deployment, those 4 seats reduce to **2 effective keys**: the 1-of-1 Safe's only owner is one of the two admin EOAs, and both admin EOAs are among the 2-of-5 Safe's signers. `AccessControl` roles have no threshold and the role is its own admin, so either key can act alone, including revoking the other holders, with no timelock. The implementation is upgradeable (UUPS).

Decomposed rather than quoted from DefiLlama's dashboard: GBeraAssetManager (`0x3F7755...eBcE` on Berachain, itself an EIP-1967 proxy) reports `totalAssets()` of **4,102,552 WBERA** at the first check and 4,102,664 WBERA on 2026-09-30.

| | |
|---|---|
| **Total value** | **~$1.05M** on 2026-09-30 (WBERA at $0.2584 on CoinGecko and $0.2528 on DefiLlama). At the first check it was **~$750K** (WBERA/USD averaged from CoinGecko at $0.183385 and DefiLlama's coins API at $0.182396, cross-checked against a Kodiak/BeraSwap on-chain pool price in the same $0.182-$0.183 band): the change is the WBERA price, not the balance |
| **Sitting directly at the address** | at the first check, ~3,856 WBERA plus 34 native BERA, roughly $712 total (direct `balanceOf`/`eth_getBalance` result) |
| **The rest (~4.10M WBERA)** | not missing or fabricated: disassembling the proxy's bytecode shows it calling Berachain's own canonical validator deposit contract (`depositContract()` resolves to `0x4242...4242`, the chain's `BeaconDepositContract`) plus validator-commission and node-data functions, meaning it's real value actively staked with validators under this manager's direction, not idle tokens in one wallet |
| **Access control** | sits behind the 4-seat, 2-key `AccessControl` set described above |

Small TVL, exactly the range where this kind of gap tends to survive unnoticed.

### DELTA LSW: the one loose end from the first pass, now closed

The original version of this research flagged cVault Finance's DELTA LSW contract as using "a non-standard access scheme this couldn't identify," genuinely unknown, not assumed safe. It's no longer unknown. `DELTA_FINANCIAL_MULTISIG` (the variable name implies a multisig) is checked by an `onlyMultisig()` modifier that is really just `require(msg.sender == DELTA_FINANCIAL_MULTISIG)`, a single address, no threshold, despite the name. That address resolves to a small contract literally called `Fixer`, deployed by the same cVault Finance EOA already named above, and `Fixer.owner()`, a plain `onlyOwner`, is that identical EOA. Two layers of naming that both suggest a multisig, and neither one is. The contract still holds real value (~$36K, mostly WETH), dormant since 2022.

### Fake World Assets / FWA (zero audits, live 2026)

`owner()` on the FWA token resolves to a bare EOA tagged `tokenworks.eth` on Etherscan, matching the project's own declared Twitter handle (`token_works`) on DefiLlama, so this is the team's own key, not a stranger's. The verified source shows that same owner can redirect where purchase proceeds go (`setDistributor`, `setPool`, `setRouteSplit`) and holds a `payable launch()` function: real control over fund routing, not a cosmetic setting. The FWA token contract itself holds negligible value directly (checked via `eth_getBalance` and `balanceOf`: 0 ETH, 0 WETH, ~$160 in USDC), so the risk here is entirely about redirecting where future proceeds flow, not funds already parked in the contract.

This is an active key, not an old one: 2,227 transactions, the most recent three days before the check. It has also recently received transfers from addresses Etherscan tags `Fake_Phishing`, the same pattern already seen with cVault Finance's deployer wallet, on a completely unrelated project. DefiLlama records zero audits for FWA.

### The same key runs a second product

TokenWorks NFT Strategies is a separate product line from the same `tokenworks.eth` EOA already named above for FWA, the wallet that has received transfers from addresses Etherscan tags `Fake_Phishing`. `owner()` of the NFTStrategyFactory, and the root of the PunkStrategy ownership chain (PunkStrategy -> Patch -> the Patch's own owner -> PunkStrategyOwnerNFT), both resolve to that same bare EOA, confirmed on two independent RPCs. Verified source (Sourcify) shows real power: it receives the protocol's fee slice today, can override per-collection fees via a hook, and controls the router allowlist that gates transfers of every strategy token.

What the key cannot reach: PunkStrategy's own 21.97 ETH, or the Patch's 37 CryptoPunks. The Patch's owner contract (not independently verified) exposes only `setPriceMultiplier`, `updateFeeBips` and `transferOwnership` in its bytecode, no sweep function, so that treasury sits behind a deliberately narrower final-owner contract with its own 24-hour delay. Same defect as JayPeggers below (a bare EOA with no threshold), same limited-reach reasoning: rated Medium, not Critical or High, since there is no principal a single compromised key could walk away with, only fee routing and transfer gating.

### UwU Lend (fork of Aave, hacked once already)

The UwU governance/reward token's `owner()` is a bare EOA (Key A), a single key rather than a multisig. The key holder was checked against public on-chain labels; the named mapping is not published here. The protocol lost roughly $19.4M in June 2024 to an oracle-manipulation exploit, a different vulnerability class than the one described here, already extensively covered by security firms at the time.

What's new: more than a year after that public hack, the same single EOA still holds `onlyOwner` access to `addMinter` / `addBurner` on the UwU token, unrestricted power to mint new UwU or burn anyone's balance. The token's own market value is small today, and now priced from two independent points rather than one: **$48,000 to $62,000** depending on source (CoinGecko's $0.00299935, a snapshot about 26 days old when checked, versus $0.003860 read directly off the UwU/WETH Sushiswap pool's live reserves, both against the confirmed 16,000,000 total supply). That pool itself holds only about $1,256 of real two-sided liquidity, so neither number is fully extractable at once, which isn't really the point. The governance of this protocol was never rebuilt after a $19M+ incident that made international crypto news.

### JayPeggers: the same defect, a much smaller blast radius

`owner()` on the JAY token is a bare EOA. A bonding-curve design means the ETH itself sits in the contract, pricing buys and sells against its own balance, re-confirmed here with a direct `eth_getBalance` call down to the last wei.

| | |
|---|---|
| **Balance held** | 76.338649208883439422 ETH, worth **~$188,460** (ETH/USD averaged from CoinGecko at $2,468.75 and DefiLlama's coins API at $2,468.79, essentially identical) |
| **Owner's real power** | narrow: `setFeeAddress` and `setSellFee`/`setBuyFee` redirect roughly a 3% cut of each trade, with the sell fee only ever allowed to move in the user's favor |
| **What the owner can't do** | sweep the full ETH balance directly; reading the full source rather than just grepping for `onlyOwner` finds no function for that |
| **Why it's included** | same missing-multisig pattern as the cases above, but a genuinely smaller amount of damage a compromised key could actually do |

### APY Finance: a "1-of-N Safe" made concrete

This project's own methodology (above) names "1-of-N Safe: a real Gnosis Safe, but with a single signer" as a distinct risk category. Here's a live example.

| | |
|---|---|
| **Signers** | 6 named addresses (confirmed directly via `getOwners()`) |
| **Threshold** | 1 of 6: any single signer can act alone, the other five exist on paper only for this purpose |
| **Token value** | **~$51,300**, decomposed against the verified `totalSupply()` (100,000,000 APY) instead of quoted from a single aggregator (CoinGecko at $0.00051303 and DefiLlama's coins API at $0.00051309, both live, cross-checked against a real Uniswap ETH pool holding $13,075 of liquidity at essentially the same price) |
| **Held directly by the Safe** | 36,101,859 APY (confirmed with a direct `balanceOf` call), more than a third of total supply, worth roughly $18,500 at the same price, movable by any one of the six signers today with one signature, on top of whatever `onlyOwner` powers the token contract grants over the rest |

The point here is the pattern, not the amount, but the amount is real too. Re-checked on 2026-09-19: same six signers, same threshold of 1, same balance to the wei; only the token price has moved (the Safe's holding is now worth about $19,400).

### Sentora: a 1-of-1 Safe at the $800M scale

Sentora curates the two main Morpho vaults for PayPal's PYUSD and Ripple's RLUSD on Ethereum. Together they hold about **$814.7M** (441.19M PYUSD and 373.52M RLUSD read with `totalAssets()`, both priced at $0.9999 by DefiLlama and CoinGecko), from more than 200 depositors each.

| | |
|---|---|
| **Owner** | a Gnosis Safe with a threshold of 1 and a single owner, a plain wallet that has sent 326 transactions |
| **Curator** | a second 1-of-1 Safe, again one active wallet (305 transactions), also an allocator and a sentinel |
| **What one key can do at once** | change allocators, block new deposits, set fees within the contract's hard caps |
| **What it cannot do at once** | route funds to a new market or adapter (3-day timelock) or stop withdrawals (all three withdrawal-side gates are permanently given up on-chain) |

This is why it sits at Medium, not High: a stolen key would have to announce any move on the money three days ahead, and depositors could leave in the meantime. Morpho's own curator guide asks for a real multisig "or an equivalent institutional-grade MPC wallet" for the owner role; an MPC wallet behind a 1-of-1 Safe would look exactly like this on-chain, and nothing on-chain can confirm or rule that out. Sentora hasn't published its signer setup.

### Morpho vault owners: six more single-key setups

UltraYield and K3 Capital were checked on 2026-09-19, alongside the five large curators listed under [What came back safe](#what-came-back-safe). The other four come from a sweep on 2026-09-21 of every Morpho vault owner holding more than $1M of stated assets, listed from Morpho's own API, with every role then re-read on-chain on two independent endpoints per chain (1337 USDC, above, is the fifth case from that sweep). Stated assets are the vault's own figures unless a section says otherwise.

#### UltraYield (Morpho vaults, Ethereum)

UltraYield USDC Core (`0x244f46262D9aD408B746E74aBdD010E9002fb7eE`) returns the same address for `owner()` and `curator()`: a Safe (`0x1280e86Cd7787FfA55d37759C0342F8CD3c7594a`) that is also owner and curator of UltraYield USDT Core (`0x85F3d81a39dF458E45d5EA20f9EB937fAafd282f`) and YieldNest RWA (`0xA1B096268D200d0ecFD57015700F6a0DA9c494e2`). `getThreshold()` returns 1 with five owners, only one of which has ever sent a transaction. Adding an adapter goes through a 7-day timelock. Assets across the three vaults, per Morpho's API: about $240K (~$0.13M, ~$0.10M and ~$0.01M). Medium: one key, over a small amount.

#### K3 Capital (Morpho vault, Ethereum)

Pendlend USDT (`0x9646eBD6346C8C3a9f3d408f71C312eB0CbE8507`): `owner()` is a Safe (`0xdD84A24eeddE63F10Ec3e928f1c8302A47538b6B`) whose `getThreshold()` is 1, with three EOA owners. Assets per Morpho's API: about $0. Low: recorded for the pattern, not the amount.

#### frobUSDC (Morpho vault, Arbitrum)

The vault's owner is a Safe (`0x9b72a0b8576ace2586972ad212d0927096f99a2f` on Arbitrum) whose `getThreshold()` is 1 with a single owner: one key, wrapped in Safe bytecode. `timelock()` returns 86400 (24 hours) and `guardian()` returns a non-zero address, so adding a new market is delayed and can be vetoed. Stated assets about $1.1M. Medium: the single-key pattern is real, but not an instant path to the funds.

#### Duplicated Key (Morpho vault, Ethereum)

Vault `0x0B6C8ef0DE1Be5ed1B59E6e7a67fB9442FB9E49C`. `owner()`, `guardian()` and `curator()` all return the same address, a bare EOA (empty `eth_getCode`, 548 transactions sent), so the two roles meant to check the owner are held by the owner. `timelock()` is 0, so, as described for 1337 USDC above, market caps and allocators change at once. `totalAssets()` reads 1,471,224.22 USDC, and the owner's own shares are negligible, so essentially all of it belongs to depositors. The vault's only position, 1,256,929 USDC in the RLP market, sits at 100% utilisation and cannot currently be withdrawn. Medium: one key with no delay and no independent guardian over about $1.26M of third-party assets, held down by the position being frozen rather than by any governance control.

#### Not Gauntlet (Morpho vault, Arbitrum)

Vault `0x3014ED70B39be395e1a5Eb8ab4c4b8a5378E6522`. `owner()` is a bare EOA (331 transactions sent), `timelock()` is 0 and `guardian()` is the zero address. `totalAssets()` reads 6,516,053.64 USDC, but the owner holds 99.73% of the shares, and the only live position, 132,953 units in the xUSD market, is at 100% utilisation, the rest of the stated total being accrued interest on a frozen claim. No dollar figure is asserted. Low: the money behind the key is essentially the owner's own.

#### Clearstar and 3Jane (15 Morpho vaults, Ethereum and Base)

One bare EOA (`0x30988479...`, empty `eth_getCode` on both chains) owns 10 vaults on Ethereum (3Jane, BOLD Reactor, Clearstar Yield, Clearstar USDC Reactor) and 5 on Base (Clearstar Boring USDC, Clearstar ETH Ground Station), about $6.3M of stated assets combined. Every vault checked returns `timelock()` 259200 (72 hours) and non-zero `guardian()` and `curator()` addresses, so the owner key alone cannot add a market without a 3-day delay that a separate guardian can veto. Low: recorded because one key spanning two chains is invisible when each chain is looked at on its own.

### Reservoir rUSD / srUSD (Ethereum)

Checked 2026-09-30. Addresses from Reservoir's own documentation: rUSD `0x09D4214C03D01F49544C0448DBE3A27f768F2b34` and srUSD `0x738d1115B90efa71AE468F1287fc864775e23a31`; the documentation names no admin, multisig or timelock. Neither token is a proxy, so there is no upgrade path. On both, `hasRole(DEFAULT_ADMIN_ROLE, ...)` is true for a single bare EOA (`0xb7570e32...`). Replaying the role events since deployment shows the deployer granting it that role and renouncing its own one block later, with no other admin grant since. That EOA has granted a minter-type role 8 times on rUSD, so it can grant itself minting, with no multisig and no delay.

Supply on Ethereum: 229,853.44 rUSD (~$230K) and 533,851.78 srUSD (~$622K at about $1.165), priced from DefiLlama and CoinGecko. DefiLlama puts the protocol's TVL at $72.1M across chains; exposure outside Ethereum was not decomposed. High, not Critical: no hostile third-party activity has been documented around the key (it also has no upgrade path, and the Ethereum-side amount is under $1M).

### OpenEden USDO (Ethereum)

Checked 2026-09-30. Addresses from OpenEden's own documentation: USDO `0x8238884Ec9668Ef77B90C6dfF4D1a9F4F4823BFe` and USDO Express `0x80e49D1bdCE8F80c38E88Dd5C4c004dDb9B4E887`. Both are UUPS proxies whose upgrade is gated by `UPGRADE_ROLE`. One bare EOA (`0x5EaFF7af...`) holds `DEFAULT_ADMIN_ROLE` and `UPGRADE_ROLE` on both contracts and `MINTER_ROLE` on USDO; the original admins were revoked. USDO's `totalSupply()` is 14,372,436.39, about $14.0M to $14.3M depending on the price source (CoinGecko $0.9967; DefiLlama's latest point, $0.9727, looks like a feed dip against its previous daily points around $0.997).

High, with one reserve: OpenEden is a regulated issuer of a token backed by US Treasuries, where direct issuer control is often by design, and the EOA could be an institutional MPC wallet, which nothing on-chain can confirm or rule out.

### Issuer and bridge keys on bare EOAs (Ethereum, 2026-10-01)

Checked 2026-10-01, every holder read on two public RPCs. Seven more single-key admin cases, all High under the published scale: each key is active or holds undiminished power, and no hostile third-party activity was found against any of them.

- **Custody-backed tokens (Coinbase cbETH and cbBTC, Binance wBETH, Kraken kBTC).** Addresses from each issuer's own repository, announcement or whitepaper. All four can be upgraded by a single bare EOA: cbETH, cbBTC and wBETH store their upgrade key in the older Zeppelin proxy slot rather than the EIP-1967 one, and kBTC through a ProxyAdmin owned by the same EOA that owns the token. On cbETH and cbBTC that upgrade key has never sent a transaction, which reads like a cold key; on wBETH a second EOA holds owner, minter admin, pauser and blacklister at once. Together these four tokens carry about $15B on Ethereum (wBETH ~$9.4B, cbBTC ~$3.84B, cbETH ~$1.20B, kBTC ~$573M). The same reserve as OpenEden applies: these are custody-backed tokens where direct issuer control is by design, and each EOA could be an institutional MPC wallet, which nothing on-chain can confirm or rule out and no issuer documents.
- **Agora AUSD.** Address from Agora's own deployment page. The token's ProxyAdmin is owned by a bare EOA, so one key can replace its logic, with no timelock, over about $77.2M of supply.
- **StakeStone STONE.** Addresses from StakeStone's own documentation. Minting sits with a separate contract, but the token and its vault are owned by one active EOA. On the token that owner controls the cross-chain bridge trust settings, which is an indirect path to new supply on Ethereum; on the vault it can clean up strategies and set a withdrawal fee capped at 1%. About $21.2M of STONE sits on Ethereum.
- **Socket Gateway.** One active EOA owns the gateway and alone decides which routes it runs against the token approvals users grant it. The January 2024 incident went through a route this owner had added, later abused by a third party through a bug; the key itself was never reported as compromised. No dollar figure: the contract holds almost nothing, the exposure is users' outstanding approvals.

### A cluster of abandoned keys

Not every bare-EOA key is in active use. DeFIL (a Filecoin-lending Compound fork), ChickenSwap, MiniSwap and Mars Poolin all resolve their owner/admin to a bare EOA that hasn't moved in years: DeFIL's since May 2022, ChickenSwap's and MiniSwap's since 2020. None shows the hostile activity documented around FWA's or cVault's wallets. Worth naming as its own category: an admin key nobody has touched in half a decade is a different, quieter kind of risk than one an active team still uses. If it's ever compromised, or the original holder loses access, there is no one left paying attention to react.

All four were pushed to a real dollar figure, or to a documented reason one cannot exist, the same bar as everywhere else in this research. Reserves and pool status were checked directly against each contract, not inferred from an aggregator (DexScreener's own indexer missed the three live pools below entirely):

| Protocol | Reserves checked | Live DEX pool vs WETH? | Dollar figure | Why |
|---|---|---|---|---|
| DeFIL | 50,648 eFIL, 182,288 mFIL, 3,102 FILST (via Unitroller `getAllMarkets()`) | No, `getPair()` returns the zero address for all three | None | see note below |
| ChickenSwap | pool liquidity only | Yes, found via the factory directly | ~$150.57 (pool liquidity) | CoinGecko's cached price is 458 days stale, see note below |
| MiniSwap | pool liquidity only | Yes, found via the factory directly | ~$277.41 (pool liquidity) | CoinGecko's cached price is 535 days stale, see note below |
| Mars Poolin | pool liquidity only | Yes, found via the factory directly | ~$0.10, ten cents (pool liquidity) | Same live-pool method; the pool is nearly empty |

Of these four, DeFIL alone carries no dollar figure: CoinGecko's cached prices for eFIL ($5.65) and FILST ($0.84) are frozen since 2022-06-29 and 2022-05-26 respectively (against native FIL's real price of ~$0.85 today, the same peg-vs-reality gap already documented for Aurus), mFIL has no CoinGecko price at all, and DefiLlama's coins API does return a live-looking $0.51 for FILST, but with no DEX pool behind it anywhere and no corroborating second source, so that number doesn't clear this project's two-source bar.

For ChickenSwap and MiniSwap, those same stale CoinGecko caches imply supply-wide values from $6K to $672K, the standard illiquid-token trap of multiplying total supply by a thin pool's marginal price rather than the pool's actual depth; the live pool prices in the table above were used instead.

## What came back safe

For contrast, and because most protocols checked were fine: RAAC, Compound V2, Cap (3-of-5 Safe behind a 24h Timelock, full chain traced), Frankencoin (fully immutable), Twyne, LandX Finance, Notional V2 (2-of-7 Safe), Threshold thUSD (48h Timelock), Inverse Finance Frontier (48h Timelock behind full governance), UniverseXYZ (DAO governance), Origin Dollar (48h Timelock), and cVault Finance's own DELTA Multisig (not counted separately, cVault is already a case). Also clean: TermMax (4-of-7 Safe holding its AccessManager's admin role), stake.link (24h Timelock, 6-of-8 Safe proposer/canceller), infiniFi (7-day timelock, 4-of-8 Safe proposer), Concentrator and CLever (6-of-9 Safe, no timelock), Vesper (3-of-6 Safe), AUTOfinance (three 6-of-N Safes), Harvest Finance (2-of-3 Safe, no timelock), and Treehouse tETH (checked 2026-09-30: the proxy and the vault are both owned by a timelock with a 5-day delay whose only proposer, canceller, executor and admin is a 5-of-7 Safe).

The second pass added many more: Easedefi.org (fully renounced), FIAT DAO (fully renounced), Yala, Bio Protocol, Asymmetry Finance, DeFi Franc, BOB Fusion, Metronome V1, Frax FPI, Lybra V2, Blur Lending and Resolv USR (each a genuine multi-signer Safe with a real threshold), Nsure Network and OPINION (3-of-5 Safes), Gro DAO (3-of-7), Goldfinch, mStable, and Puffer UniFi (renounced). Five of the largest Morpho vault curators were checked on 2026-09-19 as well, each on its biggest Ethereum vault: Gauntlet (4-of-7 owner, 3-of-7 curator, 7-day timelock), Steakhouse Financial (5-of-10 owner, 2-of-7 curator, 7-day timelock), RockawayX (4-of-8, 3-day timelock), Armitage by Wintermute (4-of-6 owner, 3-of-5 curator, 7-day timelock) and KPK (5-of-8 owner, 2-of-5 curator, 3-day timelock). Larger, more established names checked along the way, Compound V1, Uniswap V1, Augur, Keep3r Network, 1inch, GMX V1, NFTX, Gnosis Protocol v1, Synthetix V4, were consistently fine, reinforcing the pattern below rather than adding new findings.

The 2026-10-01 update added two more: LI.FI, whose router is owned by a 3-hour timelock whose only proposer is a genuine 3-of-6 Safe, and TrueUSD, owned through an intermediate proxy by a genuine 2-of-3 Safe with no timelock, the thin end of safe over about $315M.

The Morpho vault owner sweep of 2026-09-21 found, besides the 5 single-key cases above, 21 owner addresses that answer to a real multisig with a threshold of 2 or more, or to a governance contract: Extrafi XLend/Gauntlet (Base, 4-of-7), Origin OUSD (Ethereum, Base and HyperEVM, 4-of-7 each), Felix (HyperEVM, 4-of-6), Re7 (World Chain, 2-of-4), Hakutora (Ethereum, 2-of-3), Pangolins (Base, 2-of-3), SwissBorg (Ethereum, 5-of-7), Usual Boosted (Ethereum, 2-of-5), Gauntlet (HyperEVM, 4-of-7, and Arbitrum, 3-of-7), Lulo (Ethereum, 2-of-3), Hyperithm (Ethereum, 2-of-3), Waterline (Ethereum, 5-of-8), MEV Capital (HyperEVM, 2-of-3), Yearn/Origin (Base, 4-of-7), and four governance contracts rather than Safes: Spark's Executor (Base), Moonwell's owner (Base), Adpend's owner (Ethereum) and Compound's owner (Polygon).

Ethena's USDe caught a real secondary-source trap: a generic search for "EthenaMinting owner" turns up an address Ethena's own docs page lists, but calling `owner()` directly against the live EthenaMinting V2 contract and the USDe token itself returns a different address, an OpenZeppelin `TimelockController` with a 24-hour `getMinDelay()`. The older EthenaMinting V1 contract's `owner()` resolves to yet a third address, a genuine 5-of-10 Gnosis Safe. Either way, the docs-page address isn't the current admin of V1, V2, or the token.

Aegis YUSD (~$33M, a synthetic dollar DefiLlama lists with zero audits) is clean at the root: the YUSD token's owner, AegisMinting's default admin (behind a 3-day handover delay), AegisConfig and the staked sYUSD vault's proxy admin all resolve to the same genuine 3-of-5 Gnosis Safe, confirmed by replaying every role grant since deployment. Two operational roles (moving collateral to custodians, minting income) do sit on bare EOAs, but both are fenced in: collateral can only go to custodians the multisig itself whitelists, and income minting needs a separate trusted signer plus real collateral already in the contract. One key can slow things down, not walk away with the backing.

3F (~$32M, leveraged exposure to tokenized real-world assets built on Morpho) is the second protocol checked in the $20M-$100M band, and also clean at the root. Every contract that holds value, its core Facility, the three funded wrapper tokens and all seven leveraged vaults, upgrades only through a timelock with a 24-hour delay, and the only address that can queue anything into it is a 2-of-3 Safe whose signers are an Aragon DAO, a separate 4-of-7 Safe and one individual key.

Two findings worth writing down even so. The team's own deployment script names that Safe as the direct upgrade admin; on-chain, the timelock sits in between, which is stricter than the script suggests. And one hot operational key can rebind where an intent's money goes whenever that intent was created with a guardian quorum of zero, which 666 of 9,276 intents were. Reading every intent's balance shows about $304 left across all of them, in intents already closed to that key, so the gap is real in the code and empty in practice. DefiLlama lists 3F with zero audits; the official repository ships five.

## The pattern

Larger, higher-TVL protocols skew toward already having proper multisig/timelock hygiene. Badly-secured ones tend to get hacked and drop out of the rankings, the way Wasabi itself did. Real risk concentrates disproportionately in smaller, newer, lower-TVL protocols, exactly where Aurus and Smilee's gBERA were found. cVault Finance is the exception that tests the rule: old, not small, and still exposed, because nobody ever came back to fix it after 2020. Sentora is a second, different kind of exception: very large and recent, with single-key roles, but boxed in by the vault contract's own timelocks rather than by a multisig.

The second pass checked this claim rather than just repeating it: zero-audit protocols in the $50K-$700K range and the $150K-$5M range both turned up multiple bare-EOA and 1-of-N-Safe cases, while the same filter run against $5M-$20M protocols came back consistently clean. Three separate TVL bands, the same result each time. That isn't a coincidence from one lucky search. Those bands describe zero-audit protocols from DefiLlama's listings only: cases found outside that filter (Sentora, OpenEden USDO, Reservoir and the Morpho vault owners) are not part of that claim.

A follow-up pass went back through every case that used to be "confirmed pattern, no dollar figure" and forced each one to an actual number, or to a documented reason no number is possible, rather than leaving it unweighed; the result reinforces the existing bands (see the case sections above for each figure) rather than shifting them.

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

Last research pass: 2026-09-30 (Reservoir rUSD and OpenEden USDO added, Treehouse tETH checked clean, Smilee gBERA re-checked). Cases were checked on different dates during September 2026, each section gives its date where it has one, and a key checked earlier can read differently today.

108 entries (protocols and Morpho vault owner addresses) checked by hand, under the counting rule in [At a glance](#at-a-glance). By severity, across the 30 cases in the table: 2 Critical, 13 High, 7 Medium, 8 Low. Each case is pushed to a real dollar figure or to a documented reason none is possible or none is reachable (six cases, listed in the caveats). The $20M-$100M TVL band has two zero-audit data points, Aegis YUSD and 3F, both clean at the root; Reservoir (protocol TVL $72.1M across chains, found outside that filter) is rated High. Still too few to call a pattern, so this isn't a finished survey.

## About

[About this research program](https://realspap.github.io/methodology.html). Related work: [multisig-overlap](https://github.com/RealSpap/multisig-overlap-showcase) (shared multisig signers across protocols) and [onchain-postmortems](https://github.com/RealSpap/onchain-postmortems) (DeFi exploits independently reconstructed).

## License

All rights reserved for the findings in this repository; the verification method is available under a separate commercial license. Full terms: [LICENSE](LICENSE).
