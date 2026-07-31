# Changelog

All notable changes will be documented in this file.

The format is based on Keep a Changelog and the project follows Semantic Versioning.

## [Unreleased]

### Added

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

### Changed

- Repository discovery now prunes excluded directories before descent and never walks the vault.
- Graph and vault generation reject identity collisions and escape untrusted Markdown content.
- The Product Roadmap is now the clearly identified active plan; the original version-oriented
  roadmap remains available as an explicitly archived historical snapshot.
- Phase 1 now has complete local, browser, dependency-audit, and packaged-wheel acceptance
  evidence recorded in the Obsidian vault.
- Graph caches use schema 2 while retaining read compatibility with schema 1, and impact output
  explains relation direction, category, and provenance.
- Python structural analysis now runs behind the same graph-fragment adapter contract used by
  TypeScript and JavaScript without changing its graph semantics.
- Relation schema 2 adds `addressed-by`/`addresses` delivery semantics and broadens `changes` to
  version-control delivery records; existing graph caches require a new scan.
- Relation schema 3 adds direct `modifies`/`modified-by` history semantics while preserving
  commit-to-file `changes` as the conservative fallback.

### Fixed

- Restored reliable pointer, click, and keyboard activation for graph nodes in the local viewer.
- Generated-vault refreshes now preserve existing output during render or replacement failures,
  retry transient file locks, atomically replace changed notes, skip byte-identical writes, clean
  temporary files, and postpone stale-note deletion until every desired note is present.
