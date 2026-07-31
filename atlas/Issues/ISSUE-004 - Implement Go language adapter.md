---
id: ISSUE-004
type: issue
status: complete
phase: 5A
---
# ISSUE-004 — Implement Go language adapter

Implement ADR-006 while preserving the local-first trust boundary, deterministic graph model, and
shared phase-completion gates.

## Acceptance checklist

- [x] Go adapter registered behind the existing immutable adapter contract.
- [x] Go file, `go.mod`, type, function, method, local-import, and test behavior implemented.
- [x] Nested modules, external imports, comments, literals, and deterministic output covered by an
  original redistributable fixture.
- [x] Generated vault, CLI, local viewer, and packaged installation verified end to end.
- [x] Complete phase quality gates, Evidence, and Review pass.

## Planned implementation links

- implemented-by:: [[src - intentatlas - adapters - go.py|src/intentatlas/adapters/go.py]]
- implemented-by:: [[src - intentatlas - adapters - __init__.py|src/intentatlas/adapters/__init__.py]]
- implemented-by:: [[src - intentatlas - scanner.py|src/intentatlas/scanner.py]]
- implemented-by:: [[tests - test_scanner.py|tests/test_scanner.py]]

## Context

- Requirement: REQ-006 (linked through ADR-006)
- Decision: ADR-006 (available through the incoming `tracked-by` relationship)
- Evidence: [[Evidence/EVD-006 - Phase 5A Go adapter verification]]
- Review: [[Reviews/Phase 5A Go Adapter Review]]
