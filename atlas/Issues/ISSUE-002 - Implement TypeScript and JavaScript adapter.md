---
id: ISSUE-002
type: issue
status: complete
phase: 3
---
# ISSUE-002 — Implement TypeScript and JavaScript adapter

Implement ADR-004 without weakening the scanner trust boundary or changing existing Python graph
semantics.

## Acceptance checklist

- [x] Common adapter contract and deterministic merge implemented.
- [x] Python analysis moved behind the contract with regression parity.
- [x] TypeScript/JavaScript symbols, local imports, re-exports, and test links implemented.
- [x] Conservative parsing, size limits, and non-execution boundaries covered by tests.
- [x] CLI, vault, and viewer workflows verified with a mixed-language fixture.
- [x] Complete phase quality gates, Evidence, and Review pass.

## Planned implementation links

- implemented-by:: [[src - intentatlas - adapters - base.py|src/intentatlas/adapters/base.py]]
- implemented-by:: [[src - intentatlas - adapters - python.py|src/intentatlas/adapters/python.py]]
- implemented-by:: [[src - intentatlas - adapters - javascript.py|src/intentatlas/adapters/javascript.py]]

## Context

- Requirement: REQ-004 (linked through ADR-004)
- Decision: ADR-004 (available through the incoming `tracked-by` relationship)
- Evidence: [[Evidence/EVD-004 - Phase 3 TypeScript and JavaScript verification]]
- Review: [[Reviews/Phase 3 TypeScript and JavaScript Review]]
