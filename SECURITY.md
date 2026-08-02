# Security Policy

## Reporting a vulnerability

Please do not open a public issue for a suspected vulnerability. Use GitHub's private
vulnerability-reporting flow once it has been enabled for the public repository. Include affected
versions, reproduction steps, impact, and any suggested mitigation. Public launch is blocked until
the repository owner has enabled and verified that private channel; no public fallback report is
requested before then.

## Security model

- Scans are local and do not upload source code.
- Public GitHub acquisition occurs only after explicit TTY approval of the normalized URL,
  network request, and managed-cache write. Only repository-root HTTPS URLs are accepted; embedded
  credentials, authentication, alternate schemes/hosts/ports, queries, fragments, page paths,
  localhost/IP targets, and redirects are rejected. Git runs with fixed arguments, isolated
  configuration, no shell/prompts/credentials/hooks/filters/LFS/submodules/project execution, a
  shallow history, and time/output/file/byte/disk bounds. `atlas/Private/` is excluded before
  checkout. Cache staging is atomic and locked; metadata contains no source, logs, environment, or
  secrets; exact-target cleanup rejects traversal and links. Cache hits identify an exact cached
  revision and make no remote-freshness claim.
- Generated notes contain relationships and symbol names, not raw source contents.
- Excluded directories are pruned before descent; `atlas/Private/` is never created, enumerated,
  scanned, or used as a configured output location.
- `intentatlas.json` must be a bounded regular file containing one JSON object with unique keys,
  known fields, and strict field types; the shared reader uses non-blocking, no-follow opens where
  the platform exposes them and verifies one stable regular-file identity. Malformed configuration
  fails before traversal or writes.
- Commit subjects are treated as untrusted and redacted before persistence.
- User note IDs cannot replace scanner-owned graph identities, and generated Markdown escapes
  untrusted display text.
- Typed Markdown relation labels are matched against a fixed local vocabulary; unknown labels
  remain generic references and cannot extend executable behavior.
- Built-in language adapters receive a read-only discovered-file view, enforce the local parse-size
  limit, persist structural metadata only, and never invoke language runtimes or project code.
- TypeScript/JavaScript resolution accepts only static relative module references; bare dependency
  names, dynamic imports, and paths escaping the scanned repository are not followed. Exact-symbol
  evidence is limited to unambiguous discovered named or default declarations.
- Python exact-symbol references follow at most eight local package re-export hops, reject cycles,
  abstain when repository-root and leading-`src/` module candidates collide, and never import or
  execute a module.
- Go resolution accepts only imports matching a discovered local `go.mod` module path, prefers the
  longest nested-module match, and does not invoke the Go toolchain or resolve external modules.
  Same-directory test links require a compatible package plus an exported identifier uniquely
  owned by one production file; ambiguous names, unexported declarations, comments, and literals
  do not create symbol-reference evidence. Tests importing another local Go package require a
  qualified unique exported symbol (or a unique exported identifier for dot imports); blank and
  ambiguous imports create no direct test relationship.
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
  Git log and patch collection apply the literal Private boundary and configured exclusions as
  pathspecs before output is produced; patch collection is further restricted to bounded literal
  scanned-symbol paths. Stdout is byte-bounded while it is collected, and excessive output kills
  the child process rather than retaining a truncated result.
  Symbol-impact parsing is limited to a bounded recent commit window, zero-context patches, a
  fixed byte/hunk budget, validated commit identifiers, and safe current-side project paths;
  raw blobs are read with `git cat-file` and must match the bounded worktree file after line-ending
  normalization. Blob checks are limited to scanned paths with trusted spans and at most 1,000
  commit/path pairs; excluded paths are never opened. Stale, malformed, or excessive patch data
  produces no symbol claims.
- Test recommendations are pure queries over the already validated graph. They execute no test or
  project command, use fixed confidence rules, bound artifacts/candidates/reasons/observations and
  output size, and label every result advisory. Exact-symbol dependency propagation is limited to
  one production hop and 1,000 direct dependents; recent co-change evidence uses at most five
  latest-date commits. Imported JUnit aggregates never raise confidence.
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
- The built-in demo graph is original, pre-authored static product data built with the production
  graph model. It exercises production recommendation, Change Report, and viewer behavior after
  evidence exists, not repository discovery, AST parsing, or Git diff extraction. It does not scan
  the current directory, execute project code, or access the network; its graph exists only in an
  automatically cleaned temporary directory. The interactive viewer receives its ranked report
  from the same graph snapshot. Viewer evidence-path traversal is limited to depth 6, 800 visited
  nodes, and 6 results, and all graph labels remain escaped. The loopback server rejects foreign
  `Host` headers and applies no-store, anti-framing, MIME-sniffing, referrer, same-origin resource,
  and content-security response policies.
- Release verification uses fixed Hatchling/build/packaging versions, rejects custom build hooks
  and unreviewed project metadata fields, builds under a fixed timestamp, and requires
  byte-identical repeated wheel and source archives. It validates exact version-derived
  artifact/dist-info names, bounded and collision-free member paths, CRCs, `RECORD` hashes and
  sizes, wheel/source and dependency metadata, the canonical version source, pure-Python tags,
  console entry point, bundled web assets, and repository-matching MIT license bytes. A positive
  manifest requires every source-archive file, the exact wheel member set, and both runtime
  payloads to match the reviewed checkout bytes; only generated `PKG-INFO` is exempt from byte
  parity and is checked semantically.
  Rebuilding the verified source archive under the same fixed epoch must reproduce the direct
  wheel byte-for-byte before installation and extracted-source testing.
  Source archives reject unsafe members, links, undeclared roots, vault, local state, real-world
  benchmark, workflow, and local configuration data; only the small original corpus needed by
  packaged tests is allowed. Fixed-seed property/mutation tests exercise untrusted graph and JSON
  boundaries, a real Chrome-family browser verifies bounded rendered state, and static typing is a
  maintained-source CI gate. External Actions are policy-checked for immutable full-SHA references.
  The verifier can emit deterministic provenance binding artifact names, sizes, and SHA-256 values
  to an exact source revision and build epoch; this record is descriptive evidence, not a signature.
  Default CI verifies artifacts but never publishes them. A separate manually dispatched workflow
  requires a fixed `pypi` environment, an explicit confirmation phrase, exact source/epoch/hashes,
  an exact match between source and protected-`main` dispatch revisions, immutable Actions, and
  short-lived trusted-publishing identity. Its unprivileged job builds and
  verifies the bytes; only a separate protected job has OIDC permission, runs no project/build code,
  rechecks the transferred hashes, and publishes those same bytes. Repository environment
  protection, protected-release-ref deployment policy, and package-index trust configuration remain
  external owner responsibilities.
- Generated-vault synchronization never purges desired output before replacement. Changed notes
  use dot-prefixed same-directory temporary files and atomic replacement; recognized transient sharing
  failures retry within a fixed bound, stale cleanup runs last, symlinks are not followed during
  cleanup, and temporary files are removed on success or failure. Existing linked generated-area
  components are rejected before synchronization. This does not claim protection against a separate
  hostile process replacing a previously verified vault directory while synchronization is running;
  run scans only while the repository and vault are under the invoking user's control.
- The local viewer validates IPv4 loopback-only binding for both project and demo entry points and
  uses `127.0.0.1` by default. The accepted `localhost` alias is normalized to that numeric address
  before binding, and no reverse DNS lookup is performed. Interactive change reports are served only from the
  same bounded in-memory graph/report snapshot, are not persisted by the viewer, and never include
  raw diff lines or source contents.

Security reports are acknowledged in release notes unless the reporter requests anonymity.
