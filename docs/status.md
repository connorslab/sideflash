# Status and open decisions

As of 2026-10-04, the implementation branch contains an experimental Rust address
codec, separate recipient authorization and server acknowledgment, signature
verification, candidate route selection and Lightning-only offer extraction.
It has no deployed Sideflash endpoint and cannot initiate a Sideflash payment.

Six focused XBT Sideflash tests and workspace compilation pass in both feature branches. The full unit
suite has 36 failures also reproduced on the unchanged baseline in the test
environment. This is not a clean full-suite release result.

The [compact v1 wire document](address-v1.md) defines the current protocol
proposal. A Python fixture codec, re-signed mainnet/regtest vectors, mutation and
canonical-encoding tests, and synthetic QR checks are present. ASP/wallet Rust
feature branches now create v1 and retain v0 readers. Six codec tests and workspace
checks pass in each branch, including the feature-enabled wallet build. No stable
release or production deployment includes these changes yet.

The version-0 wire document records the legacy encoding. Whitepaper v0.2 now
describes compact wire v1, the 633-byte limit, measured sizes and version migration.
It supersedes v0.1's larger proposed limits and resolver options. Payment preparation
and recovery requirements in the paper are not claims of implemented delivery.

Before a stable version, decide and test:

The [stability decisions](stability-decisions.md) now define the initial scope and
track evidence for each item below. Mainnet/regtest fixtures are verified by Rust
and a separate Python fixture checker. QR results are synthetic only. The initial
profile deliberately rejects delegated and non-pubkey policies and requires an
online recipient for the planned remote-delivery path. Server coordination,
recovery construction and independent review remain open.

1. Chain and fork discriminator assignments, including test networks.
2. Canonical cross-implementation vectors and address size/QR practicality.
3. Recipient policies beyond pubkey and delegated binding authority.
4. Fresh status, rotation and revocation semantics without address lookups.
5. Payment preparation APIs and persisted, idempotent state transitions.
6. Exact preimage ownership and conditional VTXO recovery construction.
7. Receiver-managed preparation for ordinary Lightning-only payers.
8. Offline recipient behavior and capability negotiation.
9. Fees, inventory accounting, cancellation and recovery limits.
10. Independent review and two-server delivery/recovery evidence.

The first implementation is a foundation for these steps, not a complete
cross-server payment system. Production activation and public release require
separate review.

## Standards used

- [BOLT12](https://github.com/lightning/bolts/blob/master/12-offer-encoding.md)
- [BIP340 signatures](https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki)
- [BIP350 Bech32m](https://github.com/bitcoin/bips/blob/master/bip-0350.mediawiki)
- [RFC8949 CBOR](https://www.rfc-editor.org/rfc/rfc8949.html)

Sideflash is an application proposal built on these primitives, not a feature
already standardized by them.
