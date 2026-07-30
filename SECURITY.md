# Security Policy

## Reporting a vulnerability

Please do not open a public issue for a suspected vulnerability. Use GitHub's private
security advisory flow on the repository once it is published. Include affected versions,
reproduction steps, impact, and any suggested mitigation.

## Security model

- Scans are local and do not upload source code.
- Generated notes contain relationships and symbol names, not raw source contents.
- Excluded directories are pruned before descent; `atlas/Private/` is never enumerated or scanned.
- Commit subjects are treated as untrusted and redacted before persistence.
- User note IDs cannot replace scanner-owned graph identities, and generated Markdown escapes
  untrusted display text.
- Typed Markdown relation labels are matched against a fixed local vocabulary; unknown labels
  remain generic references and cannot extend executable behavior.
- Built-in language adapters receive a read-only discovered-file view, enforce the local parse-size
  limit, persist structural metadata only, and never invoke language runtimes or project code.
- TypeScript/JavaScript resolution accepts only static relative module references; bare dependency
  names, dynamic imports, and paths escaping the scanned repository are not followed.
- IntentAtlas invokes Git only with fixed, read-only argument lists and never through a shell.
- The local viewer binds to `127.0.0.1` by default.

Security reports are acknowledged in release notes unless the reporter requests anonymity.
