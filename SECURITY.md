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
- Go resolution accepts only imports matching a discovered local `go.mod` module path, prefers the
  longest nested-module match, and does not invoke the Go toolchain or resolve external modules.
- Coverage and test reports are opt-in, project-local XML inputs. Import rejects symbolic links,
  paths outside the project or inside `atlas/Private/`, DTD/entity declarations, oversized files,
  excessive records, malformed XML, and ambiguous file mappings.
- Imported verification evidence stores aggregate counts and durations only; raw failure output,
  test output, source content, secrets, and absolute report paths are not persisted.
- Graph diff inputs and outputs remain below the project root, cannot use `atlas/Private/`, and may
  not overwrite either input graph.
- Delivery imports are opt-in local JSON files with path, symlink, byte, record, link, schema,
  duplicate-key, field, type, identifier, and URL validation. They retain no body, comment, author,
  credential, query string, fragment, or raw provider payload.
- IntentAtlas invokes Git only with fixed, read-only argument lists and never through a shell.
  Symbol-impact parsing is limited to a bounded recent commit window, zero-context patches, a
  fixed byte/hunk budget, validated commit identifiers, and safe current-side project paths;
  raw blobs are read with `git cat-file` and must match the bounded worktree file after line-ending
  normalization. Blob checks are limited to scanned paths with trusted spans and at most 1,000
  commit/path pairs; excluded paths are never opened. Stale, malformed, or excessive patch data
  produces no symbol claims.
- The local viewer binds to `127.0.0.1` by default.

Security reports are acknowledged in release notes unless the reporter requests anonymity.
