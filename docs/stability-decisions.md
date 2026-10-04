# Initial stability decisions and evidence

Date: 2026-10-04. These are initial profile decisions, not a declaration of
production readiness. All monetary references mean bitcoin (XBT).

## 1. Chain assignments

Use the immutable compact-v1 table in `address-v1.md`, which expands the
network code to the genesis hash and v0 fork discriminator in `xbt-profile.md`.
Legacy v0 continues to carry the hashes explicitly. Permit
mainnet and isolated regtest only. Reject signet and other test networks until
their chain profiles are assigned and tested. A regtest genesis does not identify
a particular private laboratory; deployments must also pin the destination
server key. Tests verify that a mainnet address fails regtest verification and
vice versa. The discriminator is an application identifier, not a consensus rule.

## 2. Canonical vectors and QR transport

Use the frozen `tests/vectors/sideflash-v0.json` fixtures in both the Rust library
and the Python checker. The development addresses are expired, with public test
keys; they must never receive payments. Do not regenerate them casually: the
generator uses random signatures and blinded paths, so its new output differs.

The prototype's 4096-character allowance exceeded the checksum library's code
length. The initial profile now limits text to 1023 characters and payloads to
633 bytes. Native address bytes replace nested native address text. Oversized
offers fail; no truncation or silent resolver fallback is allowed. A compact
profile is now specified separately as v1, not an implicit alternate encoding.
Its Python fixtures measure 785 mainnet and 841 regtest characters, with both
signatures and the complete offer preserved. Rust feature branches now support both versions; stable deployment is outstanding.
See `tests/qr-report-v1.json` for synthetic QR results. The following numbers
refer only to the legacy v0 fixtures.

The frozen examples have 911 mainnet characters and 967 regtest characters.
Synthetic QR round-trips pass at error-correction levels M and Q, in both cases.
Uppercase reduces the M-level examples to QR version 20, rendered at 420 pixels
with four pixels per module and a four-module border. Use uppercase for QR
display and lowercase for copied text. These dense codes require physical
phone-camera tests before UI release. Synthetic decoding is not that test.

## 3. Recipient authority

The first stable profile supports pubkey policies only. Reject all other
policies. No delegated binding key is accepted. This is an intentional scope
decision, not an unimplemented capability to advertise. A later delegation
certificate must bind destination, delegate key, allowed operations, validity
and revocation, without authorizing spending. It needs a separate feature/profile.

## 4. Discovery, freshness, rotation and revocation

Embedded offers need no resolver to extract. In the initial profile, an Ark
sender configures B's authenticated service endpoint and pins B's full key.
Do not infer a URL from a node alias or search unknown servers. Lightning-only
payers reach the offer's invoice-request route.

Before preparing a payment, B must check that the registered mapping is current
and active. A proposed payment-preparation status response binds a fresh 32-byte request nonce,
destination, mapping revision, response time and expiry under B's identity key.
Limit response validity to 60 seconds and reject responses outside the accepted
clock-skew window. Exact transport and skew configuration still need tests.

Persist the highest accepted revision. Revocation blocks new intents and invoice
issuance; it does not invalidate recovery obligations for existing intents.
No address resolver or offer lookup is required in either wire profile.
Offer rotation needs new recipient authorization. Server-key rotation requires
an explicit newly authenticated address in v0, not a transparent redirect.
Without an external transparency mechanism, a malicious server can equivocate;
nonce freshness does not solve equivocation.

## 5. Preparation and durable state

Use a caller-generated 32-byte random intent ID scoped to authenticated caller
and destination server. Bind a hash of the full request to that ID. An identical
retry returns the existing intent; a changed request fails with conflict.
Preparation must transactionally reserve inventory and persist the quote before
returning it. Add database uniqueness constraints, not only process-local locks.

Proposed states: `quoted`, `reserved`, `delivery_ready`, `payment_in_flight`,
`settled_delivery_pending`, `complete`, `cancellation_pending`, `cancelled`.
Maintain separate Lightning and Ark records. Do not turn unknown settlement into
`cancelled`. Persist an outbox for external actions and reconcile after restart.
The transport API, migrations and crash tests are still to be implemented.

## 6. Preimage and recovery

Target recipient-owned preimages. Bob chooses or derives the preimage; neither
server receives it before Bob has validated and durably stored an enforceable
conditional receive and its complete recovery material. The invoice payment
hash must match that receive. Alice's conditional Ark debit and the Lightning
payment must share the correct settlement conditions and timeout relationships.

This is a required property, not a completed construction. Before implementation
is approved, specify every script, signer, amount, ancestor transaction, timeout,
fee allocation and competing spend. Prove what Bob can recover with B offline
and what Alice recovers after failed Lightning settlement. Validate those spends
under default target-node policy. A signed delivery acknowledgment is insufficient.

## 7. Ordinary Lightning payers

The desired receiver-managed profile requires B and Bob to prepare the receive
before B releases a payable invoice or accepts settlement. The payer then uses
ordinary BOLT12. The prototype only extracts offers; this delivery coordination
does not exist yet. Until proven, do not advertise plain Lightning-to-Sideflash
payment compatibility. A sender-managed profile must expose that requirement.

## 8. Offline behavior and capability negotiation

Require Bob's wallet online for remote payment preparation in the first profile.
Fail explicitly before payment when Bob is unavailable. Do not issue custodial
credit as an offline fallback. Disconnection after preparation must preserve
recovery, not invalidate the signed conditional receive.

Negotiate exact wire and delivery profile identifiers. Separate `decode_offer`
from `prepare_receive` and `receiver_managed_delivery` capabilities. Never infer
payment support from decoder support. Unknown required capabilities fail closed.

## 9. Fees, inventory and cancellation

Quotes specify XBT sats for Ark values and millisats for Lightning, with checked
integer conversions. Bind recipient net receipt, recovery allocation, service
charge, maximum routing fee and maximum sender debit to the intent. Require new
approval if any bound increases. Never silently reduce Bob's quoted net amount.

Reserve Ark inventory and Lightning capacity separately. Service revenue must
cover expected nonrecoverable costs and bounded failed-attempt/rebalancing costs;
the service must refuse uneconomic quotes rather than subsidize them. Recovery
reserves remain a separately identified liability/cost, not automatically profit.

Allow cancellation before irreversible settlement only after both state machines
confirm it is safe. A quote's wall-clock expiry must not release an in-flight
HTLC reservation. Bound intent count, amount, expiry, retries and per-peer locked
inventory. Final numeric limits depend on tested recovery timing and inventory.

## 10. Review and two-server evidence

The Python checker is a second implementation of fixture encoding/signature
checks by the same authoring process. It is not independent human review, a full
Lightning parser or an audit. Seek an external reviewer for the frozen protocol
and conditional recovery construction before stable release.

Required evidence includes two independently configured servers, local and remote
payments, Lightning-only senders, concurrent double-spend attempts, duplicate
requests, crashes at every state transition, lost replies after settlement,
revocation races, expired HTLCs, and recipient recovery with B offline. These
tests must record exact binaries, policy settings and outcomes. No such complete
two-server Sideflash evidence exists yet.
