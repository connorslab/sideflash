"""Compact v1 fixture codec. Not a production native-policy/BOLT12 validator."""
import hashlib
import cbor2
from coincurve import PublicKey, PublicKeyXOnly
from verify_vectors import ALPHABET, unpack

GENERATORS = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
FORK = hashlib.sha256(b'Sideflash/XBT/blake2b-unified-sighash/v0').digest()
PROFILES = {
    0: ('mainnet', bytes.fromhex('6fe28c0ab6f1b372c1a6a246ae63f74f931e8365e15a089c68d6190000000000'), FORK),
    1: ('regtest', bytes.fromhex('06226e46111a0b59caaf126043eb5bbf28c34f3a5e332a1fc7b2b73cf188910f'), FORK),
}

def polymod(values):
    chk = 1
    for value in values:
        top = chk >> 25
        chk = ((chk & 0x1ffffff) << 5) ^ value
        for i, generator in enumerate(GENERATORS):
            if (top >> i) & 1:
                chk ^= generator
    return chk

def expand(hrp):
    return [ord(c) >> 5 for c in hrp] + [0] + [ord(c) & 31 for c in hrp]

def pack(raw):
    acc = bits = 0
    words = []
    for byte in raw:
        acc = (acc << 8) | byte
        bits += 8
        while bits >= 5:
            bits -= 5
            words.append((acc >> bits) & 31)
    if bits:
        words.append((acc << (5 - bits)) & 31)
    return words

def wrap(raw):
    words = pack(raw)
    check = polymod(expand('sfl') + words + [0] * 6) ^ 0x2bc830a3
    return 'sfl1' + ''.join(ALPHABET[w] for w in words + [(check >> (5 * i)) & 31 for i in range(5, -1, -1)])

def validate(value):
    assert type(value) is list and len(value) == 11, 'array length'
    for i in [0, 1, 2, 6, 7, 8]:
        assert type(value[i]) is int and 0 <= value[i] < 2**64, 'uint64'
    assert value[0] == 1 and value[1] == 0, 'version/features'
    assert value[2] in PROFILES, 'unknown network profile'
    for i in [3, 4, 5, 9, 10]:
        assert type(value[i]) is bytes, 'byte string'
    assert len(value[3]) == 33 and value[3][0] in (2, 3), 'service key'
    PublicKey(value[3])
    assert 2 < len(value[4]) <= 633 and value[4][:2] == bytes([value[2], 1]), 'native network/version'
    assert 0 < len(value[5]) <= 633, 'offer bounds'
    assert value[7] < value[8], 'validity interval'
    assert len(value[9]) == len(value[10]) == 64, 'signature length'

def encode(value):
    validate(value)
    raw = cbor2.dumps(value, canonical=True)
    assert len(raw) <= 633, 'payload too large'
    text = wrap(raw)
    assert len(text) <= 1023, 'text too large'
    return text

def decode(text):
    assert len(text) <= 1023 and text.isascii(), 'text bounds'
    assert text == text.lower() or text == text.upper(), 'mixed case'
    hrp, body = text.lower().rsplit('1', 1)
    assert hrp == 'sfl' and len(body) >= 6, 'prefix'
    words = [ALPHABET.index(c) for c in body]
    assert polymod(expand(hrp) + words) == 0x2bc830a3, 'checksum'
    raw = unpack(words[:-6])
    assert len(raw) <= 633, 'payload bounds'
    value = cbor2.loads(raw)
    validate(value)
    assert cbor2.dumps(value, canonical=True) == raw, 'noncanonical/trailing data'
    return value, raw

def digest(value, server=False):
    end = 10 if server else 9
    domain = b'Sideflash/server/v1\0' if server else b'Sideflash/recipient/v1\0'
    return hashlib.sha256(domain + cbor2.dumps(value[:end], canonical=True)).digest()

def verify_fixture(value, fixture):
    validate(value)
    assert value[2] == {'mainnet': 0, 'regtest': 1}[fixture['network']]
    assert value[3].hex() == fixture['server_key']
    hrp, body = fixture['native_address'].rsplit('1', 1)
    assert ALPHABET.index(body[0]) == 1
    assert value[4] == bytes([int(hrp == 'tark'), 1]) + unpack([ALPHABET.index(c) for c in body[1:-6]])
    assert value[5] == unpack([ALPHABET.index(c) for c in fixture['offer'].split('1', 1)[1]])
    assert value[7] <= fixture['verify_at'] < value[8], 'validity'
    assert PublicKeyXOnly(bytes.fromhex(fixture['recipient_key'])[1:]).verify(value[9], digest(value))
    assert PublicKeyXOnly(value[3][1:]).verify(value[10], digest(value, server=True))
