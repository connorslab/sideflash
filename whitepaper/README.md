# Sideflash whitepaper v0.2

[Read the PDF](sideflash-whitepaper.pdf).

Updated 2026-10-04. Whitepaper revision v0.2 describes address wire version 1;
these are different version numbers. The `1` in `sfl1` remains only a separator.

This revision covers compact CBOR arrays, built-in network-profile assignments,
both signature domains, measured 785/841-character fixtures, offline extraction,
v0 migration and the remaining payment-delivery work. It removes the earlier
resolver alternative and obsolete payload-size proposal. Seven pages were
rendered and visually checked before publication.

Rebuild with Python and ReportLab:

```sh
python -m pip install reportlab
python whitepaper/build_whitepaper.py
```

The builder uses standard PDF fonts and no machine-specific paths. Legacy v0.1
remains in Git history. The wire specification and frozen vectors define exact
encoding bytes; this paper explains their purpose and integration requirements.
