---
id: ISSUE-021
type: issue
status: closed
phase: 10B
---
# ISSUE-021 — Implement bounded open evidence imports

Implement [[Decisions/ADR-023 - Separate observations from aligned execution evidence]] for
[[Requirements/REQ-023 - Import open evidence without overstating certainty]].

## Acceptance checklist

- [x] Configuration exposes explicit bounded SCIP, SARIF, and execution-map report lists.
- [x] SCIP protobuf-JSON and SARIF 2.1.0 produce source-free deterministic file observations.
- [x] Execution maps add runtime test edges only at exact HEAD and mapped-artifact freshness.
- [x] Unsafe paths, malformed/binary/oversized JSON, duplicate keys, unknown fields, raw content,
  stale data, and excessive records are rejected or withheld as designed.
- [x] Existing evidence import, clean/incremental equivalence, and recommendations do not regress.
- [x] Documentation and examples state supported formats, trust boundaries, and non-claims.
- [x] Focused/full tests, coverage, lint, security, CLI/UI E2E, determinism, and vault closure pass.

## Planned implementation links

- implemented-by:: [[src - intentatlas - evidence.py|src/intentatlas/evidence.py]]
- implemented-by:: [[src - intentatlas - config.py|src/intentatlas/config.py]]
- implemented-by:: [[src - intentatlas - git_history.py|src/intentatlas/git_history.py]]
- verified-by:: [[tests - test_evidence.py|tests/test_evidence.py]]
- verified-by:: [[tests - test_config.py|tests/test_config.py]]
- verified-by:: [[tests - test_recommendations.py|tests/test_recommendations.py]]

## Context

- Strategy: [[Brain/Phase 8-10 Strategy]]
- Kickoff: [[Sessions/2026-08-01 - Phase 10B kickoff]]
