---
id: ISSUE-019
type: issue
status: closed
phase: 9
---
# ISSUE-019 — Implement CI shadow review loop

Implement [[Decisions/ADR-021 - Compose review formats over trustworthy change reports]] for
[[Requirements/REQ-021 - Review revision ranges in CI shadow mode]].

## Acceptance checklist

- [x] Deterministic `review --base --head` Markdown and JSON reuse Change Report schema 1.
- [x] Bounded SARIF 2.1.0 distinguishes requirement candidates from analysis gaps.
- [x] Opt-in GitHub Action runs locally and read-only in shadow mode without credentials.
- [x] Test results carry commit identity/freshness and prediction-versus-outcome evidence.
- [x] Change-centric viewer and representative pilot workflows pass.
- [x] Focused/full tests, coverage, lint, security, CLI/UI E2E, determinism, and vault closure are
  recorded under final Phase 9 Evidence and Review.

## Planned implementation links

- implemented-by:: [[src/intentatlas/review.py]]
- implemented-by:: [[src - intentatlas - cli.py|src/intentatlas/cli.py]]
- implemented-by:: [[src - intentatlas - change_report.py|src/intentatlas/change_report.py]]
- implemented-by:: [[src/intentatlas/test_outcomes.py]]
- implemented-by:: [[src - intentatlas - viewer.py|src/intentatlas/viewer.py]]
- implemented-by:: [[github - actions - intentatlas-review - action.yml|.github/actions/intentatlas-review/action.yml]]
- verified-by:: [[tests/test_review.py]]
- verified-by:: [[tests - test_cli.py|tests/test_cli.py]]
- verified-by:: [[tests - test_review_pilots.py|tests/test_review_pilots.py]]
- verified-by:: [[tests - test_e2e.py|tests/test_e2e.py]]

## Context

- Strategy: [[Brain/Phase 8-10 Strategy]]
- Kickoff: [[Sessions/2026-08-01 - Phase 9 kickoff]]
