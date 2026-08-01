---
id: ISSUE-016
type: issue
status: closed
phase: 7C
---
# ISSUE-016 — Implement bounded symbol-aware test evidence

Implement ADR-018 without executing project code or weakening the advisory and trust boundaries.

## Acceptance checklist

- [x] Python explicit imports, qualified attributes, and bounded re-exports create exact symbol
  evidence.
- [x] Nested symbol ownership focuses an available owner-named test.
- [x] JavaScript/TypeScript named and default static imports create exact symbol evidence.
- [x] Exact-symbol dependency propagation is limited to one production hop and bounded fan-out.
- [x] Latest dated co-change evidence is separate, bounded, and explainable.
- [x] Independent regressions cover re-export, owner focus, one-hop dependency, co-change, and
  bound failure.
- [x] The 18-case benchmark reaches TP 23, FP 0, FN 0 at medium confidence without label changes.
- [x] Complete quality, security, package, CLI/UI, determinism, attribution, and vault gates pass.
- [x] Evidence and final review record exact results and remaining risks.

## Planned implementation links

- implemented-by:: [[src - intentatlas - adapters - python.py|src/intentatlas/adapters/python.py]]
- implemented-by:: [[src - intentatlas - adapters - javascript.py|src/intentatlas/adapters/javascript.py]]
- implemented-by:: [[src - intentatlas - recommendations.py|src/intentatlas/recommendations.py]]
- implemented-by:: [[tests - test_scanner.py|tests/test_scanner.py]]
- implemented-by:: [[tests - test_recommendations.py|tests/test_recommendations.py]]

## Context

- Requirement: REQ-018 (linked through ADR-018)
- Decision: ADR-018 (available through the incoming `tracked-by` relationship)
- Evidence: [[Evidence/EVD-018 - Phase 7C symbol-aware dependency verification]]
- Review: [[Reviews/Phase 7C Symbol-Aware Dependency Review]]
