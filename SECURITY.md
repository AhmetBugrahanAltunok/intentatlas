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
  Same-directory test links require a compatible package plus an exported identifier uniquely
  owned by one production file; ambiguous names, unexported declarations, comments, and literals
  do not create symbol-reference evidence.
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
- Test recommendations are pure queries over the already validated graph. They execute no test or
  project command, use fixed confidence rules, bound artifacts/candidates/reasons/observations and
  output size, and label every result advisory. Imported JUnit aggregates never raise confidence.
- Recommendation evaluation accepts only explicit project-local JSON outside `atlas/Private/`.
  It rejects symbolic links, unsafe paths, duplicate or unknown fields, malformed types, stale
  graph identities, and excessive bytes/cases/tests. It reuses the bounded recommendation query,
  executes no project code or tests, makes no network request, and emits timestamp-free summaries.
- Corpus manifests and every referenced graph or label remain project-local and outside
  `atlas/Private/`; direct symbolic links, unsafe paths, duplicate identities, malformed schemas,
  and excessive manifest/project/case/graph sizes are rejected. Corpus evaluation executes no
  repository code and makes no network request. One invalid project fails the complete corpus.
- Real-world manifests accept only bounded canonical GitHub URLs, full commit IDs, safe relative
  license and label paths, SPDX identifiers, and SHA-256 license digests. Evaluation is offline and
  requires an exact origin, exact HEAD, clean checkout, matching license bytes, and a pinned-commit
  label case. It ignores checkout-owned configuration, scans with fixed exclusions, executes no
  project code or tests, and persists no third-party graph or metadata. Acquisition remains a
  separate action requiring explicit network approval.
- The query-scale benchmark creates only bounded synthetic in-memory nodes and edges. Boolean,
  negative, and excessive edge or iteration counts are rejected; it reads no repository files,
  executes no project code, persists no benchmark graph, and makes no network request.
- The built-in demo graph is original static product data built with the production graph model.
  It does not scan the current directory, execute project code, or access the network; its graph
  exists only in an automatically cleaned temporary directory. Viewer evidence-path traversal is
  limited to depth 6, 800 visited nodes, and 6 results, and all graph labels remain escaped.
- Generated-vault synchronization never purges desired output before replacement. Changed notes
  use dot-prefixed same-directory temporary files and atomic replacement; recognized transient sharing
  failures retry within a fixed bound, stale cleanup runs last, symlinks are not followed during
  cleanup, and temporary files are removed on success or failure.
- The local viewer validates loopback-only binding for both project and demo entry points and uses
  `127.0.0.1` by default.

Security reports are acknowledged in release notes unless the reporter requests anonymity.
