# Authority sheet: Hop Protocol (Ethereum L1 bridges)

| | |
|---|---|
| Protocol | Hop Protocol |
| Scope | The 10 L1 bridge contracts listed in Hop's official SDK address file for Ethereum mainnet, the L1 CCTP bridge, the bridge Timelock and its admin Safe, the HOP token, the HOP Governor and the DAO Timelock (16 contracts). L2 deployments are out of scope. |
| Chain | Ethereum mainnet only |
| Read at | Block **26,124,800** (2026-10-05 07:53:35 UTC) |
| RPCs | `https://ethereum-rpc.publicnode.com` and `https://rpc.mevblocker.io`, same block, results compared line by line. Event history from `https://gateway.tenderly.co/public/mainnet` (blocks 0 to 26,124,800). |
| Contract list source | `hop-protocol/hop`, branch `develop`, `packages/sdk/src/addresses/mainnet.ts` (section `bridges.<token>.ethereum`) |
| Source code | Verified sources fetched from Sourcify (L1 ETH bridge, L1 HOP bridge, bridge Timelock, HOP token, L1 CCTP bridge), plus `hop-protocol/contracts`, branch `v1` |
| Type | Free sample, not commissioned |

Every value below is "read at block 26,124,800" unless another block is given. All values matched on both RPCs. A value that could not be read is marked "not read", never 0.

## 1. Summary

- **No upgrade path.** None of the 10 L1 bridges is a proxy: the three EIP-1967 slots are empty and the bytecode exposes no `upgradeTo` selector. Their code cannot be replaced. Their configuration can be changed.
- **One key path changes the configuration of every bridge.** All 10 bridges return the same `governance()`: a Compound-style Timelock with a **1-day** delay. Its only `admin()` is a **2-of-3 Safe**, and all three owners are plain EOAs. The owner set has not changed since 2021-12-07. The bridge Timelock also sends governance messages to Hop's L2 deployments (234 executed cross-domain calls); those deployments are out of scope here.
- **The DAO controls a separate set of contracts.** The HOP Governor and its 2-day TimelockController own the HOP token, which has an uncapped `mint`. The DAO Timelock also holds 511.5M HOP of treasury and is the `migrator` of the HOP bridge. It has no role on the other 9 bridges.
- **Shared signers: 0.** None of the 3 Safe owners sits on a multisig of another tracked protocol. This is the published figure, and the owner set it covers has not changed since.
- **The L1 CCTP bridge has no admin.** Every parameter is immutable.

## 2. Authority map

### 2.1 L1 bridges (same authority on all 10)

| Bridge | Address | Code size | Proxy | Balance held at block B | Bonders (current) |
|---|---|---|---|---|---|
| ETH | `0xb8901acB165ed027E32754E0FFe830802919727f` | 18,447 | No | 602.77 ETH | 1 |
| USDC.e | `0x3666f603Cc164936C1b87e207F36BEBa4AC5f18a` | 19,299 | No | 538,439.37 USDC | 1 |
| DAI | `0x3d4Cc8A61c7528Fd86C55cfe061a78dCBA48EDd1` | 19,373 | No | 302,284.94 DAI | 3 |
| USDT | `0x3E4a3a4796d16c0Cd582C382691998f7c06420B6` | 19,373 | No | 266,664.18 USDT | 2 |
| MATIC | `0x22B1Cbb8D98a01a3B71D034BB899775A76Eb1cc2` | 19,373 | No | 371,147.36 MATIC | 1 |
| HOP | `0x914f986a44AcB623A277d6Bd17368171FCbe4273` | 18,570 | No | 83,062,615.22 HOP | 1 |
| MAGIC | `0xf074540eb83c86211F305E145eB31743E228E57d` | 19,373 | No | 277,154.15 MAGIC | 1 |
| SNX | `0x893246FACF345c99e4235E5A7bbEE7404c988b96` | 19,373 | No | 37,338.63 SNX | 2 |
| rETH | `0x87269B23e73305117D0404557bAdc459CEd0dbEc` | 19,373 | No | 14.64 rETH | 1 |
| sUSD | `0x36443fC70E073fe9D50425f82a3eE19feF697d62` | 19,373 | No | 0 sUSD | 2 |

The same answers hold for all 10 bridges:

| Question | Answer, read on-chain |
|---|---|
| Who can upgrade? | Nobody. No proxy, no upgrade function. |
| Who changes critical parameters? | `governance()` = Timelock `0x22e3F828b3f47dAcFACd875D20bd5cc0879C96e7` on all 10. It can call `setGovernance`, `setCrossDomainMessengerWrapper` (the contract that confirms transfer roots for each chain ID), `addBonder` / `removeBonder`, `setChallengePeriod`, `setChallengeResolutionPeriod` and `setMinTransferRootBondDelay`. All 9 setter selectors were found in each of the 10 bytecodes. |
| Who can pause? | The same Timelock, per destination chain, with `setChainIdDepositsPaused(chainId, bool)`. At block B no chain ID was paused (checked for 10, 42161, 137, 100, 8453, 42170, 59144 and 1101). |
| Who can move funds? | The same Timelock, through `rescueTransferRoot`: only for the unwithdrawn part of a transfer root, and only after the 8-week `RESCUE_DELAY` from the verified source. It was executed 3 times, the last in 2022. **HOP bridge only:** `migrateTokens(recipient)` sends the bridge's entire HOP balance to any recipient, and only `migrator()` can call it. `migrator()` = DAO Timelock `0xeeA8422a08258e73c139Fc32a25e10410c14bd7a`. |
| Delay | 86,400 s (1 day). The bridge Timelock has `MINIMUM_DELAY` = 86,400 and `MAXIMUM_DELAY` = 2,592,000. It has never emitted a `NewDelay` event, so the delay has been 1 day since deployment. |
| Multisig | 2-of-3. The Safe is the Timelock's `admin()`. |
| Challenge settings | `challengePeriod` = 86,400 s, `challengeResolutionPeriod` = 1,209,600 s (14 days), `minTransferRootBondDelay` = 900 s. These values are identical on all 10. The challenge stake is the constant `CHALLENGE_AMOUNT_DIVISOR = 10`, from the verified source. |

### 2.2 Governance and related contracts

| Contract | Address | Proxy | Read at block B | What it controls |
|---|---|---|---|---|
| Bridge Timelock (Compound-style) | `0x22e3F828b3f47dAcFACd875D20bd5cc0879C96e7` | No | `admin()` = Safe `0x1ec0…6e9d`, `pendingAdmin()` = 0x0, `delay()` = 86,400, `GRACE_PERIOD()` = 1,209,600 | Bridge configuration on all 10 L1 bridges. It is also the `owner()` of 4 of the 8 ETH-bridge messenger wrappers: Optimism `0xa45D…ebd1`, Arbitrum `0xDD37…5434`, Base `0x17B5…2C95` and Nova `0x468F…9f74`. For the other 4 wrappers, `owner()` reverts. |
| Safe (bridge Timelock admin) | `0x1ec078551A5ac8F0f51fAc57Ffc48Ea7d9A86E9d` | Safe proxy, singleton `0x34cf…3f5f` (v1.1.1) | `getThreshold()` = 2, 3 owners, `VERSION()` = "1.1.1", `nonce()` = 628, no module, holds 14,415,542.55 HOP | Queues, executes and cancels on the bridge Timelock |
| HOP token | `0xc5102fE9359FD9a28f877a67E36B0F050d81a3CC` | No | `owner()` = DAO Timelock, `totalSupply()` = 1,000,000,000 HOP | `mint(dest, amount)` by the owner, with no cap in the verified source. Also `burn` of the owner's own balance and `sweep` of unclaimed airdrop tokens (claim period ended 2022-12-09). Only 2 mints since deployment, both in the constructor. |
| HOP Governor | `0xed8Bdb5895B8B7f9Fdb3c087628FD8410E853D48` | No | `timelock()` = DAO Timelock, `votingDelay()` = 1 block, `votingPeriod()` = 45,818 blocks (about 6.4 days), `proposalThreshold()` = 1,000,000 HOP, `quorumNumerator()` = 600 / `quorumDenominator()` = 10,000, `quorum(26124000)` = 60,000,000 HOP | Proposals to the DAO Timelock |
| DAO Timelock (OZ TimelockController) | `0xeeA8422a08258e73c139Fc32a25e10410c14bd7a` | No | `getMinDelay()` = 172,800 s (2 days). The PROPOSER role is held by the Governor. The EXECUTOR role is held by address(0), so anyone can execute. The admin role is held by itself only, and the deployer's admin role was revoked in 2022. Holds 511,540,519.88 HOP | Owner of the HOP token and `migrator` of the HOP bridge. It has no role on the bridge Timelock or the Safe: `hasRole` returned false for the Safe on the admin and proposer roles. |
| L1 CCTP bridge | `0x7e77461CA2a9d82d26FD5e0Da2243BF72eA45747` | No | `owner()` and `governance()` revert. The verified source has only `immutable` parameters and a fixed chain list set in the constructor. USDC balance = 0 | Nothing to administer. The contract only sends, through Circle's `depositForBurn`. |

## 3. Shared signers

| Safe | Threshold | Owner | Address | Type | On this Safe since | Seats on multisigs of other tracked protocols |
|---|---|---|---|---|---|---|
| `0x1ec0…6e9d` (bridge Timelock admin) | 2-of-3 | Key A | `0x9f8d2dafE9978268aC7c67966B366d6d55e97f07` | EOA | 2021-12-07 (block 13,760,385) | 0 |
| | | Key B | `0x404c2184a4027b0092C5877BC4599099cd63E62D` | EOA | 2021-07-09 (block 12,796,064) | 0 |
| | | Key C | `0xEb34e93f90fa76c865112F4596eAb65D6F0d2F62` | EOA | since the Safe's setup (no AddedOwner or RemovedOwner event for it) | 0 |

The keys here are labelled only within this sheet. They are not the "Key A to H" of the cross-protocol study.

- **Published figure.** The author's public cross-protocol signer study (`multisig-overlap-showcase`, README, Part 1) states that Hop Protocol's L1 bridge-governance Safe (2-of-3) shares no signer with any other tracked protocol.
- **Today's re-read.** `getOwners()` at block B returns exactly these 3 addresses, on both RPCs. A full replay of the Safe's `AddedOwner` / `RemovedOwner` / `ChangedThreshold` events finds 5 events in total, and the last one is at block 13,760,420 (2021-12-07). The Hop side of the comparison is therefore unchanged since well before the published check. The other side, signers of other protocols, was not re-run today.
- **What the 0 covers, and what it does not.** "0" means no overlap with the protocols tracked in that study. It does not mean the keys sign nothing else.

## 4. Past exploit patterns that map to this structure

These are cases from the author's public postmortem collection, `onchain-postmortems/`. "Maps" describes a structural resemblance only. It is not a claim that Hop is exposed to the same bug.

| Pattern | Postmortem folder | Where it maps in Hop's L1 structure |
|---|---|---|
| A small multisig signs a harmful admin action | `drift-protocol-durable-nonce-admin-hijack/` | 2 signatures out of 3 on the Safe can queue any bridge configuration change. The 1-day Timelock delay is the window in which the queued call is public (`QueueTransaction` event) before it can run. |
| The bridge's own signing keys authorise an unbacked release | `afx-bridge-validator-key-compromise/`, `symbiosis-sybtc-mpc-signed-mint/` | The Hop L1 bridges do not release funds on signatures alone. Funds move against transfer roots that are either confirmed through the messenger wrapper of the origin chain, or bonded by an allowlisted bonder and open to challenge for 1 day. The closest analogues are the bonder keys (11 EOAs, section 5) and the governance path that can replace a wrapper. |
| A forged message or proof is accepted as a real deposit | `kelpdao-rseth-layerzero-rpc-spoofing/`, `verus-ethereum-bridge-forged-proof/`, `across-solana-event-spoofing/`, `coreum-xrpl-bridge-deposit-forgery/` | In Hop, the L1 check of a cross-chain message is `crossDomainMessengerWrappers[chainId].verifySender(...)`. Which wrapper is trusted for each chain is a setting that governance can change. The Timelock has executed 115 `setCrossDomainMessengerWrapper` calls since 2021, counting the initial setup. |
| A forged CCTP message is accepted on the receiving side | `allbridge-cctp-forged-message/` | Does not map to the contract read here. Hop's L1 CCTP contract only sends (`depositForBurn`) and has no receive path. |
| A dormant DAO is captured and its powers used | `barnbridge-dormant-dao-controller-swap/` | The HOP DAO holds an uncapped token mint, 511.5M HOP of treasury and the HOP bridge `migrator`. On 2026-08-04 (block 25,680,023) the DAO raised its quorum from 30/10,000 (3M HOP) to 600/10,000 (60M HOP), which raises the bar this pattern relies on. |

## 5. Observations

Most important first. Each one is a fact, followed by a question for the team.

1. **Bridge configuration sits with a 2-of-3 Safe, not with the DAO.** At block B, the 10 L1 bridges answer to the bridge Timelock, and the Timelock answers to the Safe. The DAO Timelock holds no role on either. The DAO's powers over the bridges are limited to the HOP bridge `migrator`.
   *Question:* Is there a published decision, such as a forum post or a DAO vote, that delegates bridge administration to this Safe? Is a move of the Timelock `admin()` to the DAO Timelock planned?

2. **The same Safe holds team tokens and administers the bridges.** A public block-explorer name tag labels `0x1ec0…6e9d` "Hop Protocol: Future Team Tokens" (the same label appears in the public dataset `brianleect/etherscan-labels`), and the Safe holds 14,415,542.55 HOP at block B.
   *Question:* Is it intended that one Safe both holds a token allocation and is the sole admin of the bridge Timelock? Or is the explorer tag out of date?

3. **The HOP bridge has a second authority with a one-call full withdrawal.** `migrateTokens(recipient)` on `0x914f…4273` sends the bridge's whole HOP balance (83,062,615.22 HOP at block B) to any recipient chosen by the `migrator`. The `migrator` is the DAO Timelock, behind a 2-day delay and a Governor vote. The `migrator` can also replace itself through `setMigrator`.
   *Question:* What is the intended use of this function, for example a future bridge migration? Is it documented for HOP holders on L2?

4. **The bridge Timelock's 1-day delay is the only time buffer before a configuration change.** The delay has never changed (no `NewDelay` event). History up to block B: 586 distinct transactions queued and 432 executed, no `CancelTransaction` event ever emitted, and none pending at block B. The other 154 were never executed and expired after the 14-day grace period (latest eta: August 2023). The last queue was on 2025-12-03 and the last execution on 2025-12-04 (`claimFunds` on two ETH messenger wrappers).
   *Question:* Does anyone outside the three signers monitor `QueueTransaction` events and publish alerts, so that the one-day window is actually used?

5. **The Safe runs version 1.1.1, with 3 EOA owners unchanged since 2021-12-07.** Version 1.1.1 does not support transaction guards. No module is enabled.
   *Question:* Is a migration to a current Safe version, or a rotation or extension of the signer set, on the roadmap?

6. **Bonders are allowlisted EOAs, often one per bridge.** There are 11 distinct bonder addresses across the 10 bridges, rebuilt from `BonderAdded` / `BonderRemoved` events and confirmed with `getIsBonder` at block B. All have code size 0 (plain EOAs, no EIP-7702 delegation). 6 of the 10 bridges have exactly one bonder. One address, `0x2a6303e6b99d451df3566068ebb110708335658f`, was removed from 6 bridges on 2024-11-14 but is still a bonder on the SNX and sUSD bridges.
   *Question:* Is the remaining bonder seat on SNX and sUSD intended? Is a larger or permissionless bonder set planned for the single-bonder bridges?

7. **The HOP token can be minted without a cap by the DAO.** `mint` is `onlyOwner` with no limit in the verified source. The owner is the DAO Timelock. Total supply is still exactly 1,000,000,000 HOP, and no mint has happened since the constructor.
   *For information:* The quorum increase of 2026-08-04 (table in section 4) is the main safeguard on this power.

8. **No admin on the L1 CCTP bridge.** `0x7e77…5747` has only immutable parameters, so there is nothing to govern and nothing to take over on L1.

## 6. Method and reproduction

Fixed block: `B=26124800`. Each `eth_call` and `eth_getStorageAt` below was sent to both RPCs at that block, and the two results were compared. Tool: Foundry `cast`. Publicnode serves this block only while it is recent. To replay later, use an archive endpoint: mevblocker, drpc and Tenderly all served block B on 2026-10-05.

```bash
B=26124800
for RPC in https://ethereum-rpc.publicnode.com https://rpc.mevblocker.io; do
  # Proxy check (EIP-1967 implementation, admin, beacon) on each bridge
  cast storage --block $B --rpc-url $RPC <bridge> 0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc
  cast storage --block $B --rpc-url $RPC <bridge> 0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103
  cast storage --block $B --rpc-url $RPC <bridge> 0xa3f0ad74e5423aebfd80d3ef4346578335a9a72aeaee59ff6cb3582b35133d50
  # Bridge configuration
  cast call --block $B --rpc-url $RPC <bridge> "governance()(address)"
  cast call --block $B --rpc-url $RPC <bridge> "challengePeriod()(uint256)"
  cast call --block $B --rpc-url $RPC <bridge> "challengeResolutionPeriod()(uint256)"
  cast call --block $B --rpc-url $RPC <bridge> "minTransferRootBondDelay()(uint256)"
  cast call --block $B --rpc-url $RPC <bridge> "isChainIdPaused(uint256)(bool)" <chainId>
  cast call --block $B --rpc-url $RPC <bridge> "crossDomainMessengerWrappers(uint256)(address)" <chainId>
  cast call --block $B --rpc-url $RPC <bridge> "getIsBonder(address)(bool)" <bonder>
  cast call --block $B --rpc-url $RPC 0x914f986a44AcB623A277d6Bd17368171FCbe4273 "migrator()(address)"
  # Bridge Timelock
  T=0x22e3F828b3f47dAcFACd875D20bd5cc0879C96e7
  cast call --block $B --rpc-url $RPC $T "admin()(address)"
  cast call --block $B --rpc-url $RPC $T "pendingAdmin()(address)"
  cast call --block $B --rpc-url $RPC $T "delay()(uint256)"
  # Safe
  S=0x1ec078551A5ac8F0f51fAc57Ffc48Ea7d9A86E9d
  cast call --block $B --rpc-url $RPC $S "getThreshold()(uint256)"
  cast call --block $B --rpc-url $RPC $S "getOwners()(address[])"
  cast call --block $B --rpc-url $RPC $S "VERSION()(string)"
  cast call --block $B --rpc-url $RPC $S "getModulesPaginated(address,uint256)(address[],address)" 0x0000000000000000000000000000000000000001 10
  cast storage --block $B --rpc-url $RPC $S 0   # singleton (master copy)
  # HOP token, Governor, DAO Timelock
  cast call --block $B --rpc-url $RPC 0xc5102fE9359FD9a28f877a67E36B0F050d81a3CC "owner()(address)"
  cast call --block $B --rpc-url $RPC 0xed8Bdb5895B8B7f9Fdb3c087628FD8410E853D48 "timelock()(address)"
  cast call --block $B --rpc-url $RPC 0xed8Bdb5895B8B7f9Fdb3c087628FD8410E853D48 "quorumNumerator()(uint256)"
  cast call --block $B --rpc-url $RPC 0xeeA8422a08258e73c139Fc32a25e10410c14bd7a "getMinDelay()(uint256)"
  cast call --block $B --rpc-url $RPC 0xeeA8422a08258e73c139Fc32a25e10410c14bd7a "hasRole(bytes32,address)(bool)" $(cast keccak PROPOSER_ROLE) 0xed8Bdb5895B8B7f9Fdb3c087628FD8410E853D48
  cast call --block $B --rpc-url $RPC 0xeeA8422a08258e73c139Fc32a25e10410c14bd7a "hasRole(bytes32,address)(bool)" $(cast keccak EXECUTOR_ROLE) 0x0000000000000000000000000000000000000000
done
```

**Selectors and source.** `cast selectors $(cast code --block $B <bridge>)` was run on each bridge. All 10 contain the 9 governance setter selectors and none of `upgradeTo`, `upgradeToAndCall` or `changeAdmin`. The HOP bridge alone also has `setMigrator`, `migrator` and `migrateTokens`. The verified ETH bridge source matches `hop-protocol/contracts` branch `v1`, apart from one default value that was later overwritten on-chain (`challengeResolutionPeriod`).

**Event history.** `eth_getLogs` over blocks 0 to B on the bridge Timelock (`QueueTransaction` / `ExecuteTransaction` / `CancelTransaction` / `NewDelay` / `NewAdmin`), the Safe (`AddedOwner` / `RemovedOwner` / `ChangedThreshold` / `ExecutionSuccess`), the DAO Timelock (`RoleGranted` / `RoleRevoked` / `MinDelayChange` / `CallScheduled` / `CallExecuted`), the HOP token (`OwnershipTransferred`, `Transfer` from 0x0) and the 10 bridges (`BonderAdded` / `BonderRemoved`).

**Quorum history.** `quorumNumerator()` at block 25,680,022 returned 30 on mevblocker, drpc and Tenderly. Publicnode did not serve this block (archive limit), so its value is "not read".

**Not read, or not applicable:**
- `l1CanonicalToken()` on the ETH bridge reverts. This is expected: the ETH bridge has no token.
- `owner()` reverts on 4 ETH-bridge messenger wrappers (Polygon, Gnosis, Linea, Polygon zkEVM).
- `owner()` and `governance()` revert on the CCTP bridge, and `minter()` reverts on the HOP token. The verified sources have no such functions.
- Three reads on mevblocker failed with HTTP 429 on the first pass. They were read again on both RPCs at the same block and matched.

## 7. Notice

This is not a security audit and not investment advice. It describes who can change what, as read on-chain at one block. It does not assess code correctness.

Conflict of interest rule: the author holds no HOP token and no position in Hop Protocol. This sheet is a free sample, not commissioned or paid for by Hop Protocol or any third party.
