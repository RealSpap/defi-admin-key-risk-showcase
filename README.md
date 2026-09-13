# DeFi Admin-Key Risk Scanner

![License](https://img.shields.io/badge/license-all%20rights%20reserved-blue)
![Status](https://img.shields.io/badge/status-active%20research-brightgreen)
[![Check a contract: free tool](https://img.shields.io/badge/check%20a%20contract-free%20tool-orange)](https://realspap.github.io/tools/admin-key-checker.html)
![Follow](https://img.shields.io/badge/follow-%40RealSpap-000000?logo=x)

**The headline finding:** across 70+ DeFi protocols checked on-chain, several risk repeating Wasabi Protocol's $5.9M loss: a bare EOA over $3.84M+ at cVault Finance/CORE, and $750K at Smilee Finance's gBERA behind 4 unthresholded admins.

[Full findings below](#what-it-found-checked-by-hand) · [Live dashboard](https://dune.com/s_pap/defi-admin-key-risk) · [Contact for licensing / custom research](https://x.com/RealSpap)

Independent, on-chain verified research into who really holds the upgrade/admin keys behind live DeFi protocols, anchored on a real 2026 incident, plus a check that finds the same pattern elsewhere.

[![Dashboard preview](assets/dashboard-preview.png)](https://dune.com/s_pap/defi-admin-key-risk)
Live dashboard: click through for the interactive version.

## At a glance

Every case below is described in full, with sources, in [What it found, checked by hand](#what-it-found-checked-by-hand). Defect types build on the categories defined in [Method](#method), with a short qualifier added where the case itself has one (a wrapper contract, a dormant key). Every dollar figure here is copied as-is from that section; nothing here is a new calculation.

Severity is not a code-bug scale, so the usual Critical/High/Medium/Low vocabulary is adapted to what actually matters for an admin key: **Critical** = the key is demonstrably active and there is documented evidence that a third party has actively targeted it (phishing-tagged incoming transfers, address poisoning, or an unauthorized/malicious mint), not merely that the key has been used. **High** = the key is demonstrably active and holds real, undiminished power, but no third-party targeting has been documented; ordinary use by the project's own team, however risky the setup, falls here rather than Critical. **Medium** = the key or role is real but its practical reach is limited, either by a small amount at stake or by narrow on-chain powers (a bounded fee redirect rather than a full sweep). **Low** = the key has been dormant for years, or the amount at stake is negligible.

| Protocol | Defect type | Amount at risk | Severity |
|---|---|---|---|
| Aurus (TXAU/TXAG/TXPT) | Bare EOA | ~$900K (real market cap) | High |
| cVault Finance / CORE | Bare EOA | $3.84M+ | Critical |
| Smilee Finance / gBERA | AccessControl, multi-holder, no threshold | ~$750K | High |
| DELTA LSW (cVault legacy) | Bare EOA (via wrapper contract) | ~$36K | Medium |
| Fake World Assets / FWA | Bare EOA | No dollar figure (risk is future proceeds routing, not funds already parked; the contract itself holds ~$160) | Critical |
| UwU Lend | Bare EOA | $48,000 to $62,000 | High |
| JayPeggers | Bare EOA | ~$188,460 | Medium |
| APY Finance | 1-of-N Safe | ~$51,300 (of which ~$18,500 sits directly in the Safe) | High |
| DeFIL | Bare EOA, dormant | No dollar figure | Low |
| ChickenSwap | Bare EOA, dormant | ~$150.57 (pool liquidity) | Low |
| MiniSwap | Bare EOA, dormant | ~$277.41 (pool liquidity) | Low |
| Mars Poolin | Bare EOA, dormant | ~$0.10 (pool liquidity) | Low |

By severity: 2 Critical, 4 High, 2 Medium, 4 Low, across the 12 cases above. cVault Finance/CORE and Fake World Assets currently share the top spot: both Critical, both under documented active targeting right now, not just theoretically exposed.

A few of these calls are not obvious from the numbers alone:

- **cVault Finance/CORE and FWA (Critical, not just High):** both keys show documented third-party targeting (Fake_Phishing-tagged transfers and address poisoning for cVault, Fake_Phishing-tagged incoming transfers for FWA) on top of being demonstrably active. The call has nothing to do with the dollar amount.
- **Aurus (High, not Critical):** its Owner Mint transactions look alarming at first glance, but they were executed by the team's own key, with no evidence anyone outside the project has targeted it. Dangerously centralized, but ordinary operation, not exploitation.
- **DELTA LSW and JayPeggers (Medium despite active, real keys):** their practical reach is capped. DELTA LSW's balance is small and untouched since 2022; JayPeggers' owner can only redirect a bounded fee, not sweep the ETH balance.
- **APY Finance (High, not Critical):** any one of six signers can already act alone and the Safe custodies real value directly, but no targeting of a specific signer has been documented.

## What happened

On 2026-04-30, Wasabi Protocol lost ~$5.9M across Ethereum, Base, Berachain and Blast after an attacker compromised the private key of `wasabideployer.eth`. That single key held unchecked admin authority over every one of Wasabi's upgradeable vaults, with no multisig and no timelock. The protocol's own framework supported a timelock; it was just set to 0.

Compromised admin/deployer keys have overtaken smart-contract bugs as the #1 cause of DeFi losses: about 15% of incidents, but roughly 76% of dollars lost, because one key can drain everything a protocol's upgrade logic touches.

## Access to the tool

The verification method behind this research runs on demand, replayed fresh against any protocol you name, not published in this repository. Every case above was checked days or weeks ago; run the same check again today and the answer can change, because admin keys get rotated, renounced, or compromised on-chain, not because the method has gone stale. Want to check one yourself right now, free? [Admin Key Checker](https://realspap.github.io/tools/admin-key-checker.html) classifies any contract's admin-key pattern live from chain, in your browser, no account needed. For the full method, dollar-figure decomposition, and a check against documented third-party targeting, reach out via [RealSpap on X](https://x.com/RealSpap) to have it checked live this week.

## Disclaimer

This report presents an independent, factual analysis of publicly available on-chain data (smart contract code, multisig signer sets, governance transactions) as of the date noted in Status above. Statements about which addresses or individuals hold administrative, multisig, or governance keys are based solely on on-chain records and publicly disclosed information cited inline; they are not allegations of wrongdoing, and no claim of illegal conduct, fraud, or misconduct is made or implied. Concentration of control or key-holder identity is reported as an observed structural fact, not as a moral or legal judgment on the individuals named. Findings reflect a snapshot in time; on-chain configurations, signer sets, and governance parameters can and do change after publication, and this report is not updated automatically to reflect such changes. This is independent research, not commissioned or audited by the protocols discussed, and it does not constitute legal, financial, or investment advice. Any individual or entity named in this report who believes information about them is inaccurate or outdated is invited to contact the author via [X](https://x.com/RealSpap) with supporting evidence; corrections will be issued promptly and transparently. Readers should independently verify all cited addresses, transactions, and figures before relying on them.

**Disclosure:** none of the protocols named above were contacted prior to publication. Every finding rests solely on public on-chain data (contract calls and transaction history), not private communication. Any team that wants to respond, or has already remediated a finding, is invited to contact the author via [X](https://x.com/RealSpap); corrections and updates will be issued promptly.

## Method

Checks the two most common real-world admin patterns, a single-address getter (`owner()`/`admin()`) and OpenZeppelin's standard `AccessControl`, and reports what actually holds that power today:

- **Renounced (0x0)**: nobody can call it. Immutable. The safe end of the spectrum.
- **Bare EOA**: a plain wallet, zero contract code. One leaked or phished key from total loss.
- **1-of-N Safe**: a real Gnosis Safe, but with a single signer. A multisig in name only.
- **Real multisig / Safe with threshold ≥ 2**: genuinely distributed control.
- **Other contract**: a Timelock or custom governance module, needing a manual look at who can actually propose into it.

## What it found, checked by hand

Well over 70 protocols have now been checked manually across Ethereum and several L2s (Base, Optimism, Linea, Berachain, Sonic, Blast): the original ~25, plus a second pass focused on smaller, newer, zero-audit protocols pulled directly from DefiLlama's own listings. Most came back clean, see below. Several came back genuinely live and at risk, beyond the Wasabi anchor.

### Aurus (tokenized gold/silver/platinum)

`owner()` on all three of Aurus's real value-bearing tokens, TXAU (tGOLD), TXAG (tSILVER) and TXPT (tPLATINUM), resolves to the same bare EOA (`0x795B8dc0...`). This isn't theoretical: that EOA has actually executed "Owner Mint" transactions against these contracts, tagged as such by Etherscan.

One correction worth flagging on its own: DefiLlama prices Aurus's TVL at the tokens' intended gold/silver peg (~$7.9M). The tokens' real, observed on-chain trading price is far lower: TXAU trades at $11.42 against an implied peg value of $142, TXAG at $0.51 against $2.13. Real, observable market cap is closer to **$900K**, not $7.9M. Either the peg has broken down or liquidity is too thin to enforce it. Either way, the admin-key risk is real but the headline TVL number is not.

### cVault Finance / CORE (est. 2020)

Seven separate proxy contracts, CoreVault, CLEND, CoreDEX Treasury, wCORE, cBTC, coreDAI and FannyVault, all resolve `owner()` to the identical bare EOA (`0x5A16552f...`). More importantly, each proxy's actual upgrade admin was confirmed live (by calling `admin()` impersonated as the suspected admin contract, since transparent proxies only reveal the real admin to the admin itself, so this isn't a guess): all seven point to the same "Team Proxy Admin" contract, which is itself owned by that same EOA. The `CLending.sol` source on cVault Finance's own GitHub hardcodes it directly: `require(msg.sender == 0x5A16552f..., "BUM")`.

Real money, decomposed token-by-token rather than trusted from a block explorer's aggregate: **at least $3.84M**, most of it in CoreDAO and DAI, both cross-checked against two independent price sources. This required throwing out most of what Etherscan's own "token holdings" widget showed for some of these contracts. CLEND's page listed $2.92M across 18 tokens, but 15 of those are spam airdrops with fabricated prices ("Visit usd-coin.net to claim rewards" at ~4,000 units, and similar). Only ~$1.56M of that specific figure is real.

The same deployer wallet personally holds $54M+ in ETH and $15M+ in tokens, a $69M+ target, and has recently received transactions tagged `Fake_Phishing` by Etherscan, plus at least two address-poisoning attempts (lookalike addresses sending dust, hoping a future copy-paste picks the wrong one from transaction history). This is not a theoretical risk being described after the fact. It's a wallet under active attention today.

One honest counter-example from the same team: DELTA, a related product line, is secured by a genuine 2-of-4 Gnosis Safe. Whoever built cVault Finance knows how to set up a multisig. They just never did it for the CORE contracts.

### Smilee Finance / gBERA (Berachain, launched 2025)

The actual fund-holding contract (GBeraAssetManager, found via DefiLlama's own TVL adapter code, not guessed) uses `AccessControl`. Its `DEFAULT_ADMIN_ROLE` currently has **4 holders**: two bare EOAs, a 1-of-1 Safe, and one genuine 2-of-5 Safe. The real multisig doesn't help, since `AccessControl` roles have no threshold, so any single holder can act alone, including revoking the real multisig's own access. One of the bare EOAs is also, separately, the sole signer behind a different 1-of-1 Safe elsewhere in the same protocol's stack.

Decomposed rather than quoted from DefiLlama's dashboard: GBeraAssetManager (`0x3F7755...eBcE` on Berachain, itself an EIP-1967 proxy) reports `totalAssets()` of **4,102,552 WBERA**.

| | |
|---|---|
| **Total value** | **~$750K** (WBERA/USD averaged from CoinGecko at $0.183385 and DefiLlama's coins API at $0.182396, both within 0.5% of each other, cross-checked against a Kodiak/BeraSwap on-chain pool price in the same $0.182-$0.183 band) |
| **Sitting directly at the address** | ~3,856 WBERA plus 34 native BERA, roughly $712 total (direct `balanceOf`/`eth_getBalance` result) |
| **The rest (~4.10M WBERA)** | not missing or fabricated: disassembling the proxy's bytecode shows it calling Berachain's own canonical validator deposit contract (`depositContract()` resolves to `0x4242...4242`, the chain's `BeaconDepositContract`) plus validator-commission and node-data functions, meaning it's real value actively staked with validators under this manager's direction, not idle tokens in one wallet |
| **Access control** | sits behind the same 4-holder `AccessControl` set described above |

This independently confirms, rather than just repeats, the DefiLlama TVL number this section used to cite. Small TVL, exactly the range where this kind of gap tends to survive unnoticed.

### DELTA LSW: the one loose end from the first pass, now closed

The original version of this research flagged cVault Finance's DELTA LSW contract as using "a non-standard access scheme this couldn't identify," genuinely unknown, not assumed safe. It's no longer unknown. `DELTA_FINANCIAL_MULTISIG` (the variable name implies a multisig) is checked by an `onlyMultisig()` modifier that is really just `require(msg.sender == DELTA_FINANCIAL_MULTISIG)`, a single address, no threshold, despite the name. That address resolves to a small contract literally called `Fixer`, deployed by the same cVault Finance EOA already named above, and `Fixer.owner()`, a plain `onlyOwner`, is that identical EOA. Two layers of naming that both suggest a multisig, and neither one is. The contract still holds real value (~$36K, mostly WETH), dormant since 2022.

### Fake World Assets / FWA (zero audits, live 2026)

`owner()` on the FWA token resolves to a bare EOA tagged `tokenworks.eth` on Etherscan, matching the project's own declared Twitter handle (`token_works`) on DefiLlama, so this is the team's own key, not a stranger's. The verified source shows that same owner can redirect where purchase proceeds go (`setDistributor`, `setPool`, `setRouteSplit`) and holds a `payable launch()` function: real control over fund routing, not a cosmetic setting. The FWA token contract itself holds negligible value directly (checked via `eth_getBalance` and `balanceOf`: 0 ETH, 0 WETH, ~$160 in USDC), so the risk here is entirely about redirecting where future proceeds flow, not funds already parked in the contract.

This is a live wallet, not an old one: 2,227 transactions, most recent three days before this check, holding ~997 ETH and ~$400K of FWA personally. It has also recently received transfers from addresses Etherscan tags `Fake_Phishing`, the same "active target" pattern already seen with cVault Finance's deployer wallet, on a completely unrelated project. DefiLlama records zero audits for FWA.

### UwU Lend (fork of Aave, hacked once already)

The UwU governance/reward token's `owner()` is a bare EOA tagged `sifu.eth`. That identity is already public record, not something uncovered here: multiple outlets (CoinDesk, Unchained, Protos) have reported "Sifu" as Michael Patryn, co-founder of the collapsed QuadrigaCX exchange, doxxed by on-chain investigator ZachXBT in January 2022. Patryn launched UwU Lend in 2022. The protocol lost roughly $19.4M in June 2024 to an oracle-manipulation exploit, a different vulnerability class than the one described here, already extensively covered by security firms at the time.

What's new: more than a year after that public hack, the same single EOA still holds `onlyOwner` access to `addMinter` / `addBurner` on the UwU token, unrestricted power to mint new UwU or burn anyone's balance. The token's own market value is small today, and now priced from two independent points rather than one: **$48,000 to $62,000** depending on source (CoinGecko's $0.00299935, a snapshot about 26 days old when checked, versus $0.003860 read directly off the UwU/WETH Sushiswap pool's live reserves, both against the confirmed 16,000,000 total supply). That pool itself holds only about $1,256 of real two-sided liquidity, so neither number is fully extractable at once, which isn't really the point. The governance of this protocol was never rebuilt after a $19M+ incident that made international crypto news.

### JayPeggers: the same defect, a much smaller blast radius

`owner()` on the JAY token is a bare EOA. A bonding-curve design means the ETH itself sits in the contract, pricing buys and sells against its own balance, re-confirmed here with a direct `eth_getBalance` call down to the last wei.

| | |
|---|---|
| **Balance held** | 76.338649208883439422 ETH, worth **~$188,460** (ETH/USD averaged from CoinGecko at $2,468.75 and DefiLlama's coins API at $2,468.79, essentially identical) |
| **Owner's real power** | narrow: `setFeeAddress` and `setSellFee`/`setBuyFee` redirect roughly a 3% cut of each trade, with the sell fee only ever allowed to move in the user's favor |
| **What the owner can't do** | sweep the full ETH balance directly; reading the full source rather than just grepping for `onlyOwner` finds no function for that |
| **Why it's included** | same missing-multisig pattern as the cases above, but a genuinely smaller amount of damage a compromised key could actually do |

That $188K is the bonding curve's current size, the ceiling this design protects, not a number the compromised key can withdraw in one call.

### APY Finance: a "1-of-N Safe" made concrete

This project's own methodology (above) names "1-of-N Safe: a real Gnosis Safe, but with a single signer" as a distinct risk category. Here's a live example.

| | |
|---|---|
| **Signers** | 6 named addresses (confirmed directly via `getOwners()`) |
| **Threshold** | 1 of 6: any single signer can act alone, the other five exist on paper only for this purpose |
| **Token value** | **~$51,300**, decomposed against the verified `totalSupply()` (100,000,000 APY) instead of quoted from a single aggregator (CoinGecko at $0.00051303 and DefiLlama's coins API at $0.00051309, both live, cross-checked against a real Uniswap ETH pool holding $13,075 of liquidity at essentially the same price) |
| **Held directly by the Safe** | 36,101,859 APY (confirmed with a direct `balanceOf` call), more than a third of total supply, worth roughly $18,500 at the same price, movable by any one of the six signers today with one signature, on top of whatever `onlyOwner` powers the token contract grants over the rest |

The point here is the pattern, not the amount, but the amount is real too.

### A cluster of abandoned keys

Not every bare-EOA finding is a live target. DeFIL (a Filecoin-lending Compound fork), ChickenSwap, MiniSwap and Mars Poolin all resolve their owner/admin to a bare EOA that hasn't moved in years: DeFIL's since May 2022, ChickenSwap's and MiniSwap's since 2020. None show any sign of being actively watched or targeted the way FWA's or cVault's wallets are. Worth naming as its own category: an admin key nobody has touched in half a decade is a different, quieter kind of risk than one an active team still uses. If it's ever compromised, or the original holder loses access, there is no one left paying attention to react.

All four were pushed to a real dollar figure, or to a documented reason one cannot exist, the same bar as everywhere else in this research:

- **DeFIL**: three real markets sit under its Unitroller (`getAllMarkets()` called directly, not assumed), holding 50,648 eFIL, 182,288 mFIL and 3,102 FILST in cash reserves at time of check. None of the three has a real, currently tradeable price. The Uniswap V2 factory's `getPair()` returns the zero address against WETH for all three (no pool exists at all, checked directly, not just inferred from DexScreener showing zero indexed pairs), CoinGecko's cached price for eFIL ($5.65) and FILST ($0.84) are both frozen since 2022 (`last_updated_at` of 2022-06-29 and 2022-05-26 respectively, against native FIL's real price of ~$0.85 today, the same peg-vs-reality gap already documented for Aurus), and mFIL has no CoinGecko price at all. DefiLlama's coins API does return a live-looking $0.51 for FILST, but with no DEX pool behind it anywhere and no corroborating second source, that number doesn't clear this project's two-source bar, so it isn't used. No dollar figure is claimed for DeFIL.
- **ChickenSwap, MiniSwap and Mars Poolin**: unlike DeFIL, each of these three does have a live Uniswap V2 pool against WETH, found directly from the factory rather than an aggregator (DexScreener's own indexer missed all three). So a real, current, on-chain price exists for all three. But every pool is close to empty: $150.57 of total two-sided liquidity for ChickenSwap, $277.41 for MiniSwap, and $0.10, ten cents, for Mars Poolin. CoinGecko's cached prices, 458 and 535 days stale for the first two, imply supply-wide values from $6K to $672K, the standard illiquid-token trap of multiplying total supply by a thin pool's marginal price rather than the pool's actual depth. What is really sitting there, the honest ceiling on what a compromised key plus that pool could turn into cash today, is negligible: a few hundred dollars combined across all three. Confirmed structurally as bare-EOA (re-verified directly this pass, same addresses as before), priced honestly as immaterial rather than left unweighed.

## What came back safe

For contrast, and because most protocols checked were fine: RAAC, Compound V2, Cap (3-of-5 Safe behind a 24h Timelock, full chain traced), Frankencoin (fully immutable), Twyne, LandX Finance, Notional V2 (2-of-7 Safe), Threshold thUSD (48h Timelock), Inverse Finance Frontier (48h Timelock behind full governance), UniverseXYZ (DAO governance), Origin Dollar (48h Timelock), and cVault Finance's own DELTA Multisig.

The second pass added many more: Easedefi.org (fully renounced), FIAT DAO (fully renounced), Yala, Bio Protocol, Asymmetry Finance, DeFi Franc, BOB Fusion, Metronome V1, Frax FPI, Lybra V2, Blur Lending and Resolv USR (each a genuine multi-signer Safe with a real threshold), Nsure Network and OPINION (3-of-5 Safes), Gro DAO (3-of-7), Goldfinch, mStable, and Puffer UniFi (renounced). Larger, more established names checked along the way, Compound V1, Uniswap V1, Augur, Keep3r Network, 1inch, GMX V1, NFTX, Gnosis Protocol v1, Synthetix V4, were consistently fine, reinforcing the pattern below rather than adding new findings.

A third pass added Ethena's USDe, and caught a real secondary-source trap along the way. A generic search for "EthenaMinting owner" turns up an address Ethena's own docs page lists, but calling `owner()` directly against the live EthenaMinting V2 contract and the USDe token itself returns a different address, confirmed to be an OpenZeppelin `TimelockController` with a 24-hour `getMinDelay()`, not the docs-page address at all. The older EthenaMinting V1 contract's `owner()` resolves to yet a third address, a genuine 5-of-10 Gnosis Safe. Read in order: V1 (likely legacy) sits behind a 5-of-10 multisig, V2 and the token itself, the two contracts that actually matter today, sit behind a 24-hour timelock. Whatever the docs-page address is for, it isn't the current live admin of either.

## The pattern

Larger, higher-TVL protocols skew toward already having proper multisig/timelock hygiene. Badly-secured ones tend to get hacked and drop out of the rankings, the way Wasabi itself did. Real risk concentrates disproportionately in smaller, newer, lower-TVL protocols, exactly where Aurus and Smilee's gBERA were found. cVault Finance is the exception that tests the rule: old, not small, and still exposed, because nobody ever came back to fix it after 2020.

The second pass checked this claim rather than just repeating it: zero-audit protocols in the $50K-$700K range and the $150K-$5M range both turned up multiple bare-EOA and 1-of-N-Safe cases, while the same filter run against $5M-$20M protocols came back consistently clean. Three separate TVL bands, the same result each time. That isn't a coincidence from one lucky search.

A follow-up pass went back through every case that used to be "confirmed pattern, no dollar figure" and forced each one to an actual number, or to a documented reason no number is possible, rather than leaving it unweighed. The result reinforces the existing bands rather than shifting them: gBERA decomposed to ~$750K, JayPeggers to ~$188K, APY Finance to ~$51K (plus $18.5K of that sitting directly at the under-secured Safe itself), UwU Lend to $48K-$62K, right at the edge of the $50K-$5M range already described as exposed: the $62K high end clears the $50K floor, but the $48K low end sits just under it. The abandoned-key cluster (ChickenSwap, MiniSwap, Mars Poolin) turned out to be genuinely negligible once actually priced off live pool reserves instead of a stale cache, a few hundred dollars combined rather than the six-figure sums a naive aggregator read would suggest. Either way, nothing newly priced comes anywhere close to the $5M-$20M band that keeps coming back clean.

## Caveats

This is a first-pass filter plus manual verification, not an audit. A few things it does not resolve:

- Aurus also runs a fourth, much smaller tokenized asset (a Canadian-gold product, "CGR") not counted in DefiLlama's TVL for the protocol: real, but negligible activity (7 transactions ever, $0 current balance).
- Update from a later pass through this research: every bare-EOA/1-of-N-Safe candidate that previously lacked a dollar figure (Smilee Finance's gBERA, JayPeggers, APY Finance, UwU Lend, and the ChickenSwap/MiniSwap/Mars Poolin cluster) has now been decomposed token-by-token and cross-checked against at least two independent price sources, the same standard used for Aurus and cVault Finance, with every on-chain balance re-verified directly (`balanceOf`/`eth_getBalance`/`totalAssets`) rather than trusted from a prior note. DeFIL remains the one exception with no dollar figure: none of its three collateral tokens (eFIL, mFIL, FILST) has a real DEX pool anywhere, and the cached prices that do exist are years stale or uncorroborated. Nothing in this dataset is still sitting in the old "confirmed pattern, unweighed impact" bucket.
- Block explorers' "token holdings" aggregates can be badly inflated by spam tokens carrying fabricated prices. Every dollar figure in this research was decomposed token-by-token and cross-checked against a second price source before being trusted. Don't take a headline aggregate at face value, here or anywhere else.
- The tool only recognizes standard `Ownable`/`AccessControl`/Gnosis Safe patterns. A protocol that rolls its own bespoke access control (as Wasabi itself did) needs the source read by hand.

This is independent research, not an audit or a security guarantee. Everything above is stated at the confidence level the on-chain data actually supports.

## What's still open

The $5M-$20M TVL band has come back consistently clean three separate times now. The next honest test of that pattern is the $20M-$100M band, not yet checked here, one tier up from everything tested so far.

## Status

Last verified: 2026-09-13.

Well over 70 protocols checked by hand, 12 confirmed live and pushed to a real dollar figure, or to a documented reason none is possible (DeFIL, whose collateral tokens have no live DEX pool anywhere). Not a finished survey: the $20M-$100M band described in What's still open above has not yet been checked.

## About

Part of an ongoing program of independent on-chain research, same discipline throughout: primary-source anchors, on-chain reconstruction, corrections issued openly when something's found wrong. Related work: [multisig-overlap](https://github.com/RealSpap/multisig-overlap-showcase) (341 protocols screened for shared multisig signers), [block-market-concentration](https://github.com/RealSpap/block-market-concentration-showcase) (who really builds and profits from Ethereum's blocks), and [onchain-postmortems](https://github.com/RealSpap/onchain-postmortems) (40 DeFi exploits independently reconstructed, ~$783.7M recomputed). Every pass across this program has found something real; none has come back empty. Ongoing work and dashboards: [Dune](https://dune.com/s_pap), [X](https://x.com/RealSpap).

## License

All rights reserved. This repository documents the results; the tool itself is available under a commercial license, see above.
