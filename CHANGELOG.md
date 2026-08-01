# Changelog

All notable changes will be documented in this file.

The format is based on Keep a Changelog and the project follows Semantic Versioning.

## [Unreleased]

### Added

- Fixed-seed property and mutation-fuzz coverage for generated graphs and untrusted JSON, plus a
  real Chrome-family browser E2E gate for the bounded 320-node viewer scenario.
- Deterministic release provenance records bound to exact source revision, build epoch, artifact
  names, sizes, SHA-256 digests, and completed archive verification checks.
- Maintained-source static typing and a repository policy that requires immutable full-SHA
  references for every external GitHub Action.
- A separately dispatched, fixed-environment trusted-publishing workflow that requires an exact
  source revision, build epoch, approved artifact hashes, confirmation phrase, and short-lived
  identity before it can publish the same bytes it verifies.
- Executable language-adapter conformance contract version 1, shared by fresh and cached fragments,
  with deterministic fixture checks and fail-closed structural validation before graph merge.
- Deterministic bounded viewer overview and two-hop focus windows with global search, indexed graph
  access, total/rendered counts, and explicit relationship omission at large repository scale.
- Explicit bounded imports for SCIP protobuf JSON, SARIF 2.1.0, and commit-keyed per-test execution
  maps, retaining only source-free aggregate metadata and safe local graph identities.
- Aligned-only runtime test relationships: execution maps influence recommendations only when their
  full commit exactly matches repository HEAD; stale or unknown maps remain observations.
- Content-addressed per-adapter scan fragments that reuse unchanged Python, JavaScript/TypeScript,
  and Go analysis while retaining a cache-independent full-scan reference and visible CLI metrics.
- Strict bounded adapter-cache validation and atomic graph/cache replacement that preserves the
  last complete artifact on write failure and never stores raw source content.
- A deterministic `review --base --head` shadow-mode command that renders the existing bounded
  change analysis as Markdown, JSON, or path-safe SARIF 2.1.0 without publishing or blocking CI.
- An opt-in, credential-free composite Action that writes the shadow review only to the runner's
  temporary directory and leaves upload, publication, and policy to the calling workflow.
- Strict commit-keyed test outcome sidecars with explicit aligned/stale freshness and observational
  selected-versus-executed path comparison, without inferring accuracy from stale or unkeyed data.
- A change-centric `review --open` viewer backed by the exact in-memory graph and report, including
  revision scope, strategy, outcome freshness, and selected-versus-executed evidence.
- Deterministic ChangeSet schema 1 and a `changes` command for bounded commit, revision-range,
  staged, and worktree metadata without retaining raw diffs or untracked contents.
- Optional Change Analysis schema 1 with explicit `analyzed`/`fallback`/`unknown` state,
  revision-to-worktree freshness, confidence, artifact identity, and evidence provenance.
- Deterministic Change Report schema 1 with conservative requirement-impact ranking, advisory
  test targets, explicit abstention, targeted-plus-full-suite fallback strategies, and an optional
  loopback viewer panel backed by the same fresh in-memory graph.
- Initial local intent graph scanner.
- Obsidian-compatible project brain and generated graph notes.
- Local interactive viewer, impact tracing, and health status commands.
- Phase-based delivery protocol with evidence and review completion gates.
- Phase 2 typed relation catalog, inverse relationship labels, issue notes, and explicit
  `relation:: [[target]]` Markdown links.
- A deterministic built-in language-adapter contract and conservative TypeScript/JavaScript,
  TSX, and JSX symbol, local-import, re-export, and test analysis.
- Bounded, offline Cobertura coverage and JUnit test-result evidence imports.
- A versioned, timestamp-free graph diff command with deterministic JSON and optional CI checks.
- A conservative, dependency-free Go adapter for `.go` files, `go.mod` module boundaries, named
  types, functions, methods, module-local imports, and tests.
- Bounded vendor-neutral local issue and pull-request snapshots with typed intent, delivery, file,
  and known-commit relationships.
- Conservative symbol-level Git impact for recent Python changes using bounded zero-context hunks,
  commit-blob alignment, validated AST spans, and typed `modifies`/`modified-by` relationships.
- Deterministic advisory test-file recommendations with fixed confidence scores, evidence paths,
  bounded text/JSON output, filtering, deduplication, and unscored JUnit observations.
- Strict, offline recommendation evaluation against exhaustive reviewed labels, with deterministic
  per-case and micro-aggregate TP, FP, FN, precision, and recall plus a self-hosted baseline.
- Bounded cross-project corpus evaluation with low/medium/high threshold comparison and original
  Python, TypeScript, and Go graph regression scenarios.
- A lazy deterministic graph adjacency index shared by impact, orphan-health, and test
  recommendation queries, plus a bounded offline synthetic scale benchmark command.
- A one-command original local showcase and bounded viewer evidence paths that connect selected
  intent, implementation, delivery, test, evidence, and history nodes.
- Offline real-world recommendation evaluation for clean, pinned, license-reviewed public
  checkouts, with strict provenance validation, 18 reviewed cases across six Python/JavaScript/Go
  projects, and an ephemeral-only generated-output policy.
- Conservative Go same-package test links based on referenced exported declarations uniquely owned
  by one production file, with filename convention retained as weak fallback evidence.
- Bounded Python re-export and JavaScript/TypeScript static-import symbol evidence, one-hop exact
  symbol-dependent test discovery, and recent co-change test evidence with inspectable paths.
- Installed-wheel end-to-end coverage for initialization, scan, status, impact, test
  recommendation, and loopback viewer retrieval across the supported operating-system matrix.
- A local release verifier for repeated-build reproducibility, wheel integrity and metadata,
  bundled assets, license bytes, source-archive boundaries, and a documented release procedure.

### Changed

- Fresh vault initialization now creates generic guidance and templates without seeding
  IntentAtlas-specific project memory into user repositories.
- Go test references retain exact symbol targets alongside separate file navigation edges, and
  unrelated same-file symbol fallback no longer appears at the default confidence threshold.
- Graph schema 3 and relation schema 4 add bounded `calls`/`called-by` evidence so a directly
  tested Go wrapper can recover one exact callee without broad file fallback.
- Repository discovery now prunes excluded directories before descent and never walks the vault.
- Graph and vault generation reject identity collisions and escape untrusted Markdown content.
- The Product Roadmap is now the clearly identified active plan; the original version-oriented
  roadmap remains available as an explicitly archived historical snapshot.
- Phase 1 now has complete local, browser, dependency-audit, and packaged-wheel acceptance
  evidence recorded in the Obsidian vault.
- Graph caches use schema 2 while retaining read compatibility with schema 1, and impact output
  explains relation direction, category, and provenance.
- Graph loading now rejects duplicate JSON keys, non-object roots, malformed node/edge collections,
  and invalid record shapes with explicit validation errors.
- Repeated impact and recommendation lookups now traverse indexed local edge buckets instead of
  rescanning every unrelated graph relationship.
- Viewer loopback validation now applies inside the serving boundary, including direct library and
  built-in demo use.
- Python structural analysis now runs behind the same graph-fragment adapter contract used by
  TypeScript and JavaScript without changing its graph semantics.
- Python tests with an exact local symbol reference no longer inherit a broader test-to-file edge
  for that resolved module; nested changes prefer a matching owner-named test when available.
- Root-level JavaScript files named `test.js` or `tests.js` are now recognized as tests.
- Go tests importing a local package now link only through uniquely owned referenced exports
  instead of every file in that package; non-test imports remain package-level.
- Relation schema 2 adds `addressed-by`/`addresses` delivery semantics and broadens `changes` to
  version-control delivery records; existing graph caches require a new scan.
- Relation schema 3 adds direct `modifies`/`modified-by` history semantics while preserving
  commit-to-file `changes` as the conservative fallback.
- Source distributions now contain reviewable source, tests, documentation, release tooling, and
  required project metadata without bundling the Obsidian vault, benchmarks, workflows, or local
  IntentAtlas configuration.

### Fixed

- Restored reliable pointer, click, and keyboard activation for graph nodes in the local viewer.
- Loopback viewer startup no longer depends on reverse DNS resolution, preventing delayed or
  stalled binding on systems where localhost address lookups are unavailable.
- Generated-vault refreshes now preserve existing output during render or replacement failures,
  retry transient file locks, atomically replace changed notes, skip byte-identical writes, clean
  temporary files, and postpone stale-note deletion until every desired note is present.
