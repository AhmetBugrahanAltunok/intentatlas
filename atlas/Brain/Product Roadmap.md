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

## Phase 5 — Go and external delivery inputs

Status: planned

- Add Go as the next language adapter.
- Add optional issue and pull-request inputs through explicit local data sources.
- Select Rust or Java next according to demand and fixture quality.

## Phase 6 — Product experience and scale

Status: planned

- Improve graph navigation, filtering, relationship paths, and large-graph performance.
- Add change-risk and evidence-gap explanations.

## Phase 7 — Open-source release readiness

Status: planned

- Add public real-world fixtures and cross-platform end-to-end tests.
- Verify packaging, release documentation, attribution, and reproducible release checks.

## Completion rule

Every phase must end with a linked Evidence note and Review note containing the full change
inventory, test results, acceptance decision, and remaining risks. A failing or incomplete gate
keeps the phase open.
