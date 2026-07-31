---
id: ISSUE-003
type: issue
status: complete
phase: 4
---
# ISSUE-003 — Implement evidence imports and graph diff

Implement ADR-005 while preserving the local-first trust boundary and deterministic graph model.

## Acceptance checklist

- [x] Safe report configuration and path validation implemented.
- [x] Cobertura and JUnit aggregation implemented with bounded metadata.
- [x] Deterministic graph diff schema and CLI workflow implemented.
- [x] Generated vault and local viewer expose imported evidence.
- [x] Malformed, private, external, oversized, and entity-bearing inputs are covered by tests.
- [x] Complete phase quality gates, Evidence, and Review pass.

## Planned implementation links

- implemented-by:: [[src - intentatlas - evidence.py|src/intentatlas/evidence.py]]
- implemented-by:: [[src - intentatlas - graph_diff.py|src/intentatlas/graph_diff.py]]
- implemented-by:: [[src - intentatlas - config.py|src/intentatlas/config.py]]
- implemented-by:: [[src - intentatlas - cli.py|src/intentatlas/cli.py]]

## Context

- Requirement: REQ-005 (linked through ADR-005)
- Decision: ADR-005 (available through the incoming `tracked-by` relationship)
- Evidence: [[Evidence/EVD-005 - Phase 4 evidence import and graph diff verification]]
- Review: [[Reviews/Phase 4 Evidence Import and Graph Diff Review]]
