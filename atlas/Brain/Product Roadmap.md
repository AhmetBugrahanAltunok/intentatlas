---
id: product-roadmap
type: memory
status: active
---
# Product Roadmap

> **Canonical roadmap:** this is the active source for delivery phases and their completion
> status. The repository-root [Legacy Technical Roadmap](../../ROADMAP.md) is retained only as
> a historical 0.1–0.3 planning snapshot.

IntentAtlas is developed in independently verifiable phases. A phase is complete only after
the [[Brain/Phase Completion Protocol]] is satisfied and its evidence and review are linked.

The product continues to serve [[Requirements/REQ-001 - Explain change impact]] while remaining
independent, MIT-licensed, local-first, and vault-first.

## Phase 1 — Trustworthy foundation

Status: complete (2026-07-30)

- Requirement: [[Requirements/REQ-002 - Harden trust boundaries]]
- Decision: [[Decisions/ADR-002 - Pruned trust-boundary traversal]]
- Evidence: [[Evidence/EVD-002 - Phase 1 foundation verification]]
- Review: [[Reviews/Phase 1 Foundation Review]]
- Outcome: scanning and graph exploration honor the documented trust boundary and work reliably.

## Phase 2 — Typed intent chain

Status: complete (2026-07-30)

- Express Requirement → Decision → Issue → Code → Test → Evidence → Commit with typed relations.
- Add schema evolution and clearer impact explanations.
- Requirement: [[Requirements/REQ-003 - Trace a typed intent chain]]
- Decision: [[Decisions/ADR-003 - Typed relation vocabulary]]
- Delivery issue: [[Issues/ISSUE-001 - Implement typed intent chain]]
- Evidence: [[Evidence/EVD-003 - Phase 2 typed chain verification]]
- Review: [[Reviews/Phase 2 Typed Intent Chain Review]]
- Outcome: intent, delivery, implementation, verification, evidence, history, and structure
  relationships have stable forward/inverse semantics across the cache, CLI, vault, and viewer.

## Phase 3 — Adapter platform and TypeScript/JavaScript

Status: complete (2026-07-31)

- Establish a deterministic, typed language-adapter contract.
- Move Python structural analysis behind the same contract without regressions.
- Add TypeScript, JavaScript, TSX, and JSX file, symbol, import, and test relationships.
- Requirement: [[Requirements/REQ-004 - Trace TypeScript and JavaScript structure]]
- Decision: [[Decisions/ADR-004 - Built-in language adapter contract]]
- Delivery issue: [[Issues/ISSUE-002 - Implement TypeScript and JavaScript adapter]]
- Strategy: [[Brain/Language Adapter Strategy]]
- Evidence: [[Evidence/EVD-004 - Phase 3 TypeScript and JavaScript verification]]
- Review: [[Reviews/Phase 3 TypeScript and JavaScript Review]]
- Outcome: Python and TypeScript/JavaScript now share one bounded, deterministic adapter contract;
  TS, TSX, JS, and JSX structure is navigable across the cache, CLI, vault, and viewer.

## Phase 4 — Evidence import and CI graph diff

Status: complete (2026-07-31)

- Import coverage and test-result evidence without executing project code.
- Produce a stable graph diff format for CI.
- Requirement: [[Requirements/REQ-005 - Import verification evidence and compare graph changes]]
- Decision: [[Decisions/ADR-005 - Bounded evidence imports and canonical graph diff]]
- Delivery issue: [[Issues/ISSUE-003 - Implement evidence imports and graph diff]]
- Evidence: [[Evidence/EVD-005 - Phase 4 evidence import and graph diff verification]]
- Review: [[Reviews/Phase 4 Evidence Import and Graph Diff Review]]
- Outcome: existing Cobertura and JUnit reports become bounded per-file evidence, while CI can
  consume a deterministic, timestamp-free graph diff without IntentAtlas running project code.

## Phase 5A — Go language adapter

Status: complete (2026-07-31)

- Add deterministic Go file, symbol, module-local import, and test relationships.
- Requirement: [[Requirements/REQ-006 - Trace Go structure]]
- Decision: [[Decisions/ADR-006 - Conservative Go module projection]]
- Delivery issue: [[Issues/ISSUE-004 - Implement Go language adapter]]
- Strategy: [[Brain/Language Adapter Strategy]]
- Evidence: [[Evidence/EVD-006 - Phase 5A Go adapter verification]]
- Review: [[Reviews/Phase 5A Go Adapter Review]]
- Outcome: Go files, `go.mod` module boundaries, named types, functions, methods, local package
  imports, and tests are navigable through the same offline deterministic graph contract.

## Phase 5B — External delivery inputs

Status: complete (2026-07-31)

- Add optional issue and pull-request inputs through explicit local JSON snapshots.
- Requirement: [[Requirements/REQ-007 - Import local delivery context]]
- Decision: [[Decisions/ADR-007 - Explicit local delivery snapshots]]
- Delivery issue: [[Issues/ISSUE-005 - Implement local delivery imports]]
- Evidence: [[Evidence/EVD-007 - Phase 5B local delivery verification]]
- Review: [[Reviews/Phase 5B Local Delivery Review]]
- Preserve offline operation and require explicit configuration for every external data source.
- Select Rust or Java next according to demand and fixture quality after delivery inputs are
  bounded and verified.
- Outcome: explicit local snapshots connect intent, issues, pull requests, files, and known commits
  through a bounded offline delivery graph.

## Phase 6A — Symbol-level change impact foundation

Status: complete (2026-07-31)

- Map bounded Git diff hunks to exact symbols when the current language adapter exposes a
  trustworthy source span.
- Preserve file-level change relationships as a conservative fallback instead of guessing.
- Requirement: [[Requirements/REQ-008 - Trace symbol-level commit impact]]
- Decision: [[Decisions/ADR-008 - Conservative diff-to-symbol projection]]
- Delivery issue: [[Issues/ISSUE-006 - Implement symbol-level commit impact]]
- Evidence: [[Evidence/EVD-008 - Phase 6A symbol impact verification]]
- Review: [[Reviews/Phase 6A Symbol Impact Review]]
- Outcome: recent commits retain complete file history and gain direct `modifies` evidence for
  the most-specific changed Python symbols when bounded new-side hunks intersect validated AST
  spans; uncertain cases remain safely at file level.

## Phase 6B1 — Explainable test recommendations

Status: complete (2026-08-01)

- Rank direct test candidates from verified symbol and file-change evidence.
- Expose fixed confidence levels, evidence paths, filtering, and deterministic text/JSON output
  without treating inferred test necessity as fact.
- Requirement: [[Requirements/REQ-009 - Recommend tests with explainable confidence]]
- Decision: [[Decisions/ADR-009 - Evidence-ranked test recommendations]]
- Delivery issue: [[Issues/ISSUE-007 - Implement explainable test recommendations]]
- Evidence: [[Evidence/EVD-009 - Phase 6B1 test recommendation verification]]
- Review: [[Reviews/Phase 6B1 Test Recommendation Review]]
- Outcome: commits, files, and symbols now produce bounded, deterministic test candidates with
  inspectable confidence, evidence, and paths while explicitly preserving uncertainty.

## Phase 6B2A — Resilient generated vault synchronization

Status: complete (2026-08-01)

- Preserve the last complete generated vault when a transient or persistent file lock interrupts
  synchronization.
- Avoid rewriting byte-identical generated notes and remove stale notes only after desired output
  is safely in place.
- Requirement: [[Requirements/REQ-010 - Preserve generated vault integrity during synchronization]]
- Decision: [[Decisions/ADR-010 - Failure-preserving atomic vault synchronization]]
- Delivery issue: [[Issues/ISSUE-008 - Implement resilient generated vault synchronization]]
- Evidence: [[Evidence/EVD-010 - Phase 6B2A vault synchronization verification]]
- Review: [[Reviews/Phase 6B2A Vault Synchronization Review]]
- Outcome: generated notes now refresh through failure-preserving atomic replacement; unchanged
  scans avoid rewrites and a locked file cannot trigger a destructive purge.

## Phase 6B2B1 — Labeled recommendation evaluation

Status: complete (2026-08-01)

- Add a deterministic offline evaluator for exhaustive human-labeled test sets.
- Record an honest self-hosted IntentAtlas baseline before widening dependency propagation.
- Requirement: [[Requirements/REQ-011 - Measure test recommendation quality]]
- Decision: [[Decisions/ADR-011 - Closed-world recommendation evaluation]]
- Delivery issue: [[Issues/ISSUE-009 - Implement labeled recommendation evaluation]]
- Evidence: [[Evidence/EVD-011 - Phase 6B2B1 recommendation evaluation verification]]
- Review: [[Reviews/Phase 6B2B1 Recommendation Evaluation Review]]
- Outcome: strict local labels now measure the unchanged production recommendation query with
  deterministic TP, FP, FN, precision, and recall; the first reviewed baseline exposes the real
  precision/recall tradeoff without claiming general accuracy.

## Phase 6B2B2A — Cross-project recommendation benchmarks

Status: complete (2026-08-01)

- Compare low, medium, and high confidence across a bounded local corpus without changing scores.
- Add original, independently labeled Python, TypeScript, and Go graph scenarios as deterministic
  regression fixtures, not as real-world accuracy evidence.
- Requirement: [[Requirements/REQ-012 - Compare recommendation quality across projects]]
- Decision: [[Decisions/ADR-012 - Aggregate independent closed-world benchmarks]]
- Delivery issue: [[Issues/ISSUE-010 - Implement cross-project recommendation benchmarks]]
- Evidence: [[Evidence/EVD-012 - Phase 6B2B2A cross-project benchmark verification]]
- Review: [[Reviews/Phase 6B2B2A Cross-Project Benchmark Review]]
- Outcome: a strict local corpus now compares low, medium, and high thresholds across original
  Python, TypeScript, and Go graph scenarios while keeping real-world validity explicitly open.

## Phase 6B2B2B — Recommendation scale and richer paths

Status: planned

- Add public real-world benchmark repositories after license and network review.
- Add indexed graph traversal, large-repository performance gates, richer viewer paths, and
  generated output policies that further reduce Git noise.

## Phase 7 — Open-source release readiness

Status: planned

- Add public real-world fixtures and cross-platform end-to-end tests.
- Verify packaging, release documentation, attribution, and reproducible release checks.

## Completion rule

Every phase must end with a linked Evidence note and Review note containing the full change
inventory, test results, acceptance decision, and remaining risks. A failing or incomplete gate
keeps the phase open.
