# Clinical Document Platform Format (CDPF)

**Draft 0.1 — open specification for portable, block-based clinical documents.**

CDPF defines a small, application-independent format for carrying a structured clinical document,
its ordered clinical blocks, provenance, optional presentation hints, and referenced attachments.
The proposed package extension is **`.cdp`**; the protocol/specification name is **CDPF** to avoid
confusion with the many unrelated uses of “CDP”.

> **Draft status:** CDPF 0.1 is experimental. It is not a replacement for HL7 FHIR, CDA, openEHR,
> DICOM, or any jurisdiction-specific electronic health record requirement. It is intended as a
> portable clinical-document container that can later be mapped to established interoperability
> standards.

## Why CDPF?

Many clinical applications can save a note only inside their own database or render it to PDF.
PDF preserves appearance but loses most machine-readable clinical structure. CDPF keeps the
clinical meaning and document order in JSON while allowing applications to attach PDFs, images,
ECGs, and other files without making a particular database, GUI toolkit, or print layout normative.

The format follows five principles:

1. **Clinical meaning before presentation.** A reader may ignore all presentation hints and still
   recover the clinical document.
2. **Sparse semantics are meaningful.** An omitted field means *not documented*. It is not the same
   as an explicitly documented normal or absent finding.
3. **Unknown content survives round-trip.** Readers should preserve blocks, fields, and extensions
   they do not understand when performing a non-lossy edit.
4. **No mandatory terminology system.** RxNorm, SNOMED CT, ICD, LOINC, and local codes may be carried
   when available, but human-readable content remains permitted.
5. **The package is application-independent.** SQLite schemas, GUI widgets, printer geometry, and AI
   models are outside the core format.

## Repository layout

```text
spec/                 Normative Draft 0.1 specification and block guidance
schema/               JSON Schema Draft 2020-12 schemas
examples/             Unpacked examples and reproducible .cdp packages
reference/python/     Small Python reference reader/validator
tools/                 Reproducible example-package builder
tests/                 Reference implementation tests
.github/workflows/     CI validation
```

## A `.cdp` package

A `.cdp` file is a ZIP-compatible container:

```text
example.cdp
├── manifest.json
├── document.json
└── attachments/
    └── lab-summary.txt
```

`manifest.json` identifies and hashes the clinical document and every attachment. `document.json`
contains the ordered clinical blocks. Draft 0.1 does not define encryption or cryptographic
signatures; those are intentionally deferred.

## Minimal document

```json
{
  "cdpf_version": "0.1",
  "document_id": "c2d6832f-013d-45da-9fd5-f7090e346809",
  "document_type": {
    "system": "urn:cdpf:document-type",
    "code": "clinical-note",
    "display": "Clinical note"
  },
  "status": "draft",
  "created_at": "2026-08-26T09:00:00+05:30",
  "subject": {"subject_id": "example-patient-001"},
  "authors": [{"name": "Example Clinician"}],
  "blocks": [
    {
      "block_id": "557c536a-3911-47ff-bfb4-b7dc676346b0",
      "block_type": "cdpf.core.chief_complaints",
      "title": "Chief Complaints",
      "data": {"items": [{"text": "Fever for two days"}]}
    }
  ]
}
```

## Sparse clinical semantics

CDPF deliberately distinguishes omission from an explicit negative finding:

```json
{"label": "Pallor", "status": "absent"}
```

means pallor was explicitly documented as absent. If the Pallor finding is omitted entirely, CDPF
means only that no Pallor finding was documented. A consumer **must not infer normality from
omission**.

## Validate the examples

```bash
python -m pip install -r reference/python/requirements.txt
python reference/python/validate_cdpf.py examples/minimal.cdp
python reference/python/validate_cdpf.py examples/outpatient-note.cdp
python -m unittest discover -s tests -v
```

## Versioning

This repository publishes **Draft 0.1**. Draft `0.x` releases may contain breaking changes while the
model is tested. A stable compatibility policy will be frozen before 1.0.

## Licensing

- Code, JSON Schemas, tests, tooling, and reference implementations: **Apache License 2.0**.
- Normative specification and prose documentation: **CC BY 4.0**.

See `LICENSE`, `LICENSE-DOCS.md`, and `NOTICE`.

## Contributing

Issues and pull requests are welcome. See `CONTRIBUTING.md`. In particular, proposed clinical fields
should explain why they belong in the portable document format rather than in an application UI,
workflow engine, or jurisdiction-specific extension.
