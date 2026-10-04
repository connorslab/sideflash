"""Independent fixture verifier, not a production Sideflash payment parser."""
import hashlib
import json
from pathlib import Path
import cbor2
from coincurve import PublicKeyXOnly
import qrcode
import zxingcpp

ALPHABET = 'qpzry9x8gf2tvdw0s3jn54khce6mua7l'

def unpack(words):
    acc = bits = 0
    result = bytearray()
    for word in words:
        acc = (acc << 5) | word
        bits += 5
        if bits >= 8:
            bits -= 8
            result.append((acc >> bits) & 255)
    assert bits < 5 and ((acc << (8 - bits)) & 255) == 0, 'padding'
    return bytes(result)

def decode(text):
    assert len(text) <= 1023 and text.isascii()
    assert text == text.lower() or text == text.upper()
    text = text.lower()
    hrp, body = text.rsplit('1', 1)
    assert hrp == 'sfl' and len(body) >= 6
    words = [ALPHABET.index(c) for c in body]
    chk = 1
    for v in [ord(c) >> 5 for c in hrp] + [0] + [ord(c) & 31 for c in hrp] + words:
        top = chk >> 25
        chk = ((chk & 0x1ffffff) << 5) ^ v
        for i, g in enumerate([0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]):
            if (top >> i) & 1:
                chk ^= g
    assert chk == 0x2bc830a3, 'Bech32m checksum'
    raw = unpack(words[:-6])
    assert len(raw) <= 633
    value = cbor2.loads(raw)
    assert list(value) == list(range(12))
    assert cbor2.dumps(value, canonical=True) == raw, 'noncanonical CBOR'
    assert value[0] == 0 and value[1] == 0
    return value, raw

def verify(value, fixture):
    assert value[3] == hashlib.sha256(b'Sideflash/XBT/blake2b-unified-sighash/v0').digest()
    assert value[4].hex() == fixture['server_key']
    native_hrp, native_body = fixture['native_address'].rsplit('1', 1)
    assert ALPHABET.index(native_body[0]) == 1
    assert value[5] == bytes([int(native_hrp == 'tark'), 1]) + unpack([ALPHABET.index(c) for c in native_body[1:-6]])
    assert value[6] == unpack([ALPHABET.index(c) for c in fixture['offer'].split('1', 1)[1]])
    assert value[8] <= fixture['verify_at'] < value[9]
    # Fixture keys are independently supplied expected keys. A production client
    # must derive authority from the native receiving policy, not this JSON field.
    for end, key_name, domain in [(10, 'recipient_key', b'Sideflash/recipient/v0\0'),
                                   (11, 'server_key', b'Sideflash/server/v0\0')]:
        body = cbor2.dumps({k: value[k] for k in range(end)}, canonical=True)
        digest = hashlib.sha256(domain + body).digest()
        assert PublicKeyXOnly(bytes.fromhex(fixture[key_name])[1:]).verify(value[end], digest)

def main():
    fixtures = json.loads((Path(__file__).parent / 'vectors/sideflash-v0.json').read_text())['vectors']
    report = []
    for fixture in fixtures:
        text = fixture['address']
        value, raw = decode(text)
        verify(value, fixture)
        assert decode(text.upper())[0] == value
        for field in [7, 8, 9]:
            changed = dict(value)
            changed[field] += 1
            try:
                verify(changed, fixture)
            except (AssertionError, ValueError):
                pass
            else:
                raise AssertionError('accepted modified signed field')
        row = {'network': fixture['network'], 'characters': len(text), 'payload_bytes': len(raw), 'qr': []}
        for label, level in [('M', qrcode.constants.ERROR_CORRECT_M), ('Q', qrcode.constants.ERROR_CORRECT_Q)]:
            for upper in [False, True]:
                content = text.upper() if upper else text
                qr = qrcode.QRCode(error_correction=level, box_size=4, border=4)
                qr.add_data(content); qr.make(fit=True)
                image = qr.make_image().convert('RGB')
                result = zxingcpp.read_barcode(image)
                assert result is not None and result.text == content
                row['qr'].append({'ecc': label, 'uppercase': upper, 'version': qr.version,
                                  'pixels': image.size[0], 'synthetic_decode': True})
        report.append(row)
    print(json.dumps({'fixtures_verified': len(fixtures), 'results': report,
                      'limitations': 'Synthetic image decode only; no phone-camera test or independent audit.'}, indent=2))

if __name__ == '__main__':
    main()
