# Security requirements and acceptance tests

## Trust boundaries

Checksums detect transcription errors; they do not authenticate a recipient.
Recipient signatures authorize both routes. Server signatures acknowledge the
binding. Neither proves inventory, delivery, or an honest server. Obtain the
address through an authenticated recipient channel to prevent wholesale address
replacement. Pin a full server public key; DNS, TLS and short fingerprints are
not substitutes for that protocol identity.

Bound every parser input and allocation. Reject ambiguous CBOR, duplicate keys,
unsupported policies, invalid signatures, wrong networks and unknown required
features. Use distinct signature domains. Do not reuse payment signing domains.

Do not expose recipient or payment directories. Authenticate status requests.
Rate-limit registration and invoice requests. Address decoding is offline and
MUST NOT trigger resolver requests or redirects. Keep payment transport separate
from parsing. Never let an address become a request to an internal metadata service.

## Required tests

- Independent codec implementations agree on valid and invalid byte vectors.
- Truncation, oversize inputs, nonminimal lengths, duplicate fields and trailing
  bytes fail without panic or unbounded allocation.
- Substitution of the recipient, offer, server, chain, revision or validity fails.
- Both native and remote routes reach the exact authorized recipient.
- A Lightning-only client extracts and pays through the intended delivery profile.
- Simultaneous requests cannot spend a VTXO or consume a reservation twice.
- Restart at every persisted transition and replay every request and response.
- Handle lost responses after successful payment without a second debit.
- Exercise unavailable recipients, expired invoices, insufficient inventory,
  stuck HTLCs, route failures, stale mappings and revoked destinations.
- Demonstrate recovery with the receiving server unavailable under the negotiated
  profile. A successful cooperative payment is not sufficient evidence.
- Existing Ark wallets and ordinary Lightning payments remain functional.

Do not enable production interoperability until the delivery proof and these
tests are complete. The initial codec tests cover only a subset of this list.
