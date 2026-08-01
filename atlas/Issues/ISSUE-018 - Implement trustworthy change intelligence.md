---
id: ISSUE-018
type: issue
status: closed
phase: 8
---
# ISSUE-018 — Implement trustworthy change intelligence

Implement [[Decisions/ADR-020 - Separate exact change evidence from fallback]] for
[[Requirements/REQ-020 - Explain revision-scoped change confidence]].

## Acceptance checklist

- [x] Fresh vault initialization is generic, minimal, deterministic, and preserves user edits.
- [x] Same-file JavaScript/TypeScript and Go symbol cases do not create default false positives.
- [x] Commit, range, staged, and worktree changes share one bounded change-set model.
- [x] Analysis completeness and evidence provenance/revision/scope/freshness are explicit.
- [x] Requirement-impact and test reports support honest abstention and full-test fallback.
- [x] Adversarial holdout and pinned public-project benchmarks pass.
- [x] Focused and complete tests, coverage, lint, security, CLI/UI E2E, determinism, and vault
  closure gates pass and are recorded.

## Planned implementation links

- implemented-by:: [[src - intentatlas - vault.py|src/intentatlas/vault.py]]
- implemented-by:: [[src - intentatlas - change_set.py|src/intentatlas/change_set.py]]
- implemented-by:: [[src - intentatlas - change_analysis.py|src/intentatlas/change_analysis.py]]
- implemented-by:: [[src - intentatlas - change_report.py|src/intentatlas/change_report.py]]
- implemented-by:: [[src - intentatlas - recommendations.py|src/intentatlas/recommendations.py]]
- implemented-by:: [[src - intentatlas - adapters - go.py|src/intentatlas/adapters/go.py]]
- verified-by:: [[tests - test_vault.py|tests/test_vault.py]]
- verified-by:: [[tests - test_change_set.py|tests/test_change_set.py]]
- verified-by:: [[tests - test_change_analysis.py|tests/test_change_analysis.py]]
- verified-by:: [[tests - test_change_report.py|tests/test_change_report.py]]
- verified-by:: [[tests - test_scanner.py|tests/test_scanner.py]]
- verified-by:: [[tests - test_recommendations.py|tests/test_recommendations.py]]
- verified-by:: [[Evidence/EVD-020 - Phase 8 trustworthy change intelligence verification]]

## Context

- Strategy: [[Brain/Phase 8-10 Strategy]]
- Kickoff: [[Sessions/2026-08-01 - Phase 8 kickoff]]
