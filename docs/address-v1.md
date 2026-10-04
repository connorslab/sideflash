# Compact embedded address profile v1

Experimental, unassigned development profile. Implemented in the protocol
repository's Python fixture codec; **not yet supported by the ASP or wallet Rust
codecs**. No resolver, registry lookup, redirect or external offer reference is
used. Offline decoding recovers the complete offer. Payment and fresh invoice
negotiation still require connectivity.

## Envelope and canonical representation

Keep HRP `sfl`, Bech32m, maximum 1023 ASCII characters and 633 decoded bytes.
The `1` in `sfl1` is the separator, not the version. Accept uniform upper or lower
case, reject mixed case and nonzero or excessive conversion padding.

Replace the v0 map with a deterministic CBOR array of exactly 11 elements:

| Index | Type | Meaning |
| --- | --- | --- |
| 0 | uint64 | Version: 1 |
| 1 | uint64 | Required envelope features: 0 |
| 2 | uint64 | Locally defined network profile: 0 or 1 |
| 3 | bytes, 33 | Full compressed destination service public key |
| 4 | bytes | Unchanged binary native destination from v0 |
| 5 | bytes | Complete, exact BOLT12 offer TLV bytes |
| 6 | uint64 | Binding revision |
| 7 | uint64 | Inclusive validity start, Unix seconds |
| 8 | uint64 | Exclusive expiry, Unix seconds |
| 9 | bytes, 64 | Recipient BIP340 authorization |
| 10 | bytes, 64 | Service BIP340 acknowledgment |

Use definite lengths, shortest integer and length forms, no CBOR tags, and no
additional elements or trailing bytes. Booleans are not integers. Reject negative
or overflowing integers, invalid public keys, wrong signature lengths, empty
offers, unsupported versions/features/policies and empty validity intervals.
Apply bounds before nested parsing; native length-prefixed fields must fit the
remaining native byte string. Neither native nor offer data is compressed or
reconstructed from a remote source. Preserve all offer TLVs, including optional
ones, byte for byte.

## Network profile assignments

These assignments are **local to Sideflash development version 1**, not global
chain IDs or BOLT feature allocations. Their semantics are immutable for v1.
Implementations ship this table; they never fetch it when decoding an address.
Unknown profiles fail closed. Do not guess from address HRPs or genesis alone.

Both profiles expand to fork discriminator
`d0566e5a56534f7a0b10e91d69a18290c8a00079e9084b22966f8cacfde230ab`,
SHA256 of ASCII `Sideflash/XBT/blake2b-unified-sighash/v0` without NUL.

| Code | Chain | Genesis hash, Lightning chain-hash byte order | Native network flag |
| --- | --- | --- | --- |
| 0 | bitcoin (XBT) mainnet | `6fe28c0ab6f1b372c1a6a246ae63f74f931e8365e15a089c68d6190000000000` | 0 |
| 1 | isolated bitcoin (XBT) regtest | `06226e46111a0b59caaf126043eb5bbf28c34f3a5e332a1fc7b2b73cf188910f` | 1 |

Check the expanded profile against the configured chain, the native network,
and the offer chain. Continue requiring offer identity bit 512 and rejecting
unsupported mandatory offer features. Signet and other networks remain
unsupported. Regtest does not identify a particular laboratory; retain full
service-identity pinning. No chain/fork security check is removed by compression.

## Authentication

Let `A(n)` be canonical CBOR serialization of the first n elements, with the array
header encoding n, not the full envelope length. Compute:

```
recipient_digest = SHA256("Sideflash/recipient/v1" || 0x00 || A(9))
service_digest   = SHA256("Sideflash/server/v1"    || 0x00 || A(10))
```

Element 9 signs the recipient digest under the native pubkey-policy authority.
Element 10 signs the service digest under element 3's x-only public key. The
service signature includes the recipient signature. Both signatures remain;
no secret key sharing or signature aggregation is introduced.

Derive the recipient key from the native policy and verify the full service
identity against authenticated context, as in v0. The short native fingerprint
alone is insufficient. Authenticate delivery of the address itself: an attacker
can replace the entire address with another correctly signed address.

## Migration and extraction

Version 0 remains the historical 12-entry map and retains its original signature
domains. Version 1 is the 11-element array above. A multi-version reader dispatches
by container shape and explicit version, never by trial verification or inferred
network. Unsupported versions fail explicitly. A v0 address cannot be converted
by copying signatures: both recipient and service must authorize the v1 binding.
Do not silently downgrade, reinterpret a v0 map as v1, or change existing offers.

After validation, encode element 5 as ordinary `lno1` BOLT12 text without a
Bech32m checksum. Extraction works offline; current availability, revocation,
invoice negotiation and safe payment delivery are separate checks. No resolver
is required for Ark destination or offer extraction.

## Measured fixtures

| Fixture | v0 bytes / characters | v1 bytes / characters | Saved |
| --- | --- | --- | --- |
| Mainnet | 563 / 911 | 484 / 785 | 79 bytes / 126 characters |
| Regtest | 598 / 967 | 519 / 841 | 79 bytes / 126 characters |

For these fixtures, replacing two 32-byte hash fields with one small profile
integer saves 67 CBOR bytes, and removing 12 map keys saves 12 more. Counts vary
with offer size and integer widths; these are not fixed address lengths. Mainnet
is about 13.8% shorter. Both use the exact original native destination and offer,
new v1 signatures, known public test keys and expired validity intervals.

See [v1 fixtures](../tests/vectors/sideflash-v1.json), the bounded
[fixture codec](../tests/compact_v1.py), [tests](../tests/test_compact_v1.py), and
[synthetic QR results](../tests/qr-report-v1.json). These are not an independent
complete implementation, production payment parser or security audit. Physical
camera tests, Rust migration and complete delivery/recovery tests remain open.
