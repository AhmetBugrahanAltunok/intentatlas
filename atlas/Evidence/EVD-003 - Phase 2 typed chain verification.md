---
id: EVD-003
type: evidence
status: verified
phase: 2
verified_on: 2026-07-30
---
# Phase 2 typed chain verification

This evidence verifies the Phase 2 requirement and decision under the completion protocol.

- proves:: [[Requirements/REQ-003 - Trace a typed intent chain]]
- references:: [[Decisions/ADR-003 - Typed relation vocabulary]]
- references:: [[Brain/Phase Completion Protocol]]
- references:: [[Issues/ISSUE-001 - Implement typed intent chain]]

## Change inventory

- Added a deterministic ten-relation catalog with inverse labels, categories, descriptions, and
  an allowlist for author-written typed links.
- Advanced the graph cache to schema 2 with embedded relation metadata while retaining safe
  schema-1 loading and validating inconsistent cached metadata.
- Added `relation:: [[target]]` parsing; unknown author labels safely remain generic references.
- Added user-owned `Issues/` ingestion, an Issue template, graph styling, and vault ownership
  documentation.
- Updated the CLI, generated Obsidian notes, and local viewer to explain forward and reverse
  traversal using relation, inverse, category, and provenance.
- Added REQ-003, ADR-003, ISSUE-001, this evidence record, the phase review, and the saved language
  adapter sequence: TypeScript/JavaScript, Go, then Rust or Java according to demand.
- Updated English and Turkish readmes, architecture, security guidance, roadmap, changelog, and
  agent boundaries.

## Focused regression verification

- Command: `python -m pytest tests/test_relations.py tests/test_graph.py tests/test_scanner.py tests/test_cli.py tests/test_vault.py tests/test_viewer.py`
- Result: 23 passed.
- Dedicated tests cover catalog ordering and invertibility, schema-1 migration, schema-2 metadata
  validation, typed Markdown parsing, unknown-label fallback, issue preservation, inverse CLI and
  vault rendering, and packaged viewer behavior.

## Complete quality suite

- `python -m pytest`: 30 passed.
- `python -m pytest --cov=intentatlas --cov-report=term-missing --cov-fail-under=80`:
  30 passed, 86.51% branch-aware coverage.
- `python -m ruff check .`: all checks passed.
- `python -m bandit -q -r src`: no findings.
- `python -m pip check`: no broken requirements.
- `node --check src/intentatlas/web/app.js`: JavaScript syntax passed.
- `git diff --check`: passed.

## Repository, graph, and CLI acceptance

- Existing schema-1 cache loaded successfully before the real scan; the next scan emitted schema 2
  and relation-schema version 1 with all ten relation definitions.
- Pre-closing repository scan: 193 nodes, 290 relationships, and 177 generated notes.
- Final repository scan after adding this Evidence and its Review: 195 nodes, 304 relationships,
  and 177 generated notes.
- Graph health: 0 orphaned durable notes.
- The final scan preserved all 18 user-owned notes byte-for-byte.
- A second unchanged scan rewrote 0 of 178 generated files; after excluding the allowed
  `generated_at` timestamp, the serialized graph was byte-for-byte equivalent.
- `intentatlas impact REQ-003 --depth 3` traversed `drives` to ADR-003, `tracked-by` to ISSUE-001,
  and `implemented-by` to the four implementation files while reporting category and provenance.
- Generated code notes render incoming `implements` relationships with implementation category and
  wikilink evidence.
- Path-level inspection confirmed that neither `atlas/Private/` nor the ignored repository-root
  `.obsidian/` appears in the graph.

## Local graphical acceptance

- The loopback viewer first loaded the 193-node, 290-relationship pre-closing graph successfully.
- Search selected REQ-003, and the detail workflow traversed REQ-003 → ADR-003 → ISSUE-001 →
  `src/intentatlas/relations.py`.
- Details showed `drives`/`driven-by`, `tracked-by`/`tracks`, and
  `implemented-by`/`implements` with the expected categories and evidence sources.
- The Issue node appeared as a first-class accessible graph node.
- The final 195-node, 304-relationship graph then loaded successfully; search selected EVD-003
  and its detail panel showed `proves` → REQ-003 with evidence category and wikilink provenance.
- No browser console warnings or errors were reported in either run.

## Packaging and clean-install acceptance

- `python -m pip wheel . --no-deps --no-build-isolation` built
  `intentatlas-0.1.0-py3-none-any.whl` successfully.
- Wheel SHA-256: `e1dcf025f5495649c596774ca6834274bfeecf5bda9ac5dcf2e9c3a698cd3163`.
- All required typed-relation modules, viewer assets, metadata, and CLI entry points were present
  among 22 wheel entries.
- Installing the wheel into a clean virtual environment and running `init`, `scan`, and `status`
  succeeded with 6 nodes, 9 relationships, and 0 durable orphans.

## Dependency and network note

- Phase 2 adds no dependency and does not change dependency declarations.
- Local dependency integrity and source security checks passed.
- No new networked audit was run because network access requires explicit approval; the Phase 1
  audit remains the latest approved network result.

## Remaining risks

- The relation vocabulary validates semantics but does not yet constrain allowed endpoint-kind
  combinations.
- Coverage and imported test-result evidence remain Phase 3 work.
- Large-graph filtering, path exploration, and performance work remain Phase 4 scope.
- This evidence is not linked to a Phase 2 commit until the owner authorizes creating that commit.
