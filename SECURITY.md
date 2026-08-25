# Security and Privacy

CDPF files may contain protected health information. The format itself does not grant permission to
collect, disclose, or transmit clinical data. Implementers are responsible for applicable privacy,
security, retention, consent, and medical-record requirements.

Draft 0.1 packages are ordinary ZIP containers and **are not encrypted by CDPF**.

Readers should, at minimum:

- reject absolute paths, `..` traversal, backslash-based traversal, and symbolic links;
- enforce configurable limits on member count and total uncompressed bytes to mitigate ZIP bombs;
- reject encrypted members unless an implementation explicitly supports them;
- verify SHA-256 and byte size for `document.json` and attachments before use;
- treat attachment media types as untrusted metadata and apply normal content-sniffing/sandbox rules;
- never execute embedded content merely because it is present in a package;
- avoid logging clinical payloads by default.

The Python reference validator demonstrates these checks but is not a certified security product.

Please report vulnerabilities privately to the repository maintainer rather than including patient
information or exploit payloads in a public issue.
