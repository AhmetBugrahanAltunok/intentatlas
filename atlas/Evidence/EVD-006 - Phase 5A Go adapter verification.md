---
id: EVD-006
type: evidence
status: verified
phase: 5A
verified_on: 2026-07-31
---
# Phase 5A Go adapter verification

This evidence verifies Phase 5A against its accepted requirement, architecture decision, delivery
issue, and completion protocol.

- proves:: [[Requirements/REQ-006 - Trace Go structure]]
- references:: [[Decisions/ADR-006 - Conservative Go module projection]]
- references:: [[Issues/ISSUE-004 - Implement Go language adapter]]
- references:: [[Brain/Phase Completion Protocol]]
- recorded-in:: [[Commit 88fb6ce - feat- add deterministic Go structure tracing]]

## Change inventory

- Added a built-in Go adapter behind the existing immutable, bounded graph-fragment contract.
- Added a dependency-free structural lexer that masks comments and literals, extracts explicit
  named types, grouped types, generic functions, functions, and methods, and records stable source
  lines without running Go or project code.
- Added lexical import parsing so import-like text inside comments, interpreted strings, runes,
  and raw strings cannot create relationships.
- Added `go.mod` discovery and module-path resolution, including longest-prefix selection for
  nested modules. Module-local package imports project to discovered non-test Go files; external
  and unresolved packages are omitted.
- Added Go test classification, test-import relationships, and conservative `name_test.go` to
  `name.go` filename links.
- Added an original redistributable fixture covering generics, grouped types, methods, single and
  block imports, aliases, root and nested modules, external imports, comments, literals, and tests.
- Updated English/Turkish product documentation, architecture, security guidance, changelog,
  language strategy, and the active roadmap.

## Focused regression verification

- Command: `python -m pytest tests/test_adapters.py tests/test_scanner.py`
- Result: 11 passed.
- Coverage includes the shared immutable/size-bounded adapter contract, deterministic repeated Go
  scans, Go/go.mod metadata, named symbols, module-local package projection, nested module
  selection, external import omission, false import/symbol suppression inside comments and
  literals, oversized-file omission, unclosed-import fail-closed behavior, and both test
  relationship forms.

## Complete quality suite

- `python -m pytest`: 47 passed.
- `python -m pytest --cov=intentatlas --cov-branch --cov-report=term-missing`: 47 passed,
  88.12% branch-aware coverage; the Go adapter itself reports 86%.
- `python -m ruff check .`: all checks passed.
- `python -m bandit -q -r src`: no findings.
- `python -m pip check`: no broken requirements.
- `node --check src/intentatlas/web/app.js`: JavaScript syntax passed.
- `git diff --check`: passed.

## Repository, graph, and CLI acceptance

- Two final unchanged repository scans produced 382 nodes, 614 relationships, and 349 generated
  notes after this Evidence and Review were added.
- A baseline copied from the first graph produced diff schema 1 with `has_changes: false` after the
  second scan.
- SHA-256 tree digests before and after a final unchanged scan confirmed both
  `user_notes_preserved=True` and `generated_notes_deterministic=True`.
- Graph health reported 0 orphaned durable notes.
- `intentatlas impact REQ-006 --depth 3` traversed REQ-006 → ADR-006 → ISSUE-004 and the Go adapter,
  adapter registry, scanner, and regression test through typed relationships.
- A final isolated Go project initialized and scanned to 26 nodes, 25 relationships, 20 generated
  notes, and 0 durable orphans.
- Its CLI impact output showed `cmd/app/main.go` importing both files in the local math package and
  the nested-module worker through `go-structural`, while defining the `main` symbol.
- Repeated fixture scans produced identical nodes and relationships. Neither unresolved external
  imports nor import-looking raw-string content created internal edges.
- Existing ownership regression tests prove `atlas/Private/` is not enumerated and user-owned vault
  notes are not overwritten. The ignored repository-root `.obsidian/` remains outside the source
  model.

## Local graphical acceptance

- The loopback viewer loaded an isolated Go graph with distinct file, config, symbol, and test
  layers and no browser console warnings or errors.
- The `cmd/app/main.go` detail showed Go metadata, three module-local `imports` relationships with
  `go-structural` provenance, and a `defines` relationship to `main`.
- The `internal/math/add_test.go` detail showed Go test metadata, a filename-convention `tests`
  relationship to `internal/math/add.go`, and a `defines` relationship to `TestAdd`.
- Keyboard node activation and graph fitting worked, demonstrating accessible navigation for the
  new Go nodes without adding a Go-specific viewer path.

## Packaging and clean-install acceptance

- `python -m pip wheel . --no-deps --no-build-isolation` built
  `intentatlas-0.1.0-py3-none-any.whl` successfully.
- Wheel SHA-256: `ba7105a79e9ce16b9283bc4e296e062f2c7e0601155d48cc67b8abbffb40a0cc`.
- The wheel contains 29 entries, including `intentatlas/adapters/go.py`, viewer assets, metadata,
  and the CLI entry point.
- Installing the wheel into a clean virtual environment with `--no-index --no-deps`, then running
  `scan` and `status` on the final Go fixture, reproduced 26 nodes, 25 relationships, 20 generated
  notes, and 0 durable orphans.

## Dependency, toolchain, and network note

- Phase 5A adds no dependency and does not change dependency declarations.
- The local machine does not have the Go toolchain installed, so an independent `go test ./...`
  syntax/compile check was unavailable. IntentAtlas itself intentionally requires no Go runtime;
  its structural fixture behavior is covered by deterministic Python tests and clean-wheel CLI
  verification.
- No networked audit was run because network access requires explicit approval and no dependency
  changed.

## Remaining risks

- The conservative lexer is not a complete Go parser. It intentionally omits Unicode identifiers,
  build-constraint evaluation, generated-code detection, local declarations, and interface method
  symbols rather than guessing.
- A package import projects to every discovered non-test file in that package. This avoids an
  arbitrary representative but can create dense relationships in large packages; first-class
  package nodes may become preferable at scale.
- Syntax validity was not independently checked with a Go compiler on this machine.
- Go workspace files, `replace` semantics, vendoring semantics, and dependency graph resolution are
  outside this phase; only discovered `go.mod` module declarations define local boundaries.
- External issue and pull-request inputs remain deliberately deferred to Phase 5B.
