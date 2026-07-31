---
id: ISSUE-011
type: issue
status: closed
phase: 6B2B2B1
---
# ISSUE-011 — Implement indexed graph queries and scale benchmark

Implement ADR-013 without changing graph or recommendation semantics.

## Acceptance checklist

- [x] GraphIndex provides deterministic incoming/outgoing and relation-filtered buckets.
- [x] The lazy index is reused and invalidated after edge insertion.
- [x] Degree, orphan, impact, and recommendation queries use the index.
- [x] Existing query and corpus outputs remain byte-compatible.
- [x] Bounded offline scale benchmark exposes cold and warm measurements plus stable result counts.
- [x] README, architecture, security, changelog, roadmap, Evidence, and Review are updated.
- [x] Focused and complete CLI/UI, package, determinism, and security gates pass.

## Planned implementation links

- implemented-by:: [[src - intentatlas - graph.py|src/intentatlas/graph.py]]
- implemented-by:: [[src - intentatlas - recommendations.py|src/intentatlas/recommendations.py]]
- implemented-by:: [[src - intentatlas - scale.py|src/intentatlas/scale.py]]
- implemented-by:: [[tests - test_scale.py|tests/test_scale.py]]

## Context

- Requirement: REQ-013 (linked through ADR-013)
- Decision: ADR-013 (available through the incoming `tracked-by` relationship)
- Evidence: [[Evidence/EVD-013 - Phase 6B2B2B1 indexed query verification]]
- Review: [[Reviews/Phase 6B2B2B1 Indexed Query Review]]
