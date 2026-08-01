---
id: ISSUE-014
type: issue
status: closed
phase: 7A
---
# ISSUE-014 — Implement conservative Go symbol test links

Implement ADR-016 without package-wide guessing or execution.

## Acceptance checklist

- [x] Compatible same-package and external-package tests are recognized.
- [x] Only unique exported declarations create `go-symbol-reference` edges.
- [x] Comments, strings, and ambiguous declarations are covered by negative regressions.
- [x] Filename convention remains available as weak fallback evidence.
- [x] The pinned real-world benchmark reaches 100% medium recall for its nine reviewed cases.
- [x] Complete quality, security, package, CLI/UI, determinism, attribution, and vault gates pass.
- [x] Evidence and final review record exact results and remaining risks.

## Planned implementation links

- implemented-by:: [[src - intentatlas - adapters - go.py|src/intentatlas/adapters/go.py]]
- implemented-by:: [[tests - test_adapters.py|tests/test_adapters.py]]
- implemented-by:: [[tests - test_scanner.py|tests/test_scanner.py]]

## Context

- Requirement: REQ-016 (linked through ADR-016)
- Decision: ADR-016 (available through the incoming `tracked-by` relationship)
- Evidence: [[Evidence/EVD-016 - Phase 7A Go symbol-reference verification]]
- Review: [[Reviews/Phase 7A Go Symbol-Reference Review]]
