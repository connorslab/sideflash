"""Build the Sideflash v0.2 whitepaper with ReportLab; no external font files."""
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

ROOT = Path(__file__).parent
NAVY = colors.HexColor('#112137')
ORANGE = colors.HexColor('#f3652e')
MUTED = colors.HexColor('#56677b')
styles = getSampleStyleSheet()
for name, font, size, leading in [('Text', 'Helvetica', 10.3, 14.6),
                                 ('Small', 'Helvetica', 8.6, 11.6),
                                 ('TitleText', 'Helvetica-Bold', 38, 43),
                                 ('Section', 'Helvetica-Bold', 23, 28),
                                 ('Subsection', 'Helvetica-Bold', 12, 17),
                                 ('CodeText', 'Courier', 8.2, 12)]:
    styles.add(ParagraphStyle(name=name, fontName=font, fontSize=size, leading=leading,
                             textColor=NAVY, spaceAfter=10,
                             keepWithNext=name in ('Section', 'Subsection')))
story = []


def p(text, style='Text'):
    story.append(Paragraph(text, styles[style]))


def h(text):
    p(text, 'Section')


def sub(text):
    p(text, 'Subsection')


def page():
    story.append(PageBreak())


def table(rows, widths):
    cells = [[Paragraph(str(c), styles['Small']) for c in row] for row in rows]
    t = Table(cells, colWidths=widths, hAlign='LEFT')
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e9eef4')),
        ('LINEBELOW', (0, 0), (-1, 0), 1, ORANGE),
        ('LINEBELOW', (0, 1), (-1, -1), .35, colors.HexColor('#d8dfe8')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))


p('PROTOCOL WHITEPAPER', 'Small')
story.append(Spacer(1, 18))
p('Sideflash', 'TitleText')
p('One embedded address for Ark and Lightning', 'Section')
p('Whitepaper v0.2 | 4 October 2026 | Experimental, not audited', 'Small')
story.append(Spacer(1, 14))
sub('Abstract')
p('Sideflash combines a native Ark destination and a reusable BOLT12 offer in one authenticated address. A compatible wallet selects the native Ark route when the sender and recipient use the same Ark service provider (ASP). Across ASPs, the intended route uses Lightning with separate safeguards for delivery into the recipient\'s Ark balance. A Lightning-only client can extract the embedded offer without an Ark wallet or an address lookup service.')
p('The address binds both destinations to the recipient\'s receiving key and the destination ASP\'s full public key. It includes network context, revision, validity and two signatures. These authenticate the binding; they do not prove liquidity, fresh registration or successful Ark delivery.')
sub('What changes in v0.2')
p('This revision specifies the compact, fully embedded <b>wire profile v1</b>. A fixed CBOR array replaces the original map. A built-in network-profile code replaces two explicit 32-byte hashes without removing their verification semantics. The complete offer, native destination and both signatures remain embedded. There is no resolver or directory lookup.')
table([['Frozen example', 'Legacy v0', 'Compact v1'],
       ['Mainnet', '911 characters', '<b>785 characters</b>'],
       ['Regtest', '967 characters', '<b>841 characters</b>']], [220, 136, 136])
p('Both examples save 126 characters. The mainnet example is approximately 13.8% shorter. Length depends on offer size and integer widths; these are measurements, not a fixed address length.', 'Small')
p('<b>Version distinction:</b> v0.2 is the whitepaper revision. Version 1 is the encoded address format. The 1 in sfl1 is only the Bech32 separator.', 'Small')

page()
h('1  Compact address anatomy')
p('An address has four outer parts. Its fields are encoded as one binary payload; field boundaries are not independent readable words in the text.')
table([['Prefix', 'Separator', 'Encoded payload', 'Checksum'],
       ['sfl', '1', '5-bit Bech32 symbols', '6 Bech32m symbols']], [70, 75, 237, 110])
p('For the 785-character mainnet fixture, positions 1-3 are the prefix, position 4 is the separator, positions 5-779 carry the payload, and positions 780-785 carry the checksum. These ranges apply only to that fixture.', 'Small')
sub('Canonical CBOR array')
table([['Index', 'Type', 'Content'],
       ['0', 'uint64', 'Wire version: 1'],
       ['1', 'uint64', 'Required envelope features: 0'],
       ['2', 'uint64', 'Built-in network profile: 0 or 1'],
       ['3', '33-byte string', 'Full compressed ASP public key'],
       ['4', 'byte string', 'Binary native Ark destination'],
       ['5', 'byte string', 'Complete, exact BOLT12 offer TLV bytes'],
       ['6', 'uint64', 'Binding revision'],
       ['7', 'uint64', 'Inclusive valid-from time, Unix seconds'],
       ['8', 'uint64', 'Exclusive expiry time, Unix seconds'],
       ['9', '64-byte string', 'Recipient BIP340 authorization'],
       ['10', '64-byte string', 'ASP BIP340 acknowledgment']], [43, 123, 326])
p('The array contains exactly 11 elements. Use definite lengths and shortest integer/length encodings. Reject tags, booleans in integer fields, negative or overflowing integers, extra elements and trailing bytes. Unknown versions, network profiles, required features and recipient policies fail explicitly.')
p('The outer limits remain <b>633 decoded bytes and 1023 ASCII characters</b>. Reject oversized input before nested parsing. Accept uniformly lowercase or uppercase text; reject mixed case and invalid padding. Uppercase QR encoding can reduce QR size. Never truncate an offer or replace it with a lookup reference.')

page()
h('2  Network identity and signatures')
sub('Built-in network profiles')
p('Version 1 defines local development assignments: code <b>0</b> identifies bitcoin (XBT) mainnet; code <b>1</b> identifies isolated bitcoin (XBT) regtest. Implementations ship the same immutable table. Each code expands locally to a genesis hash and fork discriminator. No network request is necessary. These are not globally assigned chain identifiers.')
p('Genesis hashes below use Lightning chain-hash byte order:', 'Small')
p('0: 6fe28c0ab6f1b372c1a6a246ae63f74f931e8365e15a089c68d6190000000000', 'CodeText')
p('1: 06226e46111a0b59caaf126043eb5bbf28c34f3a5e332a1fc7b2b73cf188910f', 'CodeText')
p('Both use the existing discriminator: SHA256 of the ASCII string below, with no terminating NUL. Its spelling is a frozen protocol identifier.', 'Small')
p('Sideflash/XBT/blake2b-unified-sighash/v0', 'CodeText')
p('A reader compares the expanded profile with its configured chain, the native network and the offer chain. The offer must require identity bit 512; unsupported mandatory offer features are rejected. Signet and other networks are not assigned. A shared genesis or address prefix is insufficient. Regtest does not identify a particular laboratory; full ASP identity pinning is still required.')
sub('Two authorizations, retained')
p('Let A(n) be canonical CBOR encoding of the first n array elements, including an array header of length n. The signature digests are:')
p('recipient_digest = SHA256(<br/>  "Sideflash/recipient/v1" || 0x00 || A(9))<br/>service_digest = SHA256(<br/>  "Sideflash/server/v1" || 0x00 || A(10))', 'CodeText')
p('Element 9 signs the recipient digest under the native pubkey-policy receiving authority. Element 10 signs the service digest under the x-only form of element 3. The ASP acknowledgment includes the recipient signature. Neither party needs the other party\'s secret key.')
p('Authenticate the recipient channel and pin the full ASP identity from trusted context. A short native fingerprint is not an identity anchor. Valid signatures do not prevent wholesale substitution with an attacker\'s separately valid address. The binding signatures do not replace BOLT12 invoice signatures or transaction signing rules.')

page()
h('3  Savings, parsing and migration')
table([['Fixture', 'v0 payload', 'v1 payload', 'Text saving'],
       ['Mainnet', '563 bytes', '484 bytes', '126 characters'],
       ['Regtest', '598 bytes', '519 bytes', '126 characters']], [132, 112, 112, 136])
p('For these fixtures, two 32-byte CBOR byte strings become one small profile integer: 67 bytes saved. Removing the original map\'s 12 integer keys saves 12 more bytes. Total: <b>79 payload bytes</b>. No signature is removed. No offer is truncated. The Ark destination and offer bytes are identical to those in the legacy fixtures.')
sub('Verify before use')
p('First check text bounds, prefix, checksum and padding. Then parse the exact versioned structure, reject noncanonical encodings, and enforce nested bounds. Validate native policy lengths before allocation. The initial policy is a pubkey destination; delegated or scripted authorities are not supported.')
p('Derive the recipient verification key from the native policy, check its ASP fingerprint against the full pinned key, verify network and validity, then verify both signatures. Validate the complete offer under BOLT12, including chain, expiry and mandatory features. Encode its exact TLV bytes as lno1 text without adding the envelope checksum. This extraction is local and offline.')
sub('Preserve legacy readers')
p('Wire v0 remains a 12-entry CBOR map with explicit genesis and fork hashes and v0 signing domains. Wire v1 is the 11-element array in this paper. Readers dispatch on container shape and explicit version. They must not guess, silently downgrade or interpret one container as the other.')
p('Re-encoding a decoded v0 address retains its original version and signatures. Issuing a compact replacement requires <b>fresh recipient authorization and ASP acknowledgment</b>. Copying v0 signatures into a v1 envelope fails. Existing native Ark addresses and BOLT12 offers retain their original formats.')
sub('QR practicality')
p('The mainnet fixture at QR error correction M fits version 18 when uppercase, versus version 20 for the legacy fixture. At four pixels per module plus a four-module border, these render at 388 and 420 pixels respectively. Synthetic decoding passes in both letter cases at M and Q correction levels. Real phone-camera tests remain necessary; size measurements do not prove scanning reliability.')

page()
h('4  Registration and route selection')
p('The recipient wallet obtains an authenticated ASP identity and an Ark pubkey destination. The ASP associates a reusable BOLT12 offer with that destination. The wallet verifies the exact offer bytes and signs the v1 binding. The ASP checks recipient authority, persists the association and countersigns it.')
p('The wallet must persist its registration request and compare the returned binding with that exact request, including revision and validity. A response that merely belongs to the same wallet is not enough. An access token can control registration access; it cannot replace recipient authorization.')
table([['Sender', 'Intended route'],
       ['Ark wallet using the same ASP', 'Compare full ASP keys; use the native Ark destination.'],
       ['Ark wallet using another ASP', 'Extract the offer; use Lightning with safe delivery preparation.'],
       ['Lightning-only wallet', 'Extract the offer; use normal invoice negotiation only when receiver-managed delivery is supported.']], [200, 292])
sub('No resolver requirement')
p('The address contains both destinations. It does not carry a URL to fetch them or depend on an online recipient directory. A lightweight extractor can recover the BOLT12 offer offline. Normal invoice requests use the offer\'s embedded Lightning reachability information.')
p('A full ASP identity key is not an HTTP hostname. If an application delivery profile uses a separate ASP API, its endpoint must be configured or authenticated independently. That transport question is distinct from address extraction and is not solved by inventing a resolver dependency.')
sub('Freshness and rotation')
p('An embedded offer can expire, be revoked or lose liquidity. Offline verification cannot prove current availability. The receiver must check the active persisted mapping before issuing an invoice or preparing delivery. Payment-status responses, where used, must bind a fresh request nonce, revision, destination and expiry.')
p('Changing the offer requires a newly authorized binding. ASP key rotation requires a newly authenticated identity or an explicitly specified rotation mechanism; a replacement key cannot authorize itself. Remembering revisions helps detect rollback but does not prevent a malicious ASP from equivocating. Do not silently substitute another offer.')

page()
h('5  Payment preparation and recovery')
p('The address establishes which routes the recipient authorized. It does not itself make Lightning settlement atomic with an Ark receive. Safe delivery is a separate implementation requirement, not a property of the checksum or signatures.')
sub('Bind one payment intent')
p('Use a unique persisted intent identifier. Bind the destination, revision, exact offer, invoice, payment hash, invoice amount in millisats, recipient net amount in sats, fees, inventory reservation and expiry. Retrying the same intent must return the same result; changing its parameters must fail rather than start another payment.')
p('Show the sender the route, recipient net receipt, maximum total debit and routing fee limit before approval. If fees or available inventory change, request a new approval. Never silently lower the recipient\'s amount. Invoice and offer validation continue to follow BOLT12.')
sub('Prepare delivery before irreversible settlement')
p('The receiving ASP reserves Ark inventory and prepares an enforceable conditional receive for the recipient. The recipient validates and durably stores the recovery material before the settlement condition can be released. The delivery design must specify who controls the preimage, which payment hash is used, timeouts, funding ancestry and claim/refund paths.')
p('The target is recipient-controlled settlement release after safe preparation. This remains a requirement to prove, not a completed construction. A signed acknowledgment or a Lightning preimage alone is not proof that the recipient can recover Ark value if the ASP disappears.')
sub('Crash and failure behavior')
p('Persist preparation, reservations and payment state before external actions. Reconcile uncertain outcomes after restart. A timeout is not a definitive failure: do not issue and pay a replacement invoice while the original may have settled. Concurrent requests must not spend the same source VTXO or reserve the same inventory twice.')
p('Cancellation must wait until it is safe to release reservations. Quote expiry must not release inventory backing an in-flight HTLC. Offline recipients need a separately verified delivery design; an ordinary custodial credit is not an acceptable silent fallback.')
sub('Liquidity is still required')
p('Lightning transfers channel balance between services. It does not turn channel backing into Ark backing. The receiving ASP still needs Ark inventory and recovery capacity. Quotes must cover nonrecoverable costs and bounded failure/rebalancing costs without assuming an ASP subsidy. Recovery allocations, service fees and routing fees must be shown separately.')

page()
h('6  Evidence and release boundary')
p('As of 4 October 2026, compact v1 exists in the protocol fixture codec and experimental Rust ASP/wallet branches. New authorizations use v1; readers retain v0 verification and encoding. An opt-in experimental CLN plugin also verifies bindings and extracts offers. These are address capabilities, not a deployed Sideflash payment system.')
table([['Evidence', 'What it establishes'],
       ['Four frozen v0/v1 fixtures', 'Mainnet/regtest canonical bytes, signatures and exact native/offer extraction agree in the tested codecs.'],
       ['Rust branch checks', 'Six focused codec tests per branch, workspace compilation, and the feature-enabled wallet build pass.'],
       ['Python and QR checks', 'Signed-field mutations, malformed input, version separation and synthetic QR round-trips pass.'],
       ['Experimental CLN plugin', 'Seven local tests include a manifest handshake, payload mutations and mocked local RPC dispatch. No payment is attempted.']], [165, 327])
p('The fixtures use known test keys and expired validity intervals. Never fund them. Agreement between these implementations is not independent human review or a security audit. CLN mocked dispatch does not replace live daemon testing.')
sub('Before payment release')
p('Complete persistent registration, wallet UI and capability negotiation. Demonstrate same-ASP payments and two separately configured ASPs delivering over Lightning. Prove recovery after disconnection, duplicate requests, double-spend attempts, crashes, lost replies, expired HTLCs and inadequate liquidity. Test ordinary Lightning-only payers with receiver-managed preparation. Test physical QR scanning and keep compatibility with ordinary Ark and Lightning clients.')
sub('References and normative details')
refs = [
    ('Compact v1 specification and network assignments', 'https://github.com/connorslab/sideflash/blob/main/docs/address-v1.md'),
    ('Frozen fixtures and codec tests', 'https://github.com/connorslab/sideflash/tree/main/tests'),
    ('Draft Sideflash BOLT proposal - number unassigned', 'https://github.com/lightning-blake2b/bolts/pull/7'),
    ('BOLT12 offer and invoice protocol', 'https://github.com/lightning-blake2b/bolts/blob/master/12-offer-encoding.md'),
    ('BIP340 signatures', 'https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki'),
    ('BIP350 Bech32m', 'https://github.com/bitcoin/bips/blob/master/bip-0350.mediawiki'),
    ('RFC8949 CBOR', 'https://www.rfc-editor.org/rfc/rfc8949.html'),
]
for title, url in refs:
    p(f'<link href="{url}" color="#b84219">{title}</link>', 'Small')
p('This revision supersedes v0.1\'s larger proposed bounds, resolver options and unfrozen map design. The experimental wire specification and frozen vectors define exact bytes. No BOLT number, new Lightning feature bit or consensus change is assigned by this paper.', 'Small')


def footer(canvas, doc):
    canvas.setFillColor(ORANGE)
    canvas.rect(54, 751, 34, 3, fill=1, stroke=0)
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(54, 30, 'Sideflash | Whitepaper v0.2 | Compact wire profile v1')
    canvas.drawRightString(558, 30, str(doc.page))


SimpleDocTemplate(str(ROOT / 'sideflash-whitepaper.pdf'), pagesize=(612, 792),
                  leftMargin=54, rightMargin=54, topMargin=56, bottomMargin=52,
                  title='Sideflash - Whitepaper v0.2', author='',
                  subject='Fully embedded compact Ark and Lightning addresses').build(
                      story, onFirstPage=footer, onLaterPages=footer)
