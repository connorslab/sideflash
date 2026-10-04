"""Canonical encoding, authentication, migration and synthetic QR regression tests."""
import copy
import json
from pathlib import Path
import unittest
import cbor2
import qrcode
import zxingcpp
from compact_v1 import decode, encode, verify_fixture, wrap
from verify_vectors import decode as decode_v0

ROOT = Path(__file__).parent
VECTORS = json.loads((ROOT / 'vectors/sideflash-v1.json').read_text())['vectors']

class CompactTests(unittest.TestCase):
    def rejected(self, raw):
        with self.assertRaises((AssertionError, ValueError, cbor2.CBORDecodeError)):
            decode(wrap(raw))

    def test_roundtrip_and_size(self):
        old = json.loads((ROOT / 'vectors/sideflash-v0.json').read_text())['vectors']
        for fixture, legacy, length in zip(VECTORS, old, (785, 841)):
            value, raw = decode(fixture['address'])
            verify_fixture(value, fixture)
            self.assertEqual(encode(value), fixture['address'])
            self.assertEqual(decode(fixture['address'].upper())[0], value)
            self.assertEqual(len(fixture['address']), length)
            self.assertEqual(len(legacy['address']) - length, 126)
            self.assertEqual(fixture['offer'], legacy['offer'])
            self.assertEqual(fixture['native_address'], legacy['native_address'])

    def test_all_signed_fields_and_signatures(self):
        for fixture in VECTORS:
            value, _ = decode(fixture['address'])
            for i in range(11):
                with self.subTest(network=fixture['network'], field=i):
                    changed = copy.deepcopy(value)
                    if type(changed[i]) is int:
                        changed[i] += 1
                    else:
                        b = bytearray(changed[i]); b[-1] ^= 1; changed[i] = bytes(b)
                    with self.assertRaises((AssertionError, ValueError)):
                        verify_fixture(changed, fixture)

    def test_invalid_encoding(self):
        value, raw = decode(VECTORS[0]['address'])
        for invalid in (raw + b'\x00', b'\x98\x0b' + raw[1:], b'\x9f' + raw[1:] + b'\xff',
                        b'\x8b\x18\x01' + raw[2:], cbor2.dumps(value[:-1]), cbor2.dumps(value + [0]),
                        cbor2.dumps(dict(enumerate(value)))):
            self.rejected(invalid)
        for i, invalid in [(0, 0), (1, 1), (2, 2), (2, True), (3, bytes(32)),
                           (4, bytes([1, 1, 0])), (5, b''), (6, -1), (6, 2**64),
                           (7, value[8]), (9, bytes(63))]:
            changed = list(value); changed[i] = invalid
            self.rejected(cbor2.dumps(changed))
        changed = list(value); changed[5] = bytes(634)
        self.rejected(cbor2.dumps(changed))

    def test_text_and_version_separation(self):
        text = VECTORS[0]['address']
        for invalid in (text[:2].upper() + text[2:], text[:-1], text + 'q',
                        text[:-1] + ('q' if text[-1] != 'q' else 'p'), 'sfl1' + 'q' * 1020):
            with self.assertRaises((AssertionError, ValueError)):
                decode(invalid)
        for v0 in json.loads((ROOT / 'vectors/sideflash-v0.json').read_text())['vectors']:
            with self.assertRaises(AssertionError):
                decode(v0['address'])
        for fixture, v0 in zip(VECTORS, json.loads((ROOT / 'vectors/sideflash-v0.json').read_text())['vectors']):
            value, _ = decode(fixture['address'])
            old, _ = decode_v0(v0['address'])
            for new_index, old_index in ((9, 10), (10, 11)):
                changed = list(value); changed[new_index] = old[old_index]
                with self.assertRaises(AssertionError):
                    verify_fixture(changed, fixture)

    def test_network_time_and_authority(self):
        fixture = VECTORS[0]
        value, _ = decode(fixture['address'])
        for changes in ({'network': 'regtest'}, {'verify_at': value[7] - 1},
                        {'verify_at': value[8]}, {'recipient_key': fixture['server_key']},
                        {'server_key': fixture['recipient_key']}):
            with self.assertRaises((AssertionError, ValueError)):
                verify_fixture(value, dict(fixture, **changes))

    def test_synthetic_qr(self):
        report = []
        for fixture in VECTORS:
            _, raw = decode(fixture['address'])
            row = {'network': fixture['network'], 'characters': len(fixture['address']), 'payload_bytes': len(raw), 'qr': []}
            for label, level in [('M', qrcode.constants.ERROR_CORRECT_M), ('Q', qrcode.constants.ERROR_CORRECT_Q)]:
                for upper in (False, True):
                    content = fixture['address'].upper() if upper else fixture['address']
                    qr = qrcode.QRCode(error_correction=level, box_size=4, border=4)
                    qr.add_data(content); qr.make(fit=True)
                    image = qr.make_image().convert('RGB')
                    result = zxingcpp.read_barcode(image)
                    self.assertIsNotNone(result)
                    self.assertEqual(result.text, content)
                    row['qr'].append({'ecc': label, 'uppercase': upper, 'version': qr.version, 'pixels': image.size[0], 'synthetic_decode': True})
            report.append(row)
        (ROOT / 'qr-report-v1.json').write_text(json.dumps({'fixtures_verified': len(VECTORS), 'results': report,
            'limitations': 'Synthetic decoding only; no camera test, independent review or payment test.'}, indent=2) + '\n')

if __name__ == '__main__':
    unittest.main()
