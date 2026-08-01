---
id: ISSUE-020
type: issue
status: closed
phase: 10A
---
# ISSUE-020 — Implement content-addressed scan foundation

Implement [[Decisions/ADR-022 - Cache adapter fragments by declared input fingerprint]] for
[[Requirements/REQ-022 - Reuse trustworthy scan work safely]].

## Acceptance checklist

- [x] Built-in adapters declare complete cache input suffixes and cache versions.
- [x] Strict content-addressed fragment storage reuses only exact compatible inputs.
- [x] Changed, corrupt, unsafe, or unstable inputs rebuild or fail closed as specified.
- [x] Graph and fragment cache writes preserve the previous complete artifact on failure.
- [x] CLI reports reuse/rebuild behavior and matches a clean reference scan.
- [x] Focused/full tests, coverage, lint, security, CLI/UI E2E, determinism, and vault closure are
  recorded under final Phase 10A Evidence and Review.

## Planned implementation links

- implemented-by:: [[src - intentatlas - scanner.py|src/intentatlas/scanner.py]]
- implemented-by:: [[src - intentatlas - graph.py|src/intentatlas/graph.py]]
- implemented-by:: [[src - intentatlas - cli.py|src/intentatlas/cli.py]]
- verified-by:: [[tests - test_scanner.py|tests/test_scanner.py]]
- verified-by:: [[tests - test_graph.py|tests/test_graph.py]]
- verified-by:: [[tests - test_cli.py|tests/test_cli.py]]

## Context

- Strategy: [[Brain/Phase 8-10 Strategy]]
- Kickoff: [[Sessions/2026-08-01 - Phase 10A kickoff]]
