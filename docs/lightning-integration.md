# Lightning integration recommendations

## Minimal sender support

A Lightning-only wallet does not need an Ark balance or an Ark server to pay a
Sideflash destination. It needs an address decoder and binding verifier:

1. Decode the bounded `sfl1` Bech32m envelope and canonical CBOR.
2. Check the chain profile, validity, recipient authorization and server signature.
3. Extract the exact BOLT12 offer TLV bytes. Use the Lightning library to encode
   these as an `lno1` offer when a text API requires one.
4. Request and validate an invoice through normal BOLT12 mechanisms.
5. Approve the amount and fees, then pay using the existing Lightning engine.

The Rust prototype API for both v0 and v1 is `SideflashAddress::decode` followed by `verified_offer`.
New authorizations use compact v1. The same frozen vectors pass in Python and Rust.
It requires caller-supplied chain context and an authenticated destination server
key. It verifies the binding, not current revocation or Ark delivery. A future
portable decoder need not embed a complete Ark wallet; it does need enough
native policy parsing to verify recipient control. The first profile supports
pubkey policies only.

No new Lightning wire message or channel policy is required merely to extract
an offer. Existing nodes will not recognize `sfl1` automatically: this can be a
wallet-side adapter before the node's existing offer-fetch/payment API.

## Receiving-side requirements

The Ark receiving service must finish safe delivery preparation before accepting
Lightning settlement. A minimal Lightning sender cannot be expected to manage
Bob's VTXOs or validate Ark recovery graphs. The receiver-managed delivery profile
must therefore coordinate with Bob or an authorized agent before it settles.

Do not claim this is available today solely because offer extraction works. If
the selected profile needs sender-side preparation, a plain BOLT12 payer is not
yet sufficient. Negotiate an explicit compatible profile or reject the payment.
Unattended/offline receiving needs a separately verified recovery design.

## Invoice checks

Use the implementation's BOLT12 invoice validation, including offer/request
association, chain, signatures, features, amount and expiry. Keep network-specific
feature checks in the payment engine. A signed fork discriminator in Sideflash
does not change invoice consensus or prevent cross-chain misuse on its own.

Enforce invoice and route fee limits. Treat a payment timeout as unresolved until
the node reports a definitive outcome. Do not fetch and pay a new invoice as an
automatic retry of a payment that might have succeeded.

## Privacy

Extraction can be offline. Do not upload addresses to a third-party decoding
service. Reusable addresses remain linkable. Blinded Lightning paths do not
hide the recipient mapping from the Ark server that maintains it. Both address
profiles are fully embedded and contain no resolver URL. Tor transport for
payment communication is separate from local address decoding.
