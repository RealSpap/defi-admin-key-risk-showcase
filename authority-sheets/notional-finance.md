# Notional Finance: authority sheet (Ethereum mainnet)

Free sample of an authority sheet. Not commissioned by Notional or by anyone else.

| | |
|---|---|
| Protocol | Notional Finance (fixed-rate lending, NOTE governance token) |
| Scope | 14 entries on Ethereum mainnet: the V3 and V2 proxies, the V3 beacons, NOTE, sNOTE, the TreasuryManager, the TradingModule, the owner timelock, the GovernorAlpha, three leveraged vaults, and the legacy V1 Escrow with its ProxyAdmin. Other chains are not covered. |
| Read at | Block **26,124,800** (2026-10-05 07:53:35 UTC) |
| RPCs | Final pass on the core values (99 reads): `rpc.mevblocker.io` and `eth.drpc.org`, all identical on both. Other reads (the 17 outside Safes, the sNOTE pool claim, the TradingModule oracle entry): `ethereum-rpc.publicnode.com` and `rpc.mevblocker.io`, identical on both. Event history: `gateway.tenderly.co/public/mainnet` |
| Address sources | Notional's own docs ([Deployments (Mainnet)](https://docs.notional.finance/notional-v3/smart-contracts/deployments-mainnet), [Governance Reference](https://docs.notional.finance/developer-documentation/on-chain/notional-governance-reference)) and its own GitHub registries: `contracts-v3/v3.mainnet.json`, `contracts-v3/v2.mainnet.json`, `staked-note/v2.mainnet.json`, `leveraged-vaults/vaults.json`, and `contracts/mainnet.json` for V1 |

**State of the protocol at this block.** The on-chain lending markets have been wound down. The V2 proxy runs a `FinalV2Router` (since 2024-08-22) whose only functions are owner transfers of final balances and upgrade. The V3 proxy runs a `TimelockRouter` (since 2026-01-08) whose only functions are ownership transfer and upgrade. The three vaults read here hold 0 LP tokens and 0 vault shares. Authority still matters for five things: the NOTE token, sNOTE, the TreasuryManager, the TradingModule, and the upgrade path of every proxy above, including the legacy V1 contracts. Products deployed outside the contracts listed below are out of scope.

## 1. Authority map

Three Safes and one timelock hold every role below:

- **Safe A** `0x02479bfc7dce53a02e26fe7baea45a0852cb0909`: 3-of-7
- **Safe B** `0xD9D5a9dc6a952b7aD6B05a983b399537B7c0Ee88`: 2-of-7
- **Safe C** `0x22341fB5D92D3d801144aA5A925F401A91418A05`: 3-of-5
- **Timelock** `0x375eafe4348c6aa851cdfa5f84ec268f73643235`: OpenZeppelin `TimelockController`, minimum delay **172,800 s (48 h)**; proposer, executor and canceller: Safe A only

| # | Contract | Address | Proxy | Who can upgrade | Who can pause or change critical parameters | Delay |
|---|---|---|---|---|---|---|
| 1 | Notional V3 proxy | `0x6e7058c91F85E0F6db4fc9da2CA41241f5e4263f` | Yes, UUPS (`nProxy`). EIP-1967 admin slot empty. Implementation `0x7cfe9866…0068`, verified as `TimelockRouter` | `owner()` = Timelock, driven by Safe A | Nothing else exposed by the current router. `pauseGuardian()` still returns Safe B, but `TimelockRouter` only accepts upgrades from the owner | 48 h |
| 2 | V3 beacons (nToken, pCash, pDebt) | `0xc4FD259b…3DB7`, `0x1F681977…A6A9`, `0xDF08039c…7640` | Upgradeable beacons | `owner()` = the V3 proxy itself; `upgradeBeacon` is not exposed by the current router, so only after a V3 upgrade | Same | 48 h (through row 1) |
| 3 | Notional V2 proxy | `0x1344A36A1B56144C3Bc62E7757377D288fDE0369` | Yes, UUPS. Admin slot empty. Implementation `0x5c424c3d…923f`, verified as `FinalV2Router` | `owner()` = Safe A, directly | Safe A: `transferFinalBalances`, `transferBalance`, `transferFinalNOTE`. `pauseGuardian()` returns Safe B, unused by this router | None |
| 4 | NOTE token | `0xCFEAead4947f0705A14ec42aC3D44129E1Ef3eD5` | Yes, UUPS. Admin slot empty. Implementation `0x95df7e34…6ba3`, verified as `NoteERC20` | `owner()` = **Safe B**, directly (`_authorizeUpgrade` is `onlyOwner`) | Safe B: `transferOwnership`. Total supply 100,000,000 NOTE | None |
| 5 | sNOTE (staked NOTE) | `0x38DE42F4BA8a35056b33A746A6b45bE9B1c3B9d2` | Yes, UUPS. Admin slot empty. Implementation `0x00c2eea3…a940` | `owner()` = Safe C, directly | Safe C: `extractTokensForCollateralShortfall` (up to 50% of the pool tokens, once per 7 days), cooldown up to 30 days (now 1,296,000 s, 15 days), voting window, pool fee, gauge migration | None |
| 6 | TreasuryManager | `0x53144559c0d4a3304e2dd9dafbd685247429216d` | Yes, UUPS. Admin slot empty. Implementation `0xe801b59e…5b0a` | `owner()` = Safe A, directly | Safe A: `withdraw(token, amount)` for any token, `setManager`, purchase limit, burn percentage. `manager()` = `0x7459…f7Ed`, an EOA that Notional's own code names `RELAYER_ADDRESS`: trades, harvests, reinvestment | None |
| 7 | TradingModule | `0x594734c7e06C3D483466ADBCe401C6Bd269746C8` | Yes, UUPS. Admin slot empty. Implementation `0x179a2d24…c823` | `NOTIONAL.owner()` (`NOTIONAL()` = row 1), so the Timelock | Timelock: `setPriceOracle`, `setTokenPermissions`, oracle freshness | 48 h |
| 8 | Owner timelock | `0x375eafe4348c6aa851cdfa5f84ec268f73643235` | No | Not upgradeable. `DEFAULT_ADMIN_ROLE` held by the timelock itself only, so role changes need a timelocked operation | Proposer, executor, canceller: Safe A. No open executor (`hasRole(EXECUTOR_ROLE, 0x0)` = false) | 48 h |
| 9 | GovernorAlpha | `0x086b4ecD75c494dD36641195E89c25373E06d7cB` | No | Not upgradeable | Its own timelock delay is 43,200 s (12 h). `guardian()` = Safe B (may cancel proposals). Quorum 4,000,000 NOTE, proposal threshold 1,000,000 NOTE, voting delay 1 block, voting period 13,292 blocks. 4 proposals, all in state Executed. Owns none of the other 13 entries | 12 h (own) |
| 10 | Vault SingleSidedLP:Convex:[USDC]/crvUSD | `0xba4eb30f7F2e378249cf94E08F581e704326e9c6` | Yes, UUPS. Implementation `0x14f3361c…6c3b`, verified as `Curve2TokenConvexVault` | `NOTIONAL.owner()`, so the Timelock | Role admin (`DEFAULT_ADMIN_ROLE`): Safe A, directly. `EMERGENCY_EXIT_ROLE`: Safe A and Safe B. Holds 0 LP tokens, 0 vault shares | 48 h for code, none for roles |
| 11 | Vault SingleSidedLP:Convex:[USDT]/crvUSD | `0x86B222d44AC6cC56e75b3df01fdAD5Dc371EF538` | Yes, UUPS. Implementation `0x98247ef3…0ab4` | Timelock | Same as row 10. Holds 0 LP tokens, 0 vault shares | 48 h for code, none for roles |
| 12 | Vault SingleSidedLP:Convex:[WBTC]/tBTC | `0xe20048FA0F165A49b780DFA9A8caBa845332f848` | Yes, UUPS. Implementation `0x5c8f33d6…801b` | Timelock | Role admin: Safe A. `EMERGENCY_EXIT_ROLE`: Safe B only. Holds 0 LP tokens, 0 vault shares | 48 h for code, none for roles |
| 13 | V1 Escrow (legacy) | `0x9abd0b8868546105F6F48298eaDC1D9c82f7f683` | Yes, transparent. Admin slot = row 14. Implementation `0x7885484e…2848`, verified as `EmptyProxy` | Row 14, so Safe C | `owner()` = Safe C. Holds 14,211.894948 USDC and 18.216201 WETH | None |
| 14 | V1 ProxyAdmin (legacy) | `0x09DbA4Fa1826f7d0E284513333FE71867b324261` | No | `owner()` = Safe C, directly | Also the EIP-1967 admin of V1 Portfolios, ERC1155Trade and Directory | None |

**What it takes to act, as read at block 26,124,800:**

| Action | Signatures needed | Delay |
|---|---|---|
| Replace the NOTE token's code | 2 of Safe B's 7 | none |
| Replace sNOTE's code, or extract up to 50% of its pool tokens | 3 of Safe C's 5 | none |
| Withdraw any token from the TreasuryManager | 3 of Safe A's 7 | none |
| Upgrade the V2 proxy | 3 of Safe A's 7 | none |
| Grant a role on a vault | 3 of Safe A's 7 | none |
| Upgrade the V3 proxy, the TradingModule or a vault's code | 3 of Safe A's 7, then the timelock | 48 h |
| Upgrade a V1 legacy proxy | 3 of Safe C's 5 | none |

### The three Safes, read on-chain

| | Safe A | Safe B | Safe C |
|---|---|---|---|
| Address | `0x02479bfc…0909` | `0xD9D5a9dc…Ee88` | `0x22341fB5…8A05` |
| Threshold | 3 of 7 | 2 of 7 | 3 of 5 |
| Version | 1.2.0 | 1.2.0 | 1.1.1 |
| Nonce (transactions executed) | 492 | 7 | 386 |
| Modules enabled | none | none | none |
| Transaction guard | not supported before Safe 1.3.0 | not supported | not supported |
| Roles in this sheet | V2 owner, TreasuryManager owner, sole proposer, executor and canceller of the timelock, vault role admin, vault emergency exit (2 vaults) | NOTE owner, pause guardian slot on V2 and V3, GovernorAlpha guardian, vault emergency exit (3 vaults) | sNOTE owner, V1 Escrow owner, V1 ProxyAdmin owner |

## 2. Shared signers

Signers are shown under labels local to this sheet (Key N1 to Key N9) and by shortened address, which anyone can recover with `getOwners()`. These labels are distinct from the Key A to Key H labels of the [multisig-overlap research](https://github.com/RealSpap/multisig-overlap-showcase).

| Key | Address | Safe A | Safe B | Safe C | Other mainnet Safes |
|---|---|---|---|---|---|
| N1 | `0xa6e8…eef6` | yes | yes | yes | 1 (a 5-of-7) |
| N2 | `0x46A6…07e8` | yes | yes | yes | 2 |
| N3 | `0x7d79…1254` | yes | yes | yes | 7 (five of them 1-of-2) |
| N4 | `0xe885…470E` | yes | yes | | 1 |
| N5 | `0xbFc8…1cb6` | yes | yes | | 0 |
| N6 | `0x93BC…9df1` | yes | | yes | **8** (five 3-of-5, two 2-of-3, one 4-of-7) |
| N7 | `0x5256…8be2` | yes | | | 1 |
| N8 | `0x0A86…Ab5f` | | yes | | 0 |
| N9 | `0xE400…f93C` | | yes | yes | 1 (a 1-of-2) |

**Inside Notional.** 9 distinct keys hold 19 seats. Safe A and Safe B share 5 of their 7 signers. Keys N1, N2 and N3 sit on all three Safes, so these three keys alone meet the threshold of each one: 3 of Safe A, 2 of Safe B, 3 of Safe C.

**Outside Notional.** Per Safe, the number of signers that also sit on at least one other Ethereum Safe:

| Safe | Signers also seated elsewhere | Attributed to another protocol in the published research |
|---|---|---|
| Safe A (3-of-7) | 6 of 7 (N1, N2, N3, N4, N6, N7) | 0 |
| Safe B (2-of-7) | 5 of 7 (N1, N2, N3, N4, N9) | 0 |
| Safe C (3-of-5) | 5 of 5 (N1, N2, N3, N6, N9) | 0 |

The 17 other Safes involved were listed from the Safe Transaction Service index (used as a lead only), then each one was re-read on-chain with `getOwners()` and `getThreshold()` on both RPCs: all 17 confirmed, every listed key present. Who those 17 Safes belong to is not established in this sample. Three of them carry two or three Notional keys at once (`0xFE4202c3…3E2a` 3-of-5 with N2, N3 and N4; `0xf22f7b6F…976B` 1-of-2 with N2 and N3; `0xfFe9D890…9B85` 2-of-3 with N3 and N7), which suggests team-run Safes but does not prove it. The other 14 carry exactly one Notional key, 8 of them through Key N6.

**Against the published data.** None of the 9 keys matches a signer address published by the multisig-overlap research or embedded in its public [Check your Safe](https://realspap.github.io/tools/check-your-safe.html) tool (3 full signer addresses), and Notional appears in none of the protocol lists of its Keys A to H. No Notional Safe or signer address appears anywhere in that repository. A paid sheet would attribute the 17 outside Safes one by one.

## 3. Past exploit patterns that apply to this structure

From the public [onchain-postmortems](https://github.com/RealSpap/onchain-postmortems) collection:

- **[notional-v1-escrow](https://github.com/RealSpap/onchain-postmortems/tree/main/notional-v1-escrow/)**, same protocol. The 2026-09-03/04 overflow exploit hit the legacy V1 Escrow (row 13). Read for this sheet: Safe C upgraded the Escrow, through the V1 ProxyAdmin, to an `EmptyProxy` implementation at block 25,901,449 (2026-09-04 04:06:11 UTC, transaction `0x012fc554b165b3b3ccf3121018ae26503cab50031fa84adea29253b1cd5831d9`), 4 h 4 min 36 s after the extraction block. The legacy surface had kept its live, undelayed upgrade path, and that path is what allowed the fast response.
- **[drift-protocol-durable-nonce-admin-hijack](https://github.com/RealSpap/onchain-postmortems/tree/main/drift-protocol-durable-nonce-admin-hijack/)**: two multisig signers were induced to pre-sign transactions that were broadcast weeks later to take the admin role. The structural match here is Safe B: 2 signatures, no delay, ownership of the NOTE token. A Safe signature for the current nonce stays executable until that nonce is used, and Safe B has executed 7 transactions in total.
- **[fetchai-nunet-dual-key-compromise](https://github.com/RealSpap/onchain-postmortems/tree/main/fetchai-nunet-dual-key-compromise/)**: keys holding mint or release authority over a token were used directly. A UUPS upgrade of NOTE (row 4) replaces its code entirely, which is at least equivalent to mint authority.
- **[barnbridge-dormant-dao-controller-swap](https://github.com/RealSpap/onchain-postmortems/tree/main/barnbridge-dormant-dao-controller-swap/)** and **[termfinance-metavault-governance](https://github.com/RealSpap/onchain-postmortems/tree/main/termfinance-metavault-governance/)**: token-voted governance, dormant or lightly watched, used to pass a hostile proposal. Notional's GovernorAlpha (row 9) owns none of the contracts read here and the 48 h timelock accepts proposals only from Safe A, so this pattern does not apply today. It would apply again if authority were ever handed back to the governor.
- **[safe-uniswapv4-module-unauthenticated-executor](https://github.com/RealSpap/onchain-postmortems/tree/main/safe-uniswapv4-module-unauthenticated-executor/)** and **[flashloopadapter-safe-module-caller-spoof](https://github.com/RealSpap/onchain-postmortems/tree/main/flashloopadapter-safe-module-caller-spoof/)**: Safe modules that could be driven by outsiders. Checked: no module is enabled on Safe A, B or C (`getModulesPaginated` returns an empty list on all three). Not applicable today.

## 4. Observations

Ranked from most to least significant. Each one is a reading at block 26,124,800, followed by a question for the team.

1. **The NOTE token can be upgraded by 2 of 7 signatures, with no delay.** `NOTE.owner()` is Safe B (2-of-7) and no ownership transfer event has ever been emitted by the token. Safe B has executed 7 transactions. The 48 h timelock introduced in January 2026 covers the V3 proxy, the TradingModule and vault code, but not the token. *Is NOTE meant to stay outside the timelock? Is a move of its ownership behind the timelock, or to a higher threshold, planned?*
2. **The three Safes are not independent.** Safe A and Safe B share 5 of 7 signers, and Keys N1, N2 and N3 together meet the threshold of all three Safes. The split between owner, guardian and legacy roles therefore separates functions, not key holders. *Is the overlap deliberate, for example for availability, and is it documented for token holders?*
3. **Delay coverage is uneven.** With 48 h of notice: V3 proxy, beacons, TradingModule, vault code. With no notice: the V2 proxy and the TreasuryManager (Safe A, directly; the TreasuryManager holds 1,093,949.69 NOTE and 5,913.39 USDC and its owner can withdraw any token), vault role administration (Safe A), sNOTE (Safe C; 301,826.09 sNOTE outstanding, whose pool claim reads about 9.77 WETH and 23,321,858.80 NOTE through `getTokenClaim`), and the V1 legacy proxies (Safe C). Day-to-day treasury functions sit with one EOA, `0x7459…f7Ed`. *Which of these are expected to move behind the timelock?*
4. **Two keys hold many outside seats.** Key N6 (on Safe A and Safe C) also signs on 8 other Ethereum Safes, and Key N3 (on all three Safes) on 7, five of them 1-of-2. *Are these outside roles disclosed? Are they part of the team's availability or key-hygiene policy?*
5. **One timelock operation has been executable for months.** Operation `0x5860108201b683c1d2f28b1c68fdaa9ed2e3a46d7d802888d6686cb4fee746d5`, scheduled 2026-03-12 11:08:47 UTC (block 24,640,991), is in state Ready (`getOperationState` = 2) since 2026-03-14 11:08:47 UTC, neither executed nor cancelled. It calls `setPriceOracle` on the TradingModule for token `0x12b004719fb632f1e7c010c6f5d6009fb4258442` (on-chain symbol `liUSD-1w`), whose oracle reads unset today. A twin operation for `liUSD-4w` was scheduled the next day and executed on 2026-03-17. Safe A can execute the pending one at any moment, with no new public notice. *Is it still wanted, or should it be cancelled?*
6. **The public governance page describes an older setup.** Notional's Governance Reference (marked "Last updated 4 years ago" when fetched on 2026-10-05) describes a 3-of-5 owner multisig, a 2-of-3 Pause Guardian and no timelock. On-chain: the V3 owner is a 48 h timelock driven by a 3-of-7 Safe, the Pause Guardian is 2-of-7, and the 3-of-5 Safe now holds sNOTE and the V1 contracts. The Deployments page lists no Safe or timelock. *Can the page be updated with the current addresses and roles?*
7. **The GovernorAlpha is still deployed with a guardian.** It holds no authority over the 14 entries read here, its 4 proposals are executed, and Safe B keeps its guardian (cancel) role. Its parameters are low by today's standards for a live governor: a 1-block voting delay, a quorum of 4% of supply. *Is it formally retired, and should its guardian role be renounced so it cannot be confused with a live governance path?*
8. **Residual balances on V1.** The sealed V1 Escrow still holds 14,211.894948 USDC and 18.216201 WETH, recoverable only through a new upgrade by Safe C. V1 Portfolios, ERC1155Trade and Directory remain administered by the same ProxyAdmin. *Is a plan for these balances and for the remaining V1 proxies published?*
9. **Safe software is old.** Safe A and Safe B run version 1.2.0, Safe C 1.1.1; neither supports transaction guards (introduced in 1.3.0). *Is a migration planned?*

## 5. Method and reproduction

Every value above comes from a direct read, at block 26,124,800, on two independent public RPCs. An RPC failure is recorded as "not read", never as 0, and a read is used only when both RPCs return the same value. The final pass made 99 reads on `rpc.mevblocker.io` and `eth.drpc.org`; all 99 returned identical values on both. `ethereum-rpc.publicnode.com` served the first pass while the block was recent; it now asks for a personal token for that block, so replay there needs `latest` or an archive endpoint.

```bash
B=26124800
R=https://rpc.mevblocker.io          # second RPC: https://eth.drpc.org
IMPL=0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc   # EIP-1967 implementation slot
ADMIN=0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103  # EIP-1967 admin slot

# Proxies: implementation, admin, owner (repeat for every row of the table)
cast storage 0x6e7058c91F85E0F6db4fc9da2CA41241f5e4263f $IMPL  -b $B -r $R
cast storage 0x6e7058c91F85E0F6db4fc9da2CA41241f5e4263f $ADMIN -b $B -r $R
cast call    0x6e7058c91F85E0F6db4fc9da2CA41241f5e4263f "owner()(address)" -b $B -r $R
cast call    0x6e7058c91F85E0F6db4fc9da2CA41241f5e4263f "pauseGuardian()(address)" -b $B -r $R
cast storage 0x6e7058c91F85E0F6db4fc9da2CA41241f5e4263f 13 -b $B -r $R      # pendingOwner (StorageLayoutV2): 0
cast call    0xCFEAead4947f0705A14ec42aC3D44129E1Ef3eD5 "owner()(address)" -b $B -r $R
cast call    0x38DE42F4BA8a35056b33A746A6b45bE9B1c3B9d2 "owner()(address)" -b $B -r $R
cast call    0x53144559c0d4a3304e2dd9dafbd685247429216d "manager()(address)" -b $B -r $R
cast call    0x594734c7e06C3D483466ADBCe401C6Bd269746C8 "NOTIONAL()(address)" -b $B -r $R
cast call    0xc4FD259b816d081C8bdd22D6bbd3495DB1573DB7 "owner()(address)" -b $B -r $R   # beacons
cast call    0x09DbA4Fa1826f7d0E284513333FE71867b324261 "owner()(address)" -b $B -r $R

# Timelock: delay, roles, pending operation
TL=0x375eafe4348c6aa851cdfa5f84ec268f73643235
cast call $TL "getMinDelay()(uint256)" -b $B -r $R
cast call $TL "hasRole(bytes32,address)(bool)" $(cast keccak PROPOSER_ROLE) 0x02479bfc7dce53a02e26fe7baea45a0852cb0909 -b $B -r $R
cast call $TL "hasRole(bytes32,address)(bool)" $(cast keccak EXECUTOR_ROLE) 0x0000000000000000000000000000000000000000 -b $B -r $R
cast call $TL "getOperationState(bytes32)(uint8)" 0x5860108201b683c1d2f28b1c68fdaa9ed2e3a46d7d802888d6686cb4fee746d5 -b $B -r $R

# GovernorAlpha
GA=0x086b4ecD75c494dD36641195E89c25373E06d7cB
for f in "getMinDelay()(uint256)" "guardian()(address)" "quorumVotes()(uint96)" "proposalThreshold()(uint96)" "votingDelayBlocks()(uint32)" "votingPeriodBlocks()(uint32)" "proposalCount()(uint256)"; do cast call $GA "$f" -b $B -r $R; done

# Safes: threshold, owners, version, nonce, modules
for S in 0x02479bfc7dce53a02e26fe7baea45a0852cb0909 0xD9D5a9dc6a952b7aD6B05a983b399537B7c0Ee88 0x22341fB5D92D3d801144aA5A925F401A91418A05; do
  cast call $S "getThreshold()(uint256)" -b $B -r $R
  cast call $S "getOwners()(address[])" -b $B -r $R
  cast call $S "VERSION()(string)" -b $B -r $R
  cast call $S "nonce()(uint256)" -b $B -r $R
  cast call $S "getModulesPaginated(address,uint256)(address[],address)" 0x0000000000000000000000000000000000000001 10 -b $B -r $R
done

# Vaults: role holders and holdings
V=0xba4eb30f7F2e378249cf94E08F581e704326e9c6
cast call $V "hasRole(bytes32,address)(bool)" 0x0000000000000000000000000000000000000000000000000000000000000000 0x02479bfc7dce53a02e26fe7baea45a0852cb0909 -b $B -r $R
cast call $V "hasRole(bytes32,address)(bool)" $(cast keccak EMERGENCY_EXIT_ROLE) 0xD9D5a9dc6a952b7aD6B05a983b399537B7c0Ee88 -b $B -r $R
cast call $V "getStrategyVaultInfo()((address,uint8,uint256,uint256,uint256,uint256))" -b $B -r $R
```

**Event history** (full range, `gateway.tenderly.co/public/mainnet`, `eth_getLogs` from block 0 to 26,124,800):

- `Upgraded(address)` and `OwnershipTransferred(address,address)` on rows 1, 3 to 7 and 13: give the router history (V3 downgraded to its pause router at block 23,719,842 on 2025-11-03, then `FinalRouterV3`, then `TimelockRouter` at block 24,193,048 on 2026-01-08; V3 ownership claimed by the timelock at block 24,278,576 on 2026-01-20; V2 moved from Safe C to Safe A at block 20,577,955 on 2024-08-21) and the Escrow upgrade of 2026-09-04.
- `RoleGranted` and `RoleRevoked` on the timelock (all grants at its deployment, block 24,184,618, 2026-01-07; no revocation) and on the three vaults.
- `CallScheduled`, `CallExecuted` and `Cancelled` on the timelock: 3 scheduled, 2 executed, 0 cancelled.
- `ChangedThreshold`, `AddedOwner` and `RemovedOwner` on the three Safes: Safe A's threshold was set to 3 at block 13,531,141 (2021-11-01) and has not changed since.

**Implementation names** come from Sourcify's verified-source API (`sourcify.dev/server/v2/contract/1/<address>`), and the access rules quoted (`onlyOwner`, `onlyNotionalOwner`, `_authorizeUpgrade`) from that verified source or from Notional's own repositories. **Outside Safes** (section 2) come from `safe-transaction-mainnet.safe.global/api/v1/owners/<signer>/safes/`, used only to find candidates; each candidate was then re-read on-chain. That index covers Safe contracts known to the service, not other multisig types.

**Reconciliation with an earlier public note.** The [defi-admin-key-risk research](https://github.com/RealSpap/defi-admin-key-risk-showcase), section "What came back safe", lists "Notional V2 (2-of-7 Safe)". Read today, the owner of the V2 proxy is Safe A, 3-of-7, with threshold 3 since 2021; the 2-of-7 Safe in this structure is Safe B, the pause guardian and NOTE owner. That line was corrected in the same update, on 2026-10-05.

## 6. Disclaimer and conflict of interest

This is not a security audit and not investment advice. It describes who can change what, read on-chain at one block; it does not review contract logic, and it rates nothing.

Conflict-of-interest rule: the author does not hold the token of a protocol covered by a sheet. For this sheet: no NOTE and no sNOTE. This sample is free and was not commissioned by Notional or by any other party.

Corrections are welcome via [@RealSpap](https://x.com/RealSpap) on X; verified corrections are published with the date of the change.
