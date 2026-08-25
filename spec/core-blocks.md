# CDPF Draft 0.1 Core Block Guidance

This document defines recommended payload shapes for core blocks. The generic block envelope remains
valid even when a consumer does not implement a profile-specific schema.

## Narrative-style blocks

`cdpf.core.chief_complaints`, `cdpf.core.history`, `cdpf.core.diagnosis`,
`cdpf.core.investigations`, and `cdpf.core.advice` MAY use human-readable text and structured items.

Example chief complaints:

```json
{
  "block_type": "cdpf.core.chief_complaints",
  "data": {
    "items": [
      {"text": "Fever", "onset": "2 days"},
      {"text": "Dry cough", "onset": "1 day"}
    ]
  }
}
```

A producer should prefer structured values when it genuinely knows their semantics, but must not
invent structure by guessing from free text.

## Examination blocks

Examination blocks SHOULD use a `findings` array. Each finding may contain a label, optional code,
explicit status, value, unit, note, and extensions.

```json
{
  "block_type": "cdpf.core.examination.general",
  "data": {
    "findings": [
      {"label": "Pallor", "status": "absent"},
      {"label": "Pulse", "status": "present", "value": 78, "unit": "/min"}
    ]
  }
}
```

If Pallor had not been documented, the Pallor finding would be omitted entirely. Do not emit
`"status": "normal"` merely to fill a form default.

## Medications

`cdpf.core.medications` uses an ordered `items` array. The medication identity and prescription
instructions are separate.

```json
{
  "block_type": "cdpf.core.medications",
  "data": {
    "items": [
      {
        "medication": {
          "display": "Telmisartan 40 mg tablet",
          "generic_name": "Telmisartan",
          "strength": "40 mg",
          "dose_form": "Tablet",
          "codes": [
            {
              "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
              "code": "73494",
              "display": "telmisartan"
            }
          ]
        },
        "dose": "1 tablet",
        "frequency": "once daily",
        "timing": "after food",
        "duration": "30 days"
      }
    ]
  }
}
```

Coding is optional. An uncoded Indian brand or locally compounded medicine is still representable.

## Attachment-backed clinical objects

Later profiles may standardize ECG, image, drawing, report, certificate, and referral payloads.
Draft 0.1 implementations may already carry them as custom/extension blocks using an
`attachment_id` reference whose file metadata and SHA-256 live in `manifest.json`.
