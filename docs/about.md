# Access to the tool, authority sheets, about, licence

## Access to the tool

Findings and on-chain sources are always public; the tooling that produces them is private. A case checked days or weeks ago can read differently today: admin keys get rotated, renounced, or compromised on-chain. Want to check one yourself right now, free? [Admin Key Checker](https://realspap.github.io/tools/admin-key-checker.html) classifies any contract's admin-key pattern live from chain, in your browser, no account needed. For a full check of a named protocol, with the dollar-figure decomposition and a look for documented hostile activity around the key, reach out via [RealSpap on X](https://x.com/RealSpap).

## Sample authority sheets

Two free samples of a per-protocol authority sheet: who can upgrade, pause or reconfigure each core contract, behind which delay and which multisig threshold, which signers sit on other protocols, and every on-chain read needed to reproduce it. Neither was commissioned.

- [Notional Finance](../authority-sheets/notional-finance.md) (lending, Ethereum)
- [Hop Protocol](../authority-sheets/hop-protocol.md) (bridge, Ethereum L1)

A sheet for another protocol can be requested on [X](https://x.com/RealSpap).

## About

[About this research program](https://realspap.github.io/method.html#disclaimer). Related work: [multisig-overlap](https://github.com/RealSpap/multisig-overlap-showcase) (shared multisig signers across protocols) and [onchain-postmortems](https://github.com/RealSpap/onchain-postmortems) (DeFi exploits independently reconstructed).

## License

Findings, data, documentation and the sample authority sheets: [CC BY 4.0](../LICENSE). Reuse them freely, including commercially, with credit to RealSpap and a link to this repository. Scripts and workflows (`scripts/`, `.github/`): [MIT](../LICENSE-CODE). The private tooling that produces the findings is not part of this repository.
