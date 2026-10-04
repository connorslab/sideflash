# Sideflash

Sideflash proposes one receive address for native Ark transfers and Lightning
payments on **Blake2b Bitcoin (XBT)**. This repository targets XBT specifically,
not SHA-256 BTC. An address starts with `sfl1`. A compatible sender uses native Ark
when both parties use the same server. Otherwise, it extracts an authenticated
BOLT12 offer and pays over Lightning. The recipient receives Ark value.

**Status: experimental protocol design and initial codec implementation.**
No stable wire format, independent audit, or complete cross-server delivery
implementation is claimed. Do not treat a valid address as proof of safe payment
delivery. Do not use the development addresses for real payments yet.

## Read the protocol

- [XBT network and feature requirements](docs/xbt-profile.md)
- [Protocol overview and payment lifecycle](docs/protocol.md)
- [Development address wire specification](docs/address-v0.md)
- [Ark server and wallet integration](docs/ark-integration.md)
- [Lightning wallet and node integration](docs/lightning-integration.md)
- [Security requirements and acceptance tests](docs/security-and-tests.md)
- [Implementation status and open decisions](docs/status.md)
- [Design whitepaper](whitepaper/sideflash-whitepaper.pdf)

This repository is the protocol discussion and integration reference. The
experimental Rust implementation lives in the
[Sideflash implementation branch](https://github.com/connorslab/paperclip-asp/tree/feature/sideflash).
Implementation-specific releases do not automatically stabilize this protocol.

The name prefix is `sfl`. The following `1` is the Bech32 separator, not a version.
Existing Ark addresses and BOLT12 offers retain their own formats and semantics.

## Scope

Sideflash defines destination authentication and payment route selection. It also
defines the requirements for safe delivery between independent Ark servers.
It is not a new blockchain, asset, consensus rule or public recipient directory.
It does not make Lightning channel balances into Ark backing or remove the need
for destination liquidity and recovery reserves.

Propose incompatible changes as a new profile. Include encoding vectors,
threat assumptions, failure behavior and compatibility consequences. The
development profile is not ready for external interoperability commitments.
