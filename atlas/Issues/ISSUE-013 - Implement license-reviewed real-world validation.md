---
id: ISSUE-013
type: issue
status: closed
phase: 6B2B2B2B
---
# ISSUE-013 — Implement license-reviewed real-world validation

Implement ADR-015 without weakening local-only scanning, untrusted-input handling, or the existing
MIT attribution boundary.

## Acceptance checklist

- [x] Explicit network approval was received before repository research and acquisition.
- [x] Three small public projects cover Python, JavaScript, and Go under reviewed MIT licenses.
- [x] Repository, commit, checkout cleanliness, and license bytes fail closed.
- [x] The offline evaluator ignores checkout configuration and persists no third-party output.
- [x] Commit, file, and symbol labels were written from bounded manual review.
- [x] Root-level `test.js` discovery found during validation is covered by a focused regression.
- [x] Deterministic low, medium, and high metrics run through the unchanged production query.
- [x] Complete quality, security, package, CLI/UI, attribution, determinism, and vault gates pass.
- [x] Evidence and final review record exact results and remaining risks.

## Planned implementation links

- implemented-by:: [[src - intentatlas - real_world.py|src/intentatlas/real_world.py]]
- implemented-by:: [[src - intentatlas - cli.py|src/intentatlas/cli.py]]
- implemented-by:: [[src - intentatlas - scanner.py|src/intentatlas/scanner.py]]
- implemented-by:: [[tests - test_real_world.py|tests/test_real_world.py]]

## Context

- Requirement: REQ-015 (linked through ADR-015)
- Decision: ADR-015 (available through the incoming `tracked-by` relationship)
- Evidence: [[Evidence/EVD-015 - Phase 6B2B2B2B real-world verification]]
- Review: [[Reviews/Phase 6B2B2B2B Real-World Validation Review]]
