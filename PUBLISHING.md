# First GitHub Publication Checklist

Suggested repository name: `clinical-document-platform-format`.

Suggested GitHub description:

> Open draft specification and reference implementation for portable, block-based clinical documents.

Suggested topics: `clinical-document`, `health-informatics`, `ehr`, `emr`, `json-schema`,
`interoperability`, `open-specification`, `healthcare`.

1. Create a public GitHub repository with no auto-generated license/README (this package already has them).
2. Push the Draft 0.1 tree.
3. Confirm GitHub displays Apache-2.0 for the root code license and keep `LICENSE-DOCS.md` visible for CC BY 4.0 documentation terms.
4. Enable GitHub Actions and confirm the `validate` workflow passes.
5. Create a release/tag such as `v0.1.0-draft` with title **CDPF Draft 0.1**.
6. State clearly in the release notes that the format is experimental and not a replacement for FHIR/CDA/openEHR/DICOM.
7. Invite implementation feedback before freezing any 1.0 compatibility promises.

Do not publish real patient data in examples, issues, release assets, or test fixtures.
