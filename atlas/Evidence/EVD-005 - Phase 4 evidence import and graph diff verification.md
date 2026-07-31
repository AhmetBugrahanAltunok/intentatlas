---
id: EVD-005
type: evidence
status: verified
phase: 4
verified_on: 2026-07-31
---
# Phase 4 evidence import and graph diff verification

This evidence verifies Phase 4 against its accepted requirement, architecture decision, delivery
issue, and completion protocol.

- proves:: [[Requirements/REQ-005 - Import verification evidence and compare graph changes]]
- references:: [[Decisions/ADR-005 - Bounded evidence imports and canonical graph diff]]
- references:: [[Issues/ISSUE-003 - Implement evidence imports and graph diff]]
- references:: [[Brain/Phase Completion Protocol]]

## Change inventory

- Added opt-in `coverage_reports` and `test_reports` configuration with typed list, count, duplicate,
  and empty-path validation.
- Added offline Cobertura and JUnit XML import with project-relative path confinement, Private and
  symlink rejection, byte and record limits, DTD/entity rejection, format validation, conservative
  file mapping, and bounded duration handling.
- Aggregated coverage and test results per discovered file into deterministic generated `coverage`
  and `test-result` nodes with typed `proves` relationships and explicit provenance.
- Persisted only relative report paths, counts, rates, statuses, and durations; raw failures, test
  output, source content, secrets, absolute paths, and unmapped records are discarded.
- Added graph diff schema 1 with sorted node additions/removals/changes and edge
  additions/removals, no timestamp, deterministic JSON, safe output confinement, overwrite guards,
  and opt-in `--check` exit status.
- Added original redistributable evidence fixtures, focused security/regression tests, generated
  Obsidian note routing, viewer colors/filters, and English/Turkish documentation.
- Recorded Phase 3 in commit `cabeadd` and linked its Evidence to the generated commit node.

## Focused regression verification

- Command: `python -m pytest tests/test_evidence.py tests/test_graph_diff.py tests/test_config.py tests/test_cli.py tests/test_scanner.py tests/test_vault.py tests/test_viewer.py`
- Result: 30 passed.
- Coverage includes safe/missing/private/external report paths, DTD/entity and malformed XML,
  wrong formats, byte/record/duration bounds, aggregate correctness, no raw-output persistence,
  deterministic imports, deterministic diffs, CLI output confinement, overwrite prevention,
  `--check`, vault generation, scanner parity, and packaged viewer behavior.

## Complete quality suite

- `python -m pytest`: 45 passed.
- `python -m pytest --cov=intentatlas --cov-report=term-missing --cov-fail-under=80`:
  45 passed, 88.54% branch-aware coverage.
- `python -m ruff check .`: all checks passed.
- `python -m bandit -q -r src`: no findings.
- `python -m pip check`: no broken requirements.
- `node --check src/intentatlas/web/app.js`: JavaScript syntax passed.
- `git diff --check`: passed.

## Repository, graph, and CLI acceptance

- Final repository scan: 340 nodes, 542 relationships, and 312 generated notes.
- Graph health: 0 orphaned durable notes.
- Two unchanged scans produced identical generated-note trees and identical serialized graphs after
  excluding the explicit `generated_at` timestamp.
- The scans preserved all user-owned Brain, Requirements, Decisions, Issues, Evidence, Reviews,
  and Sessions notes byte-for-byte.
- `intentatlas impact REQ-005 --depth 3` traversed the requirement, ADR, issue, and four planned
  implementation files with typed categories and wikilink provenance.
- An isolated configured project scanned to 12 nodes and 13 relationships with one coverage node,
  one test-result node, six generated notes, and 0 durable orphans.
- CLI impact showed `coverage -> proves -> src/app.py` via `cobertura-xml` and
  `test-result -> proves -> tests/app_check.py` via `junit-xml`.
- A baseline copied from the same graph produced diff schema 1 with `has_changes: false`; focused
  CLI tests prove stable changed output and `--check` exit status 1.
- Neither `atlas/Private/` nor the ignored repository-root `.obsidian/` appears in the graph or
  generated project notes.

## Local graphical acceptance

- The loopback viewer loaded the isolated 12-node, 13-relationship graph successfully.
- Coverage and test-result appeared as separate first-class filter layers and accessible nodes.
- Coverage details showed Cobertura format, relative report path, 2/2 covered lines, rate 1, and a
  typed `proves` relationship to `src/app.py` with `cobertura-xml` provenance.
- Test-result details showed JUnit format, relative report path, aggregate status/duration fields,
  and a typed `proves` relationship to `tests/app_check.py` with `junit-xml` provenance.
- No browser console warnings or errors were reported.

## Packaging and clean-install acceptance

- `python -m pip wheel . --no-deps --no-build-isolation` built
  `intentatlas-0.1.0-py3-none-any.whl` successfully.
- Wheel SHA-256: `7a1fb627c818c16c95455552b8ff93aa2a01520b660a2a661639d881c85f3aa1`.
- Evidence import, graph diff, viewer assets, metadata, and CLI entry points were present among 28
  wheel entries.
- Installing the final wheel into a clean virtual environment and running `scan`, `impact`,
  `diff --check`, and `status` on the configured fixture succeeded with 12 nodes, 13 relationships,
  six generated notes, a zero-change diff, and 0 durable orphans.

## Dependency and network note

- Phase 4 adds no dependency and does not change dependency declarations.
- XML parsing uses the standard library only after enforcing file-size limits and rejecting
  DTD/entity declarations; the two exact Bandit false-positive sites carry scoped suppressions.
- Local dependency integrity, lint, syntax, and source security checks passed.
- No networked audit was run because network access requires explicit approval.

## Remaining risks

- The initial importers support Cobertura-compatible and JUnit XML only; LCOV, JaCoCo-specific
  semantics, native Go formats, and other report adapters remain future work.
- File mapping intentionally requires one conservative project-relative match, so ambiguous or
  tool-specific source roots may omit evidence instead of guessing.
- Aggregate evidence does not preserve individual test names, stack traces, logs, branch coverage,
  or threshold policy; CI remains responsible for generating and enforcing those reports.
- Large graph diffs include full changed node/edge objects and may need a streaming or summary-only
  mode at higher scale.
- The Phase 4 commit link will be added after the phase is recorded in Git and becomes visible on
  the next repository scan.
