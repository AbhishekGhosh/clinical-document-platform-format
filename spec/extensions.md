# CDPF Extension Model — Draft 0.1

CDPF uses explicit extension containers rather than allowing private meanings to hide inside core
fields.

## Extension keys

An `extensions` object maps a collision-resistant key to any JSON value. Absolute URIs are
recommended:

```json
{
  "extensions": {
    "https://example.org/cdpf/extensions/local-triage-score": {
      "value": 3,
      "scale": "example-v1"
    }
  }
}
```

Reverse-DNS keys such as `org.example.local_triage_score` are acceptable for local/private use.

## Rules

- An extension MUST NOT change the meaning of a core field.
- A reader that does not understand an extension SHOULD preserve it during non-lossy round-trip.
- A document MUST remain clinically interpretable at its declared core conformance level without a
  private extension unless a separate profile explicitly requires that extension.
- New broadly useful concepts should be proposed for the core specification rather than squatting
  on another project's namespace.

## Custom block types

Applications may define custom block types using the same collision-resistant naming principle:

```json
{
  "block_type": "org.example.dermatology.lesion_map",
  "data": {"...": "..."}
}
```

Custom blocks are first-class document blocks. Their unknown status does not make the surrounding
CDPF document invalid.
