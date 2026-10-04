"""Deterministically migrate public, expired v0 test fixtures; never real keys."""
import json
from pathlib import Path
from coincurve import PrivateKey
from compact_v1 import digest, encode, decode, verify_fixture, PROFILES
from verify_vectors import decode as decode_v0, verify as verify_v0

root = Path(__file__).parent
source = json.loads((root / 'vectors/sideflash-v0.json').read_text())
vectors = []
keys = {PrivateKey(bytes([i]) * 32).public_key.format().hex(): PrivateKey(bytes([i]) * 32) for i in (1, 2, 3)}
for fixture in source['vectors']:
    old, _ = decode_v0(fixture['address'])
    verify_v0(old, fixture)
    value = [1, 0, {'mainnet': 0, 'regtest': 1}[fixture['network']], old[4], old[5], old[6], old[7], old[8], old[9]]
    assert PROFILES[value[2]] == (fixture['network'], old[2], old[3])
    value.append(keys[fixture['recipient_key']].sign_schnorr(digest(value), aux_randomness=bytes(32)))
    value.append(keys[fixture['server_key']].sign_schnorr(digest(value, server=True), aux_randomness=bytes(32)))
    result = dict(fixture, address=encode(value))
    decoded, _ = decode(result['address'])
    verify_fixture(decoded, result)
    vectors.append(result)
(root / 'vectors/sideflash-v1.json').write_text(json.dumps({'profile': 'sideflash-v1-xbt', 'vectors': vectors}, indent=2) + '\n')
