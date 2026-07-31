---
id: ISSUE-009
type: issue
status: closed
phase: 6B2B1
---
# ISSUE-009 — Implement labeled recommendation evaluation

Implement ADR-011 as a bounded, deterministic, offline evaluator over the existing recommendation
engine.

## Acceptance checklist

- [x] Schema-1 complete-test-set labels are strictly parsed and bounded.
- [x] Paths, symlinks, duplicate keys, duplicate cases, unknown fields, and graph identities are
  validated without reading `atlas/Private/`.
- [x] Per-case TP, FP, FN, precision, recall, and ranked recommendations are deterministic.
- [x] Micro totals use summed counts and undefined metrics remain explicit.
- [x] CLI supports confidence, limit, text, and JSON output without executing tests.
- [x] A reviewed IntentAtlas label file and baseline results are committed.
- [x] README, architecture, security, changelog, roadmap, Evidence, and Review are updated.
- [x] Focused and complete CLI/UI, package, determinism, and security gates pass.

## Planned implementation links

- implemented-by:: [[src - intentatlas - evaluation.py|src/intentatlas/evaluation.py]]
- implemented-by:: [[src - intentatlas - cli.py|src/intentatlas/cli.py]]
- implemented-by:: [[tests - test_evaluation.py|tests/test_evaluation.py]]
- implemented-by:: [[benchmarks - intentatlas-recommendations.json|benchmarks/intentatlas-recommendations.json]]

## Context

- Requirement: REQ-011 (linked through ADR-011)
- Decision: ADR-011 (available through the incoming `tracked-by` relationship)
- Planned evidence: [[Evidence/EVD-011 - Phase 6B2B1 recommendation evaluation verification]]
- Planned review: [[Reviews/Phase 6B2B1 Recommendation Evaluation Review]]
