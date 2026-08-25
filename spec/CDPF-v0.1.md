# Clinical Document Platform Format (CDPF) — Draft 0.1

**Status:** Public draft  
**Format version:** `0.1`  
**Proposed package extension:** `.cdp`  
**Normative data encoding:** UTF-8 JSON inside a ZIP-compatible container

## 1. Scope

CDPF is a portable clinical-document format. It standardizes a document envelope, ordered clinical
blocks, common data primitives, extensions, and attachment integrity. It does not standardize
clinical workflow, billing, scheduling, user interface layout, AI behavior, authorization,
transport, or a database schema.

CDPF is complementary to established healthcare interoperability standards. Draft 0.1 does not
claim semantic equivalence with FHIR, CDA, openEHR, DICOM, or any national EHR specification.

## 2. Conformance language

Uppercase requirement words such as MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are normative.

A **CDPF package reader** reads `.cdp` containers. A **CDPF document reader** reads `document.json`
independently of the package. An implementation may conform to either or both roles.

## 3. Package model

A Draft 0.1 `.cdp` package MUST be a ZIP-compatible archive containing at its root:

- `manifest.json`
- the clinical document identified by `manifest.document.path` (normally `document.json`)

Attachment payloads MAY appear anywhere under relative package paths, although
`attachments/<filename>` is RECOMMENDED.

Package member names MUST use `/` as the separator and SHOULD be encoded as UTF-8 names. A
conforming reader MUST reject absolute paths, parent traversal (`..`), backslashes, and symbolic
links. ZIP directory entries MAY be present and do not count as payload files. A reader SHOULD
enforce limits on the number of members and total uncompressed size.

Draft 0.1 defines no registered media type. Implementers should treat `.cdp` as a ZIP container when
transport metadata is required.

### 3.1 Manifest

`manifest.json` MUST conform to `schema/manifest.schema.json` and contains:

- `cdpf_version`
- `package_id`
- `created_at`
- `document`: path, SHA-256, byte size, and media type
- optional `attachments`: IDs, paths, hashes, sizes, media types, and human metadata
- optional `generator`
- optional `extensions`

Every attachment referenced by `document.json` MUST be listed in the manifest. Draft 0.1 packages
MUST NOT contain unlisted payload files other than `manifest.json` and the declared document.

A package reader MUST verify document and attachment hash/size before exposing the package as valid.
Hashes are calculated over the exact uncompressed member bytes; Draft 0.1 defines no JSON
canonicalization step for integrity hashes.

## 4. Clinical document model

`document.json` MUST conform to `schema/document.schema.json`.

Required fields are:

- `cdpf_version`
- `document_id` — UUID
- `document_type` — coded document type
- `status`
- `created_at`
- `subject`
- `authors`
- `blocks`

`blocks` is an ordered JSON array. Array order is the normative clinical/document order.

### 4.1 Block envelope

Every block MUST contain:

- `block_id` — UUID stable for the lifetime of the logical block
- `block_type` — namespaced string
- `data` — JSON value carrying the block payload

A block MAY contain `title` and `extensions`.

The core namespace is `cdpf.core.*`. Third-party block types MUST use a collision-resistant namespace
such as a reverse-DNS name (`org.example.my_block`) or an absolute URI-derived convention.

A reader that does not understand a block type SHOULD preserve its complete JSON object during a
non-lossy read/edit/write round-trip. It MAY omit it only in an explicitly lossy export.

### 4.2 Sparse semantics

**Omission is semantically significant.** A missing clinical field means *not documented in this
CDPF document*. It MUST NOT be interpreted as normal, absent, negative, or not applicable.

When an application needs to document a negative/normal state, it SHOULD emit an explicit finding,
for example:

```json
{"label": "Pallor", "status": "absent"}
```

Draft 0.1 common finding statuses are:

- `normal`
- `abnormal`
- `present`
- `absent`
- `not_assessed`
- `indeterminate`

`not_assessed` is itself an explicit statement and is therefore different from omission.

### 4.3 Clinical versus presentation data

Clinical meaning MUST NOT depend on `presentation`. A reader MAY ignore presentation hints without
changing the clinical interpretation of the document.

`presentation` is intentionally open-ended in Draft 0.1. Examples include a local layout profile,
page size hint, or preferred print template. Font files, executable layout code, and application UI
state are not part of the core model.

## 5. Common primitives

`schema/common.schema.json` defines reusable structures.

### 5.1 Coding

A coding object contains `code` and MAY contain `system`, `display`, and `version`.

CDPF does not mandate a terminology system. Implementers SHOULD include `display` when a code may not
be resolvable by the receiving system.

### 5.2 Identifier

Identifiers contain a `value` and MAY identify their `system`, `type`, and `use`. Local identifiers
are allowed.

### 5.3 Quantity

A quantity contains `value` and MAY contain `unit`, coded unit metadata, and comparator.

### 5.4 Attachment reference

Clinical JSON references a packaged attachment by `attachment_id`. Paths and hashes are owned by the
manifest rather than duplicated throughout the clinical document.

## 6. Core block types

Draft 0.1 reserves these block types:

- `cdpf.core.chief_complaints`
- `cdpf.core.history`
- `cdpf.core.examination.general`
- `cdpf.core.examination.cardiovascular`
- `cdpf.core.examination.respiratory`
- `cdpf.core.examination.neurological`
- `cdpf.core.examination.eye`
- `cdpf.core.examination.abdominal`
- `cdpf.core.examination.ent`
- `cdpf.core.examination.urological`
- `cdpf.core.examination.gynae_obstetric`
- `cdpf.core.examination.other`
- `cdpf.core.investigations`
- `cdpf.core.diagnosis`
- `cdpf.core.medications`
- `cdpf.core.advice`

The following names are reserved for future profiles but their payloads are not normative in 0.1:

- `cdpf.core.ecg`
- `cdpf.core.image`
- `cdpf.core.clinical_drawing`
- `cdpf.core.certificate`
- `cdpf.core.referral`

See `spec/core-blocks.md`.

## 7. Medications

A CDPF prescribed medication distinguishes the medication concept from the prescription directions.
A medication may carry a generic name, brand name, strength, dose form, route, display text, and zero
or more codings. Prescription directions such as dose, frequency, timing, duration, and instructions
are separate fields.

A receiver MUST NOT infer that two medicines are equivalent solely because their display names are
similar. Terminology identifiers are optional and must be interpreted according to their declared
system.

## 8. Subject, encounter, and author

`subject.subject_id` is required in Draft 0.1 and may be local, pseudonymous, or cross-system. Human
name/demographics and external identifiers are optional.

`encounter` is optional because not every clinical document is tied to a conventional encounter.

`authors` contains one or more author objects. Draft 0.1 does not define cryptographic signatures;
author metadata is provenance, not proof of identity.

## 9. Extensions

`extensions` is a JSON object whose keys MUST be collision-resistant identifiers. Absolute URIs are
RECOMMENDED for interoperable extensions. Extension values may be any JSON value.

Core meaning MUST NOT depend on a private extension unless both parties have separately agreed to
that extension profile.

See `spec/extensions.md`.

## 10. Unknown fields and forward compatibility

Readers SHOULD preserve unknown JSON object members and unknown blocks during non-lossy processing.
Writers MUST NOT repurpose a standardized field with incompatible semantics.

Because Draft 0.x is experimental, readers SHOULD validate the exact `cdpf_version` they support.
A stable major-version compatibility policy will be defined before 1.0.

## 11. Integrity, privacy, and security

SHA-256 in the manifest protects against accidental or malicious payload substitution but does not
provide authenticity. Cryptographic signatures are out of scope for Draft 0.1.

CDPF may contain sensitive clinical information. Encryption, authorization, consent, audit logging,
and transport security are responsibilities of the implementation/environment in Draft 0.1.

Readers MUST treat attachments as untrusted content and MUST NOT execute them automatically.

## 12. Serialization

JSON files MUST be UTF-8. Writers SHOULD produce ordinary JSON without comments. Field order inside
JSON objects is not semantically meaningful. Array order is meaningful where explicitly stated,
including `blocks` and medication item lists.

UUID values SHOULD use lowercase canonical textual form. Timestamps use ISO 8601 / RFC 3339 style
strings with timezone offsets or `Z`.

## 13. Validation

JSON Schema validates structural conformance but cannot establish clinical correctness. Passing a
schema does not mean that a diagnosis, prescription, examination finding, identifier, or code is
clinically valid.

The reference validator additionally performs package-path, file-size, attachment membership, and
SHA-256 checks.

## 14. Non-goals for Draft 0.1

Draft 0.1 does not define:

- cryptographic document signatures;
- encrypted package format;
- clinical decision support or interaction checking;
- AI prompts, model outputs, or agent behavior;
- billing/coding workflow;
- database persistence;
- pixel-perfect printing;
- DICOM transport;
- FHIR/CDA conversion rules.

These may be addressed by later profiles or separate projects.
