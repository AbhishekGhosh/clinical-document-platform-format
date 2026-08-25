# CDPF Draft 0.1 — Release Notes

This is the first public draft of the **Clinical Document Platform Format (CDPF)**, an open,
application-independent format for portable, block-based clinical documents.

Draft 0.1 introduces:

- ZIP-compatible `.cdp` packages with `manifest.json` and `document.json`;
- ordered UUID-addressed clinical blocks;
- explicit sparse semantics where omission is not treated as normal/absent;
- common coding, identifier, quantity, finding, and attachment-reference primitives;
- core guidance for narrative, examination, medication, investigation, diagnosis, and advice blocks;
- optional presentation hints separated from clinical meaning;
- SHA-256 and byte-size integrity checks for the clinical document and attachments;
- an extension namespace model designed for round-trip preservation;
- JSON Schema Draft 2020-12 schemas;
- a Python reference validator with ZIP safety checks;
- fictional example packages and reproducible example generation;
- Apache-2.0 licensing for code/schemas and CC BY 4.0 for specification/prose.

## Important draft limitations

CDPF 0.1 is experimental and may change incompatibly before 1.0. It is not a replacement for FHIR,
CDA, openEHR, DICOM, or national EHR requirements. Draft 0.1 does not define encryption,
cryptographic signatures, clinical decision support, AI behavior, database persistence, or
pixel-perfect print layout.

Feedback from implementers is especially welcome on sparse finding semantics, block portability,
attachment handling, medication representation, and unknown-block round-trip behavior.
