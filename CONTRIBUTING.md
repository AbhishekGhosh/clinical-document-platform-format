# Contributing

CDPF welcomes issues, examples, implementation reports, and pull requests.

## Specification changes

A proposal that changes portable clinical meaning should include:

1. the interoperability problem being solved;
2. at least one concrete JSON example;
3. sparse/unknown-value semantics;
4. backward-compatibility impact;
5. whether the requirement belongs in core CDPF or an extension;
6. JSON Schema changes when applicable;
7. tests or example-package updates.

Avoid adding fields solely because one UI happens to display them. CDPF standardizes portable
clinical-document meaning, not a particular screen layout.

## Normative language

The keywords MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT, RECOMMENDED, MAY, and
OPTIONAL are interpreted as requirement levels when they appear in uppercase in the specification.

## Privacy

Never submit real patient-identifying data in examples, issues, tests, or screenshots. Use fictional
or clearly synthetic data.

## Licensing contributions

By submitting a contribution, you agree that code/schema contributions are provided under Apache
License 2.0 and specification/prose contributions under CC BY 4.0, consistent with this repository.
