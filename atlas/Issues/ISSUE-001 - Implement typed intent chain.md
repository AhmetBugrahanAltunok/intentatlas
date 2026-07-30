---
id: ISSUE-001
type: issue
status: complete
phase: 2
---
# ISSUE-001 — Implement typed intent chain

Implement the accepted Phase 2 vocabulary, schema migration, Markdown syntax, and user-facing
impact explanations without weakening Phase 1 trust boundaries.

## Acceptance checklist

- [x] Relation catalog and schema migration implemented.
- [x] Typed Markdown links and issue ingestion implemented.
- [x] CLI, generated vault notes, and viewer show inverse/category information.
- [x] Focused and complete verification passes.
- [x] Evidence and review records close the phase.

## Implementation links

- implemented-by:: [[src - intentatlas - relations.py|src/intentatlas/relations.py]]
- implemented-by:: [[src - intentatlas - models.py|src/intentatlas/models.py]]
- implemented-by:: [[src - intentatlas - graph.py|src/intentatlas/graph.py]]
- implemented-by:: [[src - intentatlas - scanner.py|src/intentatlas/scanner.py]]

## Context

- Requirement: REQ-003 (linked through ADR-003)
- Decision: ADR-003 (available through the incoming `tracked-by` relationship)
- Evidence: [[Evidence/EVD-003 - Phase 2 typed chain verification]]
- Review: [[Reviews/Phase 2 Typed Intent Chain Review]]
