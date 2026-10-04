# Payment and recovery prerequisite tests

Date: 2026-10-04. Network: isolated bitcoin regtest. No mainnet payments or
production service changes. Tests used existing compiled Ark/Lightning binaries
and fresh test directories. These are **prerequisite tests, not a completed
Sideflash payment test**. No Sideflash server endpoint exists yet.

| Test | Result |
| --- | --- |
| Reusable BOLT12 receive: repeated/concurrent payments, restart, cancellation, offline recipient | Passed |
| BOLT12 receive with empty inventory | Passed; payment fails safely |
| Funded Lightning settlement and failed-send refund | Passed |
| Incoming HTLC emergency claim | Passed |
| Outgoing HTLC emergency refund | Passed |
| Empty inventory keeps preimage private | Passed |
| Receive after pool inventory ages | Passed |

The BOLT12 run executed 2 tests in 86.555 seconds. The funded-recovery run
executed 5 tests in 85.057 seconds. Both ran through the existing integration
test runner. An initial attempt selected zero tests; it is not counted as a pass.
The final runs used an isolated harness with the current test source copied in.

Test definitions:

- [BOLT12 receive scenarios](https://github.com/connorslab/paperclip-asp/blob/9b5ddc3/tests/bolt12-receive.rs)
- [Funded Lightning recovery scenarios](https://github.com/connorslab/paperclip-asp/blob/9b5ddc3/tests/funded-lightning.rs)

## Binary identities

SHA256 values of the reused test binaries:

| Binary | SHA256 |
| --- | --- |
| Ark server | `411a624f99cf3275ccd4ca6f22f25ec1786615b2e15dc35f2b36f47e885724c6` |
| Wallet | `4ba6acd6571d64be28c1456727396199e016ca65619c9bc8ca84916f44437500` |
| Watchman | `2ede62aa4c1cb6ac47089e6e67c029c34a3bc3586d91a0337e3dc070c07399f8` |
| Chain daemon | `d04cd8211e711af989a7a62d0b8b55a8cfe496694392518da0ccb848469b3799` |

## What remains unproven

These tests validate the existing receive/recovery primitives. They do not bind
a Sideflash payment intent to two independent Ark servers, prove the complete
cross-server timeout construction, test the new wallet methods with funds, or
establish offline Sideflash delivery. Registration, durable preparation and
end-to-end Sideflash payment/recovery remain release blockers.
