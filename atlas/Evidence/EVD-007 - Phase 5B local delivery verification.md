---
id: EVD-007
type: evidence
status: verified
phase: 5B
verified_on: 2026-07-31
---
# Phase 5B local delivery verification

- proves:: [[Requirements/REQ-007 - Import local delivery context]]
- references:: [[Decisions/ADR-007 - Explicit local delivery snapshots]]
- references:: [[Issues/ISSUE-005 - Implement local delivery imports]]
- references:: [[Brain/Phase Completion Protocol]]

## Change inventory

- Added bounded `delivery_reports` configuration and an offline schema-1 JSON importer.
- Added path confinement, Private/symlink/size rejection, strict UTF-8 JSON, duplicate-key and
  unknown-field rejection, record/link/list/string bounds, identifier/state validation, and plain
  HTTP(S) URL validation without credentials, queries, or fragments.
- Added deterministic delivery-issue and pull-request nodes retaining only bounded metadata. Bodies,
  comments, reviews, authors, logs, tokens, raw payloads, and unmatched paths are not persisted.
- Added exact `tracked-by`, `addressed-by`, `changes`, and known-commit `references` relationships.
- Added relation schema 2 with invertible `addressed-by`/`addresses` semantics.
- Routed generated delivery notes below `Commits/Issues/` and `Commits/Pull Requests/`, added viewer
  layers, an original fixture, schema documentation, and English/Turkish product guidance.
- Linked Phase 5A evidence to commit `88fb6ce`.

## Focused verification

- `python -m pytest tests/test_delivery.py tests/test_config.py tests/test_graph.py
  tests/test_relations.py tests/test_vault.py tests/test_viewer.py`: 30 passed.
- Coverage includes deterministic import, exact intent/issue/file/commit links, omitted unknown
  references, nested generated-note cleanup, unsafe/missing/Private/symlink paths, duplicate keys,
  unknown fields, invalid schema/types/URLs, byte bounds, configuration, relation schema, and viewer
  assets.

## Complete quality suite

- `python -m pytest`: 58 passed.
- Branch-aware coverage: 88.18% overall; delivery importer 89%.
- `python -m ruff check .`: all checks passed.
- `python -m bandit -q -r src`: no findings.
- `python -m pip check`: no broken requirements.
- `node --check src/intentatlas/web/app.js`: passed.
- `git diff --check`: passed.

## CLI and graphical acceptance

- An isolated configured snapshot scanned to 11 nodes, 13 relationships, four generated notes,
  and 0 durable orphans.
- CLI impact traversed REQ-DELIVERY → delivery issue → pull request → changed file → symbol with
  typed relation categories and `delivery-json` provenance.
- Generated issue and pull-request notes appeared in their nested `Commits/` subfolders and
  remained deterministic across repeated syncs.
- The loopback viewer displayed separate delivery-issue and pull-request layers. PR details showed
  source/repository/state/draft/report metadata, inverse `addresses`, and outgoing `changes`.
  Issue details showed bounded labels, inverse `tracks`, and outgoing `addressed-by`.
- Browser console warnings/errors: none.

## Packaging acceptance

- Built `intentatlas-0.1.0-py3-none-any.whl` with 30 entries.
- SHA-256: `05d6c063ee75c1aa050abc8ab26cfbb6cbdc96818f8ad97fb5facf200742f73b`.
- The wheel contains `intentatlas/delivery.py`, viewer assets, metadata, and the CLI entry point.
- Clean `--no-index --no-deps` installation reproduced the isolated 11-node, 13-relationship,
  0-orphan graph and the typed CLI impact chain.

## Repository and determinism acceptance

- Two final clean scans produced 418 nodes, 695 relationships, 380 generated notes, and 0 durable
  orphans. Their graph diff reported `has_changes: false`.
- SHA-256 tree digests confirmed `user_notes_preserved=True` and
  `generated_notes_deterministic=True` across the unchanged scan.
- One scan encountered a transient Windows lock on an Obsidian-open generated note; it was rejected
  as evidence. The immediate clean rerun succeeded, and final determinism uses only clean scans.
- No network, credential, push, publication, deployment, or external repository action occurred.

## Remaining risks

- Snapshots are user/CI-produced and can become stale; IntentAtlas validates structure, not remote
  truth or authorization.
- Direct provider connectors, authentication, pagination, rate limits, and webhook freshness remain
  outside this phase and require explicit approval.
- Relation-schema-1 graph caches require a new scan before status, impact, or diff operations.
- Cross-report duplicates intentionally fail by graph identity collision rather than merging
  potentially inconsistent snapshots.
- Review state, checks, reviewers, milestones, assignees, and discussion content are intentionally
  absent from schema 1.
- The Phase 5B commit link will be added after Git records this phase.
