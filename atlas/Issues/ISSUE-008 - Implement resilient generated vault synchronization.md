---
id: ISSUE-008
type: issue
status: closed
phase: 6B2A
---
# ISSUE-008 — Implement resilient generated vault synchronization

Implement ADR-010 without changing the ownership boundary between user-authored and generated
vault areas.

## Acceptance checklist

- [x] Purge-before-write behavior is removed.
- [x] Desired notes are rendered before filesystem mutation.
- [x] Identical notes are not rewritten.
- [x] Changed notes use cleaned-up same-directory temporary files and atomic replacement.
- [x] Transient replace and delete locks retry within a fixed bound.
- [x] Persistent replacement failure preserves the previous target and skips stale cleanup.
- [x] Stale cleanup removes only marked generated notes after desired writes succeed.
- [x] Symlinks, manual notes, user-owned areas, and `atlas/Private/` remain protected.
- [x] Architecture, security, changelog, roadmap, Evidence, and Review are updated.
- [x] Focused and complete CLI/UI, package, determinism, and security gates pass.

## Planned implementation links

- implemented-by:: [[src - intentatlas - vault.py|src/intentatlas/vault.py]]
- implemented-by:: [[tests - test_vault.py|tests/test_vault.py]]

## Context

- Requirement: REQ-010 (linked through ADR-010)
- Decision: ADR-010 (available through the incoming `tracked-by` relationship)
- Planned evidence: [[Evidence/EVD-010 - Phase 6B2A vault synchronization verification]]
- Planned review: [[Reviews/Phase 6B2A Vault Synchronization Review]]
