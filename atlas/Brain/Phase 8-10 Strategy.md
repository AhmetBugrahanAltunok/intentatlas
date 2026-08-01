---
id: phase-8-10-strategy
type: memory
status: active
---
# Phase 8–10 Strategy

This strategy extends [[Brain/Product Roadmap]] without changing the vault-first product contract.
Markdown and wikilinks remain portable source material; caches, indexes, reports, and generated
notes remain rebuildable.

## Product target

Given a revision-scoped change, explain which requirements may be affected and which tests are
worth running. Every claim must expose its evidence and uncertainty. Missing evidence must produce
an explicit fallback or abstention, never invented certainty.

## Phase 8 — Trustworthy change intelligence

Deliver [[Requirements/REQ-020 - Explain revision-scoped change confidence]] through
[[Decisions/ADR-020 - Separate exact change evidence from fallback]] and
[[Issues/ISSUE-018 - Implement trustworthy change intelligence]].

1. Start every new user vault with generic guidance and templates, not IntentAtlas's own product
   requirements, decisions, evidence, reviews, or dated sessions.
2. Normalize commit, `base..head`, staged, and worktree input into one bounded change-set model.
3. Improve JavaScript/TypeScript and Go symbol spans and exact test evidence. A file relationship
   must not become medium-confidence proof for an unrelated symbol in that file.
4. Record analysis state (`analyzed`, `fallback`, or `unknown`) and evidence provenance, revision,
   scope, confidence, and freshness.
5. Produce a dedicated requirement-impact and test-recommendation report. When completeness is
   unknown, abstain or recommend a clearly labeled full-test fallback.
6. Expand holdout cases with same-file multi-symbol changes, renames, deletions, configuration,
   reflection, dynamic imports, and the independent `auth.py` / REQ-9 / REQ-18 scenario.

Exit requires the full [[Brain/Phase Completion Protocol]], including focused and complete tests,
quality/security checks, CLI and viewer E2E, deterministic output, acceptance evidence, and a final
review. Until then Phase 8 remains open.

## Phase 9 — Pull-request and CI evidence loop

1. Add `intentatlas review --base <revision> --head <revision>`.
2. Emit deterministic Markdown and JSON, plus bounded SARIF for CI annotations.
3. Provide a read-only GitHub Action in opt-in shadow mode before any blocking policy.
4. Import actual test results keyed by commit and freshness; compare prediction with outcome.
5. Add a change-centric viewer and validate the workflow in representative pilot repositories.

Target release: `0.2.0-beta` after all Phase 9 gates pass.

## Phase 10 — Scale and open evidence ecosystem

1. Add content-hash incremental scans and atomic graph snapshots or a derived SQLite/sharded index.
2. Preserve rename/move aliases and make generated vault materialization optional at large scale.
3. Import SCIP, SARIF, and per-test execution maps behind bounded local parsers.
4. Publish an adapter conformance contract without weakening built-in conservative semantics.
5. Move large-graph viewer work to bounded subgraphs and background computation or canvas.
6. Add property/fuzz tests, browser E2E, static typing, SHA-pinned Actions, artifact provenance,
   and approval-gated trusted publishing.

Target release: `0.3.0` after all Phase 10 gates pass. A `1.0` release waits for sustained pilot
evidence, documented compatibility guarantees, and a stable extension contract.

## Non-goals

- No claim of perfect impact analysis or complete test selection.
- No execution of scanned projects during static scanning.
- No mandatory network, hosted account, telemetry, or model API.
- No copying of third-party code, branding, vaults, or repository history.
