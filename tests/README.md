# Development fixture checks

Use Python 3.12 in an isolated virtual environment:

```sh
python -m pip install -r tests/requirements.txt
python tests/verify_vectors.py
```

The frozen vectors use public test keys and expired validity intervals. They are
not payable addresses. Rust generates the fixtures and consumes the same saved
bytes in its unit tests. Python independently checks the Bech32m checksum,
canonical CBOR, fixture identity and native address bytes, BOLT12 byte extraction,
BIP340 signatures, validity and modified signed fields. It also creates QR
images and decodes them with ZXing.

This checker trusts the expected recipient key in each fixture. It is not a
general native-policy validator, full BOLT12 verifier or production payment
client. Tests use assertions: do not run Python with optimization enabled.

`qr-report.json` records synthetic results. It is not evidence of camera
performance, hostile-image tolerance or independent human security review.
