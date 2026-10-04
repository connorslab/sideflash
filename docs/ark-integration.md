# Ark integration recommendations

## Wallet

- Recognize `sfl1` in addition to existing address formats. Enforce payload limits
  before parsing. Reject unknown versions and required features.
- Verify recipient and server signatures. Check the locally configured chain
  profile and full server identity. Do not trust a short server fingerprint alone.
- Use native Ark for a matching server. Otherwise present a Lightning-backed
  transfer with explicit net receipt, total debit and maximum fees.
- Require explicit authorization if fees or route change. Do not initiate a
  second route while the first payment is unresolved.
- Preserve conditional recovery material before irreversible settlement.
  Show delivery pending separately from payment failed.

## Server

Add opt-in capabilities for recipient registration, mapping status and payment
preparation. Persist recipient authorization and server acknowledgment. Sign
freshness responses over a request nonce, destination, revision and expiry.
Never treat an old response as evidence of current revocation status.

Bind each offer to one destination. Persist offers across restarts and make
invoice issuance, inventory reservations, HTLC handling and Ark receive state
part of a coordinated lifecycle. An unprepared invoice must not settle as
unsecured custodial credit. The receiving service must fail closed if it cannot
provide the negotiated delivery guarantees.

Suggested application operations are registration, resolution, preparation and
status reconciliation. Their transport schemas and endpoint paths are not yet
stable. Use authenticated requests, bounded inputs and explicit error classes.
Public read access must not expose a directory of all recipients or payment data.

Use transactional reservations and unique payment identifiers. Reject conflicting
VTXO spends, duplicate claims and competing reservations. Release locked value
only after reconciliation establishes that release cannot conflict with settlement.

## Compatibility and rollout

Do not change native Ark address parsing or existing wallet RPC semantics.
Advertise Sideflash as a separate optional capability. Unsupported wallets
continue to use ordinary Ark or BOLT12 destinations. Do not enable a capability
until its full delivery profile is operational, not merely its codec.

First deploy two isolated servers on a test network. Exercise same-server and
remote payments, independent recovery, restarts and double-spend attempts. Only
then consider a limited monetary test with explicit amounts and authorization.
