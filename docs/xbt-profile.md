# XBT network profile

All payment and integration guidance in this repository targets bitcoin
(XBT). References to native Ark and Lightning mean their XBT-compatible versions.
SHA-256 BTC interoperability is not a goal of this implementation profile.

The address requires both a genesis hash and an explicit fork discriminator.
Development profile v0 uses SHA256 of the ASCII string
`Sideflash/XBT/blake2b-unified-sighash/v0`, without a terminating NUL. This is a
Sideflash-local discriminator, not a claim of a globally registered chain ID.
Changing this assignment requires a profile migration before stable release.

Require XBT identity bit 512 in the embedded BOLT12 offer and reject unsupported
required features. Invoice requests, invoices, node negotiation and transaction
signatures must continue to follow the deployed XBT implementation's rules.
Do not blindly copy node feature bits into an offer: feature fields have distinct
contexts. In particular, channel/signature negotiation is not established merely
by an offer's identity bit or a Sideflash signature.

Use the XBT consensus and recovery rules in the underlying Ark implementation.
Sideflash binding signatures are application-level BIP340 signatures; they do
not replace XBT transaction sighash rules. Lightning payment hashes retain their
existing semantics. Never substitute another hash just because the chain uses
Blake2b proof of work.

Test on isolated XBT regtest, then on explicitly authorized XBT mainnet amounts.
Never infer the chain from `bc1`, `lnbc`, a native Ark prefix, or a shared genesis
alone. Wallet displays, quotes, balances and fees must identify XBT and XBT sats.
