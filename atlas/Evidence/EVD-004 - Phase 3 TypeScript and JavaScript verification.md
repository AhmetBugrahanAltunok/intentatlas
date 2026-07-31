---
id: EVD-004
type: evidence
status: verified
phase: 3
verified_on: 2026-07-31
---
# Phase 3 TypeScript and JavaScript verification

This evidence verifies Phase 3 against its accepted requirement, architecture decision, delivery
issue, and completion protocol.

- proves:: [[Requirements/REQ-004 - Trace TypeScript and JavaScript structure]]
- references:: [[Decisions/ADR-004 - Built-in language adapter contract]]
- references:: [[Issues/ISSUE-002 - Implement TypeScript and JavaScript adapter]]
- references:: [[Brain/Phase Completion Protocol]]
- recorded-in:: [[Commit cabeadd - feat- add TypeScript and JavaScript adapters]]

## Change inventory

- Added an immutable adapter context, deterministic graph fragments, and a language-adapter
  protocol; the scanner validates adapter edges before merging them.
- Moved existing Python AST analysis behind the adapter contract without changing Python graph
  semantics.
- Added conservative, dependency-free TS, TSX, JS, and JSX analysis for named symbols, static
  relative imports, re-exports, CommonJS `require`, directory indexes, and filename test links.
- Rejects ambiguous module aliases and ignores bare packages, dynamic imports, paths outside the
  project, oversized inputs, comments, string/template decoys, malformed input, and unsupported
  syntax rather than inventing internal relationships or executing code.
- Added an original redistributable mixed-language fixture and adapter/scanner regression tests.
- Updated English and Turkish readmes, architecture, security guidance, roadmap, changelog, and
  the saved language-adapter strategy.
- Rebuilt generated Obsidian code, symbol, test, commit, and dashboard notes from the local graph.

## Focused regression verification

- Command: `python -m pytest tests/test_adapters.py tests/test_scanner.py`
- Result: 9 passed.
- Coverage includes adapter immutability and size bounds, invalid fragment rejection, Python parity,
  deterministic TS/JS output, declarations, local imports and re-exports, CommonJS, test links,
  ambiguous aliases, outside-root paths, bare packages, dynamic imports, and phantom-symbol guards.

## Complete quality suite

- `python -m pytest`: 33 passed.
- `python -m pytest --cov=intentatlas --cov-report=term-missing --cov-fail-under=80`:
  33 passed, 87.20% branch-aware coverage.
- `python -m ruff check .`: all checks passed.
- `python -m bandit -q -r src`: no findings.
- `python -m pip check`: no broken requirements.
- `node --check src/intentatlas/web/app.js`: JavaScript syntax passed.
- `git diff --check`: passed.

## Repository, graph, and CLI acceptance

- Final repository scan: 293 nodes, 438 relationships, and 270 generated notes.
- Graph health: 0 orphaned durable notes.
- Two unchanged scans produced identical generated-note trees and identical serialized graphs after
  excluding the explicit `generated_at` timestamp.
- The scans preserved all user-owned Brain, Requirements, Decisions, Issues, Evidence, Reviews,
  and Sessions notes byte-for-byte.
- `intentatlas impact REQ-004 --depth 3` traversed the requirement, ADR, issue, and three adapter
  implementation files with typed categories and provenance.
- `intentatlas impact src/main.ts ... --depth 2` on the installed mixed-language fixture showed
  TypeScript symbols, local imports, inverse test links, and `javascript-structural` provenance.
- Neither `atlas/Private/` nor the ignored repository-root `.obsidian/` appears in the graph.

## Local graphical acceptance

- The loopback viewer loaded the repository graph and exposed JavaScript and TypeScript nodes.
- Search and keyboard selection opened `src/intentatlas/web/app.js`; its details showed JavaScript
  and named definitions such as `boot`, `applySearch`, and `bindEvents` with
  `javascript-structural` provenance.
- The TypeScript fixture detail showed language, named definitions, local test/import relationships,
  categories, inverse labels, and evidence sources.
- REQ-004 opened as a first-class requirement and linked to ADR-004 and the saved adapter strategy.
- No browser console warnings or errors were reported.

## Packaging and clean-install acceptance

- `python -m pip wheel . --no-deps --no-build-isolation` built
  `intentatlas-0.1.0-py3-none-any.whl` successfully.
- Wheel SHA-256: `d449528e22cab85c402f7202def464403d6228e05ad63025be60e6b36724ee54`.
- All four adapter modules, viewer assets, metadata, and CLI entry points were present among 26
  wheel entries.
- Installing the wheel into a clean virtual environment and running `init`, `scan`, `status`, and
  `impact` on the mixed-language fixture succeeded with 44 nodes, 37 relationships, and 0 durable
  orphans.

## Dependency and network note

- Phase 3 adds no dependency and does not change dependency declarations.
- Local dependency integrity, lint, syntax, and source security checks passed.
- No networked audit was run because network access requires explicit approval.

## Remaining risks

- The conservative structural parser intentionally prefers missing an uncertain relationship over
  inventing one; TypeScript compiler-level semantics are outside this phase.
- Package aliases, monorepo workspace resolution, source maps, and runtime/dynamic imports are not
  resolved.
- Public real-world fixtures and cross-platform end-to-end coverage remain later release-readiness
  work.
- Coverage/test-result evidence import and stable CI graph diff are Phase 4 scope.
- Phase 3 is recorded in commit `cabeadd` and is visible through the generated commit note.
