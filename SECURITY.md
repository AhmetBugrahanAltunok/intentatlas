# Security Policy

## Reporting a vulnerability

Please do not open a public issue for a suspected vulnerability. Use GitHub's private
security advisory flow on the repository once it is published. Include affected versions,
reproduction steps, impact, and any suggested mitigation.

## Security model

- Scans are local and do not upload source code.
- Generated notes contain relationships and symbol names, not raw source contents.
- `atlas/Private/` is ignored and never scanned.
- Commit subjects are treated as untrusted and redacted before persistence.
- IntentAtlas invokes Git only with fixed, read-only argument lists and never through a shell.
- The local viewer binds to `127.0.0.1` by default.

Security reports are acknowledged in release notes unless the reporter requests anonymity.
