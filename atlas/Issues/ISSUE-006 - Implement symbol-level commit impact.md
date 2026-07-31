---
id: ISSUE-006
type: issue
status: complete
phase: 6A
---
# ISSUE-006 — Implement symbol-level commit impact

Implement ADR-008 without removing file-level history, executing project code, adding network
access, or treating inferred impact as fact.

## Acceptance checklist

- [x] Python symbols publish validated inclusive source spans.
- [x] Bounded Git hunk collection and deterministic parser are implemented.
- [x] Historical hunks are projected only when the current file matches the commit blob.
- [x] Blob checks are bounded and limited to adapters with trusted spans.
- [x] Exact most-specific symbol projection and typed relation are implemented.
- [x] Ambiguous, deleted, unsupported, malformed, and excessive inputs fall back safely.
- [x] Cache, CLI, vault, viewer, documentation, and migration behavior are verified.
- [x] Complete CLI/UI, package, determinism, Evidence, and Review gates pass.

## Planned implementation links

- implemented-by:: [[src - intentatlas - adapters - python.py|src/intentatlas/adapters/python.py]]
- implemented-by:: [[src - intentatlas - git_history.py|src/intentatlas/git_history.py]]
- implemented-by:: [[src - intentatlas - scanner.py|src/intentatlas/scanner.py]]
- implemented-by:: [[src - intentatlas - relations.py|src/intentatlas/relations.py]]
- implemented-by:: [[tests - test_git_history.py|tests/test_git_history.py]]
- implemented-by:: [[tests - test_scanner.py|tests/test_scanner.py]]

## Context

- Requirement: REQ-008 (linked through ADR-008)
- Decision: ADR-008 (available through the incoming `tracked-by` relationship)
- Planned evidence: [[Evidence/EVD-008 - Phase 6A symbol impact verification]]
- Planned review: [[Reviews/Phase 6A Symbol Impact Review]]
