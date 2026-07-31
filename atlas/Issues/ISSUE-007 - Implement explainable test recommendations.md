---
id: ISSUE-007
type: issue
status: closed
phase: 6B1
---
# ISSUE-007 — Implement explainable test recommendations

Implement ADR-009 as a bounded, deterministic, offline query without executing project code or
presenting inferred test necessity as fact.

## Acceptance checklist

- [x] Pure recommendation model and deterministic confidence policy are implemented.
- [x] Commit, file, and symbol targets are supported with safe validation.
- [x] Exact-symbol, file-fallback, filename, and changed-test signals are ranked as documented.
- [x] Deduplication preserves all unique reasons and evidence paths.
- [x] JUnit observations are displayed without changing confidence.
- [x] Text and schema-1 JSON CLI output, confidence filtering, and bounded limits are implemented.
- [x] Unsupported and no-result cases are explicit and non-misleading.
- [x] README, architecture, security, changelog, and roadmap are updated.
- [x] Focused and complete CLI/UI, package, determinism, Evidence, and Review gates pass.

## Planned implementation links

- implemented-by:: [[src - intentatlas - recommendations.py|src/intentatlas/recommendations.py]]
- implemented-by:: [[src - intentatlas - cli.py|src/intentatlas/cli.py]]
- implemented-by:: [[tests - test_recommendations.py|tests/test_recommendations.py]]
- implemented-by:: [[tests - test_cli.py|tests/test_cli.py]]

## Context

- Requirement: REQ-009 (linked through ADR-009)
- Decision: ADR-009 (available through the incoming `tracked-by` relationship)
- Planned evidence: [[Evidence/EVD-009 - Phase 6B1 test recommendation verification]]
- Planned review: [[Reviews/Phase 6B1 Test Recommendation Review]]
